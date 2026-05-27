# Local Development Stack

## Prerequisites

- Docker Engine 24+
- Docker Compose v2

## Quick start

```bash
docker compose up -d --build
```

The first run seeds the database with sample data (~15 farmers, sensor readings, alerts).

## Access

| Service | URL |
|---|---|
| Dashboard | http://localhost |
| API docs | http://localhost/api/docs |
| Backend direct | http://localhost:8000/api/v1/health |
| PostgreSQL | localhost:5432 (user: agricoop, pass: agricoop_local) |

## Useful commands

```bash
# Tail logs from all services
docker compose logs -f

# Tail only the backend
docker compose logs -f backend

# Restart backend after code change
docker compose up -d --build backend

# Nuke everything (including DB volume)
docker compose down -v
```
