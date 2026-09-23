import os

os.environ.setdefault("NVIDIA_API_KEY", "test-nvidia-api-key")

import httpx
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
