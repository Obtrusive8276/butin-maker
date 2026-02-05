import httpx
from typing import Optional, List, Dict, Any
from app.config import settings, user_settings


class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def _get_user_tmdb_key(self) -> Optional[str]:
        data = user_settings.get()
        tmdb_data = data.get("tmdb", {})
        api_key = tmdb_data.get("api_key")
        return api_key or None

    def _get_api_key(self) -> Optional[str]:
        # La clé des paramètres utilisateur prévaut sur la variable d'environnement
        user_key = self._get_user_tmdb_key()
        return user_key or settings.tmdb_api_key
    
    def has_api_key(self) -> bool:
        """Vérifie si une clé API TMDB est configurée."""
        return bool(self._get_api_key())
    
    def _get_headers(self) -> dict:
        api_key = self._get_api_key()
        if api_key and not self._is_v3_key():
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        return {"Content-Type": "application/json"}

    def _is_v3_key(self) -> bool:
        api_key = self._get_api_key()
        return bool(api_key) and len(api_key) == 32 and api_key.isalnum()
    
    async def search_movie(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for movies on TMDB"""
        api_key = self._get_api_key()
        if not api_key:
            return []
        
        params = {
            "query": query,
            "language": "fr-FR",
            "include_adult": False
        }
        if self._is_v3_key():
            params["api_key"] = api_key
        if year:
            params["year"] = year
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/movie",
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("results", [])[:10]:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "original_title": item.get("original_title"),
                    "year": item.get("release_date", "")[:4] if item.get("release_date") else None,
                    "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                    "overview": item.get("overview"),
                    "vote_average": item.get("vote_average"),
                    "type": "movie"
                })
            
            return results
    
    async def search_tv(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for TV shows on TMDB"""
        api_key = self._get_api_key()
        if not api_key:
            return []
        
        params = {
            "query": query,
            "language": "fr-FR",
            "include_adult": False
        }
        if self._is_v3_key():
            params["api_key"] = api_key
        if year:
            params["first_air_date_year"] = year
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/tv",
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("results", [])[:10]:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("name"),
                    "original_title": item.get("original_name"),
                    "year": item.get("first_air_date", "")[:4] if item.get("first_air_date") else None,
                    "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                    "overview": item.get("overview"),
                    "vote_average": item.get("vote_average"),
                    "type": "tv"
                })
            
            return results
    
    async def search_multi(self, query: str) -> List[Dict[str, Any]]:
        """Search for movies and TV shows"""
        api_key = self._get_api_key()
        if not api_key:
            return []
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/search/multi",
                params={
                    "query": query,
                    "language": "fr-FR",
                    "include_adult": False,
                    **({"api_key": api_key} if self._is_v3_key() else {})
                },
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("results", [])[:15]:
                media_type = item.get("media_type")
                if media_type not in ["movie", "tv"]:
                    continue
                
                if media_type == "movie":
                    results.append({
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "original_title": item.get("original_title"),
                        "year": item.get("release_date", "")[:4] if item.get("release_date") else None,
                        "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                        "overview": item.get("overview"),
                        "vote_average": item.get("vote_average"),
                        "type": "movie"
                    })
                else:
                    results.append({
                        "id": item.get("id"),
                        "title": item.get("name"),
                        "original_title": item.get("original_name"),
                        "year": item.get("first_air_date", "")[:4] if item.get("first_air_date") else None,
                        "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                        "overview": item.get("overview"),
                        "vote_average": item.get("vote_average"),
                        "type": "tv"
                    })
            
            return results
    
    async def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information"""
        api_key = self._get_api_key()
        if not api_key:
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/movie/{movie_id}",
                params={
                    "language": "fr-FR",
                    **({"api_key": api_key} if self._is_v3_key() else {})
                },
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                return None
            
            item = response.json()
            
            genres = [g.get("name") for g in item.get("genres", [])]
            
            return {
                "id": item.get("id"),
                "title": item.get("title"),
                "original_title": item.get("original_title"),
                "year": item.get("release_date", "")[:4] if item.get("release_date") else None,
                "release_date": item.get("release_date"),
                "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                "backdrop_path": f"{self.IMAGE_BASE_URL}/original{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
                "overview": item.get("overview"),
                "vote_average": round(item.get("vote_average", 0), 1),
                "genres": ", ".join(genres),
                "runtime": item.get("runtime"),
                "tagline": item.get("tagline"),
                "imdb_id": item.get("imdb_id"),
                "type": "movie"
            }
    
    async def get_tv_details(self, tv_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed TV show information"""
        api_key = self._get_api_key()
        if not api_key:
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/tv/{tv_id}",
                params={
                    "language": "fr-FR",
                    **({"api_key": api_key} if self._is_v3_key() else {})
                },
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                return None
            
            item = response.json()
            
            genres = [g.get("name") for g in item.get("genres", [])]
            
            return {
                "id": item.get("id"),
                "title": item.get("name"),
                "original_title": item.get("original_name"),
                "year": item.get("first_air_date", "")[:4] if item.get("first_air_date") else None,
                "release_date": item.get("first_air_date"),
                "poster_path": f"{self.IMAGE_BASE_URL}/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                "backdrop_path": f"{self.IMAGE_BASE_URL}/original{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
                "overview": item.get("overview"),
                "vote_average": round(item.get("vote_average", 0), 1),
                "genres": ", ".join(genres),
                "number_of_seasons": item.get("number_of_seasons"),
                "number_of_episodes": item.get("number_of_episodes"),
                "status": item.get("status"),
                "type": "tv"
            }


tmdb_service = TMDBService()
