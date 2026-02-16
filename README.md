# READMEEE

**"Read Me, Read My Log"**
매일 AI가 건네는 질문에 답하며 나를 기록하고, 타인과 연결되는 소셜 다이어리 플랫폼입니다.

---

## 📅 프로젝트 개요
*   **개발 기간**: 2024.12
*   **주요 컨셉**:
    *   **Daily Question**: Claude 3.7 AI가 매일 새로운 질문을 생성합니다.
    *   **Deep Connection**: 24시간 후 비공개되는 글을 통해 "지금 이 순간"에 집중합니다.
    *   **Visual Archive**: 나의 기록이 점들을 잇는 선으로 시각화됩니다 (Connecting Dots).

---

## ✨ 핵심 기능

### 1. AI 기반 콘텐츠 생성 (`backend/questions`)
*   **Daily Question**: 매일 자정, AI가 '자기성찰', '창의성', '추억' 등 다양한 카테고리의 질문을 생성합니다.
*   **Seasonal Logic**: 연말(회고), 새해(다짐) 등 시즌에 맞는 테마 질문을 우선 배정합니다.
*   **Music Recommendation**: 질문의 분위기에 어울리는 음악을 AI가 추천하고, **YouTube API**를 통해 바로 재생 가능한 링크를 제공합니다.

### 2. 몰입형 사용자 경험 (`frontend`)
*   **Masonry Feed**: 다양한 길이의 답변을 심미적으로 배치하는 벽돌형 레이아웃을 구현했습니다.
*   **Connecting Dots**: 사용자의 기록이 하나하나의 점이 되어, 선으로 이어지는 독창적인 아카이빙 UI를 제공합니다.
*   **Scroll & Animation**: 부드러운 스크롤 인터랙션과 감성적인 마이크로 인터랙션을 적용했습니다.

### 3. 소셜 및 커뮤니티 (`accounts`, `articles`)
*   **Social Login**: Google, Kakao, Naver 소셜 로그인 및 계정 연동을 지원합니다.
*   **Interaction**: 팔로우, 좋아요, 댓글 기능을 통해 다른 유저와 소통할 수 있습니다.
*   **Weekly Best**: '좋아요' 수와 '체류 시간(Dwell Time)'을 복합적으로 계산하여 주간 베스트 글을 선정합니다.

### 4. 데이터 분석 및 통계 (`statistics`)
*   **Word Cloud**: 내가 자주 사용한 단어를 시각적으로 보여줍니다.
*   **Monthly Report**: 월별 기록 횟수, 감정 흐름 등을 통계로 제공합니다.

---

## 🛠 기술 스택

### Backend
*   **Framework**: Django 5.2, Django REST Framework (DRF)
*   **Database**: PostgreSQL / SQLite (Dev)
*   **Scheduling**: APScheduler (일일 질문 자동 생성)
*   **AI & API**: Anthropic Claude 3.7 Sonnet, YouTube Data API v3
*   **Auth**: JWT, OAuth2 (Social Login), Supabase (Storage)

### Frontend
*   **Framework**: Vue.js 3 (Composition API)
*   **State Management**: Pinia
*   **Styling**: Tailwind CSS, Pretendard Font
*   **HTTP Client**: Axios (Iterceptors 적용)


---

## 📡 API Reference

```bash
# 🔐 인증 및 계정 (Accounts)
POST /api/accounts/register/        # 회원가입
POST /api/accounts/login/           # 로그인
POST /api/accounts/logout/          # 로그아웃
GET  /api/accounts/profile/my/      # 내 프로필 정보 조회
POST /api/accounts/profile/update/  # 프로필 정보 수정
POST /api/accounts/password/change/ # 비밀번호 변경
POST /api/accounts/upload-url/      # 이미지 업로드용 URL 발급 (Smart Fallback)
GET  /api/accounts/users/<str:un>/  # 타인 프로필 조회
POST /api/accounts/users/<str:un>/follow/ # 팔로우/언팔로우 토글

# ❓ 리멤버 질문 (Questions)
GET  /api/questions/today/          # 오늘의 질문 조회
GET  /api/questions/<str:date>/     # 특정 날짜의 질문 조회

# ✍️ 기록 및 소통 (Articles)
GET  /api/articles/                 # 전체 게시글 목록 (피드)
POST /api/articles/                 # 오늘의 답변 등록 (이미지 포함)
GET  /api/articles/<int:id>/        # 게시글 상세 조회
GET  /api/articles/weekly_best/     # 주간 베스트 게시글 목록
POST /api/articles/<int:id>/like/   # 좋아요 토글
POST /api/articles/<int:id>/comments/ # 댓글 등록
DELETE /api/articles/comments/<int:id>/ # 댓글 삭제 (본인)

# 📊 통계 (Statistics)
GET  /api/articles/statistics/my/   # 사용자 기록 통계 (월별 빈도 등)
GET  /api/articles/statistics/word_frequency/ # 단어 빈도 분석 (워드클라우드용)
```

