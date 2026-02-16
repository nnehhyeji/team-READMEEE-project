# # 2025년 9월~11월 데이터 생성용 코드
# # AI 프롬프트 확인용 + 목업 데이터 생성

import os
import sys
import time
import random
import requests  # 클로드 API 호출을 위해 requests 사용
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from questions.models import Question
from dotenv import load_dotenv

load_dotenv()

class Command(BaseCommand):
    help = 'Claude 3.7을 사용하여 다정한 소꿉친구 톤의 직구 질문을 생성합니다.'

    def handle(self, *args, **kwargs):
        sys.stdout.reconfigure(encoding='utf-8')
        
        # [0] GMS 클로드 설정
        api_key = os.getenv("GMS_KEY")
        endpoint = "https://gms.ssafy.io/gmsapi/api.anthropic.com/v1/messages"
        
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ GMS_KEY가 없습니다."))
            return

        # [1] 날짜 범위 설정
        start_date = date(2025, 9, 1)
        end_date = date(2025, 12, 31)
        current_date = start_date

        # [2] 카테고리 가이드라인
        category_guidelines = {
            'culture': '시사/문화: "옷 사이즈 다른데 가격 똑같은 건 왜일까?" 같은 세상의 의문.',
            'reflection': '자기성찰: "오늘 제일 뿌듯했던 순간은 언제야?", "전연인 재회, 찬성이야 반대야?" 같은 솔직한 질문.',
            'daily': '일상기록: "붕어빵 머리부터 먹어, 꼬리부터 먹어?", "탕수육 부먹? 찍먹?" 같은 가벼운 취향.',
            'creative': '창의적: "하늘이 빨간색이면 어떨 것 같아?", "지금 이름으로 삼행시 하나 지어줄래?" 같은 뜬금없는 미션.'
        }

        self.stdout.write(self.style.HTTP_INFO(f"⚡ Claude 3.7 '다정한 직구' 모드 시작!"))

        while current_date <= end_date:
            if Question.objects.filter(release_date=current_date).exists():
                current_date += timedelta(days=1)
                continue

            recent_qs = list(Question.objects.order_by('-id')[:20].values_list('content', flat=True))
            exclusion_text = "\n".join([f"- {q}" for q in recent_qs]) if recent_qs else "없음"
            category = random.choices(list(category_guidelines.keys()), weights=[30, 25, 25, 20])[0]

            # [3] Claude API 요청 데이터 설정
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "claude-3-7-sonnet-latest",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "너는 본론만 툭 던지는 10년 지기 친구야. 말이 길어지는 걸 혐오해. "
                            "상대방이 무슨 행동을 했다고 가정하지 말고, 궁금한 본론만 바로 물어봐.\n\n"
                            
                            "[질문 생성 4원칙 - 위반 시 실패]\n"
                            "1. 인칭대칭어 절대 금지: '나', '너', '네가', '나도', '너도', '우리'라는 단어를 단 한 번도 쓰지 마.\n"
                            "2. 상황 가정 금지: '사용자가 ~했을 때', '~라면' 같은 전제를 깔지 마. 그냥 현상에 대해 바로 물어봐.\n"
                            "3. 진짜 질문: '어쩌라고' 식의 감탄사가 아니라, 상대가 의견을 말할 수 있는 명확한 질문을 해.\n"
                            "4. 극도의 간결함: 수식어 다 빼고 한 문장으로 끝내.\n\n"
                            
                            f"현재 카테고리: [{category}]\n"
                            f"가이드 예시: {category_guidelines[category]}\n"
                            f"--- 최근 질문 목록 (중복 피할 것) ---\n{exclusion_text}"
                        )
                    }
                ]
            }

            try:
                response = requests.post(endpoint, headers=headers, json=payload)
                response_data = response.json()
                
                # Claude 응답 구조에서 텍스트 추출
                content = response_data['content'][0]['text'].strip().split('\n')[0]

                # DB 저장
                Question.objects.create(content=content, category=category, release_date=current_date)
                self.stdout.write(f"✅ {current_date} [{category}]: {content}")
                
                time.sleep(0.2) # 크레딧 소모 및 부하 방지

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ 에러 발생: {e}"))
                break

            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f"✨ Claude 3.7 질문 생성 완료!"))