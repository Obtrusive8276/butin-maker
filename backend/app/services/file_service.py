from pathlib import Path
from typing import List, Optional, Tuple
import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)


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
                        except Exception:
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
            logger.error("Erreur listage: %s", e)
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
            if not self._is_path_allowed(path):
                return None
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
            if not self._is_path_allowed(path):
                return 0
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        except Exception:
            pass
        return total_size
    
    def get_first_video_file(self, directory_path: str) -> Optional[dict]:
        """Trouve le premier fichier vidéo dans un dossier (récursif)"""
        try:
            path = Path(directory_path)
            if not self._is_path_allowed(path):
                return None
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
            logger.error("Erreur recherche vidéo: %s", e)
            return None
    
    def count_video_files(self, directory_path: str) -> int:
        """Compte le nombre de fichiers vidéo dans un dossier"""
        try:
            path = Path(directory_path)
            if not self._is_path_allowed(path):
                return 0
            if not path.exists() or not path.is_dir():
                return 0
            
            video_extensions = self.MEDIA_EXTENSIONS['video']
            count = 0
            
            for item in path.rglob('*'):
                if item.is_file() and item.suffix.lower() in video_extensions:
                    count += 1
            
            return count
        except Exception:
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
                        except Exception:
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
            logger.error("Erreur recherche: %s", e)
            return []
    
    def _validate_hardlink_paths(self, source: Path, destination: Path) -> Optional[str]:
        """Valide les chemins source et destination pour un hardlink.
        
        Returns:
            None si valide, message d'erreur sinon.
        """
        if not source.exists():
            return f"La source n'existe pas: {source}"
        
        if not self._is_path_allowed(source):
            return "Accès refusé: la source n'est pas dans le répertoire média"
        
        from app.config import user_settings
        hardlink_path = user_settings.get().get("paths", {}).get("hardlink_path", "")
        if hardlink_path:
            try:
                destination.resolve().relative_to(Path(hardlink_path).resolve())
            except ValueError:
                return "Accès refusé: la destination n'est pas dans le répertoire de hardlinks configuré"
        else:
            if not self._is_path_allowed(destination):
                return "Accès refusé: la destination n'est pas dans le répertoire média. Configurez un dossier de hardlinks dans les paramètres."
        
        return None

    def _build_existing_inodes(self, directory: Path) -> dict:
        """Construit un index inode → chemin relatif pour les fichiers existants dans un dossier.
        
        Utilise os.scandir récursif pour minimiser les appels système (1 stat par fichier
        au lieu de exists() + stat() + stat() = 3 appels).
        
        Returns:
            Dict {chemin_relatif_str: inode} des fichiers existants.
        """
        existing = {}
        if not directory.exists():
            return existing
        
        def _scan(current: Path, rel_prefix: Path):
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        rel = rel_prefix / entry.name
                        if entry.is_file(follow_symlinks=False):
                            try:
                                # entry.stat().st_ino peut retourner 0 sur Windows via scandir
                                # Utiliser Path.stat() qui retourne toujours le bon inode
                                existing[str(rel)] = Path(entry.path).stat().st_ino
                            except OSError:
                                pass
                        elif entry.is_dir(follow_symlinks=False):
                            _scan(Path(entry.path), rel)
            except PermissionError:
                pass
        
        _scan(directory, Path('.'))
        return existing

    def _collect_source_files(self, source: Path) -> List[Path]:
        """Collecte tous les fichiers source en une seule passe avec os.scandir.
        
        Returns:
            Liste de Path relatifs des fichiers dans le dossier source.
        """
        files = []
        
        def _scan(current: Path, rel_prefix: Path):
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        rel = rel_prefix / entry.name
                        if entry.is_file(follow_symlinks=False):
                            files.append(rel)
                        elif entry.is_dir(follow_symlinks=False):
                            _scan(Path(entry.path), rel)
            except PermissionError:
                pass
        
        _scan(source, Path('.'))
        return files

    def create_hardlink(self, source_path: str, destination_path: str) -> Tuple[bool, str]:
        """Crée un hardlink entre la source et la destination.
        
        Pour les fichiers: crée un hardlink direct.
        Pour les dossiers: crée l'arborescence et hardlink chaque fichier.
        
        Optimisé pour les dossiers de séries : pré-indexe les inodes existants
        en une seule passe (os.scandir) pour éviter les appels exists()/stat()
        répétés par fichier.
        
        Args:
            source_path: Chemin du fichier/dossier source
            destination_path: Chemin de destination du hardlink
            
        Returns:
            Tuple (success, message)
        """
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            # Validation des chemins
            error = self._validate_hardlink_paths(source, destination)
            if error:
                return False, error
            
            # Créer le dossier parent de destination s'il n'existe pas
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Impossible de créer le dossier destination: {str(e)}"
            
            # === CAS FICHIER ===
            if source.is_file():
                # Vérifier si la destination existe déjà
                if destination.exists():
                    try:
                        if destination.stat().st_ino == source.stat().st_ino:
                            return True, f"Hardlink déjà existant: {destination_path}"
                    except Exception:
                        pass
                    return False, f"La destination existe déjà: {destination_path}"
                
                try:
                    os.link(source, destination)
                    return True, f"Hardlink créé: {destination_path}"
                except OSError as e:
                    if e.errno == 18:  # EXDEV - Cross-device link
                        return False, "Impossible de créer le hardlink: la source et la destination doivent être sur le même système de fichiers"
                    elif e.errno == 1:  # EPERM - Operation not permitted
                        return False, f"Impossible de créer le hardlink: {str(e)}"
                    else:
                        return False, f"Erreur lors de la création du hardlink: {str(e)}"
            
            # === CAS DOSSIER ===
            elif source.is_dir():
                try:
                    destination.mkdir(parents=True, exist_ok=True)
                    
                    # Phase 1: Collecter tous les fichiers source en une passe
                    source_files = self._collect_source_files(source)
                    total_files = len(source_files)
                    
                    if total_files == 0:
                        return True, "Dossier vide, rien à traiter"
                    
                    # Phase 2: Indexer les fichiers existants à la destination (1 seule passe)
                    existing_inodes = self._build_existing_inodes(destination)
                    
                    # Phase 3: Créer les sous-dossiers nécessaires en batch
                    needed_dirs = set()
                    for rel_path in source_files:
                        parent = rel_path.parent
                        if str(parent) != '.':
                            needed_dirs.add(parent)
                    
                    for dir_path in sorted(needed_dirs):
                        (destination / dir_path).mkdir(parents=True, exist_ok=True)
                    
                    # Phase 4: Créer les hardlinks
                    linked_count = 0
                    skipped_count = 0
                    error_count = 0
                    errors = []
                    
                    for rel_path in source_files:
                        rel_str = str(rel_path)
                        source_file = source / rel_path
                        dest_file = destination / rel_path
                        
                        # Vérifier via l'index si le fichier existe déjà
                        if rel_str in existing_inodes:
                            existing_ino = existing_inodes[rel_str]
                            try:
                                source_ino = source_file.stat().st_ino
                                if existing_ino == source_ino:
                                    skipped_count += 1  # Déjà hardlinké
                                    continue
                                else:
                                    skipped_count += 1  # Fichier différent, on skip
                                    continue
                            except OSError:
                                skipped_count += 1
                                continue
                        
                        # Créer le hardlink
                        try:
                            os.link(source_file, dest_file)
                            linked_count += 1
                        except OSError as e:
                            error_count += 1
                            if len(errors) < 3:  # Limiter les messages d'erreur
                                errors.append(f"{rel_path}: {e}")
                    
                    # Construire le message de résultat
                    messages = []
                    if linked_count > 0:
                        messages.append(f"{linked_count} hardlinks créés")
                    if skipped_count > 0:
                        messages.append(f"{skipped_count} fichiers déjà existants ignorés")
                    if error_count > 0:
                        error_detail = "; ".join(errors)
                        messages.append(f"{error_count} erreurs ({error_detail})")
                    
                    success = error_count == 0 or linked_count > 0
                    return success, f"Dossier traité ({total_files} fichiers): {', '.join(messages)}"
                    
                except Exception as e:
                    return False, f"Erreur lors de la création des hardlinks: {str(e)}"
            
            return False, "Type de source non supporté"
            
        except Exception as e:
            return False, f"Erreur inattendue: {str(e)}"


file_service = FileService()
