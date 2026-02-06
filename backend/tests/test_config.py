"""Tests pour config.py - UserSettings et Settings"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from app.config import UserSettings, Settings, settings


class TestUserSettingsDefaults:
    """Tests des valeurs par défaut de UserSettings"""
    
    def test_defaults_has_qbittorrent(self):
        """Vérifie que DEFAULTS contient qbittorrent"""
        assert "qbittorrent" in UserSettings.DEFAULTS
        assert "host" in UserSettings.DEFAULTS["qbittorrent"]
        assert "port" in UserSettings.DEFAULTS["qbittorrent"]
        assert "username" in UserSettings.DEFAULTS["qbittorrent"]
        assert "password" in UserSettings.DEFAULTS["qbittorrent"]
    
    def test_defaults_has_tracker(self):
        """Vérifie que DEFAULTS contient tracker"""
        assert "tracker" in UserSettings.DEFAULTS
        assert "announce_url" in UserSettings.DEFAULTS["tracker"]
        assert "upload_url" in UserSettings.DEFAULTS["tracker"]
    
    def test_defaults_has_paths(self):
        """Vérifie que DEFAULTS contient paths"""
        assert "paths" in UserSettings.DEFAULTS
        assert "default_browse_path" in UserSettings.DEFAULTS["paths"]
        assert "hardlink_path" in UserSettings.DEFAULTS["paths"]
        assert "qbittorrent_download_path" in UserSettings.DEFAULTS["paths"]
        assert "output_path" in UserSettings.DEFAULTS["paths"]
    
    def test_defaults_has_tmdb(self):
        """Vérifie que DEFAULTS contient tmdb"""
        assert "tmdb" in UserSettings.DEFAULTS
        assert "api_key" in UserSettings.DEFAULTS["tmdb"]
    
    def test_defaults_upload_url_value(self):
        """Vérifie la valeur par défaut de upload_url"""
        assert UserSettings.DEFAULTS["tracker"]["upload_url"] == "https://la-cale.space/upload"
    
    def test_defaults_qbittorrent_port(self):
        """Vérifie le port par défaut de qBittorrent"""
        assert UserSettings.DEFAULTS["qbittorrent"]["port"] == 8080


class TestUserSettingsLoad:
    """Tests de la méthode _load"""
    
    def test_load_returns_defaults_when_no_file(self):
        """Retourne les defaults si le fichier n'existe pas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = Path(tmpdir) / "settings.json"
            test_settings._data = test_settings._load()
            assert test_settings._data == UserSettings.DEFAULTS
    
    def test_load_reads_existing_file(self):
        """Charge les données depuis un fichier existant"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            custom_data = {
                "qbittorrent": {
                    "host": "http://custom-host",
                    "port": 9090,
                    "username": "custom_user",
                    "password": "custom_pass"
                }
            }
            with open(settings_file, "w") as f:
                json.dump(custom_data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = test_settings._load()
            assert test_settings._data["qbittorrent"]["host"] == "http://custom-host"
            assert test_settings._data["qbittorrent"]["port"] == 9090


class TestUserSettingsGet:
    """Tests de la méthode get() - fusion avec defaults"""
    
    def test_get_merges_with_defaults(self):
        """Vérifie que get() fusionne les données avec les defaults"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            # Fichier partiel - seulement qbittorrent
            partial_data = {
                "qbittorrent": {
                    "host": "http://my-server",
                    "port": 8080,
                    "username": "admin",
                    "password": "secret"
                }
            }
            with open(settings_file, "w") as f:
                json.dump(partial_data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = test_settings._load()
            result = test_settings.get()
            
            # Les données custom sont présentes
            assert result["qbittorrent"]["host"] == "http://my-server"
            assert result["qbittorrent"]["password"] == "secret"
            
            # Les sections manquantes sont ajoutées depuis defaults
            assert "tracker" in result
            assert "paths" in result
            assert "tmdb" in result
            assert result["tracker"]["upload_url"] == "https://la-cale.space/upload"
    
    def test_get_merges_nested_dicts(self):
        """Vérifie la fusion des sous-dictionnaires"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            # Fichier avec paths partiel
            partial_data = {
                "paths": {
                    "default_browse_path": "/custom/path"
                    # hardlink_path et autres manquants
                }
            }
            with open(settings_file, "w") as f:
                json.dump(partial_data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = test_settings._load()
            result = test_settings.get()
            
            # La valeur custom est présente
            assert result["paths"]["default_browse_path"] == "/custom/path"
            
            # Les clés manquantes sont ajoutées depuis defaults
            assert "hardlink_path" in result["paths"]
            assert "qbittorrent_download_path" in result["paths"]
            assert "output_path" in result["paths"]
    
    def test_get_all_keys_present(self):
        """Vérifie que toutes les clés sont présentes après get()"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = Path(tmpdir) / "settings.json"
            test_settings._data = test_settings._load()
            result = test_settings.get()
            
            # Toutes les sections principales
            assert "qbittorrent" in result
            assert "tracker" in result
            assert "paths" in result
            assert "tmdb" in result
            
            # Toutes les clés de paths
            assert "default_browse_path" in result["paths"]
            assert "hardlink_path" in result["paths"]
            assert "qbittorrent_download_path" in result["paths"]
            assert "output_path" in result["paths"]


class TestUserSettingsSave:
    """Tests de la méthode save()"""
    
    def test_save_writes_to_file(self):
        """Vérifie que save() écrit dans le fichier"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = {}
            
            new_data = {
                "qbittorrent": {"host": "http://new-host", "port": 1234, "username": "u", "password": "p"},
                "tracker": {"announce_url": "http://tracker", "upload_url": "http://upload"},
                "paths": {"default_browse_path": "/new/path", "hardlink_path": "", "qbittorrent_download_path": "", "output_path": ""},
                "tmdb": {"api_key": "new-key"}
            }
            test_settings.save(new_data)
            
            # Vérifier que le fichier a été créé
            assert settings_file.exists()
            
            # Vérifier le contenu
            with open(settings_file) as f:
                saved_data = json.load(f)
            assert saved_data["qbittorrent"]["host"] == "http://new-host"
            assert saved_data["tmdb"]["api_key"] == "new-key"
    
    def test_save_updates_internal_data(self):
        """Vérifie que save() met à jour _data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = {}
            
            new_data = {"test": "value"}
            test_settings.save(new_data)
            
            assert test_settings._data == new_data


class TestUserSettingsUpdate:
    """Tests de la méthode update()"""
    
    def test_update_modifies_specific_key(self):
        """Vérifie que update() modifie une clé spécifique"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = UserSettings.DEFAULTS.copy()
            
            test_settings.update("qbittorrent", {"host": "http://updated", "port": 9999, "username": "u", "password": "p"})
            
            assert test_settings._data["qbittorrent"]["host"] == "http://updated"
            assert test_settings._data["qbittorrent"]["port"] == 9999


class TestUserSettingsLaCaleApiKey:
    """Tests pour le champ lacale_api_key dans les settings"""
    
    def test_defaults_include_lacale_api_key(self):
        """Vérifie que DEFAULTS contient tracker.lacale_api_key"""
        assert "tracker" in UserSettings.DEFAULTS
        assert "lacale_api_key" in UserSettings.DEFAULTS["tracker"]
        assert UserSettings.DEFAULTS["tracker"]["lacale_api_key"] == ""
    
    def test_get_returns_lacale_api_key_when_absent(self):
        """Vérifie que get() retourne lacale_api_key même si absent du JSON sauvegardé"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            # Fichier sans lacale_api_key
            partial_data = {
                "tracker": {
                    "announce_url": "http://test",
                    "upload_url": "https://la-cale.space/upload"
                }
            }
            with open(settings_file, "w") as f:
                json.dump(partial_data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = test_settings._load()
            result = test_settings.get()
            
            # lacale_api_key doit être présent avec la valeur par défaut
            assert "lacale_api_key" in result["tracker"]
            assert result["tracker"]["lacale_api_key"] == ""
    
    def test_save_and_reload_lacale_api_key(self):
        """Vérifie que l'API key La Cale est correctement sauvegardée et rechargée"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            # Créer settings, sauvegarder avec API key
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._data = test_settings._load()
            
            data = test_settings.get()
            data["tracker"]["lacale_api_key"] = "test_api_key_123"
            test_settings.save(data)
            
            # Recharger depuis le fichier
            test_settings2 = UserSettings.__new__(UserSettings)
            test_settings2.settings_file = settings_file
            test_settings2._data = test_settings2._load()
            result = test_settings2.get()
            
            assert result["tracker"]["lacale_api_key"] == "test_api_key_123"


class TestSettingsClass:
    """Tests de la classe Settings (Pydantic)"""
    
    def test_settings_default_values(self):
        """Vérifie les valeurs par défaut de Settings"""
        s = Settings()
        assert s.backend_host == "127.0.0.1"
        assert s.backend_port == 8000
        assert s.qbittorrent_port == 8080
        assert s.lacale_upload_url == "https://la-cale.space/upload"
    
    def test_settings_media_root_default(self):
        """Vérifie le chemin media_root par défaut"""
        s = Settings()
        assert s.media_root == Path("/data")
    
    def test_settings_output_dir_default(self):
        """Vérifie le chemin output_dir par défaut"""
        s = Settings()
        assert s.output_dir == Path("/app/output")
    
    def test_settings_config_dir_default(self):
        """Vérifie le chemin config_dir par défaut"""
        s = Settings()
        assert s.config_dir == Path("/config")
