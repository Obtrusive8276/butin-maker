from pydantic import BaseModel


class QBittorrentSettings(BaseModel):
    host: str = "http://localhost"
    port: int = 8080
    username: str = "admin"
    password: str = ""


class TrackerSettings(BaseModel):
    announce_url: str = ""
    upload_url: str = "https://la-cale.space/upload"
    lacale_api_key: str = ""


class PathSettings(BaseModel):
    default_browse_path: str = ""
    hardlink_path: str = ""
    qbittorrent_download_path: str = ""
    output_path: str = ""


class TMDBSettings(BaseModel):
    api_key: str = ""


class SettingsModel(BaseModel):
    qbittorrent: QBittorrentSettings = QBittorrentSettings()
    tracker: TrackerSettings = TrackerSettings()
    paths: PathSettings = PathSettings()
    tmdb: TMDBSettings = TMDBSettings()
