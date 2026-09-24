import pytest

from app.history.dependencies import get_conversation_store
from app.history.store import SQLiteConversationStore
from app.main import app


@pytest.fixture
def conversation_store(tmp_path):
    store = SQLiteConversationStore(str(tmp_path / "history.db"))
    app.dependency_overrides[get_conversation_store] = lambda: store
    yield store
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_conversation_crud(client, conversation_store):
    created = await client.post("/api/conversations", json={"title": " Session "})
    assert created.status_code == 201
    conversation_id = created.json()["id"]
    assert created.json()["title"] == "Session"
    assert created.json()["messages"] == []

    listed = await client.get("/api/conversations")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == conversation_id

    detail = await client.get(f"/api/conversations/{conversation_id}")
    assert detail.status_code == 200

    deleted = await client.delete(f"/api/conversations/{conversation_id}")
    assert deleted.status_code == 204
    assert await conversation_store.list() == []

    missing = await client.get(f"/api/conversations/{conversation_id}")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Conversation not found"}


@pytest.mark.asyncio
async def test_conversation_request_rejects_unknown_fields(client, conversation_store):
    response = await client.post(
        "/api/conversations", json={"title": "Session", "unexpected": True}
    )
    assert response.status_code == 422
