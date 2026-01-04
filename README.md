# PPT 문서 자동화 (PPT Doc Automation)

**PPT Doc Automation**은 마크다운(`.md`) 파일로부터 파워포인트(`.pptx`) 발표 자료를 자동으로 생성하도록 설계된 풀스택 애플리케이션입니다. 구조화된 마크다운 콘텐츠를 파싱하고 이를 파워포인트 템플릿에 매핑하여 슬라이드 데크 생성을 간소화합니다.

## 🚀 주요 기능

- **자동 생성**: 마크다운 텍스트를 분석하여 PPT 슬라이드 자동 생성
- **템플릿 지원**: 다양한 PPT 템플릿 적용 가능
- **다국어 지원**: 한국어, 영어, 베트남어 UI 지원
- **이력 관리**: 생성된 문서의 이력 조회 및 재다운로드

## 🛠 기술 스택

| 구분 | 기술 |
|------|------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, python-pptx |
| **Frontend** | Vue.js 3, Vite, Pinia, Vue I18n |
| **Database** | SQLite |
| **Infra** | Docker, Docker Compose |

## 🏗 아키텍처

- **Frontend (`ppt-doc-automation/frontend/`)**: Vue.js SPA. 템플릿 관리, 마크다운 업로드, 생성 요청 처리.
- **Backend (`ppt-doc-automation/backend/`)**: FastAPI REST API. 파일 처리, 데이터베이스 작업, `python-pptx`를 이용한 슬라이드 렌더링.

## 🏁 시작하기

### 사전 요구 사항
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (선택 사항)

### 로컬에서 실행하기

**1. 백엔드 (FastAPI)**
```bash
cd ppt-doc-automation/backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. 프론트엔드 (Vue.js)**
```bash
cd ppt-doc-automation/frontend
npm install
npm run dev
```

### Docker로 실행하기
```bash
cd ppt-doc-automation
docker-compose up --build
```

- **프론트엔드**: `http://localhost:3000`
- **백엔드**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`

## 📚 문서

상세 문서는 `ppt-doc-automation/docs/` 디렉토리에서 확인할 수 있습니다.

- [시스템 요구 사항](ppt-doc-automation/docs/REQUIREMENTS.md)
- [데이터베이스 스키마](ppt-doc-automation/docs/DB_SCHEMA.md)
- [API 엔드포인트](ppt-doc-automation/docs/API_SPEC.md)
- [마크다운 문법 가이드](ppt-doc-automation/docs/MD_FORMAT.md)
- [사용자 매뉴얼](ppt-doc-automation/docs/USER_MANUAL.md)

## 📄 라이선스

MIT License