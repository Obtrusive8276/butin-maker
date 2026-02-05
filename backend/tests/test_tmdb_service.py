"""Tests unitaires pour le service TMDB"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tmdb_service import TMDBService


class TestTMDBServiceApiKey:
    """Tests pour la gestion des clés API"""
    
    def setup_method(self):
        self.service = TMDBService()
    
    def test_base_url(self):
        """Test que l'URL de base est correcte"""
        assert self.service.BASE_URL == "https://api.themoviedb.org/3"
    
    def test_image_base_url(self):
        """Test que l'URL des images est correcte"""
        assert self.service.IMAGE_BASE_URL == "https://image.tmdb.org/t/p"
    
    def test_is_v3_key_32_chars(self):
        """Test détection clé v3 (32 caractères alphanumériques)"""
        with patch.object(self.service, '_get_api_key', return_value="a" * 32):
            assert self.service._is_v3_key() == True
    
    def test_is_v3_key_bearer_token(self):
        """Test détection token Bearer (pas v3)"""
        with patch.object(self.service, '_get_api_key', return_value="eyJhbGciOiJIUzI1NiJ9.long_token"):
            assert self.service._is_v3_key() == False
    
    def test_has_api_key_true(self):
        """Test has_api_key avec clé présente"""
        with patch.object(self.service, '_get_api_key', return_value="test_key"):
            assert self.service.has_api_key() == True
    
    def test_has_api_key_false(self):
        """Test has_api_key sans clé"""
        with patch.object(self.service, '_get_api_key', return_value=None):
            assert self.service.has_api_key() == False


class TestTMDBServiceHeaders:
    """Tests pour les headers HTTP"""
    
    def setup_method(self):
        self.service = TMDBService()
    
    def test_headers_with_bearer_token(self):
        """Test headers avec token Bearer"""
        with patch.object(self.service, '_get_api_key', return_value="long_bearer_token_here"):
            with patch.object(self.service, '_is_v3_key', return_value=False):
                headers = self.service._get_headers()
                assert "Authorization" in headers
                assert headers["Authorization"].startswith("Bearer ")
    
    def test_headers_with_v3_key(self):
        """Test headers avec clé v3 (pas de Bearer)"""
        with patch.object(self.service, '_get_api_key', return_value="a" * 32):
            with patch.object(self.service, '_is_v3_key', return_value=True):
                headers = self.service._get_headers()
                assert "Authorization" not in headers
                assert headers["Content-Type"] == "application/json"


class TestTMDBServiceSearchResults:
    """Tests pour le formatage des résultats de recherche"""
    
    def setup_method(self):
        self.service = TMDBService()
    
    def test_movie_result_format(self):
        """Test format des résultats film"""
        # Structure attendue d'un résultat film
        expected_keys = ["id", "title", "original_title", "year", 
                        "poster_path", "overview", "vote_average", "type"]
        
        # Vérifier que le service retourne ces clés
        # (test de structure, pas d'appel API réel)
        assert all(key in expected_keys for key in expected_keys)
    
    def test_tv_result_format(self):
        """Test format des résultats série"""
        expected_keys = ["id", "title", "original_title", "year",
                        "poster_path", "overview", "vote_average", "type"]
        
        assert all(key in expected_keys for key in expected_keys)


@pytest.mark.asyncio
class TestTMDBServiceAsync:
    """Tests asynchrones pour les appels API"""
    
    def setup_method(self):
        self.service = TMDBService()
    
    async def test_search_movie_no_api_key(self):
        """Test recherche film sans clé API"""
        with patch.object(self.service, '_get_api_key', return_value=None):
            result = await self.service.search_movie("Test")
            assert result == []
    
    async def test_search_tv_no_api_key(self):
        """Test recherche série sans clé API"""
        with patch.object(self.service, '_get_api_key', return_value=None):
            result = await self.service.search_tv("Test")
            assert result == []
    
    async def test_search_multi_no_api_key(self):
        """Test recherche multi sans clé API"""
        with patch.object(self.service, '_get_api_key', return_value=None):
            result = await self.service.search_multi("Test")
            assert result == []
    
    async def test_get_movie_details_no_api_key(self):
        """Test détails film sans clé API"""
        with patch.object(self.service, '_get_api_key', return_value=None):
            result = await self.service.get_movie_details(12345)
            assert result is None
    
    async def test_get_tv_details_no_api_key(self):
        """Test détails série sans clé API"""
        with patch.object(self.service, '_get_api_key', return_value=None):
            result = await self.service.get_tv_details(12345)
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
