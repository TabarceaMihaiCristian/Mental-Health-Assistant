"""Wait until the configured database accepts simple SQL queries."""

from __future__ import annotations

import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


def main() -> None:
    """Poll the database before startup-time migrations or app boot."""

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    attempts = 30
    delay_seconds = 2

    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database is ready.", flush=True)
            return
        except SQLAlchemyError as exc:
            if attempt == attempts:
                raise RuntimeError("Database did not become ready in time.") from exc
            print(
                f"Database is unavailable; retrying {attempt}/{attempts}...",
                flush=True,
            )
            time.sleep(delay_seconds)


if __name__ == "__main__":
    main()
