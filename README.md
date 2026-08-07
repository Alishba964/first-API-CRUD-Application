# Task API

A small CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with **Python** and **FastAPI**. The project evolved across three assignments — starting with in-memory storage, moving to SQLite, and finally to Postgres running in Docker.

## Project evolution

| Stage | Storage | What changed |
|---|---|---|
| Assignment 1 | In-memory Python list | Built the core CRUD API and Swagger docs |
| Assignment 2 | SQLite (`tasks.db`) | Swapped the list for a real database file — data survives a restart |
| Assignment 3 | Postgres in Docker | Swapped SQLite for Postgres via a repository layer; app + database now run together with `docker compose up` |

The important thing across all three: **the API itself never changed.** The same endpoints, same request/response shapes, same status codes — only the storage underneath was swapped out. This is handled by a layered structure:

```
first.py        → routes (HTTP layer, talks to the service)
service.py       → business logic (validation), talks to the repository
repository.py    → talks to the actual database (in-memory or Postgres)
```

Because routes and service never reference SQL directly, switching databases meant changing `repository.py` and nothing else.

## How to run (recommended: Docker Compose)

This runs the API and Postgres together, with no local Python setup needed.

1. Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop) is installed and running.
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Start everything:
   ```bash
   docker compose up --build
   ```
4. The API is now running at `http://localhost:8000`, and Swagger UI at `http://localhost:8000/docs`.

To stop everything: `Ctrl+C`, or `docker compose down` from another terminal. Data is kept in a Docker volume, so it survives restarts — see **Persistence proof** below.

## How to run locally (without Docker)

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/Scripts/activate   # Windows (Git Bash)
   # source venv/bin/activate     # Mac/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure Postgres is reachable and `.env` has a valid `DATABASE_URL` pointing at `localhost` instead of `db` (Compose uses the service name `db`; running locally needs `localhost`).
4. Start the server:
   ```bash
   uvicorn first:app --reload --port 8000
   ```

## Environment variables

Connection details live in `.env` (gitignored — never committed, since it can hold real credentials). `.env.example` is committed and shows the expected format:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/taskdb
```

When running via Docker Compose, the app connects to the database using the service name `db` instead of `localhost` — this is set directly in `docker-compose.yml`.

## Example request

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Persistence proof

Data is stored in Postgres, running in a Docker container with a named volume (`pgdata`) mounted to `/var/lib/postgresql/data`. This was verified by:

1. Creating a task via `POST /tasks` (confirmed with `GET /tasks`).
2. Stopping the whole stack (`Ctrl+C` on `docker compose up`).
3. Starting it again (`docker compose up`).
4. Running `GET /tasks` again — the task created in step 1 was still present.

This confirms data survives both an application restart and a container restart, because the volume is not removed when containers stop (only `docker compose down -v` would delete it, and that command was intentionally avoided).


