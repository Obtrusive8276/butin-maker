from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import Optional
from ..services.presentation_service import presentation_service

router = APIRouter(prefix="/presentation", tags=["presentation"])


class PresentationData(BaseModel):
    poster_url: Optional[str] = ""
    title: str = "Titre"
    rating: Optional[str] = "N/A"
    genre: Optional[str] = ""
    synopsis: Optional[str] = ""
    quality: Optional[str] = ""
    format: Optional[str] = ""
    video_codec: Optional[str] = ""
    audio_codec: Optional[str] = ""
    languages: Optional[str] = ""
    subtitles: Optional[str] = "Aucun"
    size: Optional[str] = ""


@router.post("/generate")
async def generate_presentation(data: PresentationData):
    result = presentation_service.generate_presentation(data.model_dump())
    return {"bbcode": result}


@router.get("/template")
async def get_template():
    template = presentation_service.get_template()
    return {"template": template}


@router.post("/template")
async def save_template(template: str = Body(..., embed=True)):
    success = presentation_service.save_template(template)
    return {"success": success}
