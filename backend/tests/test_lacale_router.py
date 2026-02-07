"""Tests unitaires pour le router La Cale (TDD - écrits avant l'implémentation)"""
import pytest
import sys
import os
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.lacale_service import LaCaleError


# ============================================================================
# ROUTER EXISTENCE
# ============================================================================

class TestLaCaleRouterExists:
    """Tests pour la structure du router La Cale"""
    
    def test_lacale_router_exists(self):
        """Vérifie que le router lacale existe et a le bon préfixe"""
        from app.routers.lacale import router
        assert router is not None
        assert router.prefix == "/lacale"
    
    def test_lacale_router_registered_in_app(self):
        """Vérifie que le router est enregistré dans l'application"""
        from app.main import app
        
        routes = [route.path for route in app.routes]
        # Au moins un endpoint /lacale/ doit être enregistré
        lacale_routes = [r for r in routes if "/lacale" in r]
        assert len(lacale_routes) > 0


# ============================================================================
# GET /lacale/meta
# ============================================================================

class TestLaCaleMetaEndpoint:
    """Tests pour l'endpoint GET /lacale/meta"""
    
    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)
    
    def test_meta_success(self, client):
        """Vérifie que GET /lacale/meta retourne les métadonnées"""
        mock_meta = {
            "categories": [
                {
                    "id": "cat_video", "name": "Vidéo", "slug": "video",
                    "children": [
                        {"id": "cat_films", "name": "Films", "slug": "films"},
                        {"id": "cat_series", "name": "Séries TV", "slug": "series"}
                    ]
                }
            ],
            "tagGroups": [
                {
                    "id": "tg_quality", "name": "Qualité", "slug": "quality",
                    "order": 1,
                    "tags": [{"id": "tag_1080p", "name": "1080p", "slug": "1080p"}]
                }
            ],
            "ungroupedTags": []
        }
        
        with patch('app.routers.lacale.LaCaleService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.fetch_meta = AsyncMock(return_value=mock_meta)
            MockService.return_value = mock_instance
            
            response = client.get("/lacale/meta")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "tagGroups" in data
    
    def test_meta_no_api_key(self, client):
        """Vérifie l'erreur quand l'API key n'est pas configurée"""
        with patch('app.routers.lacale.LaCaleService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.fetch_meta = AsyncMock(
                side_effect=Exception("401: API key manquante")
            )
            MockService.return_value = mock_instance
            
            response = client.get("/lacale/meta")
        
        # Doit retourner une erreur (pas 200)
        assert response.status_code != 200 or (
            response.status_code == 200 and "error" in response.json()
        )
    
    def test_meta_invalid_api_key(self, client):
        """Vérifie l'erreur quand l'API key est invalide (403)"""
        with patch('app.routers.lacale.LaCaleService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.fetch_meta = AsyncMock(
                side_effect=Exception("403: API key invalide ou révoquée")
            )
            MockService.return_value = mock_instance
            
            response = client.get("/lacale/meta")
        
        assert response.status_code != 200 or (
            response.status_code == 200 and "error" in response.json()
        )


# ============================================================================
# POST /lacale/upload
# ============================================================================

class TestLaCaleUploadEndpoint:
    """Tests pour l'endpoint POST /lacale/upload"""
    
    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)
    
    def test_upload_success(self, client):
        """Vérifie un upload réussi via l'endpoint"""
        mock_result = {
            "success": True,
            "id": "ckx9f3p5x0000abcd1234",
            "slug": "ma-cargaison",
            "link": "https://la-cale.space/torrents/ma-cargaison"
        }
        
        with patch('app.routers.lacale.LaCaleService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.upload = AsyncMock(return_value=mock_result)
            MockService.return_value = mock_instance
            
            response = client.post("/lacale/upload", json={
                "title": "Mon.Film.2024.MULTi.1080p.BluRay.x264-TEAM",
                "category_id": "cat_films",
                "torrent_file_path": "/app/output/test.torrent",
                "tag_ids": ["tag_1080p"],
                "description": "Test description",
                "tmdb_id": "12345",
                "tmdb_type": "MOVIE"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["link"] == "https://la-cale.space/torrents/ma-cargaison"
    
    def test_upload_missing_required_fields(self, client):
        """Vérifie la validation des champs requis"""
        response = client.post("/lacale/upload", json={})
        
        # FastAPI doit retourner 422 pour champs manquants
        assert response.status_code == 422
    
    def test_upload_duplicate_409(self, client):
        """Vérifie la gestion du torrent déjà existant via endpoint"""
        with patch('app.routers.lacale.LaCaleService') as MockService:
            mock_instance = AsyncMock()
            mock_instance.upload = AsyncMock(
                side_effect=LaCaleError("409 - Torrent déjà existant (même InfoHash)", status_code=409)
            )
            MockService.return_value = mock_instance
            
            response = client.post("/lacale/upload", json={
                "title": "Test",
                "category_id": "cat_films",
                "torrent_file_path": "/app/output/test.torrent"
            })
        
        # Le router doit propager l'erreur 409
        assert response.status_code == 409 or (
            response.status_code == 200 and "error" in response.json()
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
