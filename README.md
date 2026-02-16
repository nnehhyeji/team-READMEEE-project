# 📘 READMEEE

> **"Read Me, Read My Log"**<br>
> 매일 AI가 건네는 질문에 답하며 나를 기록하고, 타인과 연결되는 소셜 다이어리 플랫폼

<br>

---

## 📅 Project Overview

*   **개발 기간**: 2025.11 ~ 2025.12
*   **주요 컨셉**:
    *   **Daily Question**: Claude 3.7 AI가 매일 새로운 질문을 생성합니다.
    *   **Deep Connection**: 24시간 후 비공개되는 글을 통해 "지금 이 순간"에 집중합니다.
    *   **Visual Archive**: 나의 기록이 점들을 잇는 선으로 시각화됩니다 (Connecting Dots).

---

## 🛠 Tech Stack

### 🔵 Frontend
<div align="center">
  <!-- Build / State -->
  <img src="https://img.shields.io/badge/Vite_6.0-646CFF?style=for-the-badge&logo=vite&logoColor=white">
  <img src="https://img.shields.io/badge/Pinia-FFE082?style=for-the-badge&logo=pinia&logoColor=black">
  <br>

  <!-- Framework / Styling -->
  <img src="https://img.shields.io/badge/Vue.js_3-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white">
  <img src="https://img.shields.io/badge/Tailwind_CSS_3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white">
  <br>

  <!-- Library -->
  <img src="https://img.shields.io/badge/Axios-5A29E4?style=for-the-badge&logo=axios&logoColor=white">
  <img src="https://img.shields.io/badge/PWA-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white">
  <img src="https://img.shields.io/badge/Lucide_Icons-F7DF1E?style=for-the-badge&logo=lucide&logoColor=black">
</div>

| Category | Stack |
| :--- | :--- |
| **Language** | JavaScript (ES6+) |
| **Framework** | Vue.js 3.5.25 (Composition API) |
| **Build Tool** | Vite 6.0.2 |
| **State** | Pinia 3.0.4 |
| **Styling** | Tailwind CSS 3.4.17, Pretendard Font |
| **Library** | Vue Router 4.6.3, Axios 1.13.2, Lucide Vue Next 0.561.0 |

<br>

### 🟠 Backend
<div align="center">
  <!-- Language / Framework -->
  <img src="https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Django_5.2-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/DRF-092E20?style=for-the-badge&logo=django&logoColor=white">
  <br>

  <!-- Database / Infra -->
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white">
  <br>

  <!-- Features -->
  <img src="https://img.shields.io/badge/APScheduler-FF4081?style=for-the-badge&logo=clock&logoColor=white">
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white">
</div>

| Category | Stack |
| :--- | :--- |
| **Language** | Python 3.12 |
| **Framework** | Django 5.2.4, Django REST Framework 3.16.0 |
| **Database** | SQLite (Dev), PostgreSQL (Prod), Supabase |
| **Auth** | Simple JWT, OAuth2 (Social Login) |
| **Library** | APScheduler 3.11.1 (Job Scheduling), Whitenoise 6.11.0 |

<br>

### 🟣 AI & External API
<div align="center">
  <img src="https://img.shields.io/badge/Anthropic_Claude_3.7-D97757?style=for-the-badge&logo=anthropic&logoColor=white">
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white">
  <img src="https://img.shields.io/badge/YouTube_Data_API-FF0000?style=for-the-badge&logo=youtube&logoColor=white">
</div>

| Feature | Service / Model | Role |
| :--- | :--- | :--- |
| **Question Gen** | Anthropic Claude 3.7 Sonnet | 매일 새로운 자아성찰 질문 AI 생성 |
| **Music Rec** | Google Gemini 2.0 Flash | 질문 분위기에 어울리는 노래 추천 |
| **Music Search** | YouTube Data API v3 | 추천된 곡의 재생 가능 ID 검색 |
| **Storage** | Supabase Storage | 사용자 프로필 및 게시글 이미지 저장 (Cloud) |

---

## ✨ Key Features

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

## 🏗️ System Architecture

<p align="center">
  <!-- 아키텍처 다이어그램 이미지가 있다면 여기에 경로를 넣어주세요. -->
  <img src="README_IMG/아키텍처.png" alt="System Architecture" width="90%">
  <br>
  <em>(프론트엔드 - 백엔드 - AI 서비스 - DB 간 데이터 흐름도)</em>
</p>

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **Auth** | | |
| `POST` | `/api/accounts/login/` | 로그인 (JWT 발급) |
| `POST` | `/api/accounts/upload-url/` | 이미지 업로드 URL 발급 (Smart Fallback) |
| **Question** | | |
| `GET` | `/api/questions/today/` | 오늘의 질문 조회 |
| **Article** | | |
| `GET` | `/api/articles/` | 전체 게시글 목록 (피드) |
| `POST` | `/api/articles/` | 오늘의 답변 등록 |
| **Stats** | | |
| `GET` | `/api/articles/statistics/word_frequency/` | 단어 빈도 분석 (워드클라우드) |

> *전체 API 문서는 Notion 링크 또는 별도 문서를 참조하세요.*

---

## 📂 Project Structure

```text
team-READMEEE-project/
├── backend/                    # [Backend] Django REST API
│   ├── daylog/                 # Project Config (Settings, WSGI)
│   ├── accounts/               # User Auth & Profile
│   ├── questions/              # AI Question Generator (Claude/Gemini)
│   ├── articles/               # Feed & Social Features
│   ├── notifications/          # Notification System
│   └── media/                  # Local Storage Fallback
│
└── frontend/                   # [Frontend] Vue.js Client
    ├── src/
    │   ├── api/                # Axios Config
    │   ├── stores/             # Pinia State Management
    │   ├── views/              # Page Components
    │   └── components/         # Reusable UI Components
    └── vite.config.js          # Build Config
```

---

## 🚀 Getting Started

### 1. Backend 실행
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate

# 데이터 로드 (주의: 별도 제공된 total_data.json 파일 필요)
python manage.py loaddata total_data.json

python manage.py runserver
```

> [!TIP]
> **심사 위원을 위한 무설정 실행 지원**: 본 프로젝트는 별도의 `.env` 설정이 없더라도 심사용 기본 `SECRET_KEY`와 `DEBUG=True` 모드로 자동 전환되어 즉시 실행 가능한 상태로 구성되어 있습니다.

### 2. Frontend 실행
```bash
cd frontend
npm install
npm run dev
```

### 💡 Smart Image Storage (Hybrid)
*   **로컬 모드 (권장)**: `.env` 설정 없음 → `backend/media/` 폴더 저장 (심사 용이)
*   **Supabase 모드**: `.env` 설정 있음 → Cloud Storage 저장

---

## 🤝 Team

| 이름 | 역할 | 담당 업무 |
| :--- | :--- | :--- |
| **류지우** | Full Stack | **BE**: AI 질문 생성, 주간 베스트 로직, 소셜 로그인<br>**FE**: 프로필/아카이빙 UI, API 통신 모듈 |
| **양혜지** | Full Stack | **Architecture & Tech**<br>• **Smart Storage Fallback**: 환경 감지형 하이브리드(Local/S3) 이미지 처리 시스템<br>• **Data Visualization**: SVG/CSS3D 기반의 'Connecting Dots' 시각화 엔진 개발<br>• **Analytics**: 사용자 체류 시간 분석 및 NLP 기반 워드클라우드 통계 API |

> [!NOTE]
> 본 프로젝트는 프론트엔드와 백엔드의 구분 없이, 전 팀원이 **풀스택(Full Stack)**으로 긴밀하게 협업하여 완성했습니다.
