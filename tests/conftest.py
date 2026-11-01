import os
from pathlib import Path

# Must be set before any scheduler import so Settings (and Alembic's env.py) target the test DB.
TEST_DB = "djs_test"
os.environ["DATABASE_URL"] = f"postgresql+psycopg2://postgres:postgres@localhost:5432/{TEST_DB}"

import psycopg2  # noqa: E402
import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

from scheduler.core.db import SessionLocal, engine  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def _migrated_test_db():
    admin = psycopg2.connect(host="localhost", user="postgres", password="postgres", dbname="postgres")
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)")
        cur.execute(f"CREATE DATABASE {TEST_DB}")
    admin.close()

    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    command.upgrade(cfg, "head")
    yield
    engine.dispose()


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        with engine.begin() as conn:
            conn.exec_driver_sql("TRUNCATE job_runs, job_definitions CASCADE")
