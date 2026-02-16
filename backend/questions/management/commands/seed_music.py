from django.core.management.base import BaseCommand
from django.utils import timezone
from questions.models import Question
from datetime import date, timedelta
import os
import sys
import json
import requests
import time

def get_youtube_video_id(song_title, artist):
    """
    YouTube Data API v3 (Official)를 사용하여 비디오 ID를 검색합니다.
    """
    # 💡 .env에서 전용 유튜브 API 키를 가져옵니다.
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    search_url = "https://www.googleapis.com/youtube/v3/search"

    if not youtube_api_key:
        print("❌ YOUTUBE_API_KEY가 설정되지 않았습니다.")
        return None

    params = {
        'key': youtube_api_key,
        'q': f"{artist} {song_title} official audio",
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1
    }

    try:
        # 공식 API는 표준 GET 요청을 사용합니다.
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            results = response.json().get('items')
            if results:
                # 💡 문서 구조에 따라 id 객체 내부의 videoId를 추출합니다.
                return results[0]['id']['videoId']
        else:
            print(f"⚠️ YouTube API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ 유튜브 검색 중 오류: {e}")
    return None

class Command(BaseCommand):
    help = 'Gemini(GMS)로 음악을 추천받고 공식 YouTube API로 ID를 저장합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')

    def handle(self, *args, **kwargs):
        sys.stdout.reconfigure(encoding='utf-8')
        
        # 💡 Gemini 호출을 위한 GMS 키 설정
        gms_key = os.getenv("GMS_API_KEY") or os.getenv("GMS_KEY")
        if not gms_key:
            self.stdout.write(self.style.ERROR("❌ GMS_KEY가 없습니다."))
            return

        # GMS Proxy Gemini Endpoint
        gemini_endpoint = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={gms_key}"
        
        # 날짜 설정
        start_date = date.fromisoformat(kwargs['start']) if kwargs['start'] else date(2025, 9, 1)
        end_date = date.fromisoformat(kwargs['end']) if kwargs['end'] else date(2025, 12, 31)
        current_date = start_date

        self.stdout.write(self.style.HTTP_INFO(f"🚀 데이터 생성 시작: {start_date} ~ {end_date}"))

        # 기존 추천 곡 가져오기 (중복 방지용)
        existing_questions = Question.objects.exclude(rec_title__isnull=True).exclude(rec_title='')
        used_music = set()
        for q in existing_questions:
            if q.rec_title and q.rec_artist:
                used_music.add(f"{q.rec_artist} - {q.rec_title}")
        
        self.stdout.write(f"📋 이미 추천된 곡 수: {len(used_music)}개")

        while current_date <= end_date:
            question = Question.objects.filter(release_date=current_date).first()
            
            if not question:
                current_date += timedelta(days=1)
                continue
                
            # 1. 이미 추천은 있는데 유튜브 ID만 없는 경우 보완
            if question.rec_title and not question.rec_video_id:
                self.stdout.write(f"🔍 {current_date}: 기존 추천곡의 유튜브 ID 검색 중...")
                video_id = get_youtube_video_id(question.rec_title, question.rec_artist)
                if video_id:
                    question.rec_video_id = video_id
                    question.save()
                    self.stdout.write(self.style.SUCCESS(f"✅ ID 업데이트: {video_id}"))
                current_date += timedelta(days=1)
                continue

            # 2. 신규 추천 생성 (데이터가 아예 없는 경우)
            if not question.rec_title:
                self.stdout.write(f"📝 {current_date} 질문 분석 중: {question.content}")

                payload = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                f"질문: \"{question.content}\"\n"
                                "위 질문에 어울리는 음악 1곡을 JSON 형식으로 추천해줘. "
                                "이유는 담백하게 한 줄로 작성하고 뻔한 AI 추천은 피할 것.\n"
                                f"제외할 곡(이미 추천함): {', '.join(list(used_music))}\n"
                                "형식: {\"music_title\": \"\", \"music_artist\": \"\", \"reason\": \"\"}"
                            )
                        }]
                    }],
                    "generationConfig": {"response_mime_type": "application/json"}
                }
                
                try:
                    res = requests.post(gemini_endpoint, json=payload)
                    if res.status_code == 200:
                        res_json = res.json()
                        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                        
                        # Markdown 코드 블록 제거 로직
                        if "```json" in raw_text:
                            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                        
                        data = json.loads(raw_text)
                        
                        question.rec_title = data.get('music_title')
                        question.rec_artist = data.get('music_artist')
                        question.rec_reason = data.get('reason')
                        
                        # 즉시 유튜브 ID 검색
                        video_id = get_youtube_video_id(question.rec_title, question.rec_artist)
                        question.rec_video_id = video_id
                        question.save()

                        # 중복 방지 목록에 추가
                        used_music.add(f"{question.rec_artist} - {question.rec_title}")
                        
                        self.stdout.write(self.style.SUCCESS(f"🎵 추천 완료: {question.rec_title}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"❌ Gemini API 오류: {res.status_code}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ 처리 중 에러: {e}"))

            current_date += timedelta(days=1)
            time.sleep(0.5) # API 할당량 보호

        self.stdout.write(self.style.SUCCESS("✨ 모든 작업이 완료되었습니다!"))