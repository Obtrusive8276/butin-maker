from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import copy
import json
import os
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    
    qbittorrent_host: str = "http://localhost"
    qbittorrent_port: int = 8080
    qbittorrent_username: str = "admin"
    qbittorrent_password: str = "adminadmin"
    
    tracker_announce_url: str = ""
    lacale_upload_url: str = "https://la-cale.space/upload"
    
    tmdb_api_key: Optional[str] = None
    
    # Docker volume paths
    media_root: Path = Field(default=Path("/data"))
    config_dir: Path = Field(default=Path("/config"))
    output_dir: Path = Field(default=Path("/app/output"))
    
    @property
    def base_path(self) -> Path:
        return Path(__file__).parent.parent
    
    @property
    def data_path(self) -> Path:
        """Retourne le chemin pour les données/config"""
        if self.config_dir.exists():
            return self.config_dir
        path = self.base_path / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def output_path(self) -> Path:
        """Retourne le chemin pour les fichiers générés (utilise user_settings si disponible)"""
        # Import tardif pour éviter la dépendance circulaire
        try:
            user_output = user_settings.get().get("paths", {}).get("output_path", "")
            if user_output:
                return Path(user_output)
        except NameError:
            pass  # user_settings pas encore créé
        return Path(os.getenv("OUTPUT_DIR", "/app/output"))


settings = Settings()


class UserSettings:
    # Valeurs par défaut définies une seule fois
    DEFAULTS = {
        "qbittorrent": {
            "host": "http://localhost",
            "port": 8080,
            "username": "admin",
            "password": ""
        },
        "tracker": {
            "announce_url": "",
            "upload_url": "https://la-cale.space/upload",
            "lacale_api_key": ""
        },
        "paths": {
            "default_browse_path": "",
            "hardlink_path": "",
            "qbittorrent_download_path": "",
            "output_path": ""
        },
        "tmdb": {
            "api_key": "7b82b012524705130d16604a7e6b325d"
        }
    }

    def __init__(self):
        self.settings_file = settings.data_path / "settings.json"
        self._data = self._load()
    
    def _load(self) -> dict:
        if self.settings_file.exists():
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return copy.deepcopy(self.DEFAULTS)
    
    def save(self, data: dict):
        self._data = data
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get(self) -> dict:
        # Fusionner les données persistées avec les valeurs par défaut
        result = {}
        for key, default_value in self.DEFAULTS.items():
            if key in self._data:
                if isinstance(default_value, dict):
                    # Fusionner les sous-dictionnaires: utiliser le default uniquement si la clé est absente
                    merged = {}
                    for k, v in default_value.items():
                        if k in self._data[key]:
                            merged[k] = self._data[key][k]
                        else:
                            merged[k] = v
                    result[key] = merged
                else:
                    result[key] = self._data[key]
            else:
                result[key] = copy.deepcopy(default_value)
        return result
    
    def update(self, key: str, value: dict):
        self._data[key] = value
        self.save(self._data)


user_settings = UserSettings()
