from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Football AI analytical backend API",
)


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
    }
