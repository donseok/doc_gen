# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드 작업 시 참고할 수 있는 가이드를 제공합니다.

## 프로젝트 개요

PPT 문서 자동화 - 마크다운(.md) 파일 또는 구조화된 JSON에서 고품질 파워포인트 프레젠테이션을 자동으로 생성하는 시스템입니다. Python/FastAPI 백엔드와 Vue.js 3 프론트엔드로 구성되어 있습니다.

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

### PPT 직접 생성 (CLI)
```bash
cd ppt-doc-automation/backend
python run_generator.py  # 기본 JSON 파일로 PPT 생성
# 또는
python -m app.services.json_to_ppt_generator <json_path> [output_dir]
```

## 아키텍처

### 데이터 흐름 (2가지 파이프라인)

**파이프라인 1: 마크다운 기반 (레거시)**
```
마크다운 파일 → MarkdownParser → ContentSummarizer → PPTDesigner → .pptx 파일
```

**파이프라인 2: JSON v2 기반 (권장)**
```
원본 문서 → LLM (JSON 구조 생성) → JsonToPptGenerator → .pptx 파일
```

### 백엔드 구조 (`backend/app/`)
- `main.py` - FastAPI 진입점, CORS 설정, 라우터 등록
- `config.py` - Pydantic 설정 (DB URL, 디렉토리, CORS 출처)
- `database.py` - SQLAlchemy 엔진 및 세션 관리
- `models/` - SQLAlchemy ORM 모델 (Template, Document, 상태 열거형)
- `schemas/` - Pydantic 요청/응답 스키마
- `routers/` - API 엔드포인트: templates, documents, generate
- `services/` - 핵심 비즈니스 로직:
  - `json_to_ppt_generator.py` - **JSON v2 형식 → PPTX 변환** (권장, 1600+ lines)
  - `template_analyzer.py` - 템플릿 분석 서비스 (색상/폰트/레이아웃 추출)
  - `md_parser.py` - AST 기반 마크다운 파서 (mistune 활용)
  - `content_summarizer.py` - 콘텐츠 요약 에이전트
  - `ppt_designer.py` - PPT 디자인 에이전트 (레거시)
  - `ppt_generator.py` - python-pptx 기반 생성기 (레거시)
  - `storage.py` - 스토리지 추상화 (로컬/S3 지원)

### 프론트엔드 구조 (`frontend/src/`)
- `router/` - 지연 로딩 뷰를 사용하는 Vue Router
- `stores/` - Pinia 상태 관리 (template, document 스토어)
- `api/` - 리소스별 Axios API 클라이언트
- `i18n/` - 다국어 지원 (한국어, 영어, 베트남어)
- `views/` - 페이지 컴포넌트: Home, Templates, Generate, Documents

## 핵심 서비스

### JsonToPptGenerator (권장)

`services/json_to_ppt_generator.py` - JSON v2 형식을 고품질 PPTX로 변환

**사용법:**
```python
from app.services.json_to_ppt_generator import generate_ppt_from_json

result = generate_ppt_from_json(
    json_path='path/to/presentation.json',
    output_dir='path/to/output'
)
```

**지원하는 시각 요소 (custom_elements):**
| 요소 타입 | 설명 | 렌더링 메서드 |
|----------|------|--------------|
| `big_number_display` | KPI 대형 숫자 카드 | `_render_big_numbers()` |
| `pain_point_cards` | 문제점/Pain Point 카드 | `_render_pain_points()` |
| `comparison_bar_chart` | As-Is/To-Be 비교 차트 | `_render_comparison_chart()` |
| `icon_card_grid` / `icon_box_grid` | 아이콘 + 제목 + 설명 카드 그리드 | `_render_icon_cards()` |
| `feature_cards` / `numbered_step_cards` | 번호형 기능 카드 | `_render_feature_cards()` |
| `horizontal_process_flow` | 수평 프로세스 플로우 | `_render_process_flow()` |
| `tech_stack_grid` | 기술 스택 레이어 | `_render_tech_stack()` |
| `organization_cards` | 조직도 카드 | `_render_organization()` |
| `donut_chart_with_table` | 도넛 차트 + 테이블 | `_render_donut_with_table()` |
| `gantt_timeline` | 간트 타임라인 | `_render_timeline()` |
| `milestone_cards_grid` | 마일스톤 카드 그리드 | `_render_milestones()` |
| `two_column_icon_list` | 2열 아이콘 리스트 | `_render_two_column_list()` |
| `risk_matrix_cards` | 위험 매트릭스 | `_render_risk_matrix()` |
| `checklist_cards` | 체크리스트 카드 | `_render_checklist_cards()` |
| `table` | 데이터 테이블 | `_render_table()` |

