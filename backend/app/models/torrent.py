from pydantic import BaseModel
from typing import Optional, List


class TorrentCreate(BaseModel):
    source_path: str
    name: Optional[str] = None
    piece_size: Optional[int] = None
    private: bool = True
    tracker_url: Optional[str] = None


class TorrentResponse(BaseModel):
    success: bool
    torrent_path: Optional[str] = None
    torrent_name: Optional[str] = None
    info_hash: Optional[str] = None
    size: Optional[int] = None
    piece_count: Optional[int] = None
    error: Optional[str] = None