---

## 📂 상세 프로젝트 구조 및 설명

```text
v2_ReadMe/
├── README.md                   # 프로젝트 전체 개요 및 실행 가이드
├── .gitignore                  # Git 제외 파일 목록 (db.sqlite3, .env 등 포함 여부 관리)
│
├── backend/                    # [Backend] Django REST API 서버
│   ├── manage.py               # Django 프로젝트 관리 커맨드 (runserver, migrate 등)
│   ├── requirements.txt        # Python 의존성 패키지 목록
│   ├── .env                    # (비공개) 환경변수 (Secret Key, DB URL, API Keys)
│   ├── .env.example            # 환경변수 예시 파일 (제출용 가이드)
│   ├── total_data.json         # [최종] 미디어 경로가 로컬로 수정된 전체 데이터 (loaddata용) - sqlite3 사용 시, 해당 파일로 loaddata
│   ├── data.json               # [최종] 미디어 경로가 로컬로 수정된 전체 데이터 (loaddata용) - postgresql 사용 시, 해당 파일로 loaddata
│   ├── download_media.py       # [유틸] Supabase 이미지를 로컬 media/로 일괄 다운로드하는 스크립트
│   ├── db.sqlite3              # 로컬 데이터베이스 파일 (SQLite)
│   │
│   ├── daylog/                 # [Project Config]
│   │   ├── settings.py         # 프로젝트 설정 (DB, JWT, CORS, Smart Fallback 로직 포함)
│   │   ├── urls.py             # 루트 URL 설정 (Media/Static 서빙 포함)
│   │   └── wsgi.py             # WSGI 서버 진입점
│   │
│   ├── accounts/               # [App] 사용자 인증 및 프로필
│   │   ├── models.py           # User(확장), Follow 모델 정의
│   │   ├── views.py            # 회원가입, 로그인, 프로필 조회/수정 (Storage Fallback 뷰 포함)
│   │   └── serializers.py      # 유저 정보 직렬화 (프로필 이미지 경로 처리)
│   │
│   ├── questions/              # [App] AI 질문 생성 (Core)
│   │   ├── models.py           # Question 모델 (질문 내용, 추천 음악 등)
│   │   └── management/commands/
│   │       ├── generate_question.py # [배치] Claude API 연동 일일 질문 생성 스크립트
│   │       ├── seed_questions.py    # [배치] 소꿉친구 말투 2025년 데이터 생성용 스크립트
│   │       ├── seed_music.py        # [배치] Gemini 연동 음악 추천 및 유튜브 ID 저장 스크립트
│   │       └── run_scheduler.py     # APScheduler 실행 스크립트
│   │
│   ├── articles/               # [App] 게시글 및 상호작용
│   │   ├── models.py           # Article, Comment, Like 모델
│   │   ├── views.py            # 게시글 CRUD 및 주간 베스트 로직
│   │   └── serializers.py      # 게시글 직렬화 (이미지 업로드 및 로컬/Cloud 경로 변환)
│   │
│   ├── notifications/          # [App] 알림 시스템
│   │   └── models.py           # 알림 생성 및 읽음 처리
│   │
│   └── media/                  # [Storage] 사용자 업로드 파일 저장소
│       ├── profiles/           # 유저 프로필 이미지 저장 폴더 (download_media 실행 시 생성)
│       └── articles/           # 게시글 첨부 이미지 저장 폴더 (download_media 실행 시 생성)
│
└── frontend/                   # [Frontend] Vue.js 3 Client
    ├── package.json            # Node.js 패키지 의존성 및 스크립트
    ├── vite.config.js          # Vite 필드 설정 (프록시 설정 포함)
    └── src/
        ├── main.js             # 앱 진입점 (Pinia, Router 마운트)
        ├── App.vue             # 루트 컴포넌트
        │
        ├── api/                # [Network]
        │   └── axios.js        # Axios 인스턴스 및 인터셉터
        │
        ├── lib/                # [Library]
        │   └── supabase.js     # Supabase SDK 초기화 설정
        │
        ├── components/         # [UI Components]
        │   ├── NavBar.vue      # 상단 네비게이션
        │   ├── ArticleCard.vue # 피드 게시글 카드
        │   ├── MasonryGrid.vue # 벽돌형 레이아웃 컴포넌트
        │   └── Modals/         # 각종 팝업 (WriteModal, AlertModal 등)
        │
        ├── stores/             # [State Management - Pinia]
        │   ├── auth.js         # 로그인 및 프로필 업데이트 로직
        │   ├── articles.js     # 게시글 CRUD 및 좋아요 처리
        │   └── question.js     # 오늘의 질문 데이터 상태
        │
        └── views/              # [Pages]
            ├── MainFeed.vue    # 메인 페이지 (피드)
            ├── ProfilePage.vue # 개인 프로필 (Connecting Dots 시각화)
            ├── SettingsPage.vue# 환경설정 (이미지 업로드 Fallback 로직 적용)
            └── BestAnswers.vue # 주간 베스트 페이지
```

