from fastapi import APIRouter

from app import config

router = APIRouter(tags=["health"])


@router.get("/")
def root():
    return {"service": config.APP_NAME, "version": config.APP_VERSION, "docs": "/docs"}


@router.get("/health")
def health():
    return {"status": "ok"}
