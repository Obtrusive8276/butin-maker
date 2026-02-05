"""Tests unitaires pour le service de fichiers"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFileServiceMediaExtensions:
    """Tests pour les extensions média"""
    
    def test_video_extensions(self):
        """Test que les extensions vidéo sont définies"""
        from app.services.file_service import FileService
        
        service = FileService()
        video_ext = service.MEDIA_EXTENSIONS['video']
        
        assert '.mkv' in video_ext
        assert '.mp4' in video_ext
        assert '.avi' in video_ext
        assert '.ts' in video_ext
    
    def test_audio_extensions(self):
        """Test que les extensions audio sont définies"""
        from app.services.file_service import FileService
        
        service = FileService()
        audio_ext = service.MEDIA_EXTENSIONS['audio']
        
        assert '.mp3' in audio_ext
        assert '.flac' in audio_ext
        assert '.aac' in audio_ext
    
    def test_ebook_extensions(self):
        """Test que les extensions ebook sont définies"""
        from app.services.file_service import FileService
        
        service = FileService()
        ebook_ext = service.MEDIA_EXTENSIONS['ebook']
        
        assert '.pdf' in ebook_ext
        assert '.epub' in ebook_ext


class TestFileServiceIsVideoFile:
    """Tests pour la détection de fichiers vidéo"""
    
    def test_is_video_file_mkv(self):
        """Test détection fichier MKV"""
        from app.services.file_service import FileService
        
        service = FileService()
        assert service.is_video_file("/path/to/file.mkv") == True
    
    def test_is_video_file_mp4(self):
        """Test détection fichier MP4"""
        from app.services.file_service import FileService
        
        service = FileService()
        assert service.is_video_file("/path/to/file.mp4") == True
    
    def test_is_video_file_txt(self):
        """Test non-détection fichier texte"""
        from app.services.file_service import FileService
        
        service = FileService()
        assert service.is_video_file("/path/to/file.txt") == False
    
    def test_is_video_file_case_insensitive(self):
        """Test détection insensible à la casse"""
        from app.services.file_service import FileService
        
        service = FileService()
        assert service.is_video_file("/path/to/file.MKV") == True
        assert service.is_video_file("/path/to/file.Mp4") == True


class TestFileServicePathSecurity:
    """Tests pour la sécurité des chemins"""
    
    def test_is_path_allowed_valid(self):
        """Test chemin valide dans media_root"""
        from app.services.file_service import FileService
        
        service = FileService()
        # Le chemin doit être dans media_root
        valid_path = service.media_root / "subdir"
        assert service._is_path_allowed(valid_path) == True
    
    def test_is_path_allowed_traversal(self):
        """Test protection contre directory traversal"""
        from app.services.file_service import FileService
        
        service = FileService()
        # Chemin qui tente de sortir de media_root
        invalid_path = Path("/etc/passwd")
        result = service._is_path_allowed(invalid_path)
        # Doit retourner False si le chemin est hors de media_root
        # (sauf si media_root est /)
        if str(service.media_root) != "/":
            assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
