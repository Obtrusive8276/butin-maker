from fastapi import APIRouter, Query
from typing import Optional, List
from ..services.file_service import file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/root")
async def get_root():
    """Get the media root directory"""
    return file_service.get_root()


@router.get("/list")
async def list_directory(
    path: str = Query(..., description="Chemin du répertoire"),
    filter_type: Optional[str] = Query(None, description="Filtrer par type: video, audio, ebook, archive")
):
    items = file_service.list_directory(path, filter_type)
    parent = file_service.get_parent_path(path)
    return {
        "current_path": path,
        "parent_path": parent,
        "items": items
    }


@router.get("/info")
async def get_file_info(path: str = Query(..., description="Chemin du fichier")):
    info = file_service.get_file_info(path)
    if info is None:
        return {"error": "Fichier non trouvé"}
    return info


@router.get("/directory-size")
async def get_directory_size(path: str = Query(..., description="Chemin du répertoire")):
    size = file_service.get_directory_size(path)
    return {"path": path, "size": size}


@router.get("/first-video")
async def get_first_video(path: str = Query(..., description="Chemin du répertoire")):
    """Trouve le premier fichier vidéo dans un dossier"""
    video = file_service.get_first_video_file(path)
    if video is None:
        return {"error": "Aucun fichier vidéo trouvé"}
    return video


@router.get("/video-count")
async def get_video_count(path: str = Query(..., description="Chemin du répertoire")):
    """Compte le nombre de fichiers vidéo dans un dossier"""
    count = file_service.count_video_files(path)
    return {"path": path, "count": count}


@router.get("/search")
async def search_files(
    path: str = Query(..., description="Chemin de base pour la recherche"),
    query: str = Query(..., description="Terme de recherche"),
    filter_type: Optional[str] = Query(None, description="Filtrer par type: video, audio, ebook, archive")
):
    """Recherche des fichiers par nom dans un répertoire"""
    results = file_service.search_files(path, query, filter_type)
    return {
        "query": query,
        "path": path,
        "results": results
    }
