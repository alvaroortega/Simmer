from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from simmer_backend.db.models import Recipe, RecipeVersion

PAYLOAD = {
    "content": {
        "title": "  Weeknight tomato pasta  ",
        "ingredients": [
            {"original_text": "200 g spaghetti", "item": "spaghetti", "quantity": 200, "unit": "g"},
            {"original_text": "add cream"},
        ],
        "steps": [
            {"instruction": "Boil the pasta."},
            {"instruction": "Stir in the sauce."},
        ],
    }
}


def test_creates_approved_manual_recipe(client: TestClient) -> None:
    res = client.post("/recipes", json=PAYLOAD)

    assert res.status_code == 201
    body = res.json()
    version = body["current_version"]
    assert version["origin"] == "user_edit"
    assert version["review_status"] == "approved"
    assert version["approved_at"] is not None
    assert version["schema_version"] == 1

    content = version["content"]
    assert content["title"] == "Weeknight tomato pasta"
    assert [s["instruction"] for s in content["steps"]] == ["Boil the pasta.", "Stir in the sauce."]
    # Missing facts stay missing.
    cream = content["ingredients"][1]
    assert cream["quantity"] is None and cream["unit"] is None
    # Stable IDs are generated for ingredients and steps.
    assert all(UUID(i["id"]) for i in content["ingredients"] + content["steps"])


def test_persists_recipe_owned_by_current_owner(
    client: TestClient, db: Session, owner_id: UUID
) -> None:
    body = client.post("/recipes", json=PAYLOAD).json()

    recipe = db.get(Recipe, UUID(body["id"]))
    assert recipe is not None
    assert recipe.owner_id == owner_id
    assert recipe.current_version_id == UUID(body["current_version"]["id"])

    version = db.get(RecipeVersion, recipe.current_version_id)
    assert version is not None
    assert version.recipe_id == recipe.id
    assert version.parent_version_id is None
    assert version.content["title"] == "Weeknight tomato pasta"


def test_client_cannot_set_owner_or_review_fields(client: TestClient, db: Session) -> None:
    for extra in ({"owner_id": "00000000-0000-4000-8000-0000000000ff"}, {"review_status": "draft"}):
        res = client.post("/recipes", json={**PAYLOAD, **extra})
        assert res.status_code == 422

    assert db.query(Recipe).count() == 0


def test_rejects_invalid_content(client: TestClient, db: Session) -> None:
    invalid = [
        {"content": {"title": "   "}},
        {"content": {"title": "x", "ingredients": [{"original_text": "eggs", "quantity": -1}]}},
        {"content": {"title": "x", "steps": [{"instruction": ""}]}},
        {"content": {"title": "x", "unknown": True}},
        {},
    ]
    for payload in invalid:
        assert client.post("/recipes", json=payload).status_code == 422, payload

    assert db.query(Recipe).count() == 0
