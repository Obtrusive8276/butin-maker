"""Tests unitaires pour le service La Cale (TDD - écrits avant l'implémentation)"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.lacale_service import LaCaleService


# ============================================================================
# INITIALISATION
# ============================================================================

class TestLaCaleServiceInit:
    """Tests pour l'initialisation du service La Cale"""
    
    def test_init_with_api_key(self):
        """Vérifie que le service s'initialise avec une API key"""
        service = LaCaleService(api_key="test_key_123")
        assert service.api_key == "test_key_123"
    
    def test_init_without_api_key(self):
        """Vérifie que le service s'initialise avec api_key vide"""
        service = LaCaleService(api_key="")
        assert service.api_key == ""
    
    def test_init_default_base_url(self):
        """Vérifie que la base URL par défaut est correcte"""
        service = LaCaleService(api_key="test")
        assert service.base_url == "https://la-cale.space"
    
    def test_init_custom_base_url(self):
        """Vérifie qu'on peut personnaliser la base URL"""
        service = LaCaleService(api_key="test", base_url="https://custom.example.com")
        assert service.base_url == "https://custom.example.com"
    
    def test_init_base_url_strips_trailing_slash(self):
        """Vérifie que le trailing slash est supprimé de la base URL"""
        service = LaCaleService(api_key="test", base_url="https://la-cale.space/")
        assert service.base_url == "https://la-cale.space"


# ============================================================================
# HEADERS
# ============================================================================

class TestLaCaleServiceHeaders:
    """Tests pour la construction des headers HTTP"""
    
    def test_headers_include_api_key(self):
        """Vérifie que le header X-Api-Key est présent"""
        service = LaCaleService(api_key="my_secret_key")
        headers = service._get_headers()
        assert "X-Api-Key" in headers
        assert headers["X-Api-Key"] == "my_secret_key"
    
    def test_headers_without_api_key(self):
        """Vérifie les headers sans API key (clé vide)"""
        service = LaCaleService(api_key="")
        headers = service._get_headers()
        # Le header doit quand même être présent (le serveur renverra 401)
        assert "X-Api-Key" in headers
        assert headers["X-Api-Key"] == ""


# ============================================================================
# FETCH META
# ============================================================================

