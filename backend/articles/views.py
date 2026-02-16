from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, generics
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Count, F, Avg, Sum, Case, When, Value, BooleanField, ExpressionWrapper, FloatField
from django.utils import timezone
from datetime import timedelta
from collections import Counter
import os
from supabase import create_client, Client

# ==================== Signed URL 발급 View ====================
class GetUploadUrlView(generics.GenericAPIView):
    """
    [Security] 프론트엔드에게 업로드용 Signed URL 발급 (게시글용)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. 파일명 및 확장자 확인
        filename = request.data.get('filename')
        if not filename:
            return Response({'error': 'Filename is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Supabase 클라이언트 초기화
        from dotenv import load_dotenv
        load_dotenv()
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        # [Fallback] Supabase 설정이 없으면 로컬 업로드 모드로 전환
        if not url or not key:
            return Response({'storage': 'local'})
        
        supabase: Client = create_client(url, key)

        # 3. 경로 설정 (유저별 폴더 격리)
        # 예: uploads/user_id/timestamp_filename
        storage_path = f"uploads/{request.user.id}/{filename}"
        
        try:
            # 4. Signed URL 생성 (60초 유효)
            res = supabase.storage.from_('ReadMe-images').create_signed_upload_url(storage_path)
            
            return Response({
                'signedUrl': res['signed_url'],
                'path': storage_path
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import Article, Like, Comment, DwellTime
from .serializers import (
    ArticleSerializer,
    ArticleCreateSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    DwellTimeSerializer
)

# ==================== 헬퍼 함수 ====================

def update_consecutive_days(user):
    """
    연속 기록 일수 업데이트
    - 로직: 오늘 작성한 글이 '첫 번째' 글인 경우에만 어제 기록을 확인하여 갱신
    """
    today = timezone.localdate()
    
    # 1. 오늘 작성된 글의 개수 확인 (방금 저장된 글 포함)
    today_article_count = Article.objects.filter(
        author=user,
        created_at__date=today
    ).count()

    # 2. 오늘 작성한 글이 2개 이상이면 이미 갱신되었으므로 로직 종료 (중복 증가 방지)
    if today_article_count > 1:
        return

    # 3. 오늘 첫 글이라면, '어제' 쓴 글이 있는지 확인
    yesterday = today - timedelta(days=1)
    has_posted_yesterday = Article.objects.filter(
        author=user,
        created_at__date=yesterday
    ).exists()

    if has_posted_yesterday:
        # 어제도 썼다면 연속 기록 +1
        user.consecutive_days += 1
        if user.consecutive_days > user.max_consecutive_days:
            user.max_consecutive_days = user.consecutive_days
    else:
        # 어제 안 썼다면 연속 기록 1일로 초기화
        user.consecutive_days = 1
    
    user.save()

# ==================== 게시글 ViewSet ====================

class ArticleViewSet(viewsets.ModelViewSet):
    """
    게시글 CRUD, 좋아요, 댓글, 체류시간 기록을 처리하는 ViewSet
    """
    
    def get_queryset(self):
        return Article.objects.annotate(
            comment_count=Count('comments')
        ).select_related('author', 'question')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        if self.action == 'comment_create': 
             return CommentCreateSerializer 
        if self.action == 'comment_list': 
             return CommentSerializer
        if self.action == 'record_dwell_time':
            return DwellTimeSerializer
        return ArticleSerializer
    
    def get_permissions(self):
        # AllowAny: list (feed), retrieve, record_dwell_time, comment_list
        if self.action in ['list', 'retrieve', 'comment_list', 'record_dwell_time']:
            permission_classes = [AllowAny]
        else:
            # IsAuthenticated: create, destroy, like, comment_create, my_archive
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # [1] 게시글 목록 조회 (피드)
    def list(self, request, *args, **kwargs):
        """
        게시글 목록 조회 로직:
        1. 전체 피드 조회 시: 24시간 이내 + 공개 게시글만
        2. 타인 프로필 조회 시: 24시간 이내 + 공개 게시글만
        3. 내 프로필 조회 시: 시간 제한 없음 + 모든 내 게시글
        """
        username = request.query_params.get('username')
        now = timezone.now()
        
        # 1. 일단 전체 게시글에서 시작
        queryset = self.get_queryset()

        if username:
            # --- [프로필 페이지 접속 시] ---
            if request.user.is_authenticated and request.user.username == username:
                # (A) 내 프로필: 시간 제한 없이 내 글 전부 다 보여줌
                queryset = queryset.filter(author__username=username).order_by('-created_at')
            else:
                # (B) 타인 프로필: 24시간 이내 + 공개된 글만 보여줌
                queryset = queryset.filter(
                    author__username=username,
                    is_visible_to_others=True,
                    is_public=True,
                    expires_at__gt=now,
                    created_at__lte=now  
                ).order_by('-created_at')
        else:
            # --- [메인 피드 접속 시] ---
            # 기본 조건: 24시간 이내 & 미래 글 아님
            base_filters = {
                'is_visible_to_others': True,
                'expires_at__gt': now,
                'created_at__lte': now
            }
            
            # 공개 범위 조건: (전체 공개) OR (내 글)
            if request.user.is_authenticated:
                from django.db.models import Q
                queryset = queryset.filter(
                    Q(is_public=True) | Q(author=request.user),
                    **base_filters
                )
            else:
                # 비로그인 유저는 공개된 글만
                queryset = queryset.filter(
                    is_public=True,
                    **base_filters
                )

            # 로그인한 사용자의 경우 팔로우한 사람의 글을 우선 정렬
            if request.user.is_authenticated:
                following_ids = request.user.following.values_list('following_id', flat=True)
                
                queryset = queryset.annotate(
                    is_followed=Case(
                        When(author_id__in=following_ids, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField()
                    )
                ).order_by('-is_followed', '-created_at')
            else:
                # 비로그인: 최신순
                queryset = queryset.order_by('-created_at')

        # DRF 표준 페이지네이션 처리
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # [2] 게시글 작성
    def perform_create(self, serializer):
        # 실제 저장은 여기서 수행 (작성자 정보 주입)
        serializer.save(author=self.request.user)
        # 작성 후 연속 기록 업데이트 함수 호출
        update_consecutive_days(self.request.user)
    
    def create(self, request, *args, **kwargs):
        """게시글 작성 후 ArticleSerializer(상세 정보)로 응답"""
        # 1. 입력 시리얼라이저로 유효성 검사 및 저장
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # 2. 저장된 객체를 가져와서 출력용 시리얼라이저로 변환
        article_instance = serializer.instance
        article_with_counts = self.get_queryset().get(pk=article_instance.pk)
        
        output_serializer = ArticleSerializer(
            article_with_counts,
            context={'request': request}
        )
        
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    # [3] 게시글 상세 조회
    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        
        if not article.is_visible_to_others:
            if not request.user.is_authenticated or article.author != request.user:
                return Response(
                    {'error': '접근할 수 없는 게시글입니다.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    # [4] 게시글 삭제
    def destroy(self, request, *args, **kwargs):
        article = self.get_object()
        
        if article.author != request.user:
            return Response(
                {'error': '삭제 권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if timezone.now() > article.expires_at:
            return Response(
                {'error': '24시간이 지난 게시글은 삭제할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 

    # [5] 내 아카이브 조회 (검색 및 월별 필터링 추가)
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def my_archive(self, request):
        queryset = self.get_queryset().filter(author=request.user)

        # 1. 검색 (내용 or 질문 내용)
        search_query = request.query_params.get('search')
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(content__icontains=search_query) | 
                Q(question__content__icontains=search_query)
            )

        # 2. 날짜 필터링 (연도/월)
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if year and month:
            queryset = queryset.filter(
                created_at__year=year,
                created_at__month=month
            )
        
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    # [6], [7] 좋아요 토글
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        user = request.user
        
        # 24시간이 지난 게시글은 좋아요 금지
        if timezone.now() > article.expires_at:
             return Response(
                 {'error': '집계 기간(24시간)이 지난 글에는 좋아요를 누를 수 없습니다.'}, 
                 status=status.HTTP_400_BAD_REQUEST
             )

        like_instance = Like.objects.filter(user=user, article=article).first()

        if like_instance:
            like_instance.delete()
            Article.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
            return Response({'message': '좋아요를 취소했습니다.'})
        else:
            Like.objects.create(user=user, article=article)
            Article.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
            return Response({'message': '좋아요를 눌렀습니다.'}, status=status.HTTP_201_CREATED)

    # [11] 체류시간 기록
    @action(detail=True, methods=['POST'])
    def record_dwell_time(self, request, pk=None):
        article = self.get_object()
        
        # 4시간이 지난 게시글은 체류시간 집계 제외
        if timezone.now() > article.expires_at:
            return Response({'message': '집계 기간 종료로 기록되지 않음'}, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dwell_seconds = serializer.validated_data['dwell_seconds']
        
        DwellTime.objects.create(article=article, dwell_seconds=dwell_seconds)
        Article.objects.filter(pk=pk).update(
            view_count=F('view_count') + 1,
            total_dwell_time=F('total_dwell_time') + dwell_seconds
        )
        
        return Response(
            {'message': '체류시간이 기록되었습니다.'},
            status=status.HTTP_201_CREATED
        )

    # [8] 댓글 목록 조회
    @action(detail=True, methods=['GET'])
    def comment_list(self, request, pk=None):
        article = self.get_object()
        comments = article.comments.select_related('author').order_by('created_at')
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    # [9] 댓글 작성
    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def comment_create(self, request, pk=None):
        article = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comment = serializer.save(author=request.user, article=article)
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


# ==================== 기타 Views (댓글 삭제, 통계, 베스트) ====================

class CommentDeleteView(generics.DestroyAPIView):
    """[10] 댓글 삭제 (DELETE /comments/{id}/)"""
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyStatisticsView(generics.RetrieveAPIView):
    """[12] 내 통계 조회 (특정 달 필터링 적용)"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        now = timezone.now()

        # 1. 프론트엔드에서 보낸 파라미터(?year=2025&month=12) 읽기
        try:
            year = int(request.query_params.get('year', now.year))
            month = int(request.query_params.get('month', now.month))
        except (ValueError, TypeError):
            year = now.year
            month = now.month

        # 2. 특정 연도와 월로 게시글 필터링
        # 삭제된 게시글이 포함되지 않도록 하며, 해당 유저의 해당 달 기록만 가져오기
        my_articles = Article.objects.filter(
            author=user,
            created_at__year=year,
            created_at__month=month
        )
        
        total_count = my_articles.count()
        
        # 3. 데이터가 없을 때의 응답 처리 (해당 달에 글을 안 썼을 경우)
        if total_count == 0:
            return Response({
                'year': year,
                'month': month,
                'total_articles': 0,
                'consecutive_days': user.consecutive_days,
                'max_consecutive_days': user.max_consecutive_days,
                'emotion_distribution': {},
                'avg_dwell_time': 0,
                'like_stats': {'total': 0, 'average': 0}
            })
        
        # 4. 통계 계산
        aggregated_stats = my_articles.aggregate(
            total_dwell=Sum('total_dwell_time'),
            total_views=Sum('view_count'),
            total_likes=Sum('like_count'),
            avg_likes=Avg('like_count')
        )
        
        emotion_stats = my_articles.values('emotion').annotate(count=Count('id')).order_by('-count')
        emotion_distribution = {
            item['emotion']: {
                'count': item['count'],
                'percentage': round(item['count'] / total_count * 100, 1)
            }
            for item in emotion_stats
        }
        
        total_dwell = aggregated_stats['total_dwell'] or 0
        total_views = aggregated_stats['total_views'] or 0
        avg_dwell = round(total_dwell / total_views, 1) if total_views > 0 else 0
        
        return Response({
            'year': year,
            'month': month,
            'total_articles': total_count,
            'consecutive_days': user.consecutive_days,
            'max_consecutive_days': user.max_consecutive_days,
            'emotion_distribution': emotion_distribution,
            'avg_dwell_time': avg_dwell,
            'like_stats': {
                'total': aggregated_stats['total_likes'] or 0,
                'average': round(aggregated_stats['avg_likes'] or 0, 1)
            }
        })


