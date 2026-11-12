from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from simmer_backend.db.session import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(index=True)
    current_version_id: Mapped[UUID | None] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "current_version_id"],
            ["recipe_versions.recipe_id", "recipe_versions.id"],
            name="fk_recipes_current_version",
            use_alter=True,
        ),
    )


class RecipeVersion(Base):
    __tablename__ = "recipe_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recipe_id: Mapped[UUID] = mapped_column(
        ForeignKey("recipes.id", name="fk_recipe_versions_recipe"),
    )
    parent_version_id: Mapped[UUID | None] = mapped_column()

    schema_version: Mapped[int] = mapped_column(
        server_default="1",
    )
    origin: Mapped[str] = mapped_column()
    review_status: Mapped[str] = mapped_column(
        server_default="draft",
    )
    content: Mapped[dict[str, Any]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    __table_args__ = (
        UniqueConstraint(
            "recipe_id",
            "id",
            name="uq_recipe_versions_recipe_id_id",
        ),
        ForeignKeyConstraint(
            ["recipe_id", "parent_version_id"],
            ["recipe_versions.recipe_id", "recipe_versions.id"],
            name="fk_recipe_versions_parent",
        ),
        CheckConstraint(
            "origin IN ('extracted', 'user_edit', 'ai_proposal')",
            name="ck_recipe_versions_origin",
        ),
        CheckConstraint(
            "review_status IN ('draft', 'approved', 'rejected')",
            name="ck_recipe_versions_review_status",
        ),
        CheckConstraint(
            "schema_version >= 1",
            name="ck_recipe_versions_schema_version",
        ),
        CheckConstraint(
            "parent_version_id IS NULL OR parent_version_id <> id",
            name="ck_recipe_versions_parent_not_self",
        ),
    )