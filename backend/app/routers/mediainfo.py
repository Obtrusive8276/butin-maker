from fastapi import APIRouter, Query
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from ..services.mediainfo_service import mediainfo_service
from ..config import settings

router = APIRouter(prefix="/mediainfo", tags=["mediainfo"])


@router.get("/analyze")
async def analyze_file(path: str = Query(..., description="Chemin du fichier média")):
    result = mediainfo_service.analyze_file(path)
    if result is None:
        return {"error": "Impossible d'analyser le fichier"}
    return result.model_dump()


@router.get("/raw")
async def get_raw_mediainfo(path: str = Query(..., description="Chemin du fichier média")):
    result = mediainfo_service.get_raw_mediainfo(path)
    if result is None:
        return {"error": "Impossible d'obtenir les informations"}
    return PlainTextResponse(content=result)


@router.post("/generate-nfo")
async def generate_nfo(
    path: str = Query(..., description="Chemin du fichier média"),
    release_name: str = Query(None, description="Nom de release pour le fichier NFO")
):
    success, nfo_data = mediainfo_service.generate_nfo(path, release_name)
    if not success or nfo_data is None:
        return {"success": False, "error": "Erreur lors de la génération du NFO"}
    return {
        "success": True,
        "file_path": nfo_data.file_path,
        "content": nfo_data.content
    }


@router.get("/download-nfo/{filename}")
async def download_nfo(filename: str):
    nfo_path = settings.output_path / filename
    
    if not nfo_path.exists():
        return {"error": "Fichier non trouvé"}
    
    return FileResponse(
        path=nfo_path,
        filename=filename,
        media_type="text/plain"
    )
