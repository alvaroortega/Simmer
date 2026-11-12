# Simmer
An AI-assisted recipe workspace to collect recipes from text, images, and videos, refine them through experimentation, and learn from cooking feedback.

## Idea

Simmer is a private recipe repository, starting as a single-user app. It captures recipes found online, turns the available material into structured, editable recipes, and keeps track of how they change and how they turn out when cooked.

**First slice:** capture → extract → review → save.

- **Capture** from pasted text, recipe images/screenshots, a YouTube link, or an Instagram reel link. Imports are saved immediately, even when extraction can't run yet.
- **Extract** a draft recipe with AI: ingredients, ordered steps, source references, and explicit unknowns.
- **Review** the draft alongside its source, correct it, and approve it.
- **Save** it as an immutable recipe version in the library.

**Principles**

- Never invent missing facts. A missing quantity stays missing, and conflicting information is flagged for review.
- Keep extracted source information, AI suggestions, and user corrections distinct.
- Recipes are versioned. Edits and AI proposals create new versions, so cooking feedback can point to the exact version cooked.
- Each user's imports, files, and recipes are private to them.

**Later:** cooking feedback, AI-suggested improvements, insights into what works and what doesn't, generated recipe videos, and wine pairings from a connected cellar with an external wine-database fallback.

## Stack

Nx monorepo (pnpm):

- `apps/web` — React + TypeScript + Vite frontend (`simmer-web`)
- `backend` — Python 3.13 + FastAPI backend managed with uv (`simmer-backend`)

Backend package layout (`backend/src/simmer_backend/`):

```
main.py            # creates the FastAPI app, registers routes
core/config.py     # settings loaded from backend/.env
db/session.py      # engine and sessions
db/models.py       # SQLAlchemy tables
db/migrations/     # Alembic migrations (configured in pyproject.toml)
api/dependencies.py  # shared request dependencies (DB session, current owner)
api/routes/        # endpoints, one module per resource
schemas/           # Pydantic request/response models
```

## Development

Prerequisites: Node + pnpm, [uv](https://docs.astral.sh/uv/), and Docker with `docker-compose`. On macOS the infra script starts [Colima](https://github.com/abiosoft/colima) if Docker isn't already running.

```sh
pnpm install
cd backend && uv sync && cp .env.example .env && cd ..

pnpm infra:up                                   # start Postgres
(cd backend && uv run alembic upgrade head)     # apply migrations

pnpm dev   # starts Postgres, then the API and UI in parallel
```

- UI: http://localhost:4200
- API: http://localhost:8000. In development the Vite server proxies `/api/*` to the backend, with the `/api` prefix removed.

To run the pieces separately:

```sh
pnpm infra:up                     # start Postgres and wait until it's healthy
pnpm exec nx dev simmer-backend   # API
pnpm exec nx serve simmer-web     # UI
pnpm infra:stop                   # stop Postgres (data is kept)
```

### Database

Local PostgreSQL 18 runs from `compose.yaml`, bound to `127.0.0.1:5432` only:

| Setting  | Value          |
|----------|----------------|
| Database | `simmer`       |
| User     | `simmer`       |
| Password | `simmer_local` |

```
postgresql://simmer:simmer_local@127.0.0.1:5432/simmer
```

These credentials are for local development only. Data persists in the `postgres_data` Docker volume. To wipe it and start fresh, run `docker-compose down -v`.

The backend reads its settings from `backend/.env` (see `backend/.env.example`):

- `DATABASE_URL` — SQLAlchemy URL of the dev database.
- `DEV_OWNER_ID` — the UUID that owns all data until real authentication exists.

Schema changes go through Alembic, run from `backend/`:

```sh
uv run alembic revision --autogenerate -m "describe change"   # then review the generated file
uv run alembic upgrade head
```

### Tests

```sh
pnpm exec nx test simmer-backend   # pytest, against a real Postgres
pnpm exec nx run-many -t test typecheck lint -p simmer-web
```

Backend tests need Postgres running. They create and migrate a separate `simmer_test` database (override with `TEST_DATABASE_URL`) and empty its tables after each test, so the dev data is never touched.