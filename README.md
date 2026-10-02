# Tasks API (FastAPI)

Сервис списка задач + минимальный фронтенд (`/`) и Swagger (`/docs`).

| Метод | Путь | Параметры |
|---|---|---|
| GET | `/health` | — |
| GET | `/tasks` | **query**: `done`, `priority`, `search`, `limit`, `offset` |
| GET | `/tasks/{task_id}` | **path**: `task_id` |
| POST | `/tasks` | **body**: `title`, `description`, `priority` |
| PATCH | `/tasks/{task_id}` | **path** + **body** |
| DELETE | `/tasks/{task_id}` | **path** |
| GET | `/stats` | — |

## Запуск
    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/uvicorn app.main:app --reload
    .venv/bin/pytest

## Демонстрация POST
    curl -X POST http://localhost:8000/tasks -H 'Content-Type: application/json' \
         -d '{"title":"Сдать задание","priority":"high"}'

## Деплой бесплатно (Render.com)
1. Залить папку в GitHub-репозиторий.
2. render.com → New → Web Service → выбрать репозиторий (подхватится `Dockerfile`), план **Free**.
3. Получить URL вида `https://tasks-api-xxxx.onrender.com` (`/docs` — Swagger).

Данные хранятся в памяти и сбрасываются при перезапуске (на free-плане сервис засыпает после простоя).
