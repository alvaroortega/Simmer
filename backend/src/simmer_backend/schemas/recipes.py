from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class InputModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class IngredientInput(InputModel):
    id: UUID = Field(default_factory=uuid4)
    original_text: str = Field(min_length=1)
    item: str | None = Field(default=None, min_length=1)
    quantity: float | None = Field(
        default=None,
        ge=0,
        allow_inf_nan=False,
    )
    unit: str | None = Field(default=None, min_length=1)
    preparation: str | None = None


class StepInput(InputModel):
    id: UUID = Field(default_factory=uuid4)
    instruction: str = Field(min_length=1)


class RecipeContent(InputModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = None
    language: str | None = None
    ingredients: list[IngredientInput] = Field(default_factory=list)
    steps: list[StepInput] = Field(default_factory=list)


class RecipeCreate(InputModel):
    content: RecipeContent


class RecipeVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    schema_version: int
    origin: Literal["extracted", "user_edit", "ai_proposal"]
    review_status: Literal["draft", "approved", "rejected"]
    content: RecipeContent
    created_at: datetime
    approved_at: datetime | None


class RecipeRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    current_version: RecipeVersionRead