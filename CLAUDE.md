# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드 작업 시 참고할 수 있는 가이드를 제공합니다.

## 프로젝트 개요

PPT 문서 자동화 - 마크다운(.md) 파일에서 파워포인트 프레젠테이션을 자동으로 생성하는 시스템입니다. Python/FastAPI 백엔드와 Vue.js 3 프론트엔드로 구성되어 있습니다.

## 개발 명령어

### 백엔드 (FastAPI)
```bash
cd ppt-doc-automation/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드 (Vue.js)
```bash
cd ppt-doc-automation/frontend
npm install
npm run dev      # 개발 서버 (포트 5173)
npm run build    # 프로덕션 빌드
npm run lint     # ESLint 자동 수정
```

### Docker (풀 스택)
```bash
cd ppt-doc-automation
docker-compose up --build
# 프론트엔드: http://localhost:3000
# 백엔드: http://localhost:8000
# API 문서: http://localhost:8000/docs
```

## 아키텍처

### 데이터 흐름
```
마크다운 파일 → MarkdownParser → 파싱된 데이터 → PPTGenerator → .pptx 파일
```

### 백엔드 구조 (`backend/app/`)
- `main.py` - FastAPI 진입점, CORS 설정, 라우터 등록
- `config.py` - Pydantic 설정 (DB URL, 디렉토리, CORS 출처)
- `database.py` - SQLAlchemy 엔진 및 세션 관리
- `models/` - SQLAlchemy ORM 모델 (Template, Document, 상태 열거형)
- `schemas/` - Pydantic 요청/응답 스키마
- `routers/` - API 엔드포인트: templates, documents, generate
- `services/` - 핵심 비즈니스 로직:
  - `md_parser.py` - 정규식 패턴을 사용하여 마크다운을 구조화된 슬라이드 데이터로 변환
  - `ppt_generator.py` - python-pptx를 사용하여 .pptx 파일 생성

### 프론트엔드 구조 (`frontend/src/`)
- `router/` - 지연 로딩 뷰를 사용하는 Vue Router
- `stores/` - Pinia 상태 관리 (template, document 스토어)
- `api/` - 리소스별 Axios API 클라이언트
- `i18n/` - 다국어 지원 (한국어, 영어, 베트남어)
- `views/` - 페이지 컴포넌트: Home, Templates, Generate, Documents

### 핵심 서비스

**MarkdownParser** (`services/md_parser.py`):
- `# H1`을 프레젠테이션 제목으로 파싱
- `## H2`를 기준으로 콘텐츠를 슬라이드로 분할
- 글머리 기호(`-`/`*`), 번호 목록, `### H3` 부제목 추출
- 이미지 `![alt](src)` 및 코드 블록 처리
- YAML 프론트매터 메타데이터 추출

**PPTGenerator** (`services/ppt_generator.py`):
- python-pptx 레이아웃 인덱스 사용 (TITLE=0, TITLE_CONTENT=1 등)
- 콘텐츠 유형에 따라 레이아웃 자동 선택 (image_only, image_content, code)
- UUID 접미사와 함께 `OUTPUT_DIR`에 파일 출력

### API 엔드포인트

| 엔드포인트 | 설명 |
|----------|-------------|
| `POST /api/generate/from-text` | 마크다운 문자열에서 PPT 생성 |
| `POST /api/generate/from-file` | 업로드된 .md 파일에서 PPT 생성 |
| `GET /api/documents/{id}/download` | 생성된 .pptx 다운로드 |
| `CRUD /api/templates` | PPT 템플릿 관리 |
| `CRUD /api/documents` | 생성 이력 조회/삭제 |

### 데이터베이스
- SQLite (`data/ppt_automation.db`)
- 테이블: `templates`, `documents`
- 문서 상태: pending → processing → completed/failed

### 설정 (`app/config.py`)
`.env`로 설정 가능한 주요 항목:
- `DATABASE_URL` - SQLite 연결 문자열
- `TEMPLATES_DIR`, `SAMPLES_DIR`, `OUTPUT_DIR` - 파일 경로
- `CORS_ORIGINS` - 허용된 프론트엔드 출처
- `MAX_UPLOAD_SIZE` - 기본값 10MB

## 슬라이드용 마크다운 형식

```markdown
---
type: weekly-report
project: PRJ-2025-001
author: 이름
---

# 프레젠테이션 제목

## 슬라이드 1 제목
- 글머리 기호
- 또 다른 글머리 기호

## 코드가 있는 슬라이드 2
```python
print("Hello")
```

## 이미지가 있는 슬라이드 3
![대체 텍스트](path/to/image.png)
```

문서 유형(project-plan, kickoff-report, weekly-report 등)을 포함한 전체 사양은 `docs/MD_FORMAT.md`를 참조하세요.
