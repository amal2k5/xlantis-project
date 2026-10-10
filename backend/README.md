# Xlantis RP Streamer & Content Directory - Backend

Django REST Framework backend for the Xlantis RP Streamer & Content Directory platform.

## Tech Stack
- **Python**: 3.12
- **Framework**: Django 5.2 & Django REST Framework (DRF)
- **Database**: PostgreSQL with `psycopg` (v3)
- **Configuration**: `django-environ`
- **Linter & Formatter**: Ruff
- **Testing**: pytest & pytest-django

---

## Directory Structure

```
backend/
├── .env.example              # Environment variables template
├── pyproject.toml            # Ruff & pytest configuration
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── README.md                 # Backend setup and usage guide
├── config/                   # Django core configuration
│   ├── __init__.py
│   ├── asgi.py               # ASGI server entrypoint
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL dispatcher & health check
│   └── wsgi.py               # WSGI server entrypoint
├── apps/                     # Application domain modules
│   ├── __init__.py
│   ├── directory/            # Streamer, character, and faction models & views
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── slugs.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── platforms/            # Streaming platforms integration
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
└── tests/                    # Project-level and integration tests
    ├── __init__.py
    └── test_config.py
```

---

## Getting Started

### 1. Prerequisites
- Python 3.12+
- PostgreSQL 14+ running locally or remotely
- Root virtual environment activated (`.venv`)

### 2. Activate Virtual Environment (from repo root)

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies (from repo root or backend/)
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Copy `backend/.env.example` to `backend/.env`:
```powershell
Copy-Item backend\.env.example backend\.env
```
Update `backend/.env` with your PostgreSQL credentials:
```env
DATABASE_URL=postgres://<username>:<password>@localhost:5432/<dbname>
```

### 5. Running Commands (from `backend/` directory)

Always navigate to `backend/` before running Django commands:
```powershell
cd backend
```

- **Verify Django Setup:**
  ```powershell
  python manage.py check
  ```

- **Run Migrations:**
  ```powershell
  python manage.py migrate
  ```

- **Run Tests:**
  ```powershell
  pytest
  ```

- **Run Code Quality Checks:**
  ```powershell
  ruff check .
  ruff format --check .
  ```

- **Run Development Server:**
  ```powershell
  python manage.py runserver
  ```

Available Endpoints:
- Health Check: `http://127.0.0.1:8000/api/health/`
- Directory API: `http://127.0.0.1:8000/api/v1/directory/`
- Platforms API: `http://127.0.0.1:8000/api/v1/platforms/`
- Admin Panel: `http://127.0.0.1:8000/admin/`
