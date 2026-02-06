"""Tests pour config.py - UserSettings et Settings"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

from app.config import UserSettings, Settings, settings
from app.models.settings import SettingsModel


class TestUserSettingsDefaults:
    """Tests des valeurs par défaut via SettingsModel (source unique de vérité)"""
    
    def test_defaults_has_qbittorrent(self):
        """Vérifie que les defaults contiennent qbittorrent avec tous les champs"""
        defaults = SettingsModel().model_dump()
        assert "qbittorrent" in defaults
        assert "host" in defaults["qbittorrent"]
        assert "port" in defaults["qbittorrent"]
        assert "username" in defaults["qbittorrent"]
        assert "password" in defaults["qbittorrent"]
    
    def test_defaults_has_tracker(self):
        """Vérifie que les defaults contiennent tracker avec tous les champs"""
        defaults = SettingsModel().model_dump()
        assert "tracker" in defaults
        assert "announce_url" in defaults["tracker"]
        assert "upload_url" in defaults["tracker"]
        assert "lacale_api_key" in defaults["tracker"]
    
    def test_defaults_has_paths(self):
        """Vérifie que les defaults contiennent paths avec tous les champs"""
        defaults = SettingsModel().model_dump()
        assert "paths" in defaults
        assert "default_browse_path" in defaults["paths"]
        assert "hardlink_path" in defaults["paths"]
        assert "qbittorrent_download_path" in defaults["paths"]
        assert "output_path" in defaults["paths"]
    
    def test_defaults_has_tmdb(self):
        """Vérifie que les defaults contiennent tmdb"""
        defaults = SettingsModel().model_dump()
        assert "tmdb" in defaults
        assert "api_key" in defaults["tmdb"]
    
    def test_defaults_upload_url_value(self):
        """Vérifie la valeur par défaut de upload_url"""
        defaults = SettingsModel().model_dump()
        assert defaults["tracker"]["upload_url"] == "https://la-cale.space/upload"
    
    def test_defaults_qbittorrent_port(self):
        """Vérifie le port par défaut de qBittorrent"""
        defaults = SettingsModel().model_dump()
        assert defaults["qbittorrent"]["port"] == 8080


class TestUserSettingsLoad:
    """Tests de la méthode _load"""
    
    def test_load_returns_defaults_when_no_file(self):
        """Retourne un SettingsModel avec defaults si le fichier n'existe pas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = Path(tmpdir) / "settings.json"
            test_settings._model = test_settings._load()
            result = test_settings.get()
            expected = SettingsModel().model_dump()
            assert result == expected
    
    def test_load_reads_existing_file(self):
        """Charge les données depuis un fichier existant et fusionne avec defaults"""
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
            test_settings._model = test_settings._load()
            result = test_settings.get()
            assert result["qbittorrent"]["host"] == "http://custom-host"
            assert result["qbittorrent"]["port"] == 9090
    
    def test_load_handles_corrupt_json(self):
        """Retourne les defaults si le fichier JSON est corrompu"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            settings_file.write_text("{ invalid json !!!")
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = test_settings._load()
            result = test_settings.get()
            expected = SettingsModel().model_dump()
            assert result == expected


class TestUserSettingsGet:
    """Tests de la méthode get() - fusion avec defaults via Pydantic"""
    
    def test_get_merges_with_defaults(self):
        """Vérifie que get() fusionne les données partielles avec les defaults"""
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
            test_settings._model = test_settings._load()
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
        """Vérifie la fusion des sous-dictionnaires partiels"""
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
            test_settings._model = test_settings._load()
            result = test_settings.get()
            
            # La valeur custom est présente
            assert result["paths"]["default_browse_path"] == "/custom/path"
            
            # Les clés manquantes sont ajoutées depuis defaults
            assert "hardlink_path" in result["paths"]
            assert result["paths"]["hardlink_path"] == ""
            assert "qbittorrent_download_path" in result["paths"]
            assert "output_path" in result["paths"]
    
    def test_get_all_keys_present(self):
        """Vérifie que toutes les clés sont présentes après get()"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = Path(tmpdir) / "settings.json"
            test_settings._model = test_settings._load()
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
    
    def test_get_preserves_empty_strings(self):
        """Vérifie que les chaînes vides volontaires ne sont pas remplacées par les defaults"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            data = {
                "tracker": {
                    "announce_url": "",
                    "upload_url": "",
                    "lacale_api_key": ""
                }
            }
            with open(settings_file, "w") as f:
                json.dump(data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = test_settings._load()
            result = test_settings.get()
            
            # Les chaînes vides sont conservées, pas remplacées par les defaults
            assert result["tracker"]["announce_url"] == ""
            assert result["tracker"]["upload_url"] == ""
            assert result["tracker"]["lacale_api_key"] == ""
    
    def test_get_ignores_unknown_fields(self):
        """Vérifie que les champs inconnus dans le JSON sont ignorés sans erreur"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            data = {
                "qbittorrent": {
                    "host": "http://test",
                    "port": 8080,
                    "username": "admin",
                    "password": "",
                    "unknown_field": "should_be_ignored"
                },
                "future_section": {
                    "new_key": "new_value"
                }
            }
            with open(settings_file, "w") as f:
                json.dump(data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = test_settings._load()
            result = test_settings.get()
            
            # Les champs valides sont présents
            assert result["qbittorrent"]["host"] == "http://test"
            # Les champs inconnus sont ignorés
            assert "unknown_field" not in result["qbittorrent"]
            assert "future_section" not in result


class TestUserSettingsSave:
    """Tests de la méthode save()"""
    
    def test_save_writes_to_file(self):
        """Vérifie que save() écrit dans le fichier après validation Pydantic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = SettingsModel()
            
            new_data = {
                "qbittorrent": {"host": "http://new-host", "port": 1234, "username": "u", "password": "p"},
                "tracker": {"announce_url": "http://tracker", "upload_url": "http://upload", "lacale_api_key": "key123"},
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
            assert saved_data["tracker"]["lacale_api_key"] == "key123"
    
    def test_save_updates_internal_model(self):
        """Vérifie que save() met à jour le modèle interne"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = SettingsModel()
            
            new_data = {
                "qbittorrent": {"host": "http://updated", "port": 9999, "username": "u", "password": "p"},
                "tracker": {"announce_url": "", "upload_url": "", "lacale_api_key": ""},
                "paths": {"default_browse_path": "", "hardlink_path": "", "qbittorrent_download_path": "", "output_path": ""},
                "tmdb": {"api_key": ""}
            }
            test_settings.save(new_data)
            
            result = test_settings.get()
            assert result["qbittorrent"]["host"] == "http://updated"
            assert result["qbittorrent"]["port"] == 9999
    
    def test_save_completes_partial_data(self):
        """Vérifie que save() complète les données partielles avec les defaults"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = SettingsModel()
            
            # Sauvegarder des données partielles
            partial_data = {
                "qbittorrent": {"host": "http://partial"}
            }
            test_settings.save(partial_data)
            
            # Le fichier doit contenir toutes les sections
            with open(settings_file) as f:
                saved_data = json.load(f)
            assert saved_data["qbittorrent"]["host"] == "http://partial"
            assert saved_data["qbittorrent"]["port"] == 8080  # default complété
            assert "tracker" in saved_data
            assert "paths" in saved_data
            assert "tmdb" in saved_data


class TestUserSettingsUpdate:
    """Tests de la méthode update()"""
    
    def test_update_modifies_specific_key(self):
        """Vérifie que update() modifie une clé spécifique"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = SettingsModel()
            
            test_settings.update("qbittorrent", {"host": "http://updated", "port": 9999, "username": "u", "password": "p"})
            
            result = test_settings.get()
            assert result["qbittorrent"]["host"] == "http://updated"
            assert result["qbittorrent"]["port"] == 9999
    
    def test_update_preserves_other_sections(self):
        """Vérifie que update() ne touche pas les autres sections"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = SettingsModel()
            
            # Sauvegarder d'abord une clé API
            full_data = test_settings.get()
            full_data["tracker"]["lacale_api_key"] = "my_secret_key"
            test_settings.save(full_data)
            
            # Mettre à jour seulement qbittorrent
            test_settings.update("qbittorrent", {"host": "http://new", "port": 1234, "username": "u", "password": "p"})
            
            # La clé API doit être préservée
            result = test_settings.get()
            assert result["tracker"]["lacale_api_key"] == "my_secret_key"
            assert result["qbittorrent"]["host"] == "http://new"


class TestUserSettingsLaCaleApiKey:
    """Tests pour le champ lacale_api_key dans les settings"""
    
    def test_defaults_include_lacale_api_key(self):
        """Vérifie que les defaults contiennent tracker.lacale_api_key"""
        defaults = SettingsModel().model_dump()
        assert "tracker" in defaults
        assert "lacale_api_key" in defaults["tracker"]
        assert defaults["tracker"]["lacale_api_key"] == ""
    
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
            test_settings._model = test_settings._load()
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
            test_settings._model = test_settings._load()
            
            data = test_settings.get()
            data["tracker"]["lacale_api_key"] = "test_api_key_123"
            test_settings.save(data)
            
            # Recharger depuis le fichier
            test_settings2 = UserSettings.__new__(UserSettings)
            test_settings2.settings_file = settings_file
            test_settings2._model = test_settings2._load()
            result = test_settings2.get()
            
            assert result["tracker"]["lacale_api_key"] == "test_api_key_123"


class TestUserSettingsMigration:
    """Tests de migration : fichiers JSON ancienne version"""
    
    def test_old_settings_without_lacale_api_key(self):
        """Simule un settings.json pré-upload auto (sans lacale_api_key)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            old_data = {
                "qbittorrent": {"host": "http://my-qbit", "port": 8080, "username": "admin", "password": "pass"},
                "tracker": {"announce_url": "http://announce", "upload_url": "https://la-cale.space/upload"},
                "paths": {"default_browse_path": "/data", "hardlink_path": "/data/uploads", "qbittorrent_download_path": "/data/uploads", "output_path": "/output"},
                "tmdb": {"api_key": "my_tmdb_key"}
            }
            with open(settings_file, "w") as f:
                json.dump(old_data, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = test_settings._load()
            result = test_settings.get()
            
            # Les anciennes valeurs sont préservées
            assert result["qbittorrent"]["host"] == "http://my-qbit"
            assert result["tracker"]["announce_url"] == "http://announce"
            assert result["tmdb"]["api_key"] == "my_tmdb_key"
            
            # Le nouveau champ est automatiquement ajouté
            assert result["tracker"]["lacale_api_key"] == ""
    
    def test_empty_settings_file(self):
        """Simule un settings.json vide"""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_file = Path(tmpdir) / "settings.json"
            with open(settings_file, "w") as f:
                json.dump({}, f)
            
            test_settings = UserSettings.__new__(UserSettings)
            test_settings.settings_file = settings_file
            test_settings._model = test_settings._load()
            result = test_settings.get()
            
            # Tous les defaults doivent être présents
            expected = SettingsModel().model_dump()
            assert result == expected


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
