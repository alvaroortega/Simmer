from collections.abc import Iterator
from simmer_backend.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)

class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session