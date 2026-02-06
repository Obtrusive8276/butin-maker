"""Tests unitaires pour le service qBittorrent"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.qbittorrent_service import QBittorrentService


class TestQBittorrentServiceConnection:
    """Tests pour la connexion qBittorrent"""
    
    def setup_method(self):
        self.service = QBittorrentService()
    
    def test_initial_client_none(self):
        """Test que le client est None initialement"""
        assert self.service._client is None
    
    def test_get_settings_returns_dict(self):
        """Test que _get_settings retourne un dictionnaire"""
        with patch('app.services.qbittorrent_service.user_settings') as mock_settings:
            mock_settings.get.return_value = {"qbittorrent": {"host": "http://localhost"}}
            result = self.service._get_settings()
            assert isinstance(result, dict)
    
    def test_connect_failure_wrong_credentials(self):
        """Test échec de connexion avec mauvais identifiants"""
        import qbittorrentapi
        
        with patch('qbittorrentapi.Client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.auth_log_in.side_effect = qbittorrentapi.LoginFailed()
            mock_client.return_value = mock_instance
            
            success, message = self.service.connect(
                host="http://localhost",
                port=8080,
                username="wrong",
                password="wrong"
            )
            
            assert success == False
            assert "identifiants" in message.lower()
    
    def test_test_connection_success(self):
        """Test connexion réussie"""
        with patch('qbittorrentapi.Client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.app.version = "4.5.0"
            mock_client.return_value = mock_instance
            
            success, message = self.service.test_connection(
                host="http://localhost",
                port=8080,
                username="admin",
                password="admin"
            )
            
            assert success == True
            assert "4.5.0" in message


class TestQBittorrentServiceTorrent:
    """Tests pour la création de torrents"""
    
    def setup_method(self):
        self.service = QBittorrentService()
    
    @pytest.mark.asyncio
    async def test_create_torrent_path_not_exists(self):
        """Test création torrent avec chemin inexistant"""
        success, result = await self.service.create_torrent("/nonexistent/path")
        
        assert success == False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_create_torrent_returns_dict_on_failure(self):
        """Test que create_torrent retourne un dict avec error"""
        success, result = await self.service.create_torrent("/fake/path")
        
        assert isinstance(result, dict)
        if not success:
            assert "error" in result

    @pytest.mark.asyncio
    async def test_create_torrent_file_name_includes_extension(self, tmp_path):
        """Test que le contenu inclut l'extension mais pas le nom du torrent"""
        source_file = tmp_path / "The.Onion.Movie.2008.mkv"
        source_file.write_text("fake")

        class FakeTorrent:
            last_instance = None

            def __init__(self, path):
                self.path = path
                self.name = None
                self.private = None
                self.piece_size = None
                self.trackers = None
                self.infohash = "deadbeef"
                self.size = 123
                self.pieces = 4
                FakeTorrent.last_instance = self

            def generate(self):
                return None

            def write(self, output_file, overwrite=True):
                return None

        with patch('app.services.qbittorrent_service.torf.Torrent', new=FakeTorrent):
            with patch('app.services.qbittorrent_service.settings') as mock_settings:
                mock_settings.output_path = tmp_path

                success, result = await self.service.create_torrent(
                    source_path=str(source_file),
                    name="The.Onion.Movie.2008"
                )

                assert success is True
                assert result["torrent_name"] == "The.Onion.Movie.2008"
                assert FakeTorrent.last_instance is not None
                assert FakeTorrent.last_instance.name == "The.Onion.Movie.2008.mkv"

    @pytest.mark.asyncio
    async def test_create_torrent_strips_extension_from_name(self, tmp_path):
        """Test que le nom fourni avec extension est nettoye pour le torrent"""
        source_file = tmp_path / "The.Onion.Movie.2008.mkv"
        source_file.write_text("fake")

        class FakeTorrent:
            last_instance = None

            def __init__(self, path):
                self.path = path
                self.name = None
                self.private = None
                self.piece_size = None
                self.trackers = None
                self.infohash = "deadbeef"
                self.size = 123
                self.pieces = 4
                FakeTorrent.last_instance = self

            def generate(self):
                return None

            def write(self, output_file, overwrite=True):
                return None

        with patch('app.services.qbittorrent_service.torf.Torrent', new=FakeTorrent):
            with patch('app.services.qbittorrent_service.settings') as mock_settings:
                mock_settings.output_path = tmp_path

                success, result = await self.service.create_torrent(
                    source_path=str(source_file),
                    name="The.Onion.Movie.2008.mkv"
                )

                assert success is True
                assert result["torrent_name"] == "The.Onion.Movie.2008"
                assert FakeTorrent.last_instance is not None
                assert FakeTorrent.last_instance.name == "The.Onion.Movie.2008.mkv"

    @pytest.mark.asyncio
    async def test_create_torrent_strips_extension_for_directory_name(self, tmp_path):
        """Test que le nom de torrent est nettoye pour un dossier"""
        source_dir = tmp_path / "The.Onion.Movie.2008.mkv"
        source_dir.mkdir()

        class FakeTorrent:
            last_instance = None

            def __init__(self, path):
                self.path = path
                self.name = None
                self.private = None
                self.piece_size = None
                self.trackers = None
                self.infohash = "deadbeef"
                self.size = 123
                self.pieces = 4
                FakeTorrent.last_instance = self

            def generate(self):
                return None

            def write(self, output_file, overwrite=True):
                return None

        with patch('app.services.qbittorrent_service.torf.Torrent', new=FakeTorrent):
            with patch('app.services.qbittorrent_service.settings') as mock_settings:
                mock_settings.output_path = tmp_path

                success, result = await self.service.create_torrent(
                    source_path=str(source_dir),
                    name="The.Onion.Movie.2008.mkv"
                )

                assert success is True
                assert result["torrent_name"] == "The.Onion.Movie.2008"
                assert FakeTorrent.last_instance is not None
                assert FakeTorrent.last_instance.name == "The.Onion.Movie.2008.mkv"


class TestQBittorrentServiceSeeding:
    """Tests pour l'ajout de torrents pour seeding"""
    
    def setup_method(self):
        self.service = QBittorrentService()
    
    def test_add_torrent_for_seeding_no_client(self):
        """Test ajout torrent sans client connecté"""
        # Mock la connexion pour qu'elle échoue
        with patch.object(self.service, 'connect', return_value=(False, "Connection failed")):
            success, message = self.service.add_torrent_for_seeding(
                "/path/to/torrent.torrent",
                "/path/to/content"
            )
            
            assert success == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