**동국제강 브랜드 테마 (DongkukTheme):**
| 역할 | 색상 코드 | 설명 |
|------|-----------|------|
| dk1 | `#262626` | 어두운 텍스트 기본색 |
| lt1 | `#FFFFFF` | 밝은 배경색 |
| dk2 | `#002452` | **네이비 (브랜드 컬러)** |
| lt2 | `#B6B6B6` | 밝은 회색 |
| accent1 | `#757575` | 회색 강조 |
| accent2 | `#4B6580` | 청회색 |
| accent3 | `#B7D0D4` | 연한 청록색 |
| accent4 | `#C51F2A` | **레드 (브랜드 컬러)** |
| accent5 | `#D55633` | 주황-빨강 |
| accent6 | `#E9B86E` | **골드 (브랜드 컬러)** |

### JSON v2 스키마

```json
{
  "presentation": {
    "title": "프레젠테이션 제목",
    "author": "작성자_OOOO팀",
    "date": "2025.01.06",
    "slides": [
      {
        "slide_number": 1,
        "layout_id": 1,
        "slide_type": "title",
        "placeholders": {
          "title": "문서 제목",
          "subtitle": "부서명 I 날짜"
        }
      },
      {
        "slide_number": 2,
        "layout_id": 2,
        "placeholders": {
          "toc_items": [
            { "number": "01", "title": "프로젝트 개요", "pages": "03-05" }
          ]
        }
      },
      {
        "slide_number": 3,
        "layout_id": 4,
        "slide_type": "content",
        "placeholders": {
          "main_title": "1. 프로젝트 개요",
          "action_title": "핵심 메시지를 1-2문장으로 요약합니다."
        },
        "custom_elements": [
          {
            "type": "icon_card_grid",
            "data": {
              "columns": 4,
              "items": [
                {
                  "icon": "qr_code",
                  "title": "QR코드 기반",
                  "subtitle": "부제목 (선택)",
                  "features": ["기능1", "기능2"],
                  "accent_color": "#002452"
                }
              ]
            }
          }
        ]
      }
    ]
  }
}
```

**레이아웃 ID:**
| layout_id | 용도 | 플레이스홀더 |
|-----------|------|-------------|
| 1 | 표지 (White_Big K 버전) | title, subtitle |
| 2 | 목차 (간지 1) | toc_items |
| 3 | 본문 (Action Title + Body) | main_title, action_title, body |
| 4 | 본문 (자유 콘텐츠) | main_title, action_title |
| 5 | 본문 (넓은 영역) | main_title, body |

### TemplateAnalyzer

`services/template_analyzer.py` - PPTX 템플릿 분석 서비스

**사용법:**
```python
from app.services.template_analyzer import analyze_template

style_info = analyze_template('path/to/template.pptx')
# 반환: { colors, fonts, layouts, slide_width, slide_height, margins, ... }
```

**추출 항목:**
- `ColorPalette`: primary, secondary, accent, background, text colors
- `FontSettings`: title_font, body_font, english_font, sizes
- `LayoutInfo`: 각 레이아웃의 플레이스홀더 정보
- `margins`: left, right, top, bottom, header_height

### MarkdownParser (레거시)

`services/md_parser.py`:
- AST 기반 파서 (MistuneParser) + 레거시 정규식 파서 (RegexParser)
- `# H1` → 프레젠테이션 제목, `## H2` → 슬라이드 분할
- 테이블, 이미지, 코드 블록 파싱 지원
- YAML 프론트매터 메타데이터 추출

