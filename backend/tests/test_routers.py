"""Tests unitaires pour les routers FastAPI"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFilesRouter:
    """Tests pour le router files"""
    
    def test_files_router_exists(self):
        """Test que le router files existe"""
        from app.routers.files import router
        assert router is not None
        assert router.prefix == "/files"


class TestTorrentRouter:
    """Tests pour le router torrent"""
    
    def test_torrent_router_exists(self):
        """Test que le router torrent existe"""
        from app.routers.torrent import router
        assert router is not None
        assert router.prefix == "/torrent"
    
    def test_connection_test_model(self):
        """Test le modèle ConnectionTest"""
        from app.routers.torrent import ConnectionTest
        
        data = ConnectionTest(
            host="http://localhost",
            port=8080,
            username="admin",
            password="password"
        )
        
        assert data.host == "http://localhost"
        assert data.port == 8080


class TestMediainfoRouter:
    """Tests pour le router mediainfo"""
    
    def test_mediainfo_router_exists(self):
        """Test que le router mediainfo existe"""
        from app.routers.mediainfo import router
        assert router is not None
        assert router.prefix == "/mediainfo"


class TestPresentationRouter:
    """Tests pour le router presentation"""
    
    def test_presentation_router_exists(self):
        """Test que le router presentation existe"""
        from app.routers.presentation import router
        assert router is not None
        assert router.prefix == "/presentation"


class TestSettingsRouter:
    """Tests pour le router settings"""
    
    def test_settings_router_exists(self):
        """Test que le router settings existe"""
        from app.routers.settings import router
        assert router is not None
        assert router.prefix == "/settings"


class TestTmdbRouter:
    """Tests pour le router tmdb"""
    
    def test_tmdb_router_exists(self):
        """Test que le router tmdb existe"""
        from app.routers.tmdb import router
        assert router is not None
        assert router.prefix == "/tmdb"


class TestMainApp:
    """Tests pour l'application principale"""
    
    def test_app_creation(self):
        """Test que l'application FastAPI se crée correctement"""
        from app.main import app
        assert app is not None
        assert app.title == "La Cale Upload Preparation Tool"
    
    def test_cors_middleware(self):
        """Test que le middleware CORS est configuré"""
        from app.main import app
        
        # Vérifier que les middlewares sont présents
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
