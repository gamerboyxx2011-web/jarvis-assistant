"""
JARVIS AI Assistant V3 - Health Check Route
"""

from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns information about the application status and Gemini configuration.
    """
    gemini_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())

    return {
        "application": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "gemini_configured": gemini_configured
    }