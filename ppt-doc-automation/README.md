# PPT 문서 자동화 시스템 (PPT Doc Automation)

마크다운(.md) 파일을 기반으로 PowerPoint 프레젠테이션을 자동 생성하는 시스템입니다.

## 기술 스택

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, python-pptx
- **Frontend**: Vue.js 3, Vite, Pinia, Vue I18n
- **Database**: SQLite
- **Deployment**: Docker, Docker Compose

## 프로젝트 구조

```
ppt-doc-automation/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py         # FastAPI 앱 진입점
│   │   ├── config.py       # 설정
│   │   ├── database.py     # DB 연결
│   │   ├── models/         # SQLAlchemy 모델
│   │   ├── schemas/        # Pydantic 스키마
│   │   ├── routers/        # API 라우터
│   │   ├── services/       # 비즈니스 로직
│   │   └── utils/          # 유틸리티
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/               # Vue.js 프론트엔드
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── views/
│   │   ├── components/
│   │   ├── stores/         # Pinia 상태관리
│   │   ├── i18n/           # 다국어 (ko, en, vi)
│   │   └── api/            # API 클라이언트
│   ├── package.json
│   └── Dockerfile
│
├── templates/              # PPT 템플릿 파일
├── samples/                # 샘플 .md 파일
├── docs/                   # 프로젝트 문서
├── docker-compose.yml
└── README.md
```

## 빠른 시작

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (선택사항)

### 로컬 개발 환경

#### Backend 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

### Docker로 실행

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 주요 기능

- 📝 마크다운 파일 업로드 및 파싱
- 🎨 PPT 템플릿 관리
- ⚡ 실시간 PPT 생성
- 🌐 다국어 지원 (한국어, 영어, 베트남어)
- 📊 생성 이력 관리

## 문서

- [요구사항](docs/REQUIREMENTS.md)
- [DB 스키마](docs/DB_SCHEMA.md)
- [API 명세](docs/API_SPEC.md)
- [MD 파일 규격](docs/MD_FORMAT.md)

## 라이선스

MIT License
