# Mental Health Assistant

Backend-first FastAPI service with PostgreSQL, Alembic migrations, and a Docker-based test flow.

## Repository Layout

- `backend/`: application code, tests, dependencies, and backend-only tooling
- `.github/workflows/backend-ci.yml`: backend CI workflow
- `docker-compose.yml`: local service orchestration for backend and database

## Local Validation

From the repository root:

```powershell
backend\.venv\Scripts\ruff.exe check backend\app backend\tests
```

```powershell
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/mental_health_app_test backend python -m pytest
```

Type checking from the backend directory:

```powershell
cd backend
python -m pyright
```

## Backend Setup

Create the backend virtual environment and install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements_dev.txt
```

## CI

The backend CI workflow runs three gates:

- Ruff
- Pyright
- Pytest

Pushes and pull requests that touch `backend/**` or the workflow file trigger the pipeline.
