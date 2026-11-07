"""Simple To-Do REST API built with FastAPI and PostgreSQL."""

import os
import time
from contextlib import asynccontextmanager

import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Database connection settings come from environment variables (set via docker compose / .env)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"],
}


def get_connection():
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)


def init_db(retries: int = 10, delay: float = 2.0):
    """Create the todos table, retrying until the database is reachable."""
    for attempt in range(1, retries + 1):
        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS todos (
                        id         SERIAL PRIMARY KEY,
                        title      TEXT NOT NULL,
                        done       BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
            return
        except psycopg.OperationalError:
            print(f"Database not ready (attempt {attempt}/{retries}), retrying...")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="To-Do API", lifespan=lifespan, root_path="/api")


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


@app.get("/health")
def health():
    with get_connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/todos")
def list_todos():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, title, done, created_at FROM todos ORDER BY done, created_at DESC"
        ).fetchall()


@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate):
    with get_connection() as conn:
        return conn.execute(
            "INSERT INTO todos (title) VALUES (%s) RETURNING id, title, done, created_at",
            (todo.title,),
        ).fetchone()


@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoUpdate):
    with get_connection() as conn:
        row = conn.execute(
            """
            UPDATE todos
            SET title = COALESCE(%s, title),
                done  = COALESCE(%s, done)
            WHERE id = %s
            RETURNING id, title, done, created_at
            """,
            (todo.title, todo.done, todo_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return row


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    with get_connection() as conn:
        result = conn.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
