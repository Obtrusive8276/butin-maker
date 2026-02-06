"""Router FastAPI pour l'API La Cale"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Optional

from ..config import user_settings
from ..models.lacale import LaCaleUploadRequest, LaCaleUploadResponse
from ..services.lacale_service import LaCaleService, LaCaleError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lacale", tags=["La Cale"])


def _get_service() -> LaCaleService:
    """Crée une instance du service La Cale avec l'API key depuis les settings"""
    tracker_settings = user_settings.get().get("tracker", {})
    api_key = tracker_settings.get("lacale_api_key", "")
    return LaCaleService(api_key=api_key)


@router.get("/meta")
async def get_meta():
    """Récupère les métadonnées (catégories, tags) depuis l'API La Cale"""
    service = _get_service()
    try:
        meta = await service.fetch_meta()
        return meta
    except LaCaleError as e:
        logger.error("Erreur La Cale (meta): %s", e)
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error("Erreur inattendue (meta): %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category")
async def get_category(type: str):
    """Retourne l'ID de catégorie pour un type de contenu (movie/tv)"""
    service = _get_service()
    try:
        meta = await service.fetch_meta()
        category_id = service.find_category_id(meta, type)
        
        if category_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"Catégorie non trouvée pour le type '{type}'"
            )
        
        return {"category_id": category_id}
    except HTTPException:
        raise
    except LaCaleError as e:
        logger.error("Erreur La Cale (category): %s", e)
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error("Erreur inattendue (category): %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=LaCaleUploadResponse)
async def upload_torrent(request: LaCaleUploadRequest):
    """Upload un torrent vers La Cale via l'API"""
    service = _get_service()
    try:
        result = await service.upload(
            title=request.title,
            category_id=request.category_id,
            torrent_file_path=request.torrent_file_path,
            tag_ids=request.tag_ids,
            description=request.description,
            tmdb_id=request.tmdb_id,
            tmdb_type=request.tmdb_type,
            cover_url=request.cover_url,
            nfo_file_path=request.nfo_file_path
        )
        return LaCaleUploadResponse(**result)
    except FileNotFoundError as e:
        logger.error("Fichier introuvable (upload): %s", e)
        raise HTTPException(status_code=404, detail=str(e))
    except LaCaleError as e:
        logger.error("Erreur La Cale (upload): %s", e)
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))
    except Exception as e:
        logger.error("Erreur inattendue (upload): %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
