# PPT Doc Automation

## Project Overview
**PPT Doc Automation** is a full-stack application designed to automatically generate PowerPoint (`.pptx`) presentations from Markdown (`.md`) files. It streamlines the creation of slide decks by parsing structured markdown content and mapping it to PowerPoint templates.

**Key Technologies:**
*   **Backend:** Python 3.11, FastAPI, SQLAlchemy, python-pptx
*   **Frontend:** Vue.js 3, Vite, Pinia, Vue I18n
*   **Database:** SQLite
*   **Infrastructure:** Docker, Docker Compose

## Architecture
The system follows a clear separation of concerns:
*   **Frontend (`frontend/`)**: A Vue.js Single Page Application (SPA) for managing templates, uploading markdown, and viewing generation history.
*   **Backend (`backend/`)**: A FastAPI REST API that handles file processing, database operations, and slide generation logic.
*   **Core Logic**:
    *   `MarkdownParser`: Converts markdown text into structured slide data.
    *   `PPTGenerator`: Renders the structured data into `.pptx` files using `python-pptx`.

## Getting Started

### Prerequisites
*   Python 3.11+
*   Node.js 18+
*   Docker & Docker Compose (optional but recommended)

### Running Locally

**1. Backend (FastAPI)**
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
API Documentation will be available at `http://localhost:8000/docs`.

**2. Frontend (Vue.js)**
```bash
cd ppt-doc-automation/frontend
npm install
npm run dev
```
The application will run at `http://localhost:5173` (default Vite port) or the port specified in the output.

### Running with Docker
```bash
cd ppt-doc-automation
docker-compose up --build
```
*   Frontend: `http://localhost:3000`
*   Backend: `http://localhost:8000`

## Development Conventions

*   **Project Structure:**
    *   `backend/app/`: Contains all backend application code.
    *   `frontend/src/`: Contains all frontend source code.
    *   `docs/`: Additional documentation (API specs, DB schema, MD format).
    *   `templates/`: Stores the base PowerPoint templates.
*   **Linting:**
    *   Frontend: `npm run lint` (ESLint)
*   **Internationalization:** The frontend supports multiple languages (Korean, English, Vietnamese) located in `frontend/src/i18n/`.
*   **Markdown Format:** See `docs/MD_FORMAT.md` for the specific markdown syntax required for slide generation.

## Documentation
Refer to the `docs/` directory for detailed specifications:
*   `docs/REQUIREMENTS.md`: System requirements
*   `docs/DB_SCHEMA.md`: Database schema details
*   `docs/API_SPEC.md`: API endpoints
*   `docs/MD_FORMAT.md`: Markdown syntax guide