## API 엔드포인트

| 엔드포인트 | 설명 |
|----------|-------------|
| `POST /api/generate/from-text` | 마크다운 문자열에서 PPT 생성 |
| `POST /api/generate/from-file` | 업로드된 .md 파일에서 PPT 생성 |
| `GET /api/documents/{id}/download` | 생성된 .pptx 다운로드 |
| `CRUD /api/templates` | PPT 템플릿 관리 |
| `CRUD /api/documents` | 생성 이력 조회/삭제 |

## 데이터베이스
- SQLite (`data/ppt_automation.db`)
- 테이블: `templates`, `documents`
- 문서 상태: pending → processing → completed/failed

## 설정 (`app/config.py`)
`.env`로 설정 가능한 주요 항목:
- `DATABASE_URL` - SQLite 연결 문자열
- `TEMPLATES_DIR`, `SAMPLES_DIR`, `OUTPUT_DIR` - 파일 경로
- `CORS_ORIGINS` - 허용된 프론트엔드 출처
- `MAX_UPLOAD_SIZE` - 기본값 10MB

## 문서

| 파일 | 설명 |
|------|------|
| `docs/ppt preprocess prompt.md` | **PPT JSON 생성 워크플로우**, 시각화 변환 규칙, design_prompt 구조 |
| `docs/PPT기본양식_분석보고서.md` | **템플릿 레이아웃 분석** (EMU 좌표, 플레이스홀더 ID, 테마 색상) |
| `docs/프로젝트_수행계획서.md` | 샘플 입력 문서 |
| `docs/API_SPEC.md` | API 명세 |
| `docs/DB_SCHEMA.md` | 데이터베이스 스키마 |
| `docs/MD_FORMAT.md` | 마크다운 포맷 가이드 |

## PPT 생성 워크플로우 (LLM 활용)

1. **원본 문서 분석**: 핵심 메시지, 데이터 포인트, 논리 흐름 추출
2. **JSON 구조 생성**: 슬라이드별 layout_id, 시각 요소 유형 결정
3. **시각화 변환**: 불릿 리스트 → 카드/차트, 프로세스 → 인포그래픽
4. **PPTX 생성**: `JsonToPptGenerator`로 고품질 슬라이드 렌더링

### 시각화 변환 규칙 (핵심)

> **원칙**: 3줄 이상의 불릿 리스트는 반드시 시각 요소로 변환

| 원본 데이터 | 변환 시각 요소 |
|------------|---------------|
| 숫자가 포함된 표 | Bar/Pie/Donut Chart |
| 비교 데이터 (As-Is/To-Be) | `comparison_bar_chart` |
| 순차적 단계/프로세스 | `horizontal_process_flow` |
| 핵심 수치 (1-3개) | `big_number_display` |
| 특징/기능 나열 | `icon_card_grid` |
| 단계별 설명 | `feature_cards` / `numbered_step_cards` |
| 위험 요소 | `risk_matrix_cards` |
| 마일스톤/일정 | `gantt_timeline` / `milestone_cards_grid` |
| 체크리스트 | `checklist_cards` |
| 조직/역할 | `organization_cards` |
| 기술 스택 | `tech_stack_grid` |

### 품질 기준

- 슬라이드당 핵심 메시지 1개
- Action Title: 핵심 메시지를 1-2문장으로 요약
- 시각적 다양성: 연속 3장 이상 동일 layout_id 금지
- 스토리 흐름: 도입-전개-결론 구조 유지

## 출력 디렉토리

- `backend/output/` - 생성된 PPTX 파일
- `output/` - JSON 중간 파일 (프로젝트 루트)

## 슬라이드 크기 (EMU 단위)

```python
SLIDE_WIDTH = Emu(9906000)   # 약 27.52cm (A4 가로)
SLIDE_HEIGHT = Emu(6858000)  # 약 19.05cm
MARGIN_LEFT = Emu(270064)    # 약 0.75cm
CONTENT_WIDTH = Emu(9360550)
```
