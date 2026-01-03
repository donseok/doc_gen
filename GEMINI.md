# PPT 문서 자동화 (PPT Doc Automation)

## 프로젝트 개요
**PPT Doc Automation**은 마크다운(`.md`) 파일로부터 파워포인트(`.pptx`) 발표 자료를 자동으로 생성하도록 설계된 풀스택 애플리케이션입니다. 구조화된 마크다운 콘텐츠를 파싱하고 이를 파워포인트 템플릿에 매핑하여 슬라이드 데크 생성을 간소화합니다.

**핵심 기술:**
*   **백엔드:** Python 3.11, FastAPI, SQLAlchemy, python-pptx
*   **프론트엔드:** Vue.js 3, Vite, Pinia, Vue I18n
*   **데이터베이스:** SQLite
*   **인프라:** Docker, Docker Compose

## 아키텍처
시스템은 명확한 관심사 분리 원칙을 따릅니다:
*   **프론트엔드 (`frontend/`)**: 템플릿 관리, 마크다운 업로드 및 생성 이력 조회를 위한 Vue.js 싱글 페이지 애플리케이션(SPA).
*   **백엔드 (`backend/`)**: 파일 처리, 데이터베이스 작업 및 슬라이드 생성 로직을 담당하는 FastAPI REST API.
*   **핵심 로직**:
    *   `MarkdownParser`: 마크다운 텍스트를 구조화된 슬라이드 데이터로 변환합니다.
    *   `ContentSummarizer`: 슬라이드에 적합하도록 긴 텍스트를 요약합니다.
    *   `PPTDesigner`: 슬라이드 레이아웃과 디자인 요소를 결정합니다.
    *   `TemplateAnalyzer`: 파워포인트 템플릿의 레이아웃과 플레이스홀더를 분석합니다.
    *   `PPTGenerator`: 구조화된 데이터를 `python-pptx`를 사용하여 `.pptx` 파일로 렌더링합니다.

## 시작하기

### 사전 요구 사항
*   Python 3.11+
*   Node.js 18+
*   Docker 및 Docker Compose (선택 사항이지만 권장됨)

### 로컬에서 실행하기

**1. 백엔드 (FastAPI)**
```bash
cd ppt-doc-automation/backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

**2. 프론트엔드 (Vue.js)**
```bash
cd ppt-doc-automation/frontend
npm install
npm run dev
```
애플리케이션은 `http://localhost:5173` (기본 Vite 포트) 또는 출력된 포트에서 실행됩니다.

### Docker로 실행하기
```bash
cd ppt-doc-automation
docker-compose up --build
```
*   프론트엔드: `http://localhost:3000`
*   백엔드: `http://localhost:8000`

## 개발 컨벤션

*   **프로젝트 구조:**
    *   `backend/app/`: FastAPI 기반 백엔드 로직.
    *   `backend/templates/`: 파워포인트 템플릿 파일(`.pptx`) 저장소.
    *   `backend/samples/`: 마크다운 샘플 파일 저장소.
    *   `backend/output/`: 생성된 결과물 저장소.
    *   `frontend/src/`: Vue.js 기반 프론트엔드 소스 코드.
    *   `docs/`: 프로젝트 관련 상세 문서.
*   **확장성:** 
    *   스토리지: 로컬 파일 시스템 외에 AWS S3 및 호환 스토리지(MinIO 등)를 지원하도록 설계되었습니다.
    *   파서: 기존 정규식 기반 파서 외에 확장 가능한 구조의 마크다운 파서를 제공합니다.
*   **린팅 (Linting):**
    *   프론트엔드: `npm run lint` (ESLint)
*   **국제화 (i18n):** 프론트엔드는 여러 언어(한국어, 영어, 베트남어)를 지원하며 `frontend/src/i18n/`에 위치합니다.
*   **마크다운 형식:** 슬라이드 생성에 필요한 특정 마크다운 문법은 `docs/MD_FORMAT.md`를 참조하세요.

## 문서화
상세 사양은 `docs/` 디렉토리를 참조하세요:
*   `docs/REQUIREMENTS.md`: 시스템 요구 사항
*   `docs/DB_SCHEMA.md`: 데이터베이스 스키마 상세
*   `docs/API_SPEC.md`: API 엔드포인트
*   `docs/MD_FORMAT.md`: 마크다운 문법 가이드
*   `docs/USER_MANUAL.md`: 사용자 매뉴얼
*   `docs/프로젝트_수행계획서.md`: 프로젝트 수행 계획서