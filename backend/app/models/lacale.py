"""Modèles Pydantic pour l'API La Cale"""
from pydantic import BaseModel
from typing import Optional, List


class LaCaleTag(BaseModel):
    id: str
    name: str
    slug: str


class LaCaleTagGroup(BaseModel):
    id: str
    name: str
    slug: str
    order: Optional[int] = None
    tags: List[LaCaleTag] = []


class LaCaleCategory(BaseModel):
    id: str
    name: str
    slug: str
    icon: Optional[str] = None
    parentId: Optional[str] = None
    children: List["LaCaleCategory"] = []


class LaCaleMetaResponse(BaseModel):
    categories: List[LaCaleCategory] = []
    tagGroups: List[LaCaleTagGroup] = []
    ungroupedTags: List[LaCaleTag] = []


class LaCaleUploadRequest(BaseModel):
    title: str
    category_id: str
    torrent_file_path: str
    tag_ids: List[str] = []
    description: Optional[str] = None
    tmdb_id: Optional[str] = None
    tmdb_type: Optional[str] = None  # "MOVIE" | "TV"
    cover_url: Optional[str] = None
    nfo_file_path: Optional[str] = None


class LaCaleUploadResponse(BaseModel):
    success: bool
    id: Optional[str] = None
    slug: Optional[str] = None
    link: Optional[str] = None
    error: Optional[str] = None
