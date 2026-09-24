from pathlib import Path
import pytest

@pytest.mark.asyncio
async def test_phase1_root_response_is_preserved(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "JARVIS AI Assistant V3 is running"}

@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/app", "/app/"])
async def test_web_app_entrypoint_is_served(client, path):
    response = await client.get(path)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<main class="chat-panel">' in response.text
    assert 'src="/static/app.js"' in response.text
    assert 'href="/static/styles.css"' in response.text

@pytest.mark.asyncio
@pytest.mark.parametrize(("path", "content_type"), [("/static/app.js", "text/javascript"), ("/static/styles.css", "text/css")])
async def test_frontend_assets_are_served(client, path, content_type):
    response = await client.get(path)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(content_type)

@pytest.mark.asyncio
async def test_missing_static_asset_returns_404_without_api_fallback(client):
    assert (await client.get("/static/missing.js")).status_code == 404

def test_frontend_keeps_phase3_and_security_contracts():
    script = (Path(__file__).parents[1] / "app" / "static" / "app.js").read_text()
    assert 'fetch("/api/chat"' in script
    assert "conversation_id:conversationId" in script.replace(" ", "")
    assert ".textContent" in script
    assert ".innerHTML" not in script
    assert "AbortController" in script
    assert 'buffer.indexOf("\\n\\n")' in script
