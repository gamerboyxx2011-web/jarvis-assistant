"""
JARVIS AI Assistant V3 - Main FastAPI Application
"""

from fastapi import FastAPI
from app.routes import health, chat

app = FastAPI(
    title="JARVIS AI Assistant V3",
    description="A personal desktop-style AI assistant running locally",
    version="0.1.0"
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "JARVIS AI Assistant V3 is running"}