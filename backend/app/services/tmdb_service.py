import httpx
from typing import Optional, List, Dict, Any
from app.config import settings, user_settings


class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Réutilise un client HTTP unique avec timeout"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))
        return self._client
    
    def _get_user_tmdb_key(self) -> Optional[str]:
        data = user_settings.get()
        tmdb_data = data.get("tmdb", {})
        api_key = tmdb_data.get("api_key")
        return api_key or None

    def _get_api_key(self) -> Optional[str]:
        user_key = self._get_user_tmdb_key()
        return user_key or settings.tmdb_api_key
    
    def has_api_key(self) -> bool:
        """Vérifie si une clé API TMDB est configurée."""
        return bool(self._get_api_key())
    
    def _is_v3_key(self) -> bool:
        api_key = self._get_api_key()
        return bool(api_key) and len(api_key) == 32 and api_key.isalnum()
    
    def _get_headers(self) -> dict:
        api_key = self._get_api_key()
        if api_key and not self._is_v3_key():
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        return {"Content-Type": "application/json"}
    
    def _build_params(self, **kwargs) -> dict:
        """Construit les paramètres de requête avec la clé API si nécessaire"""
        params = {"language": "fr-FR", **kwargs}
        if self._is_v3_key():
            params["api_key"] = self._get_api_key()
        return params
    
    async def _make_request(self, endpoint: str, params: dict = None) -> Optional[Dict]:
        """Effectue une requête GET vers l'API TMDB
        
        Args:
            endpoint: Endpoint API (ex: "/search/movie")
            params: Paramètres de requête
            
        Returns:
            Données JSON ou None en cas d'erreur
        """
        api_key = self._get_api_key()
        if not api_key:
            return None
        
        client = self._get_client()
        response = await client.get(
            f"{self.BASE_URL}{endpoint}",
            params=self._build_params(**(params or {})),
            headers=self._get_headers()
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
    
    def _format_movie_result(self, item: dict) -> dict:
        """Formate un résultat de film"""
        return {
            "id": item.get("id"),
            "title": item.get("title"),
            "original_title": item.get("original_title"),
            "year": item.get("release_date", "")[:4] if item.get("release_date") else None,
            "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
            "overview": item.get("overview"),
            "vote_average": item.get("vote_average"),
            "type": "movie"
        }
    
    def _format_tv_result(self, item: dict) -> dict:
        """Formate un résultat de série TV"""
        return {
            "id": item.get("id"),
            "title": item.get("name"),
            "original_title": item.get("original_name"),
            "year": item.get("first_air_date", "")[:4] if item.get("first_air_date") else None,
            "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
            "overview": item.get("overview"),
            "vote_average": item.get("vote_average"),
            "type": "tv"
        }
    
    async def search_movie(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for movies on TMDB"""
        params = {"query": query, "include_adult": False}
        if year:
            params["year"] = year
        
        data = await self._make_request("/search/movie", params)
        if not data:
            return []
        
        return [self._format_movie_result(item) for item in data.get("results", [])[:10]]
    
    async def search_tv(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for TV shows on TMDB"""
        params = {"query": query, "include_adult": False}
        if year:
            params["first_air_date_year"] = year
        
        data = await self._make_request("/search/tv", params)
        if not data:
            return []
        
        return [self._format_tv_result(item) for item in data.get("results", [])[:10]]
    
    async def search_multi(self, query: str) -> List[Dict[str, Any]]:
        """Search for movies and TV shows"""
        data = await self._make_request(
            "/search/multi", 
            {"query": query, "include_adult": False}
        )
        if not data:
            return []
        
        results = []
        for item in data.get("results", [])[:15]:
            media_type = item.get("media_type")
            if media_type == "movie":
                results.append(self._format_movie_result(item))
            elif media_type == "tv":
                results.append(self._format_tv_result(item))
        
        return results
    
    async def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information"""
        item = await self._make_request(f"/movie/{movie_id}")
        if not item:
            return None
        
        genres = [g.get("name") for g in item.get("genres", [])]
        
        return {
            **self._format_movie_result(item),
            "release_date": item.get("release_date"),
            "backdrop_path": f"{self.IMAGE_BASE_URL}/original{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
            "vote_average": round(item.get("vote_average", 0), 1),
            "genres": ", ".join(genres),
            "runtime": item.get("runtime"),
            "tagline": item.get("tagline"),
            "imdb_id": item.get("imdb_id"),
        }
    
    async def get_tv_details(self, tv_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed TV show information"""
        item = await self._make_request(f"/tv/{tv_id}")
        if not item:
            return None
        
        genres = [g.get("name") for g in item.get("genres", [])]
        
        return {
            **self._format_tv_result(item),
            "release_date": item.get("first_air_date"),
            "backdrop_path": f"{self.IMAGE_BASE_URL}/original{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
            "vote_average": round(item.get("vote_average", 0), 1),
            "genres": ", ".join(genres),
            "number_of_seasons": item.get("number_of_seasons"),
            "number_of_episodes": item.get("number_of_episodes"),
            "status": item.get("status"),
        }


tmdb_service = TMDBService()
