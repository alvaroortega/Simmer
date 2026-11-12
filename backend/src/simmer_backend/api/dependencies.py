from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from simmer_backend.core.config import settings
from simmer_backend.db.session import get_session


def get_current_owner() -> UUID:
    """Return the owner for the current request.

    Single-user for now: always the configured dev owner. Replace with real
    authentication later; every owner-scoped query goes through this.
    """
    return settings.dev_owner_id


SessionDep = Annotated[Session, Depends(get_session)]
CurrentOwnerDep = Annotated[UUID, Depends(get_current_owner)]
