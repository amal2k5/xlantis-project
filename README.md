# Xlantis RP Streamer & Content Directory - Backend

Initial Django backend foundation for the Xlantis RP Streamer & Content Directory project.

## Tech Stack
- **Python**: 3.12
- **Framework**: Django 5.2 & Django REST Framework (DRF)
- **Database**: PostgreSQL with `psycopg` (v3)
- **Configuration**: `django-environ`
- **Linter & Formatter**: Ruff
- **Testing**: pytest & pytest-django

---

## Project Structure

```
Xlantis Project/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Ruff & pytest configuration
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── README.md                 # Setup and usage guide
├── config/                   # Django core configuration
│   ├── __init__.py
│   ├── asgi.py               # ASGI server entrypoint
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL dispatcher & health check
│   └── wsgi.py               # WSGI server entrypoint
└── apps/                     # Application modules
    ├── __init__.py
    ├── directory/            # Streamer & character directory module
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py         # Models to be added in Phase 2
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    └── platforms/            # Streaming platforms integration module
        ├── admin.py
        ├── apps.py
        ├── models.py         # Models to be added in Phase 2
        ├── tests.py
        ├── urls.py
        └── views.py
```

---

## Getting Started

### 1. Prerequisites
- Python 3.12+
- PostgreSQL 14+ running locally or remotely

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Update the `.env` file with your PostgreSQL credentials:
```env
DATABASE_URL=postgres://<username>:<password>@localhost:5432/<dbname>
```

### 5. Verify Django Setup
Run the Django system check:
```powershell
python manage.py check
```

### 6. Run Tests
```powershell
pytest
```

### 7. Run Code Quality Checks
```powershell
ruff check .
ruff format --check .
```

### 8. Run Development Server
```powershell
python manage.py runserver
```

Endpoints available:
- Health Check: `http://127.0.0.1:8000/api/health/`
- Directory API: `http://127.0.0.1:8000/api/v1/directory/`
- Platforms API: `http://127.0.0.1:8000/api/v1/platforms/`
- Admin: `http://127.0.0.1:8000/admin/`
