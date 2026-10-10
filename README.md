# Xlantis Project

Monorepo for the **Xlantis RP Streamer & Content Directory** platform — connecting GTA RP roleplayers, factions, stream feeds, and viewers.

---

## Monorepo Architecture

```
Xlantis Project/
├── backend/                  # Django 5.2 & Django REST Framework API
│   ├── apps/                 # Domain modules (directory, platforms)
│   ├── config/               # Project configuration, settings, URL routing
│   ├── tests/                # Project-level and integration tests
│   ├── manage.py             # Django CLI entrypoint
│   ├── pyproject.toml        # Ruff & pytest configuration
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Backend environment template
│   └── README.md             # Backend setup and developer guide
│
├── frontend/                 # React 19 + Vite 8 + Tailwind CSS v4 SPA
│   ├── src/                  # Components, pages, layout, services
│   ├── public/               # Static assets & icons
│   ├── package.json          # Node dependencies & scripts
│   ├── vite.config.js        # Vite configuration
│   └── README.md             # Frontend guide
│
├── services/                 # Microservices and specialized integrations
│   └── integrations/         # Reserved for future FastAPI background service
│       └── README.md
│
├── docs/                     # Project architecture and technical documentation
│   └── .gitkeep
│
├── .gitignore                # Repository-wide ignore rules
├── .venv/                    # Shared Python virtual environment (root level)
└── README.md                 # This overview file
```

---

## Applications & Subprojects

### 1. Backend (`backend/`)
- **Technology**: Python 3.12, Django 5.2, Django REST Framework, PostgreSQL
- **Role**: Core data models, directory listings, faction management, platform account tracking, and REST endpoints.
- **Documentation**: See [backend/README.md](backend/README.md) for detailed setup and API documentation.
- **Quick start**:
  ```powershell
  # Activate virtual environment
  .\.venv\Scripts\Activate.ps1

  # Navigate to backend and run
  cd backend
  python manage.py check
  python manage.py runserver
  ```

### 2. Frontend (`frontend/`)
- **Technology**: React 19, Vite 8, Tailwind CSS v4, React Router v7, Axios
- **Role**: Responsive user interface featuring directory search, faction previews, creator spotlight, and individual persona profiles.
- **Quick start**:
  ```powershell
  cd frontend
  npm install
  npm run dev
  ```

### 3. Services (`services/`)
- **Integrations (`services/integrations/`)**: Reserved directory for the upcoming FastAPI service handling external streaming platform API webhooks, sync tasks, and live status integrations.

---

## Development Workflow

### Python Environment
The Python virtual environment (`.venv`) is maintained at the repository root to allow shared tooling and linting across services.
To run tests across the backend:
```powershell
cd backend
pytest
ruff check .
```

### Frontend Environment
The frontend uses standard npm scripts:
```powershell
cd frontend
npm run lint
npm run build
```
