"""JARVIS AI Assistant V3 FastAPI application."""

from fastapi import FastAPI

from app.config import settings
from app.routes import chat, conversations, health

app = FastAPI(
    title=settings.APP_NAME,
    description="A personal desktop-style AI assistant running locally",
    version=settings.VERSION,
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"{settings.APP_NAME} is running"}
