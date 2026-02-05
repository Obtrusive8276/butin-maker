from fastapi import APIRouter, Body
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from ..services.qbittorrent_service import qbittorrent_service
from ..models.torrent import TorrentCreate, TorrentResponse

router = APIRouter(prefix="/torrent", tags=["torrent"])


class ConnectionTest(BaseModel):
    host: str
    port: int
    username: str
    password: str


@router.post("/test-connection")
async def test_connection(data: ConnectionTest):
    success, message = qbittorrent_service.test_connection(
        host=data.host,
        port=data.port,
        username=data.username,
        password=data.password
    )
    return {"success": success, "message": message}


@router.post("/create", response_model=TorrentResponse)
async def create_torrent(data: TorrentCreate):
    success, result = qbittorrent_service.create_torrent(
        source_path=data.source_path,
        name=data.name,
        piece_size=data.piece_size,
        private=data.private,
        tracker_url=data.tracker_url
    )
    
    if success:
        return TorrentResponse(
            success=True,
            torrent_path=result["torrent_path"],
            torrent_name=result["torrent_name"],
            info_hash=result["info_hash"],
            size=result["size"],
            piece_count=result["piece_count"]
        )
    else:
        return TorrentResponse(
            success=False,
            error=result.get("error", "Erreur inconnue")
        )


@router.get("/download/{filename}")
async def download_torrent(filename: str):
    from ..config import settings
    torrent_path = settings.output_path / filename
    
    if not torrent_path.exists():
        return {"error": "Fichier non trouvé"}
    
    return FileResponse(
        path=torrent_path,
        filename=filename,
        media_type="application/x-bittorrent"
    )


@router.post("/add-for-seeding")
async def add_for_seeding(
    torrent_path: str = Body(...),
    content_path: str = Body(...)
):
    success, message = qbittorrent_service.add_torrent_for_seeding(
        torrent_path=torrent_path,
        content_path=content_path
    )
    return {"success": success, "message": message}