class WordFrequencyView(generics.ListAPIView):
    """[13] 단어 빈도 분석 (특정 달의 유효한 게시글만 분석)"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()
        
        # 프론트엔드 파라미터를 정수(int)로 변환
        try:
            year = int(request.query_params.get('year', now.year))
            month = int(request.query_params.get('month', now.month))
        except (ValueError, TypeError):
            year = now.year
            month = now.month
        
        # 필터링 강화
        # 1. 작성자가 나여야 함
        # 2. 요청한 연도와 월이 일치해야 함
        # 3. 삭제된 데이터가 포함되지 않도록 함
        my_articles = Article.objects.filter(
            author=user,
            created_at__year=year,
            created_at__month=month,
        )
        
        # 만약 글이 하나도 없다면 빈 결과 반환
        if not my_articles.exists():
            return Response({'word_frequency': []})
        
        all_text = ' '.join([article.content for article in my_articles])
        words = all_text.split()
        
        # 불용어(의미 없는 단어) 리스트 보강
        stopwords = {'은', '는', '이', '가', '을', '를', '에', '의', '와', '과', '도', '으로', '로', '에서', '만', '까지', '했다', '있다', '하고', '거예요', '것 같아요'}
        words = [word for word in words if word not in stopwords and len(word) > 1]
        
        word_counts = Counter(words)
        top_20 = word_counts.most_common(20)
        
        return Response({
            'year': year,   # 확인용으로 연도/월을 응답에 포함
            'month': month,
            'word_frequency': [
                {'word': word, 'count': count}
                for word, count in top_20
            ]
        })


class BestArticleListView(generics.ListAPIView):
    """주간/월간 베스트 게시글 조회 (부모 클래스)"""
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]
    # 리스트 슬라이싱([:10]) 충돌 방지를 위해 페이지네이션 비활성화
    pagination_class = None
    
    def get_queryset(self):
        # 기본: 최근 N일 + 공개된 글
        time_limit = timezone.now() - self.time_delta
        return Article.objects.filter(
            created_at__gte=time_limit,
            is_visible_to_others=True
        ).select_related('author', 'question').annotate(
            comment_count=Count('comments')
        ).order_by('-like_count', '-total_dwell_time')[:3]

class WeeklyBestView(BestArticleListView):
    """[14] 지난주(월~일) 베스트 게시글"""
    # time_delta는 더 이상 사용하지 않고 get_queryset 오버라이딩
    
    def get_queryset(self):
        today = timezone.localdate()
        # 오늘이 월요일(0) ~ 일요일(6) 이면,
        # 이번주 시작(월) = 오늘 - weekday
        start_of_this_week = today - timedelta(days=today.weekday())
        # 지난주 시작(월) = 이번주 시작 - 7일
        start_of_last_week = start_of_this_week - timedelta(days=7)
        # 지난주 종료(일요일 23:59:59.999) = 이번주 시작 - 1초 (날짜 비교시에는 그냥 이번주 시작 직전까지)
        # created_at__lt = start_of_this_week 로 하면 됨.
        
        return Article.objects.filter(
            created_at__gte=start_of_last_week, # 지난주 월요일 00:00~
            created_at__lt=start_of_this_week,  # 이번주 월요일 00:00 전까지
            is_public=True #
        ).select_related('author', 'question').annotate(
            comment_count=Count('comments'),
            # 가중치 점수 계산 (좋아요 10점 + 체류시간 0.5점)
            score=ExpressionWrapper(
                F('like_count') * 10 + F('total_dwell_time') * 0.5,
                output_field=FloatField()
            )
        ).order_by('-score')[:3]


class MonthlyBestView(BestArticleListView):
    """[15] 월간 베스트 게시글"""
    time_delta = timedelta(days=30)