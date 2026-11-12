from fastapi import APIRouter, status
from sqlalchemy import func

from simmer_backend.api.dependencies import CurrentOwnerDep, SessionDep
from simmer_backend.db.models import Recipe, RecipeVersion
from simmer_backend.schemas.recipes import RecipeCreate, RecipeRead, RecipeVersionRead

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_recipe(
    payload: RecipeCreate,
    session: SessionDep,
    owner_id: CurrentOwnerDep,
) -> RecipeRead:
    """Create a manually entered recipe.

    Manual entries are approved immediately; review-before-approval applies
    to extracted and AI-proposed versions.
    """
    recipe = Recipe(owner_id=owner_id)
    session.add(recipe)
    # recipes and recipe_versions reference each other, so insert the recipe,
    # then the version, then point the recipe at it.
    session.flush()

    version = RecipeVersion(
        recipe_id=recipe.id,
        origin="user_edit",
        review_status="approved",
        content=payload.content.model_dump(mode="json"),
        approved_at=func.now(),
    )
    session.add(version)
    session.flush()

    recipe.current_version_id = version.id
    session.commit()

    # Load server-generated timestamps.
    session.refresh(recipe)
    session.refresh(version)

    return RecipeRead(
        id=recipe.id,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        current_version=RecipeVersionRead.model_validate(version),
    )
