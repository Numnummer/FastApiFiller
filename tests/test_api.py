import pytest
from fastapi.testclient import TestClient

from app.main import app, reset_storage

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean():
    reset_storage()


def make(title="Task", **kw):
    r = client.post("/tasks", json={"title": title, **kw})
    assert r.status_code == 201
    return r.json()


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_create_task_body():
    t = make("Купить молоко", priority="high")
    assert t["id"] == 1 and t["priority"] == "high" and t["done"] is False


def test_create_validation():
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={"title": "x", "priority": "urgent"}).status_code == 422


def test_get_task_path():
    t = make()
    assert client.get(f"/tasks/{t['id']}").json()["title"] == "Task"
    assert client.get("/tasks/999").status_code == 404
    assert client.get("/tasks/abc").status_code == 422


def test_list_query_filters():
    make("Alpha", priority="low")
    b = make("Beta", priority="high")
    client.patch(f"/tasks/{b['id']}", json={"done": True})
    assert len(client.get("/tasks").json()) == 2
    assert [t["title"] for t in client.get("/tasks?priority=high").json()] == ["Beta"]
    assert [t["title"] for t in client.get("/tasks?done=false").json()] == ["Alpha"]
    assert [t["title"] for t in client.get("/tasks?search=alp").json()] == ["Alpha"]
    assert len(client.get("/tasks?limit=1&offset=1").json()) == 1
    assert client.get("/tasks?limit=0").status_code == 422


def test_patch_path_and_body():
    t = make()
    r = client.patch(f"/tasks/{t['id']}", json={"done": True, "title": "New"})
    assert r.json()["done"] is True and r.json()["title"] == "New"
    assert client.patch("/tasks/999", json={"done": True}).status_code == 404


def test_delete():
    t = make()
    assert client.delete(f"/tasks/{t['id']}").status_code == 204
    assert client.delete(f"/tasks/{t['id']}").status_code == 404


def test_stats():
    make(priority="high")
    t = make(priority="low")
    client.patch(f"/tasks/{t['id']}", json={"done": True})
    s = client.get("/stats").json()
    assert s["total"] == 2 and s["done"] == 1 and s["by_priority"]["high"] == 1


def test_index_page():
    assert client.get("/").status_code == 200
