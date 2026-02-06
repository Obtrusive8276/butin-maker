import qbittorrentapi
from typing import Optional, Tuple
from pathlib import Path
import torf
from ..config import user_settings, settings


class QBittorrentService:
    def __init__(self):
        self._client = None
    
    def _get_settings(self) -> dict:
        return user_settings.get().get("qbittorrent", {})
    
    def connect(self, host: str = None, port: int = None, 
                username: str = None, password: str = None) -> Tuple[bool, str]:
        qb_settings = self._get_settings()
        
        host = host or qb_settings.get("host", "http://localhost")
        port = port or qb_settings.get("port", 8080)
        username = username or qb_settings.get("username", "admin")
        password = password or qb_settings.get("password", "")
        
        try:
            self._client = qbittorrentapi.Client(
                host=host,
                port=port,
                username=username,
                password=password
            )
            self._client.auth_log_in()
            return True, f"Connecté à qBittorrent {self._client.app.version}"
        except qbittorrentapi.LoginFailed as e:
            return False, f"Échec de connexion: identifiants incorrects"
        except Exception as e:
            return False, f"Erreur de connexion: {str(e)}"
    
    def test_connection(self, host: str, port: int, 
                       username: str, password: str) -> Tuple[bool, str]:
        try:
            client = qbittorrentapi.Client(
                host=host,
                port=port,
                username=username,
                password=password
            )
            client.auth_log_in()
            version = client.app.version
            client.auth_log_out()
            return True, f"Connexion réussie - qBittorrent {version}"
        except qbittorrentapi.LoginFailed:
            return False, "Échec: identifiants incorrects"
        except Exception as e:
            return False, f"Échec de connexion: {str(e)}"
    
    def create_torrent(self, source_path: str, name: str = None,
                       piece_size: int = None, private: bool = True,
                       tracker_url: str = None) -> Tuple[bool, dict]:
        try:
            source = Path(source_path)
            if not source.exists():
                return False, {"error": f"Le chemin n'existe pas: {source_path}"}
            
            if source.is_file():
                source_ext = source.suffix
                base_name = name or source.stem
                if name and source_ext and name.lower().endswith(source_ext.lower()):
                    base_name = name[: -len(source_ext)]
                torrent_name = base_name
                content_name = base_name
                if source_ext:
                    content_name = f"{content_name}{source_ext}"
            else:
                content_name = name or source.name
                torrent_name = name or source.name
            
            t = torf.Torrent(path=source_path)
            t.name = content_name
            t.private = private
            
            if piece_size:
                t.piece_size = piece_size
            
            tracker_settings = user_settings.get().get("tracker", {})
            announce_url = tracker_url or tracker_settings.get("announce_url", "")
            
            if announce_url:
                t.trackers = [[announce_url]]
            
            t.generate()
            
            output_file = settings.output_path / f"{torrent_name}.torrent"
            t.write(output_file, overwrite=True)
            
            return True, {
                "torrent_path": str(output_file),
                "torrent_name": torrent_name,
                "info_hash": t.infohash,
                "size": t.size,
                "piece_count": t.pieces
            }
        except Exception as e:
            return False, {"error": str(e)}
    
    def add_torrent_for_seeding(self, torrent_path: str, 
                                 content_path: str,
                                 save_path: str = None) -> Tuple[bool, str]:
        if not self._client:
            success, msg = self.connect()
            if not success:
                return False, msg
        
        try:
            # Utiliser le save_path des settings si non fourni
            if not save_path:
                path_settings = user_settings.get().get("paths", {})
                save_path = path_settings.get("qbittorrent_download_path", "")
            
            with open(torrent_path, 'rb') as f:
                add_params = {
                    "torrent_files": f,
                    "is_skip_checking": False
                }
                # Ajouter save_path seulement s'il est défini
                if save_path:
                    add_params["save_path"] = save_path
                
                self._client.torrents_add(**add_params)
            return True, "Torrent ajouté pour seeding"
        except Exception as e:
            return False, f"Erreur lors de l'ajout: {str(e)}"


qbittorrent_service = QBittorrentService()
