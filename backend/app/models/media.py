from pydantic import BaseModel
from typing import Optional, List


class VideoTrack(BaseModel):
    codec: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    bitrate: Optional[int] = None
    framerate: Optional[float] = None
    duration: Optional[float] = None
    hdr: Optional[str] = None


class AudioTrack(BaseModel):
    codec: Optional[str] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    language: Optional[str] = None
    title: Optional[str] = None


class SubtitleTrack(BaseModel):
    codec: Optional[str] = None
    language: Optional[str] = None
    title: Optional[str] = None
    forced: bool = False


class MediaInfo(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    container: Optional[str] = None
    duration: Optional[float] = None
    video_tracks: List[VideoTrack] = []
    audio_tracks: List[AudioTrack] = []
    subtitle_tracks: List[SubtitleTrack] = []


class NFOData(BaseModel):
    file_path: str
    content: str
