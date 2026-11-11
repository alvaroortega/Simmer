from sqlalchemy import create_engine

from simmer_backend.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)