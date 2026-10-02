from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Tasks API", description="Простой сервис списка задач", version="1.0.0")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["Купить молоко"])
    description: str = Field("", max_length=500)
    priority: Literal["low", "medium", "high"] = "medium"


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[Literal["low", "medium", "high"]] = None
    done: Optional[bool] = None


class Task(TaskCreate):
    id: int
    done: bool = False
    created_at: datetime


# Хранилище в памяти (для учебного сервиса достаточно)
tasks: dict[int, Task] = {}
_next_id = 1


def reset_storage() -> None:
    global _next_id
    tasks.clear()
    _next_id = 1


@app.get("/health")
def health():
    """Проверка работоспособности (без аргументов)."""
    return {"status": "ok", "tasks": len(tasks)}


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    done: Optional[bool] = Query(None, description="Фильтр по статусу"),
    priority: Optional[Literal["low", "medium", "high"]] = Query(None),
    search: Optional[str] = Query(None, description="Подстрока в названии"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Список задач. Все аргументы — query-параметры."""
    result = list(tasks.values())
    if done is not None:
        result = [t for t in result if t.done == done]
    if priority:
        result = [t for t in result if t.priority == priority]
    if search:
        result = [t for t in result if search.lower() in t.title.lower()]
    return result[offset : offset + limit]


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    """Одна задача. task_id — path-параметр."""
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    return tasks[task_id]


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(data: TaskCreate):
    """Создать задачу. Данные — в теле запроса (body)."""
    global _next_id
    task = Task(id=_next_id, created_at=datetime.now(timezone.utc), **data.model_dump())
    tasks[task.id] = task
    _next_id += 1
    return task


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, data: TaskUpdate):
    """Изменить задачу: path (id) + body (поля)."""
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    updated = tasks[task_id].model_copy(update=data.model_dump(exclude_unset=True))
    tasks[task_id] = updated
    return updated


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if tasks.pop(task_id, None) is None:
        raise HTTPException(404, "Task not found")


@app.get("/stats")
def stats():
    """Статистика по задачам."""
    by_priority = {p: 0 for p in ("low", "medium", "high")}
    for t in tasks.values():
        by_priority[t.priority] += 1
    done = sum(t.done for t in tasks.values())
    return {"total": len(tasks), "done": done, "pending": len(tasks) - done, "by_priority": by_priority}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
