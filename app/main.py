"""JARVIS AI Assistant V3 FastAPI application."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routes import chat, conversations, health, voice
STATIC_DIR=Path(__file__).resolve().parent/"static"
app=FastAPI(title=settings.APP_NAME,description="A personal desktop-style AI assistant running locally",version=settings.VERSION)
app.include_router(health.router,prefix="/api",tags=["health"])
app.include_router(chat.router,prefix="/api",tags=["chat"])
app.include_router(voice.router,prefix="/api",tags=["voice"])
app.include_router(conversations.router,prefix="/api",tags=["conversations"])
app.mount("/static",StaticFiles(directory=STATIC_DIR),name="static")
@app.get("/")
async def root()->dict[str,str]: return {"message":f"{settings.APP_NAME} is running"}
@app.get("/app",response_class=FileResponse)
@app.get("/app/",response_class=FileResponse,include_in_schema=False)
async def web_app()->FileResponse: return FileResponse(STATIC_DIR/"index.html")
