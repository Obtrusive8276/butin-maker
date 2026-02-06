from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Configuration logging applicatif
# Uvicorn configure son propre logger mais pas le root logger Python.
# Sans ceci, les logger.info() des services sont silencieusement ignorés.
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from .routers import (
    files_router,
    torrent_router,
    mediainfo_router,
    presentation_router,
    tags_router,
    settings_router,
    tmdb_router,
    lacale_router
)

app = FastAPI(
    title="La Cale Upload Preparation Tool",
    description="API pour préparer les uploads sur le tracker La Cale",
    version="1.0.0"
)

# CORS origins configurable via env var, fallback to dev defaults
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files_router)
app.include_router(torrent_router)
app.include_router(mediainfo_router)
app.include_router(presentation_router)
app.include_router(tags_router)
app.include_router(settings_router)
app.include_router(tmdb_router)
app.include_router(lacale_router)


@app.get("/")
async def root():
    return {
        "name": "La Cale Upload Preparation Tool",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
