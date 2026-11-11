from fastapi import FastAPI

app = FastAPI(title="Simmer API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}