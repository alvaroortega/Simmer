import logging

from alembic import context

from simmer_backend.core.config import settings
from simmer_backend.db.session import Base, engine
import simmer_backend.db.models  # noqa: F401  (registers tables on Base.metadata)

config = context.config

# Config lives in pyproject.toml (no alembic.ini), so set up logging here:
# show Alembic's progress messages, keep SQLAlchemy quiet.
logging.basicConfig(format="%(levelname)-5.5s [%(name)s] %(message)s")
logging.getLogger("alembic").setLevel(logging.INFO)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()