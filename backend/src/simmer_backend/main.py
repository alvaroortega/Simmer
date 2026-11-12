from fastapi import FastAPI

from simmer_backend.api.routes import recipes

app = FastAPI(title="Simmer API")
app.include_router(recipes.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
