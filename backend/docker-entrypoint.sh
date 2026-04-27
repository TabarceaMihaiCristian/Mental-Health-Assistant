#!/usr/bin/env sh
set -eu

python -m app.scripts.wait_for_db

if [ "${AUTO_MIGRATE:-true}" = "true" ]; then
  alembic upgrade head
fi

exec "$@"
