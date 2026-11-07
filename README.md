# Docker To-Do App

A simple to-do web application, containerised with Docker and orchestrated with Docker Compose.

## Team

- Sophia Foit
- Kevin Sprenger
- Daniela Haid

## Architecture

```
Browser ──► frontend (Nginx :80) ──/api/*──► backend (FastAPI :8000) ──► db (PostgreSQL :5432)
                 │                                                         │
          published on host                                        named volume
          port 8080                                                todo_db_data
```

| Service    | Image / Build          | Purpose                                                        |
|------------|------------------------|----------------------------------------------------------------|
| `frontend` | `./frontend` (Nginx)   | Serves the static HTML/JS UI and reverse-proxies `/api` to the backend |
| `backend`  | `./backend` (Python)   | REST API (FastAPI) for creating, listing, updating and deleting to-dos |
| `db`       | `postgres:16-alpine`   | Stores the to-dos persistently                                 |

- **Persistence:** PostgreSQL data lives in the named volume `todo_db_data`, so tasks survive `docker compose down` and container rebuilds.
- **Secrets:** No passwords are written in `docker-compose.yml`. All credentials are read from a `.env` file (ignored by git). `.env.example` shows the required variables. Compose refuses to start if they are missing.
- **Networks:** The database is only reachable on the internal `backend_net`. The frontend cannot talk to the database directly.
- **Startup order:** The backend waits until the database health check (`pg_isready`) passes.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

## Getting started

```bash
# 1. Clone the repository
git clone <repo-url>
cd docker-todo

# 2. Create your .env file and set a password
cp .env.example .env

# 3. Build and start all containers
docker compose up -d --build

# 4. Open the app
open http://localhost:8080
```

API documentation (Swagger UI): http://localhost:8080/api/docs

## API endpoints

| Method   | Endpoint           | Description         |
|----------|--------------------|---------------------|
| `GET`    | `/api/health`      | Health check (incl. DB connection) |
| `GET`    | `/api/todos`       | List all to-dos     |
| `POST`   | `/api/todos`       | Create a to-do `{"title": "..."}` |
| `PATCH`  | `/api/todos/{id}`  | Update title and/or `{"done": true}` |
| `DELETE` | `/api/todos/{id}`  | Delete a to-do      |

## Useful commands

```bash
docker compose ps                 # status of all containers
docker compose logs -f backend    # follow backend logs
docker compose down               # stop containers (data is kept in the volume)
docker compose down -v            # stop containers AND delete the volume (all data lost)
docker volume ls                  # list volumes (look for ..._todo_db_data)
```

### Testing persistence

1. Add a few to-dos in the browser.
2. Run `docker compose down` and then `docker compose up -d`.
3. Reload the page: the to-dos are still there because they are stored in the named volume.

## Project structure

```
.
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/main.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── html/ (index.html, app.js, style.css)
```
