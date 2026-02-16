from rest_framework import serializers
from .models import Article, Like, Comment, DwellTime
from accounts.serializers import UserSummarySerializer
from questions.serializers import QuestionSerializer
from questions.models import Question
from django.db import IntegrityError # 중복 작성 오류 처리를 위해 필요


# [1] 게시글 리스트/상세 시리얼라이저
class ArticleSerializer(serializers.ModelSerializer):
    """게시글 조회 (FR-015 ~ FR-018)"""
    author = UserSummarySerializer(read_only=True)
    question = QuestionSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    # 모델의 @property와 명시적으로 연결
    avg_dwell_time = serializers.FloatField(read_only=True) 
    # View에서 annotate로 제공
    comment_count = serializers.IntegerField(read_only=True)
    # Weekly Best 가중치 점수 (annotate로 계산됨)
    score = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'question', 'content', 'image', 'emotion',
            'is_public', 'is_visible_to_others',
            'music_title', 'music_artist', 
            'like_count', 'view_count', 'avg_dwell_time', 'comment_count',
            'is_liked', 'created_at', 'expires_at', 'score'
        ]
        read_only_fields = [
            'id', 'author', 'like_count', 'view_count', 
            'is_visible_to_others', 'created_at', 'expires_at'
        ]
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, article=obj).exists()
        return False

    # [보안 로직] 이미지 URL을 Signed URL로 변환하여 반환
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        

        
        # 이미지가 있고, 문자열(URL) 형태라면 처리
        if instance.image:
            image_url = str(instance.image)
            
            # 1. 로컬 저장소 파일인 경우 (media/)
            if not image_url.startswith('http'):
                request = self.context.get('request')
                from django.conf import settings
                media_url = getattr(settings, 'MEDIA_URL', '/media/')
                
                if not image_url.startswith(media_url):
                    full_media_path = f"{media_url}{image_url}"
                else:
                    full_media_path = image_url
                
                if request:
                    ret['image'] = request.build_absolute_uri(full_media_path)
                else:
                    ret['image'] = full_media_path
            
            # 2. Supabase Storage URL인 경우 (이미 URL 형태)
            elif 'ReadMe-images' in image_url:
                try:
                    import os
                    supabase_url = os.environ.get("SUPABASE_URL")
                    if supabase_url:
                        if not supabase_url.endswith('/'):
                            supabase_url += '/'
                        
                        # 경로가 포함된 형태면 base_url과 결합 (만약 전체 URL이 아닐 경우)
                        if 'storage/v1/object/public' not in image_url:
                             file_path = image_url.split('ReadMe-images/')[-1]
                             ret['image'] = f"{supabase_url}storage/v1/object/public/ReadMe-images/{file_path}"
                except Exception:
                    pass
                    
        return ret


class ArticleCreateSerializer(serializers.ModelSerializer):
    """게시글 작성 (FR-007 ~ FR-011)"""
    question_id = serializers.IntegerField(write_only=True)
    # File과 String 모두 수용
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Article
        fields = [
            'content', 'emotion', 'image', 'question_id', 
            'is_public', 'music_title', 'music_artist'
        ]
    
    def validate_is_public(self, value):
        """FormData로 전송된 'true'/'false' 문자열 처리"""
        if isinstance(value, str):
            return value.lower() == 'true'
        return value

    def validate_content(self, value):
        """내용 검증"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("내용을 입력해주세요.")
        if len(value) > 1000:
            raise serializers.ValidationError("내용은 최대 1000자입니다.")
        return value
    
    def validate(self, data):
        """질문 존재 여부 및 중복 작성 제한"""
        request = self.context.get('request')
        question_id = data.get('question_id')
        
        if question_id is None:
            raise serializers.ValidationError({"question_id": "질문 ID가 필요합니다."})
        
        # 1. 질문 존재 여부 확인 및 객체로 변환
        try:
            question_instance = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": "존재하지 않는 질문입니다."})
        
        # 2. 중복 작성 확인
        if Article.objects.filter(author=request.user, question=question_instance).exists():
            raise serializers.ValidationError("이미 해당 질문에 대한 게시글을 작성했습니다.")
        
        # question_id를 question 객체로 대체하여 create 메서드로 전달 준비
        data['question'] = question_instance
        data.pop('question_id')
        
        return data
    
    # DRF 표준에 맞게 create 메서드 간결화 (author를 View에서 전달받음)
    def create(self, validated_data):
        image_data = validated_data.get('image')
        
        # 만약 업로드된 파일(File object)인 경우 로컬에 저장하고 경로를 문자열로 변환
        if image_data and not isinstance(image_data, str):
            from django.core.files.storage import default_storage
            from uuid import uuid4
            ext = image_data.name.split('.')[-1]
            filename = f"articles/{uuid4()}.{ext}"
            path = default_storage.save(filename, image_data)
            validated_data['image'] = path
            
        return Article.objects.create(**validated_data)


# [3] 좋아요 시리얼라이저
class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ['id', 'user', 'article', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


# [4] 댓글 조회 시리얼라이저
class CommentSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


# [5] 댓글 작성 시리얼라이저
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        """댓글 내용 검증"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("댓글 내용을 입력해주세요.")
        if len(value) > 300:
            raise serializers.ValidationError("댓글은 최대 300자입니다.")
        return value


# [6] 체류시간 시리얼라이저
class DwellTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DwellTime
        fields = ['dwell_seconds']
        read_only_fields = ['article']
    
    def validate_dwell_seconds(self, value):
        """ 체류시간 범위 검증 및 오류 반환"""
        if value < 1:
            raise serializers.ValidationError("체류시간은 1초 이상이어야 합니다.")
        if value > 120:
             # 값을 변환하지 않고, 오류를 반환하여 클라이언트에게 알림 (DRF 표준)
             raise serializers.ValidationError("체류시간은 최대 120초입니다.")
        return value