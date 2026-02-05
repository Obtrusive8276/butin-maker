from pathlib import Path
from typing import List, Optional
import os

from app.config import settings


class FileItem:
    def __init__(self, path: Path, is_dir: bool):
        self.path = str(path)
        self.name = path.name
        self.is_dir = is_dir
        self.size = 0 if is_dir else path.stat().st_size if path.exists() else 0
        self.extension = path.suffix.lower() if not is_dir else ""


class FileService:
    
    MEDIA_EXTENSIONS = {
        'video': ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts'],
        'audio': ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.opus'],
        'ebook': ['.pdf', '.epub', '.mobi', '.azw', '.cbr', '.cbz', '.djvu'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso']
    }
    
    def __init__(self):
        self.media_root = settings.media_root
    
    def get_root(self) -> dict:
        """Returns the media root directory info"""
        return {
            "path": str(self.media_root),
            "name": "Media",
            "is_dir": True
        }
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within media_root to prevent directory traversal"""
        try:
            path.resolve().relative_to(self.media_root.resolve())
            return True
        except ValueError:
            return False
    
    def list_directory(self, directory_path: str, 
                       filter_type: Optional[str] = None) -> List[dict]:
        try:
            path = Path(directory_path)
            
            # Security: ensure path is within media_root
            if not self._is_path_allowed(path):
                return []
            
            if not path.exists() or not path.is_dir():
                return []
            
            items = []
            
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                try:
                    if item.name.startswith('.'):
                        continue
                    
                    is_dir = item.is_dir()
                    extension = item.suffix.lower() if not is_dir else ""
                    
                    if filter_type and not is_dir:
                        allowed_extensions = self.MEDIA_EXTENSIONS.get(filter_type, [])
                        if allowed_extensions and extension not in allowed_extensions:
                            continue
                    
                    size = 0
                    if not is_dir:
                        try:
                            size = item.stat().st_size
                        except:
                            pass
                    
                    items.append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": is_dir,
                        "size": size,
                        "extension": extension
                    })
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            return items
        except PermissionError:
            return []
        except Exception as e:
            print(f"Erreur listage: {e}")
            return []
    
    def get_parent_path(self, current_path: str) -> Optional[str]:
        path = Path(current_path)
        parent = path.parent
        
        # Don't go above media_root
        if parent == path or not self._is_path_allowed(parent):
            return None
        
        return str(parent)
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "path": str(path),
                "name": path.name,
                "is_dir": path.is_dir(),
                "size": stat.st_size,
                "extension": path.suffix.lower(),
                "modified": stat.st_mtime
            }
        except Exception:
            return None
    
    def get_directory_size(self, directory_path: str) -> int:
        total_size = 0
        try:
            path = Path(directory_path)
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except:
            pass
        return total_size
    
    def get_first_video_file(self, directory_path: str) -> Optional[dict]:
        """Trouve le premier fichier vidéo dans un dossier (récursif)"""
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                return None
            
            video_extensions = self.MEDIA_EXTENSIONS['video']
            
            # Chercher les fichiers vidéo, triés par nom
            video_files = []
            for item in path.rglob('*'):
                if item.is_file() and item.suffix.lower() in video_extensions:
                    video_files.append(item)
            
            if not video_files:
                return None
            
            # Trier par nom pour avoir le premier épisode
            video_files.sort(key=lambda x: x.name.lower())
            first_video = video_files[0]
            
            return {
                "path": str(first_video),
                "name": first_video.name,
                "is_dir": False,
                "size": first_video.stat().st_size,
                "extension": first_video.suffix.lower()
            }
        except Exception as e:
            print(f"Erreur recherche vidéo: {e}")
            return None
    
    def count_video_files(self, directory_path: str) -> int:
        """Compte le nombre de fichiers vidéo dans un dossier"""
        try:
            path = Path(directory_path)
            if not path.exists() or not path.is_dir():
                return 0
            
            video_extensions = self.MEDIA_EXTENSIONS['video']
            count = 0
            
            for item in path.rglob('*'):
                if item.is_file() and item.suffix.lower() in video_extensions:
                    count += 1
            
            return count
        except:
            return 0
    
    def is_video_file(self, file_path: str) -> bool:
        """Vérifie si un fichier est un fichier vidéo"""
        path = Path(file_path)
        return path.suffix.lower() in self.MEDIA_EXTENSIONS['video']
    
    def search_files(self, base_path: str, query: str, 
                     filter_type: Optional[str] = None, max_results: int = 100) -> List[dict]:
        """Recherche des fichiers par nom dans un répertoire (récursif)"""
        try:
            path = Path(base_path)
            
            if not self._is_path_allowed(path):
                return []
            
            if not path.exists() or not path.is_dir():
                return []
            
            query_lower = query.lower()
            results = []
            
            for item in path.rglob('*'):
                if len(results) >= max_results:
                    break
                
                try:
                    if item.name.startswith('.'):
                        continue
                    
                    # Vérifier si le nom contient la requête
                    if query_lower not in item.name.lower():
                        continue
                    
                    is_dir = item.is_dir()
                    extension = item.suffix.lower() if not is_dir else ""
                    
                    # Filtrer par type si spécifié
                    if filter_type and not is_dir:
                        allowed_extensions = self.MEDIA_EXTENSIONS.get(filter_type, [])
                        if allowed_extensions and extension not in allowed_extensions:
                            continue
                    
                    size = 0
                    if not is_dir:
                        try:
                            size = item.stat().st_size
                        except:
                            pass
                    
                    results.append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": is_dir,
                        "size": size,
                        "extension": extension
                    })
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            # Trier: dossiers d'abord, puis par nom
            results.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            return results
        except Exception as e:
            print(f"Erreur recherche: {e}")
            return []


file_service = FileService()
