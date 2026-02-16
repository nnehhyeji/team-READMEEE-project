from django.core.management.base import BaseCommand
from django.utils import timezone
from questions.models import Question
import os
import sys
import random
import json
import requests

def get_youtube_video_id(song_title, artist):
    """
    YouTube Data API v3를 사용하여 공식 비디오 ID를 검색합.
    """
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    search_url = "https://www.googleapis.com/youtube/v3/search"

    if not youtube_api_key:
        return None

    params = {
        'key': youtube_api_key,
        'q': f"{artist} {song_title} official audio",
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1
    }

    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            results = response.json().get('items')
            if results:
                return results[0]['id']['videoId']
    except Exception as e:
        # print(f"⚠️ YouTube 검색 실패: {e}") # 디버그 로그 제거
        pass
    return None

class Command(BaseCommand):
    help = 'Claude 3.7 Sonnet을 통해 시기에 맞는 질문과 추천 음악을 생성합니다.'

    def handle(self, *args, **kwargs):
        # [0] 인코딩 설정
        sys.stdout.reconfigure(encoding='utf-8')

        # [1] 환경변수 확인
        api_key = os.getenv("GMS_API_KEY") or os.getenv("GMS_KEY")
        endpoint = "https://gms.ssafy.io/gmsapi/api.anthropic.com/v1/messages"
        
        today = timezone.localdate()
        month = today.month
        day = today.day

        # [2] 중복 확인
        if Question.objects.filter(release_date=today).exists():
            self.stdout.write(self.style.WARNING(f'[중복] {today} 날짜의 질문이 이미 존재합니다.'))
            return

        # [3] 시즈널 모드 체크 (연말: 12/24~12/31, 연초: 1/1~1/7)
        is_seasonal = False
        seasonal_type = None

        if month == 12 and day >= 24:
            is_seasonal = True
            seasonal_type = "YEAR_END"
        elif month == 1 and day <= 7:
            is_seasonal = True
            seasonal_type = "NEW_YEAR"

        # [4] 카테고리 및 프롬프트 선정
        if is_seasonal:
            selected_category = 'reflection'
            if seasonal_type == "YEAR_END":
                target_topic = '한 해를 차분히 마무리하며 소중한 추억이나 나 자신의 성장을 돌아볼 수 있는 따뜻하고 깊이 있는 회고 질문'
            else:
                target_topic = '새해를 맞아 새로운 시작, 설레는 목표, 혹은 나에게 주고 싶은 용기에 대한 희망찬 질문'
            self.stdout.write(self.style.NOTICE(f'🎄 [시즈널 모드] {seasonal_type} 테마로 질문을 생성합니다.'))
        else:
            categories = ['culture', 'reflection', 'daily', 'creative']
            weights = [30, 25, 25, 20]
            selected_category = random.choices(categories, weights=weights, k=1)[0]
            
            category_prompts = {
                'culture': '요즘 유행하는 생활 습관이나 사람들의 미묘한 행동 변화에 대해 가벼운 대화 주제',
                'reflection': '오늘 하루의 기분이나 작은 취향을 돌아볼 수 있는 편안한 질문',
                'daily': '오늘 먹은 것, 본 것, 들은 것 중 아주 구체적인 하나에 대해 묻는 짧은 질문',
                'creative': '일상적인 물건이나 당연한 상황을 평소와 다르게 생각해보게 만드는 엉뚱한 질문'
            }
            target_topic = category_prompts.get(selected_category, '일상적인 질문')

        # [5] AI 질문 생성 (Claude 3.7 Sonnet)
        content, rec_title, rec_artist, rec_reason = "", "", "", ""
        final_category = selected_category
        video_id = None

        try:
            if not api_key:
                raise Exception("API 키가 설정되지 않음")
            
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "claude-3-7-sonnet-latest",
                "max_tokens": 600,
                "system": (
                    "너는 감성적인 에세이 작가이자 음악 큐레이터야. "
                    "READMEEE라는 서비스의 사용자들이 매일 아침 받는 질문을 작성해야 해. "
                    "반드시 JSON 형식으로만 응답하고 다른 설명은 하지 마."
                ),
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"오늘의 주제: {target_topic}\n"
                            "1. 질문은 친근한 '해요체'를 사용하고, 너무 길지 않게 핵심만 짚어줘.\n"
                            "2. 답변할 때 배경음으로 깔기 좋은 감성적인 노래(인디, 재즈 등)를 추천해줘.\n"
                            "3. 추천 이유는 한 문장으로 시적으로 표현해줘.\n\n"
                            "응답 형식(JSON):\n"
                            "{\n"
                            '  "question": "질문 내용",\n'
                            '  "music_title": "노래 제목",\n'
                            '  "music_artist": "가수 이름",\n'
                            '  "reason": "추천 이유"\n'
                            "}"
                        )
                    }
                ]
            }

            response = requests.post(endpoint, headers=headers, json=payload)
            if response.status_code != 200:
                raise Exception(f"API Error: {response.status_code}")

            response_data = response.json()
            raw_content = response_data['content'][0]['text'].strip()

            # JSON 파싱 및 정제
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(raw_content)
            content = data.get('question', '')
            rec_title = data.get('music_title', '')
            rec_artist = data.get('music_artist', '')
            rec_reason = data.get('reason', '')
            
            # [NEW] 유튜브 비디오 ID 검색
            if rec_title and rec_artist:
                video_id = get_youtube_video_id(rec_title, rec_artist)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'⚠️ [AI 실패] {e}'))
            # 백업 로직 (시즌별 백업 질문 추가)
            if is_seasonal and seasonal_type == "YEAR_END":
                backup = ("올해 당신의 마음을 가장 따뜻하게 했던 한 문장은 무엇인가요?", "기억해줘요", "박화요비", "지나온 시간 속 소중한 목소리를 떠올려보세요.")
            elif is_seasonal and seasonal_type == "NEW_YEAR":
                backup = ("새해의 첫 페이지에 가장 먼저 적고 싶은 단어는?", "Start", "가호", "새로운 시작의 설렘을 가득 담아.")
            else:
                backup = ("오늘 나에게 해주고 싶은 가장 다정한 인사는?", "수고했어, 오늘도", "옥상달빛", "오늘 하루도 치열하게 보낸 당신에게.")
            
            content, rec_title, rec_artist, rec_reason = backup
            final_category = 'reflection'
            # 백업 유튜브 ID 검색? ( 백업 곡들은 유명해서 하드코딩 가능하지만 로직 통일 위해 검색 시도)
            video_id = get_youtube_video_id(rec_title, rec_artist)

        # [6] DB 저장
        Question.objects.create(
            content=content,
            category=final_category,
            rec_title=rec_title,
            rec_artist=rec_artist,
            rec_reason=rec_reason,
            rec_video_id=video_id, # [비디오 ID 저장
            release_date=today
        )
        self.stdout.write(self.style.SUCCESS(f'✅ [등록 완료] {today} 질문 등록 (테마: {seasonal_type if is_seasonal else selected_category})'))

        # [7] 알림 발송 (FR-032)
        try:
            from django.contrib.auth import get_user_model
            from notifications.models import Notification
            from django.db.models import Count
            from articles.models import Article
            from datetime import timedelta
            
            User = get_user_model()
            
            # 1. Daily 알림: 구독한 모든 사용자에게 발송
            daily_subscribers = User.objects.filter(noti_daily=True)
            daily_noti_count = 0
            
            for user in daily_subscribers:
                Notification.objects.create(
                    recipient=user,
                    sender=user, # 시스템 알림
                    notification_type='daily'
                )
                daily_noti_count += 1
            
            self.stdout.write(f"📢 [Daily] {daily_noti_count}명에게 새 질문 알림 발송")

            # 2. Weekly 알림: 월요일이면 지난주 베스트 선정 및 알림
            if today.weekday() == 0: # 월요일 체크
                start_of_this_week = today - timedelta(days=today.weekday())
                start_of_last_week = start_of_this_week - timedelta(days=7)
                
                # 지난주 베스트 3 선정
                weekly_best_articles = Article.objects.filter(
                    created_at__gte=start_of_last_week,
                    created_at__lt=start_of_this_week,
                    is_visible_to_others=True
                ).annotate(
                    like_cnt=Count('likes')
                ).order_by('-like_cnt', '-total_dwell_time')[:3]
                
                weekly_noti_count = 0
                for article in weekly_best_articles:
                    if article.author.noti_weekly:
                        Notification.objects.create(
                            recipient=article.author,
                            sender=article.author, # 시스템 알림
                            notification_type='weekly',
                            article=article
                        )
                        weekly_noti_count += 1
                
                self.stdout.write(f"🏆 [Weekly] 지난주 베스트 {len(weekly_best_articles)}개 선정, {weekly_noti_count}명에게 축하 알림 발송")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ [알림 실패] {str(e)}'))
