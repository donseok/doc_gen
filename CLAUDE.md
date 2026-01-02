# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PPT Doc Automation - A system that automatically generates PowerPoint presentations from Markdown (.md) files. The project uses a Python/FastAPI backend with Vue.js 3 frontend.

## Development Commands

### Backend (FastAPI)
```bash
cd ppt-doc-automation/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Vue.js)
```bash
cd ppt-doc-automation/frontend
npm install
npm run dev      # Development server (port 5173)
npm run build    # Production build
npm run lint     # ESLint with auto-fix
```

### Docker (Full Stack)
```bash
cd ppt-doc-automation
docker-compose up --build
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Architecture

### Data Flow
```
Markdown File → MarkdownParser → Parsed Data → PPTGenerator → .pptx File
```

### Backend Structure (`backend/app/`)
- `main.py` - FastAPI entry point, CORS config, router registration
- `config.py` - Pydantic settings (DB URL, directories, CORS origins)
- `database.py` - SQLAlchemy engine and session management
- `models/` - SQLAlchemy ORM models (Template, Document with status enum)
- `schemas/` - Pydantic request/response schemas
- `routers/` - API endpoints: templates, documents, generate
- `services/` - Core business logic:
  - `md_parser.py` - Converts markdown to structured slide data using regex patterns
  - `ppt_generator.py` - Creates .pptx files using python-pptx

### Frontend Structure (`frontend/src/`)
- `router/` - Vue Router with lazy-loaded views
- `stores/` - Pinia state management (template, document stores)
- `api/` - Axios API clients per resource
- `i18n/` - Internationalization (Korean, English, Vietnamese)
- `views/` - Page components: Home, Templates, Generate, Documents

### Key Services

**MarkdownParser** (`services/md_parser.py`):
- Parses `# H1` as presentation title
- Splits content by `## H2` into slides
- Extracts bullets (`-`/`*`), numbered lists, `### H3` subheadings
- Handles images `![alt](src)` and code blocks
- Extracts YAML frontmatter metadata

**PPTGenerator** (`services/ppt_generator.py`):
- Uses python-pptx layout indices (TITLE=0, TITLE_CONTENT=1, etc.)
- Auto-selects layout based on content type (image_only, image_content, code)
- Outputs files to `OUTPUT_DIR` with UUID suffix

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/generate/from-text` | Generate PPT from markdown string |
| `POST /api/generate/from-file` | Generate PPT from uploaded .md file |
| `GET /api/documents/{id}/download` | Download generated .pptx |
| `CRUD /api/templates` | Manage PPT templates |
| `CRUD /api/documents` | View/delete generation history |

### Database
- SQLite (`data/ppt_automation.db`)
- Tables: `templates`, `documents`
- Document status: pending → processing → completed/failed

### Configuration (`app/config.py`)
Key settings configurable via `.env`:
- `DATABASE_URL` - SQLite connection string
- `TEMPLATES_DIR`, `SAMPLES_DIR`, `OUTPUT_DIR` - File paths
- `CORS_ORIGINS` - Allowed frontend origins
- `MAX_UPLOAD_SIZE` - 10MB default

## Markdown Format for Slides

```markdown
---
type: weekly-report
project: PRJ-2025-001
author: Name
---

# Presentation Title

## Slide 1 Title
- Bullet point
- Another bullet

## Slide 2 with Code
```python
print("Hello")
```

## Slide 3 with Image
![alt text](path/to/image.png)
```

See `docs/MD_FORMAT.md` for complete specification including document types (project-plan, kickoff-report, weekly-report, etc.).
