# PPT 문서 자동화 시스템

마크다운(.md) 파일에서 PowerPoint 프레젠테이션을 자동으로 생성하는 시스템입니다.

## 주요 기능

- 마크다운 텍스트로 PPT 자동 생성
- .md 파일 업로드 지원
- PPT 템플릿 선택 가능
- 다국어 지원 (한국어, 영어, 베트남어)
- 생성된 PPT 즉시 다운로드

## 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Python 3.11, FastAPI, SQLAlchemy |
| 프론트엔드 | Vue.js 3, Vite, Pinia, Vue I18n |
| PPT 생성 | python-pptx |
| 데이터베이스 | SQLite |
| 배포 | Docker, Docker Compose |

## 빠른 시작

### 백엔드 실행
```bash
cd ppt-doc-automation/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드 실행
```bash
cd ppt-doc-automation/frontend
npm install
npm run dev
```

### Docker로 실행
```bash
cd ppt-doc-automation
docker-compose up --build
```

## 접속 주소

- 프론트엔드: http://localhost:5173 (개발) / http://localhost:3000 (Docker)
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 문서

- [요구사항](ppt-doc-automation/docs/REQUIREMENTS.md)
- [DB 스키마](ppt-doc-automation/docs/DB_SCHEMA.md)
- [API 명세](ppt-doc-automation/docs/API_SPEC.md)
- [MD 파일 규격](ppt-doc-automation/docs/MD_FORMAT.md)
- [사용자 매뉴얼](ppt-doc-automation/docs/USER_MANUAL.md)

## 라이선스

MIT License
