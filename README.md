# Natthaphong Kanban

A full-stack Kanban board for the CU FDE2 assignment. Three columns: **To do**, **Doing**, **Done**. Add cards, drag them between columns (or use the move dropdown), edit titles and delete cards. Search, filters, progress counts and responsive layouts are included.

## Submission

- Public source: https://github.com/treetest94-svg/Natthaphong-Kanban
- Public frontend: deployment in progress.

## Stack and request flow

**Frontend:** React, TypeScript and Vite. **Backend:** Python FastAPI, managed with uv. **Database:** Supabase Postgres. **Hosting:** Vercel serves the Vite assets and Python API on one origin, avoiding production localhost/CORS mistakes. Vercel is an alternative cloud platform listed in the course guide.

Browser → FastAPI `/api/cards` → validated payload + private board capability → Supabase RPC → PostgreSQL → JSON response → refreshed board.

Each browser gets a separate board through an HttpOnly cookie. Cards persist in Supabase across refreshes. Clearing cookies or changing browsers starts a new board. No login or seeded accounts are needed. There is no browser-storage or in-memory production database fallback.

## Run locally

Requires Node.js 24 and uv with Python 3.12+.

1. Apply `database/001_cards.sql` to a new Supabase project with the SQL editor or migrations.
2. Copy `backend/.env.example` to `backend/.env` and fill the project URL and publishable key privately.
3. Start the backend:

```sh
cd backend
uv sync --frozen
uv run uvicorn main:app --reload --port 8000
```

4. Start the frontend in another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173. Vite proxies `/api` to the local backend. Interactive API docs are at http://localhost:8000/docs.

```sh
cd backend
uv run pytest -q
uv run python ping_db.py
```

From the project root, run `npm run build` to typecheck, build the frontend and copy its output into `public/`.

## API

| Method | Route | Result |
| --- | --- | --- |
| GET | `/api/health` | Confirms database connectivity |
| GET | `/api/cards` | Current browser board's cards |
| POST | `/api/cards` | Create `{title, status?}`; 201 |
| PATCH | `/api/cards/{id}` | Update `{title?, status?}` |
| DELETE | `/api/cards/{id}` | Delete owned card; 204 |

Titles are trimmed and must be 1–240 characters. Status is exactly `todo`, `doing` or `done`. Blank/invalid inputs return 422; missing/other-board cards return 404. Documentation is exposed at `/docs`. Course-compatible `/cards` and `/health` aliases are included.

## Privacy and database access

The database table is protected by RLS with no direct anonymous SELECT/INSERT/UPDATE/DELETE privileges. A constrained RPC checks a 256-bit board capability and limits each operation to its SHA-256 hash. No raw board token is stored in the table or returned in JSON. The board cookie is HttpOnly, SameSite=Lax, and Secure on Vercel. Only a Supabase publishable key is used, kept in server environment configuration. No service-role secret is needed or exposed.

Supabase's advisor reports the deliberately exposed SECURITY DEFINER RPC; its authorization check is the board capability, not broad anonymous table access. The rejected unrestricted-table proposal was replaced with this narrower design. See `docs/adr/001-private-board-access.md`.

This is a coursework demo. Production user accounts would need Supabase Auth, account recovery, and rate limiting. The screenshot's required scope is the core Kanban board; the separate expense tracker and the course's example login/sharing/admin change requests are not represented as implemented features.

## Tests and workflow

API tests were written before endpoint implementation. The red run had 18 failing cases; implementation passed all original 19 without weakening assertions. Additional regression tests cover browser-board isolation, cookie behavior and cross-origin writes. Unit/API tests use a dependency-injected repository; live verification exercises the actual hosted Supabase database separately.

Work is developed on `feature/kanban-board`, then merged into `main`. The course-style specification, tickets, glossary and decisions are in `.scratch/kanban/`, `docs/agents/`, `GLOSSARY.md` and `docs/adr/`. These documents were authored directly from the course workflow; no unavailable third-party skills are claimed to have run.

## Deploy

Import the repository root into Vercel, select FastAPI (set by `vercel.json`), and configure `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` privately. The build command runs the frontend build. The frontend uses same-origin `/api`, so it never points at localhost in production. For separate frontend/backend hosting, set `VITE_API_URL` and `ALLOWED_ORIGINS` to the actual deployed URLs.

`.env`, private configuration, dependencies, generated assets and cookies are excluded from Git. The repository contains only example placeholders. The public source is published with the connected GitHub API rather than an authenticated local gh CLI.
