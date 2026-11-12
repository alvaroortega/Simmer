import os
from collections.abc import Iterator
from uuid import UUID

import pytest
from sqlalchemy import create_engine, make_url, text

# Point the app at a separate test database before any app module is imported.
# Environment variables take precedence over backend/.env.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://simmer:simmer_local@127.0.0.1:5432/simmer_test",
)
TEST_OWNER_ID = UUID("00000000-0000-4000-8000-000000000001")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["DEV_OWNER_ID"] = str(TEST_OWNER_ID)

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from simmer_backend.core.config import BACKEND_DIR  # noqa: E402
from simmer_backend.db.session import SessionLocal, engine  # noqa: E402
from simmer_backend.main import app  # noqa: E402


def _ensure_test_database() -> None:
    url = make_url(TEST_DATABASE_URL)
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": url.database},
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin.dispose()


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    _ensure_test_database()
    command.upgrade(Config(toml_file=BACKEND_DIR / "pyproject.toml"), "head")


@pytest.fixture(autouse=True)
def clean_tables() -> Iterator[None]:
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE recipes, recipe_versions CASCADE"))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


@pytest.fixture
def owner_id() -> UUID:
    return TEST_OWNER_ID
