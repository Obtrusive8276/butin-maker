from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import os
import time

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
    
    def _validate_hardlink_paths(self, source: Path, destination: Path,
                                   source_resolved: Path, destination_resolved: Path) -> Optional[str]:
        """Valide les chemins source et destination pour un hardlink.
        
        Les paths résolus sont passés en paramètre pour éviter de les recalculer
        (chaque resolve() fait un appel système, très lent sur NFS).
        
        Returns:
            None si valide, message d'erreur sinon.
        """
        if not source.exists():
            return f"La source n'existe pas: {source}"
        
        # Vérifier source dans media_root avec les paths déjà résolus
        try:
            source_resolved.relative_to(self.media_root.resolve())
        except ValueError:
            return "Accès refusé: la source n'est pas dans le répertoire média"
        
        from app.config import user_settings
        hardlink_path = user_settings.get().get("paths", {}).get("hardlink_path", "")
        if hardlink_path:
            try:
                destination_resolved.relative_to(Path(hardlink_path).resolve())
            except ValueError:
                return "Accès refusé: la destination n'est pas dans le répertoire de hardlinks configuré"
        else:
            try:
                destination_resolved.relative_to(self.media_root.resolve())
            except ValueError:
                return "Accès refusé: la destination n'est pas dans le répertoire média. Configurez un dossier de hardlinks dans les paramètres."
        
        return None

    def _scan_inodes(self, directory: str) -> Dict[str, int]:
        """Scanne un dossier et retourne {chemin_relatif: inode} pour chaque fichier.
        
        Utilise os.scandir récursif avec entry.stat() natif (pas de Path().stat()).
        Sur Linux, entry.stat() utilise le cache du noyau (READDIRPLUS sur NFS),
        ce qui est 10-100x plus rapide que Path().stat() qui fait un appel stat() séparé.
        
        Args:
            directory: Chemin absolu du dossier à scanner (string pour éviter Path overhead).
            
        Returns:
            Dict {chemin_relatif_str: inode} des fichiers trouvés.
        """
        inodes = {}
        
        def _scan(current_dir: str, rel_prefix: str):
            try:
                with os.scandir(current_dir) as entries:
                    for entry in entries:
                        rel = f"{rel_prefix}/{entry.name}" if rel_prefix else entry.name
                        if entry.is_file(follow_symlinks=False):
                            try:
                                inodes[rel] = entry.stat(follow_symlinks=False).st_ino
                            except OSError:
                                pass
                        elif entry.is_dir(follow_symlinks=False):
                            _scan(entry.path, rel)
            except (PermissionError, OSError):
                pass
        
        _scan(directory, "")
        return inodes

    def create_hardlink(self, source_path: str, destination_path: str) -> Tuple[bool, str]:
        """Crée un hardlink entre la source et la destination.
        
        Pour les fichiers: crée un hardlink direct.
        Pour les dossiers: crée l'arborescence et hardlink chaque fichier.
        
        Optimisé pour NFS : utilise entry.stat() natif (cache noyau), pré-indexe
        les inodes source ET destination en une seule passe, et utilise des strings
        au lieu de Path pour éviter l'overhead de construction d'objets.
        
        Args:
            source_path: Chemin du fichier/dossier source
            destination_path: Chemin de destination du hardlink
            
        Returns:
            Tuple (success, message)
        """
        t_start = time.monotonic()
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            # Résoudre les paths UNE SEULE FOIS (lent sur NFS)
            t0 = time.monotonic()
            source_resolved = source.resolve()
            destination_resolved = destination.resolve()
            t_resolve = time.monotonic() - t0
            
            # Validation des chemins (utilise les paths déjà résolus)
            t0 = time.monotonic()
            error = self._validate_hardlink_paths(source, destination,
                                                   source_resolved, destination_resolved)
            t_validate = time.monotonic() - t0
            if error:
                logger.info("[PERF] hardlink REJECTED in %.2fs (resolve=%.2fs, validate=%.2fs): %s",
                           time.monotonic() - t_start, t_resolve, t_validate, error)
                return False, error
            
            # Créer le dossier parent de destination s'il n'existe pas
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Impossible de créer le dossier destination: {str(e)}"
            
            # === CAS FICHIER ===
            if source.is_file():
                if destination.exists():
                    try:
                        if destination.stat().st_ino == source.stat().st_ino:
                            logger.info("[PERF] hardlink file ALREADY EXISTS in %.2fs", time.monotonic() - t_start)
                            return True, f"Hardlink déjà existant: {destination_path}"
                    except Exception:
                        pass
                    return False, f"La destination existe déjà: {destination_path}"
                
                try:
                    os.link(source, destination)
                    logger.info("[PERF] hardlink file CREATED in %.2fs", time.monotonic() - t_start)
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
                    
                    # Phase 1: Scanner source → {rel_path: inode}
                    t0 = time.monotonic()
                    source_inodes = self._scan_inodes(source_path)
                    total_files = len(source_inodes)
                    t_scan_source = time.monotonic() - t0
                    
                    if total_files == 0:
                        logger.info("[PERF] hardlink dir EMPTY in %.2fs", time.monotonic() - t_start)
                        return True, "Dossier vide, rien à traiter"
                    
                    # Phase 2: Scanner destination → {rel_path: inode}
                    t0 = time.monotonic()
                    existing_inodes = self._scan_inodes(destination_path)
                    t_scan_dest = time.monotonic() - t0
                    
                    # Phase 3: Créer les sous-dossiers nécessaires
                    t0 = time.monotonic()
                    needed_dirs = set()
                    for rel_path_str in source_inodes:
                        last_slash = rel_path_str.rfind('/')
                        if last_slash > 0:
                            needed_dirs.add(rel_path_str[:last_slash])
                    
                    for dir_path in sorted(needed_dirs):
                        try:
                            os.makedirs(os.path.join(destination_path, dir_path), exist_ok=True)
                        except FileExistsError:
                            pass
                    t_mkdir = time.monotonic() - t0
                    
                    # Phase 4: Créer les hardlinks
                    t0 = time.monotonic()
                    linked_count = 0
                    skipped_count = 0
                    error_count = 0
                    errors = []
                    
                    for rel_str, source_ino in source_inodes.items():
                        # Vérifier via l'index si le fichier existe déjà
                        existing_ino = existing_inodes.get(rel_str)
                        if existing_ino is not None:
                            if existing_ino == source_ino:
                                skipped_count += 1  # Déjà hardlinké (même inode)
                            else:
                                skipped_count += 1  # Fichier différent, on skip
                            continue
                        
                        # Créer le hardlink (utilise os.link avec des strings, pas des Path)
                        src = os.path.join(source_path, rel_str)
                        dst = os.path.join(destination_path, rel_str)
                        try:
                            os.link(src, dst)
                            linked_count += 1
                        except OSError as e:
                            error_count += 1
                            if len(errors) < 3:
                                errors.append(f"{rel_str}: {e}")
                    t_link = time.monotonic() - t0
                    
                    t_total = time.monotonic() - t_start
                    logger.info(
                        "[PERF] hardlink dir (%d files) in %.2fs: "
                        "resolve=%.2fs, validate=%.2fs, scan_src=%.2fs, scan_dst=%.2fs, "
                        "mkdir=%.2fs, link=%.2fs | linked=%d skipped=%d errors=%d",
                        total_files, t_total,
                        t_resolve, t_validate, t_scan_source, t_scan_dest,
                        t_mkdir, t_link,
                        linked_count, skipped_count, error_count
                    )
                    
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
