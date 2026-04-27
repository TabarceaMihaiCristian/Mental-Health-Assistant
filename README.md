# Mental Health Assistant

Backend-first FastAPI service with PostgreSQL, Alembic migrations, and a Docker-based test flow.

## Repository Layout

- `backend/`: application code, tests, dependencies, and backend-only tooling
- `.github/workflows/backend-ci.yml`: backend CI workflow
- `docker-compose.yml`: local development orchestration with bind mounts and `--reload`
- `docker-compose.prod.yml`: production-style orchestration without bind mounts or reload

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
Copy-Item .env.example .env
```

For a production-style environment template:

```powershell
Copy-Item .env.production.example .env
```

## CI

The backend CI workflow runs three gates:

- Ruff
- Pyright
- Pytest

Pushes and pull requests that touch `backend/**` or the workflow file trigger the pipeline.

## Runtime Startup

The backend Docker image uses `backend/docker-entrypoint.sh` as its entrypoint. On container start it:

1. waits until `DATABASE_URL` accepts a simple SQL query
2. runs `alembic upgrade head` when `AUTO_MIGRATE=true`
3. starts the configured server command

Local Compose sets `AUTO_MIGRATE=true` so a fresh database is migrated automatically before the API starts.

## Compose Modes

Local development:

```powershell
docker compose up --build
```

This mode is intentionally developer-friendly:

- bind mounts `./backend` into the container
- runs `uvicorn` with `--reload`
- keeps the backend editable without rebuilding the image

Production-style local run:

```powershell
docker compose -f docker-compose.prod.yml up --build -d
```

This mode is closer to deployment behavior:

- no source bind mount
- no `--reload`
- uses the Dockerfile default command
- still waits for DB and applies migrations through the entrypoint

For production deployments, keep these rules:

- use a real `SECRET_KEY`; never deploy the placeholder value
- set `DATABASE_URL`, `SECRET_KEY`, and `OPENAI_API_KEY` from the platform secret store
- restrict `BACKEND_CORS_ORIGINS` to the deployed frontend origin
- disable `--reload`; it is only for local development
- run only one scheduler owner, or set `SCHEDULER_ENABLED=false` on extra app instances

Required production env vars:

- `DATABASE_URL`: primary application database connection string
- `SECRET_KEY`: JWT/signing secret; must be high-entropy and private
- `BACKEND_CORS_ORIGINS`: JSON array of allowed frontend origins
- `OPENAI_API_KEY`: required for assistant/chat/mood-analysis features

Recommended production env vars:

- `OPENAI_MODEL`: defaults to `gpt-5-mini` if omitted
- `AUTO_MIGRATE`: keep `true` only if you want container startup to run Alembic automatically
- `SCHEDULER_ENABLED`: keep `true` only on the instance that should own scheduled jobs
- `ENVIRONMENT=production`
- `DEBUG=false`

A production-style backend container can be started with the Dockerfile default command:

```powershell
docker build -t mental-health-backend ./backend
docker run --env-file backend/.env -e AUTO_MIGRATE=true -p 8000:8000 mental-health-backend
```

Health endpoints:

- `/api/v1/health`: API process liveness
- `/api/v1/health/db`: database connectivity
- `/api/v1/health/scheduler`: scheduler runtime status
