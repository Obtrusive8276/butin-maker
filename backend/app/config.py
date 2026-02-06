from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import json
import logging
import os
from typing import Optional

from .models.settings import SettingsModel

logger = logging.getLogger(__name__)


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
        try:
            user_output = user_settings.get().get("paths", {}).get("output_path", "")
            if user_output:
                return Path(user_output)
        except NameError:
            pass  # user_settings pas encore créé
        return Path(os.getenv("OUTPUT_DIR", "/app/output"))


settings = Settings()


class UserSettings:
    """Gestion des paramètres utilisateur persistés dans settings.json.
    
    Utilise SettingsModel (Pydantic) comme source unique de vérité pour les
    valeurs par défaut et la validation. Le merge entre données persistées et
    defaults est automatique via le constructeur Pydantic.
    """

    def __init__(self):
        self.settings_file = settings.data_path / "settings.json"
        self._model = self._load()
    
    def _load(self) -> SettingsModel:
        """Charge le fichier JSON et le valide via Pydantic.
        
        Les champs manquants reçoivent automatiquement leur valeur par défaut.
        Les champs inconnus sont ignorés silencieusement (robustesse migration).
        """
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                # Pydantic fusionne automatiquement avec les defaults
                return SettingsModel(**raw)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning("Erreur lecture settings.json, utilisation des défauts: %s", e)
                return SettingsModel()
        return SettingsModel()
    
    def save(self, data: dict):
        """Sauvegarde les settings après validation Pydantic.
        
        Les données passées sont validées par SettingsModel avant écriture.
        Les champs manquants sont complétés par les valeurs par défaut.
        """
        self._model = SettingsModel(**data)
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self._model.model_dump(), f, indent=2, ensure_ascii=False)
    
    def get(self) -> dict:
        """Retourne les settings comme dict, toujours complet avec tous les champs."""
        return self._model.model_dump()
    
    def update(self, key: str, value: dict):
        """Met à jour une section spécifique des settings.
        
        Fusionne la nouvelle valeur dans le modèle existant avant sauvegarde.
        """
        current = self._model.model_dump()
        current[key] = value
        self.save(current)


user_settings = UserSettings()
