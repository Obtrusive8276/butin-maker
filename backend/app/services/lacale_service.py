"""Service pour l'API La Cale - Upload automatique vers le tracker"""
import logging
from pathlib import Path
from typing import Optional, List

import httpx

logger = logging.getLogger(__name__)


class LaCaleError(Exception):
    """Exception spécifique aux erreurs de l'API La Cale"""
    def __init__(self, message: str, status_code: int = 0):
        self.status_code = status_code
        super().__init__(message)


class LaCaleService:
    """Service pour interagir avec l'API externe de La Cale"""
    
    DEFAULT_BASE_URL = "https://la-cale.space"
    TIMEOUT = 30.0  # secondes
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        url = base_url or self.DEFAULT_BASE_URL
        # Supprimer le trailing slash
        self.base_url = url.rstrip("/")
    
    def _get_headers(self) -> dict:
        """Construit les headers HTTP avec l'API key"""
        return {
            "X-Api-Key": self.api_key
        }
    
    def _handle_error_response(self, response: httpx.Response, context: str = ""):
        """Gère les réponses d'erreur HTTP de l'API La Cale"""
        status = response.status_code
        prefix = f"{context}: " if context else ""
        
        if status == 401:
            raise LaCaleError(f"{prefix}401 - API key manquante ou invalide", status_code=401)
        elif status == 403:
            raise LaCaleError(f"{prefix}403 - API key révoquée ou accès interdit", status_code=403)
        elif status == 409:
            raise LaCaleError(f"{prefix}409 - Torrent déjà existant (même InfoHash)", status_code=409)
        elif status == 429:
            raise LaCaleError(f"{prefix}429 - Limite de requêtes dépassée (30/min)", status_code=429)
        elif status == 500:
            raise LaCaleError(f"{prefix}500 - Erreur serveur La Cale", status_code=500)
        elif status >= 400:
            raise LaCaleError(f"{prefix}{status} - Erreur API La Cale: {response.text}", status_code=status)
    
    async def fetch_meta(self) -> dict:
        """Récupère les métadonnées (catégories, tags) depuis l'API La Cale
        
        Returns:
            dict avec categories, tagGroups, ungroupedTags
        
        Raises:
            LaCaleError: En cas d'erreur HTTP (401, 403, 500, etc.)
            Exception: En cas de timeout ou erreur réseau
        """
        url = f"{self.base_url}/api/external/meta"
        headers = self._get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                self._handle_error_response(response, context="fetch_meta")
            
            data = response.json()
            logger.info("Métadonnées La Cale récupérées: %d catégories, %d groupes de tags",
                       len(data.get("categories", [])), len(data.get("tagGroups", [])))
            return data
            
        except httpx.TimeoutException as e:
            logger.error("Timeout lors de la récupération des métadonnées La Cale: %s", e)
            raise LaCaleError(f"Timeout: impossible de contacter La Cale ({e})") from e
        except LaCaleError:
            raise
        except Exception as e:
            logger.error("Erreur lors de la récupération des métadonnées La Cale: %s", e, exc_info=True)
            raise
    
    def find_category_id(self, meta_data: dict, content_type: str) -> Optional[str]:
        """Trouve l'ID de catégorie à partir du type de contenu
        
        Args:
            meta_data: Réponse de fetch_meta()
            content_type: "movie" ou "tv"
        
        Returns:
            ID de la catégorie (ex: "cat_films") ou None
        """
        # Mapping type -> slug de catégorie
        slug_map = {
            "movie": "films",
            "tv": "series"
        }
        
        target_slug = slug_map.get(content_type)
        if not target_slug:
            logger.warning("Type de contenu inconnu: %s", content_type)
            return None
        
        categories = meta_data.get("categories", [])
        
        for category in categories:
            # Vérifier dans les enfants (structure hiérarchique)
            for child in category.get("children", []):
                if child.get("slug") == target_slug:
                    return child["id"]
            # Vérifier aussi au niveau racine
            if category.get("slug") == target_slug:
                return category["id"]
        
        logger.warning("Catégorie '%s' non trouvée dans les métadonnées La Cale", target_slug)
        return None
    
    async def upload(
        self,
        title: str,
        category_id: str,
        torrent_file_path: str,
        tag_ids: List[str] = None,
        description: str = None,
        tmdb_id: str = None,
        tmdb_type: str = None,
        cover_url: str = None,
        nfo_file_path: str = None
    ) -> dict:
        """Upload un torrent vers La Cale
        
        Args:
            title: Titre de la release
            category_id: ID catégorie (ex: "cat_films")
            torrent_file_path: Chemin vers le fichier .torrent
            tag_ids: Liste d'IDs de tags
            description: Description BBCode
            tmdb_id: ID TMDB
            tmdb_type: "MOVIE" ou "TV"
            cover_url: URL de l'affiche
            nfo_file_path: Chemin vers le fichier .nfo
        
        Returns:
            dict avec success, id, slug, link
        
        Raises:
            LaCaleError: En cas d'erreur HTTP
            FileNotFoundError: Si le fichier .torrent n'existe pas
        """
        # Vérifier que le fichier torrent existe
        torrent_path = Path(torrent_file_path)
        if not torrent_path.exists():
            raise FileNotFoundError(f"Fichier torrent introuvable: {torrent_file_path}")
        
        url = f"{self.base_url}/api/external/upload"
        headers = self._get_headers()
        
        try:
            # Construire le formulaire multipart
            files = {}
            data = {}
            
            # Champs requis
            data["title"] = title
            data["categoryId"] = category_id
            
            # Fichier .torrent — lire en bytes pour compatibilité AsyncClient
            torrent_content = torrent_path.read_bytes()
            files["file"] = (
                torrent_path.name,
                torrent_content,
                "application/x-bittorrent"
            )
            
            # Champs optionnels
            if description:
                data["description"] = description
            if tmdb_id:
                data["tmdbId"] = tmdb_id
            if tmdb_type:
                data["tmdbType"] = tmdb_type
            if cover_url:
                data["coverUrl"] = cover_url
            
            # Tags (champ répété)
            # httpx gère les champs répétés via une liste de tuples
            form_data = list(data.items())
            if tag_ids:
                for tag_id in tag_ids:
                    form_data.append(("tags", tag_id))
            
            # Fichier NFO optionnel — lire en bytes pour compatibilité AsyncClient
            if nfo_file_path:
                nfo_path = Path(nfo_file_path)
                if nfo_path.exists():
                    nfo_content = nfo_path.read_bytes()
                    files["nfoFile"] = (
                        nfo_path.name,
                        nfo_content,
                        "text/plain"
                    )
            
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    data=form_data,
                    files=files
                )
            
            if response.status_code != 200:
                self._handle_error_response(response, context="upload")
            
            result = response.json()
            logger.info("Upload réussi vers La Cale: %s (id: %s)", title, result.get("id"))
            return result
            
        except httpx.TimeoutException as e:
            logger.error("Timeout lors de l'upload vers La Cale: %s", e)
            raise LaCaleError(f"Timeout: l'upload a pris trop de temps ({e})") from e
        except (LaCaleError, FileNotFoundError):
            raise
        except Exception as e:
            logger.error("Erreur lors de l'upload vers La Cale: %s", e, exc_info=True)
            raise
