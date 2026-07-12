# guaro-backend

FastAPI backend for a multi-module operations platform (orders, products, inventory, users, and related workflows).

**Author:** [Ruth Tirusew](https://github.com/ruth-tirusew)

## Stack

- **FastAPI** + **Pydantic** — REST API (`/api/v1/...`)
- **PostgreSQL** + **SQLAlchemy 2** + **Alembic** migrations
- **Keycloak** — authentication adapter with unit and integration tests
- **Docker** — production image with scripted Uvicorn launch
- **pytest** — module-level unit tests; Keycloak integration coverage

## Architecture

Domain logic is organized by module with a consistent adapter layout (`interface`, `db`, `models`, `router`). That keeps auth, persistence, and HTTP boundaries explicit and makes each area testable on its own.

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set Keycloak + database values
alembic upgrade head
./scripts/launch.sh    # http://0.0.0.0:8000
```

## Docker

```bash
docker build -t guaro-backend .
# configure env + database, then run with ./scripts/launch_prod.sh as entrypoint
```

## Tests

```bash
pytest
```
