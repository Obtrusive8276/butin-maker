from fastapi import APIRouter
from ..config import user_settings
from ..models.settings import SettingsModel, QBittorrentSettings, TrackerSettings, PathSettings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsModel)
async def get_settings():
    data = user_settings.get()
    return SettingsModel(**data)


@router.post("/")
async def save_settings(data: SettingsModel):
    user_settings.save(data.model_dump())
    return {"success": True, "message": "Paramètres sauvegardés"}


@router.patch("/qbittorrent")
async def update_qbittorrent_settings(data: QBittorrentSettings):
    user_settings.update("qbittorrent", data.model_dump())
    return {"success": True}


@router.patch("/tracker")
async def update_tracker_settings(data: TrackerSettings):
    user_settings.update("tracker", data.model_dump())
    return {"success": True}


@router.patch("/paths")
async def update_paths_settings(data: PathSettings):
    user_settings.update("paths", data.model_dump())
    return {"success": True}