class TestLaCaleServiceFetchMeta:
    """Tests pour la récupération des métadonnées (catégories, tags)"""
    
    @pytest.mark.asyncio
    async def test_fetch_meta_success(self):
        """Vérifie la récupération réussie des métadonnées"""
        service = LaCaleService(api_key="valid_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "categories": [
                {
                    "id": "cat_video",
                    "name": "Vidéo",
                    "slug": "video",
                    "children": [
                        {"id": "cat_films", "name": "Films", "slug": "films"},
                        {"id": "cat_series", "name": "Séries TV", "slug": "series"}
                    ]
                }
            ],
            "tagGroups": [
                {
                    "id": "tg_video_quality",
                    "name": "Qualité vidéo",
                    "slug": "video-quality",
                    "order": 1,
                    "tags": [
                        {"id": "tag_1080p", "name": "1080p", "slug": "1080p"},
                        {"id": "tag_4k", "name": "4K", "slug": "4k"}
                    ]
                }
            ],
            "ungroupedTags": []
        }
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            result = await service.fetch_meta()
        
        assert result is not None
        assert "categories" in result
        assert "tagGroups" in result
        assert "ungroupedTags" in result
        assert len(result["categories"]) == 1
        assert result["categories"][0]["id"] == "cat_video"
    
    @pytest.mark.asyncio
    async def test_fetch_meta_401_unauthorized(self):
        """Vérifie la gestion d'une API key manquante (401)"""
        service = LaCaleService(api_key="")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {"error": "API key manquante"}
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.fetch_meta()
            assert "401" in str(exc_info.value) or "unauthorized" in str(exc_info.value).lower() or "API key" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_fetch_meta_403_forbidden(self):
        """Vérifie la gestion d'une API key révoquée (403)"""
        service = LaCaleService(api_key="revoked_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.json.return_value = {"error": "API key révoquée"}
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.fetch_meta()
            assert "403" in str(exc_info.value) or "forbidden" in str(exc_info.value).lower() or "révoquée" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_fetch_meta_500_server_error(self):
        """Vérifie la gestion d'une erreur serveur (500)"""
        service = LaCaleService(api_key="valid_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.fetch_meta()
            assert "500" in str(exc_info.value) or "serveur" in str(exc_info.value).lower() or "server" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_fetch_meta_timeout(self):
        """Vérifie la gestion d'un timeout réseau"""
        import httpx
        service = LaCaleService(api_key="valid_key")
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Connection timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.fetch_meta()
            assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_fetch_meta_sends_correct_url(self):
        """Vérifie que l'URL appelée est /api/external/meta"""
        service = LaCaleService(api_key="test_key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"categories": [], "tagGroups": [], "ungroupedTags": []}
        
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            await service.fetch_meta()
        
        # Vérifier que l'URL appelée est correcte
        call_args = mock_client.get.call_args
        called_url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        assert "/api/external/meta" in called_url


# ============================================================================
# FIND CATEGORY ID
# ============================================================================

class TestLaCaleServiceFindCategory:
    """Tests pour la détection automatique de catégorie (film/série)"""
    
    @pytest.mark.asyncio
    async def test_find_category_movie(self):
        """Vérifie que 'movie' retourne l'ID de la catégorie Films"""
        service = LaCaleService(api_key="test_key")
        
        meta_data = {
            "categories": [
                {
                    "id": "cat_video",
                    "name": "Vidéo",
                    "slug": "video",
                    "children": [
                        {"id": "cat_films", "name": "Films", "slug": "films"},
                        {"id": "cat_series", "name": "Séries TV", "slug": "series"}
                    ]
                }
            ],
            "tagGroups": [],
            "ungroupedTags": []
        }
        
        result = service.find_category_id(meta_data, "movie")
        assert result == "cat_films"
    
    @pytest.mark.asyncio
    async def test_find_category_tv(self):
        """Vérifie que 'tv' retourne l'ID de la catégorie Séries"""
        service = LaCaleService(api_key="test_key")
        
        meta_data = {
            "categories": [
                {
                    "id": "cat_video",
                    "name": "Vidéo",
                    "slug": "video",
                    "children": [
                        {"id": "cat_films", "name": "Films", "slug": "films"},
                        {"id": "cat_series", "name": "Séries TV", "slug": "series"}
                    ]
                }
            ],
            "tagGroups": [],
            "ungroupedTags": []
        }
        
        result = service.find_category_id(meta_data, "tv")
        assert result == "cat_series"
    
    def test_find_category_not_found(self):
        """Vérifie le comportement quand la catégorie n'est pas trouvée"""
        service = LaCaleService(api_key="test_key")
        
        meta_data = {
            "categories": [
                {
                    "id": "cat_audio",
                    "name": "Audio",
                    "slug": "audio",
                    "children": []
                }
            ],
            "tagGroups": [],
            "ungroupedTags": []
        }
        
        result = service.find_category_id(meta_data, "movie")
        assert result is None
    
    def test_find_category_empty_categories(self):
        """Vérifie le comportement avec une liste de catégories vide"""
        service = LaCaleService(api_key="test_key")
        
        meta_data = {
            "categories": [],
            "tagGroups": [],
            "ungroupedTags": []
        }
        
        result = service.find_category_id(meta_data, "movie")
        assert result is None


# ============================================================================
# UPLOAD
# ============================================================================

class TestLaCaleServiceUpload:
    """Tests pour l'upload de torrent vers La Cale"""
    
    @pytest.mark.asyncio
    async def test_upload_success(self, tmp_path):
        """Vérifie un upload réussi avec tous les champs"""
        service = LaCaleService(api_key="valid_key")
        
        # Créer un fichier .torrent factice
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "id": "ckx9f3p5x0000abcd1234",
            "slug": "ma-cargaison-abc123",
            "link": "https://la-cale.space/torrents/ma-cargaison-abc123"
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            result = await service.upload(
                title="Mon.Film.2024.MULTi.1080p.BluRay.x264-TEAM",
                category_id="cat_films",
                torrent_file_path=str(torrent_file),
                tag_ids=["tag_1080p", "tag_bluray"],
                description="Description du film",
                tmdb_id="12345",
                tmdb_type="MOVIE",
                cover_url="https://image.tmdb.org/t/p/w500/poster.jpg"
            )
        
        assert result is not None
        assert result["success"] is True
        assert result["id"] == "ckx9f3p5x0000abcd1234"
        assert result["slug"] == "ma-cargaison-abc123"
        assert "la-cale.space" in result["link"]
    
    @pytest.mark.asyncio
    async def test_upload_with_nfo_file(self, tmp_path):
        """Vérifie que le fichier NFO est inclus dans l'upload"""
        service = LaCaleService(api_key="valid_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        nfo_file = tmp_path / "test.nfo"
        nfo_file.write_text("NFO content here")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "id": "abc",
            "slug": "slug",
            "link": "https://la-cale.space/torrents/slug"
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            result = await service.upload(
                title="Test",
                category_id="cat_films",
                torrent_file_path=str(torrent_file),
                nfo_file_path=str(nfo_file)
            )
        
        assert result["success"] is True
        
        # Vérifier que le post a bien été appelé
        mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_409_duplicate(self, tmp_path):
        """Vérifie la gestion d'un torrent déjà existant (409)"""
        service = LaCaleService(api_key="valid_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_response.text = "Conflict"
        mock_response.json.return_value = {"error": "Torrent déjà existant"}
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.upload(
                    title="Test",
                    category_id="cat_films",
                    torrent_file_path=str(torrent_file)
                )
            assert "409" in str(exc_info.value) or "existant" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_upload_429_rate_limit(self, tmp_path):
        """Vérifie la gestion du rate limiting (429)"""
        service = LaCaleService(api_key="valid_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.upload(
                    title="Test",
                    category_id="cat_films",
                    torrent_file_path=str(torrent_file)
                )
            assert "429" in str(exc_info.value) or "rate" in str(exc_info.value).lower() or "limite" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_upload_401_unauthorized(self, tmp_path):
        """Vérifie la gestion d'une API key invalide lors de l'upload"""
        service = LaCaleService(api_key="invalid_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.upload(
                    title="Test",
                    category_id="cat_films",
                    torrent_file_path=str(torrent_file)
                )
            assert "401" in str(exc_info.value) or "unauthorized" in str(exc_info.value).lower() or "API key" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_missing_torrent_file(self, tmp_path):
        """Vérifie l'erreur quand le fichier .torrent n'existe pas"""
        service = LaCaleService(api_key="valid_key")
        
        fake_path = str(tmp_path / "nonexistent.torrent")
        
        with pytest.raises(Exception) as exc_info:
            await service.upload(
                title="Test",
                category_id="cat_films",
                torrent_file_path=fake_path
            )
        assert "existe pas" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower() or "introuvable" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_upload_sends_correct_url(self, tmp_path):
        """Vérifie que l'URL d'upload est /api/external/upload"""
        service = LaCaleService(api_key="test_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True, "id": "x", "slug": "x", "link": "https://la-cale.space/torrents/x"
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            await service.upload(
                title="Test",
                category_id="cat_films",
                torrent_file_path=str(torrent_file)
            )
        
        call_args = mock_client.post.call_args
        called_url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
        assert "/api/external/upload" in called_url
    
    @pytest.mark.asyncio
    async def test_upload_sends_headers_with_api_key(self, tmp_path):
        """Vérifie que le header X-Api-Key est envoyé lors de l'upload"""
        service = LaCaleService(api_key="my_api_key_456")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True, "id": "x", "slug": "x", "link": "https://la-cale.space/torrents/x"
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            await service.upload(
                title="Test",
                category_id="cat_films",
                torrent_file_path=str(torrent_file)
            )
        
        call_kwargs = mock_client.post.call_args
        # Vérifier que les headers contiennent la clé API
        headers = call_kwargs[1].get("headers", {}) if call_kwargs[1] else {}
        assert headers.get("X-Api-Key") == "my_api_key_456"
    
    @pytest.mark.asyncio
    async def test_upload_500_server_error(self, tmp_path):
        """Vérifie la gestion d'une erreur serveur lors de l'upload"""
        service = LaCaleService(api_key="valid_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.upload(
                    title="Test",
                    category_id="cat_films",
                    torrent_file_path=str(torrent_file)
                )
            assert "500" in str(exc_info.value) or "serveur" in str(exc_info.value).lower() or "server" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_upload_minimal_fields(self, tmp_path):
        """Vérifie un upload avec uniquement les champs requis (title, categoryId, file)"""
        service = LaCaleService(api_key="valid_key")
        
        torrent_file = tmp_path / "minimal.torrent"
        torrent_file.write_bytes(b"minimal torrent")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True, "id": "min_id", "slug": "min-slug",
            "link": "https://la-cale.space/torrents/min-slug"
        }
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            result = await service.upload(
                title="Minimal Upload",
                category_id="cat_films",
                torrent_file_path=str(torrent_file)
                # Pas de tags, description, tmdb_id, etc.
            )
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_upload_timeout(self, tmp_path):
        """Vérifie la gestion d'un timeout lors de l'upload"""
        import httpx
        service = LaCaleService(api_key="valid_key")
        
        torrent_file = tmp_path / "test.torrent"
        torrent_file.write_bytes(b"fake torrent data")
        
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Upload timed out"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        
        with patch('app.services.lacale_service.httpx.AsyncClient', return_value=mock_client):
            with pytest.raises(Exception) as exc_info:
                await service.upload(
                    title="Test",
                    category_id="cat_films",
                    torrent_file_path=str(torrent_file)
                )
            assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
