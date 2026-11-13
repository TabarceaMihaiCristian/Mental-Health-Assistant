#!/usr/bin/env sh
set -eu

if [ "${AZURE_DEMO_MODE:-false}" != "true" ]; then
  python -m app.scripts.wait_for_db

  if [ "${AUTO_MIGRATE:-true}" = "true" ]; then
    alembic upgrade head
  fi
else
  echo "Azure demo mode enabled; skipping database wait and migrations." >&2
fi

exec "$@"