---

## � 외부 API 서비스

| 기능 | API | 모델/버전 | 용도 |
| :--- | :--- | :--- | :--- |
| 질문 텍스트 생성 | Anthropic Claude | `claude-3-7-sonnet` | 매일 새로운 자아성찰 질문 AI 생성 |
| 음악 추천 | Google Gemini | `gemini-2.0-flash` | 질문 분위기에 어울리는 노래 추천 |
| 음악 검색 | YouTube Data | API v3 | 추천된 곡의 재생 가능 ID 검색 |
| 소셜 로그인 | Google/Kakao/Naver | OAuth 2.0 | 간편 로그인 및 계정 연동 |
| 미디어 저장 | Supabase Storage | Cloud Storage | 사용자 프로필 및 게시글 이미지 저장 |

---

## �🚀 설치 및 실행 방법

### 1. Backend 실행
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate  # Windows

# 패키지 설치
pip install -r requirements.txt

# 마이그레이션 (DB 생성)
python manage.py migrate

# 데이터 로드 (초기 데이터 복원)
# 주의: db.sqlite3는 gitignore에 포함되므로, 제출된 total_data.json을 통해 데이터를 복구해야 합니다.
# total_data.json은 sqlite3 사용 시, 해당 파일로 loaddata
python manage.py loaddata total_data.json
# data.json은 postgresql 사용 시, 해당 파일로 loaddata
python manage.py loaddata data.json

> [!IMPORTANT]
> 데이터를 새로 로드한 후에는 기존 브라우저의 로그인 세션이 만료될 수 있습니다. 만약 게시글 작성 중 권한 에러(401)가 발생한다면, **로그아웃 후 다시 로그인**하여 토큰을 갱신해 주세요.

# 서버 실행
python manage.py runserver

> [!TIP]
> **심사 위원을 위한 무설정 실행 지원**: 본 프로젝트는 별도의 `.env` 설정이 없더라도 심사용 기본 `SECRET_KEY`와 `DEBUG=True` 모드로 자동 전환되어 즉시 실행 가능한 상태로 구성되어 있습니다.
```

### 2. Frontend 실행
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 💡 사진 업로드 및 저장 방식 (Smart Fallback)
본 프로젝트는 심사 환경의 편의를 위해 **하이브리드 스토리지 시스템**을 갖추고 있습니다.
- **로컬 모드 (권장)**: `.env`에 Supabase 설정이 비어 있는 경우, 시스템이 이를 자동으로 감지하여 모든 사진을 서버의 `media/` 폴더에 저장하고 서빙합니다. 제출된 `total_data.json`은 이미 이 방식으로 최적화되어 있습니다.
- **Supabase 모드**: `.env`에 `SUPABASE_URL`과 `SUPABASE_KEY`를 설정하면, 모든 사진은 Cloud Storage(Supabase)에 저장됩니다. (Signed URL 방식 사용)
- **경로 최적화**: 로컬 개발 환경(SQLite)에서도 프론트엔드와 이미지 경로 충돌이 없도록, 모든 이미지 API 응답은 서버 호스트를 포함한 **절대 URL**로 자동 변환되어 전달됩니다.
- **전환 시점**: 프론트엔드와 백엔드가 실시간으로 통신하여 최적의 업로드 방식을 결정하므로 별도의 설정 변경 없이 즉시 테스트가 가능합니다.



---

## 🚀 배포 (Deployment)

-   **Frontend**: Vercel (배포 예정)
-   **Backend**: AWS Elastic Beanstalk (배포 예정)
-   **Database**: Supabase PostgreSQL (연동 완료)
-   **Storage**: Supabase Storage (연동 완료)
## 👥 팀원 소개 (Team)

> [!NOTE]
> 본 프로젝트는 프론트엔드와 백엔드의 엄격한 구분 없이, 전 팀원이 **풀스택(Full Stack)**으로 긴밀하게 협업하여 완성했습니다. 특정 개인이 한 파트를 온전히 담당하기보다 서로의 기술적 부족함을 보완하며 모든 핵심 기능을 함께 구현했습니다.

| 이름 | 역할 | 구성 내용 |
| :--- | :--- | :--- |
| **류지우** | Full Stack Developer | **Backend** (AI 질문 추출 로직, 주간 베스트 알고리즘, 소셜 로그인 연동, 데이터 마이그레이션), **Frontend** (사용자 프로필 & 아카이빙 UI, API 인터셉터 및 데이터 통신 로직) |
| **양혜지** | Full Stack Developer | **Frontend** (Masonry Grid 피드 레이아웃, Connecting Dots 시각화 엔진, PWA 환경 구축), **Backend** (이미지 업로드 Smart Fallback 로직, 통계/단어 빈도 데이터 API 설계) |


