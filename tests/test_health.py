import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "application": "JARVIS AI Assistant V3",
        "version": "0.1.0",
        "status": "healthy",
        "nvidia_configured": True,
    }
