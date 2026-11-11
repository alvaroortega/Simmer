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

## Development

```sh
pnpm install
cd backend && uv sync && cd ..

pnpm exec nx dev simmer-backend   # API on http://localhost:8000
pnpm exec nx serve simmer-web     # UI on http://localhost:4200
```

In development the Vite server proxies `/api/*` to the backend, with the `/api` prefix removed.

```sh
pnpm exec nx run-many -t test typecheck lint
```
