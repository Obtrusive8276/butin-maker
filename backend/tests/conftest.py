"""Configuration pytest pour les tests backend"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Mock des settings pour les tests
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock les settings pour éviter les dépendances externes"""
    mock_settings = MagicMock()
    mock_settings.media_root = Path("/data")
    mock_settings.output_path = Path("/tmp/test_output")
    mock_settings.base_path = Path("/app")
    mock_settings.tmdb_api_key = None
    
    with patch('app.config.settings', mock_settings):
        yield mock_settings


@pytest.fixture
def sample_media_info():
    """Fixture avec des données MediaInfo exemple"""
    return {
        "file_path": "/data/test.mkv",
        "file_name": "test.mkv",
        "file_size": 4500000000,
        "container": "Matroska",
        "duration": 7200,
        "video_tracks": [{
            "codec": "HEVC",
            "width": 1920,
            "height": 1080,
            "bitrate": 8000000,
            "framerate": 23.976
        }],
        "audio_tracks": [{
            "codec": "DTS-HD MA",
            "channels": 6,
            "language": "French"
        }],
        "subtitle_tracks": [{
            "codec": "SRT",
            "language": "French"
        }]
    }


@pytest.fixture
def sample_tmdb_movie():
    """Fixture avec des données TMDB film exemple"""
    return {
        "id": 12345,
        "title": "Film Test",
        "original_title": "Test Movie",
        "year": "2024",
        "poster_path": "https://image.tmdb.org/t/p/w500/poster.jpg",
        "overview": "Un film de test.",
        "vote_average": 7.5,
        "genres": "Action, Aventure",
        "type": "movie"
    }


@pytest.fixture
def sample_tmdb_tv():
    """Fixture avec des données TMDB série exemple"""
    return {
        "id": 67890,
        "title": "Série Test",
        "original_title": "Test Series",
        "year": "2024",
        "poster_path": "https://image.tmdb.org/t/p/w500/poster.jpg",
        "overview": "Une série de test.",
        "vote_average": 8.0,
        "genres": "Drame",
        "number_of_seasons": 3,
        "type": "tv"
    }
