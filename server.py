"""JARVIS AI Assistant V3 entrypoint."""

from app.config import settings
from app.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
