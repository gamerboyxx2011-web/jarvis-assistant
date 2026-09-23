"""Health-check route."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str | bool]:
    return {
        "application": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "nvidia_configured": bool(settings.NVIDIA_API_KEY.strip()),
    }
