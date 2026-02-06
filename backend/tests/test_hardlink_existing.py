"""
Tests pour la création de hardlinks (fichiers et dossiers).
Couvre les optimisations de performance pour les dossiers de séries.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.file_service import FileService


@pytest.fixture
def file_service():
    """FileService avec un media_root temporaire."""
    with tempfile.TemporaryDirectory() as tmpdir:
        svc = FileService()
        svc.media_root = Path(tmpdir)
        yield svc, Path(tmpdir)


@pytest.fixture
def mock_hardlink_path(file_service):
    """Configure hardlink_path dans les settings mock."""
    svc, tmpdir = file_service
    hardlink_dir = tmpdir / "hardlinks"
    hardlink_dir.mkdir()
    settings_data = {
        "paths": {"hardlink_path": str(hardlink_dir)},
    }
    with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = settings_data
            yield svc, tmpdir, hardlink_dir


# ============================================================
# Tests fichier unique
# ============================================================

class TestHardlinkFile:
    def test_hardlink_file_success(self, file_service):
        svc, tmpdir = file_service
        source = tmpdir / "movie.mkv"
        source.write_bytes(b"fake video data")
        dest = tmpdir / "dest" / "Movie.2024.mkv"

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert success
        assert "créé" in msg
        assert dest.exists()
        assert source.stat().st_ino == dest.stat().st_ino

    def test_hardlink_file_already_exists_same_inode(self, file_service):
        svc, tmpdir = file_service
        source = tmpdir / "movie.mkv"
        source.write_bytes(b"fake video data")
        dest = tmpdir / "Movie.2024.mkv"
        os.link(source, dest)

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert success
        assert "déjà existant" in msg.lower()

    def test_hardlink_file_different_file_exists(self, file_service):
        svc, tmpdir = file_service
        source = tmpdir / "movie.mkv"
        source.write_bytes(b"source content")
        dest = tmpdir / "Movie.2024.mkv"
        dest.write_bytes(b"different content")

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert not success
        assert "existe déjà" in msg.lower()

    def test_hardlink_source_not_exists(self, file_service):
        svc, tmpdir = file_service
        success, msg = svc.create_hardlink(
            str(tmpdir / "nonexistent.mkv"),
            str(tmpdir / "dest.mkv")
        )
        assert not success
        assert "n'existe pas" in msg

    def test_hardlink_source_outside_media_root(self, file_service):
        svc, tmpdir = file_service
        with tempfile.TemporaryDirectory() as other_dir:
            source = Path(other_dir) / "movie.mkv"
            source.write_bytes(b"data")
            success, msg = svc.create_hardlink(
                str(source),
                str(tmpdir / "dest.mkv")
            )
        assert not success
        assert "accès refusé" in msg.lower()


# ============================================================
# Tests dossier (séries)
# ============================================================

class TestHardlinkDirectory:
    def _create_series(self, tmpdir: Path, name: str, episode_count: int) -> Path:
        """Crée un dossier de série avec N épisodes."""
        series_dir = tmpdir / name
        series_dir.mkdir()
        for i in range(1, episode_count + 1):
            ep = series_dir / f"{name}.S01E{i:02d}.mkv"
            ep.write_bytes(f"episode {i}".encode())
        return series_dir

    def test_hardlink_directory_success(self, file_service):
        svc, tmpdir = file_service
        source = self._create_series(tmpdir, "MyShow", 5)
        dest = tmpdir / "MyShow.S01.MULTi.1080p"

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert success
        assert "5 hardlinks créés" in msg
        assert "5 fichiers" in msg

        # Vérifier que chaque fichier est un hardlink (même inode)
        for i in range(1, 6):
            src_file = source / f"MyShow.S01E{i:02d}.mkv"
            dst_file = dest / f"MyShow.S01E{i:02d}.mkv"
            assert dst_file.exists()
            assert src_file.stat().st_ino == dst_file.stat().st_ino

    def test_hardlink_directory_already_linked(self, file_service):
        """Re-exécuter sur un dossier déjà hardlinké = tous skippés."""
        svc, tmpdir = file_service
        source = self._create_series(tmpdir, "MyShow", 3)
        dest = tmpdir / "MyShow.S01"

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}

            # Premier appel
            success1, msg1 = svc.create_hardlink(str(source), str(dest))
            assert success1
            assert "3 hardlinks créés" in msg1

            # Deuxième appel - tout est déjà linké
            success2, msg2 = svc.create_hardlink(str(source), str(dest))
            assert success2
            assert "3 fichiers déjà existants ignorés" in msg2
            assert "hardlinks créés" not in msg2

    def test_hardlink_directory_partial(self, file_service):
        """Dossier avec certains fichiers déjà existants."""
        svc, tmpdir = file_service
        source = self._create_series(tmpdir, "MyShow", 5)
        dest = tmpdir / "MyShow.S01"
        dest.mkdir()

        # Hardlinker les 3 premiers épisodes manuellement
        for i in range(1, 4):
            src = source / f"MyShow.S01E{i:02d}.mkv"
            dst = dest / f"MyShow.S01E{i:02d}.mkv"
            os.link(src, dst)

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert success
        assert "2 hardlinks créés" in msg
        assert "3 fichiers déjà existants ignorés" in msg

    def test_hardlink_directory_with_subdirs(self, file_service):
        """Dossier avec sous-dossiers (ex: Season 01/Episode 01.mkv)."""
        svc, tmpdir = file_service
        source = tmpdir / "MyShow"
        source.mkdir()
        s01 = source / "Season 01"
        s01.mkdir()
        (s01 / "ep01.mkv").write_bytes(b"ep1")
        (s01 / "ep02.mkv").write_bytes(b"ep2")
        s02 = source / "Season 02"
        s02.mkdir()
        (s02 / "ep01.mkv").write_bytes(b"ep1s2")

        dest = tmpdir / "MyShow.INTEGRALE"

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert success
        assert "3 hardlinks créés" in msg
        assert (dest / "Season 01" / "ep01.mkv").exists()
        assert (dest / "Season 02" / "ep01.mkv").exists()

    def test_hardlink_directory_empty(self, file_service):
        """Dossier vide."""
        svc, tmpdir = file_service
        source = tmpdir / "EmptyDir"
        source.mkdir()
        dest = tmpdir / "EmptyDest"

        with patch("app.config.user_settings") as mock_us:
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        assert success
        assert "vide" in msg.lower()

    def test_hardlink_no_fallback_copy(self, file_service):
        """Vérifie qu'il n'y a PAS de fallback shutil.copy2 (jamais de copie silencieuse)."""
        svc, tmpdir = file_service
        source = self._create_series(tmpdir, "MyShow", 2)
        dest = tmpdir / "Dest"

        with patch("app.config.user_settings") as mock_us, \
             patch("os.link", side_effect=OSError(18, "Cross-device link")):
            mock_us.get.return_value = {"paths": {"hardlink_path": ""}}
            success, msg = svc.create_hardlink(str(source), str(dest))

        # Doit retourner avec des erreurs, PAS copier silencieusement
        assert "2 erreurs" in msg
        # Aucun fichier ne doit avoir été créé par copie
        dest_files = list(dest.rglob("*.mkv"))
        assert len(dest_files) == 0


# ============================================================
# Tests méthodes internes (performance)
# ============================================================

class TestHardlinkInternals:
    def test_scan_inodes(self, file_service):
        """_scan_inodes indexe correctement les fichiers avec leurs inodes."""
        svc, tmpdir = file_service
        test_dir = tmpdir / "indexed"
        test_dir.mkdir()
        f1 = test_dir / "file1.mkv"
        f1.write_bytes(b"content1")
        sub = test_dir / "sub"
        sub.mkdir()
        f2 = sub / "file2.mkv"
        f2.write_bytes(b"content2")

        inodes = svc._scan_inodes(str(test_dir))

        assert "file1.mkv" in inodes
        assert "sub/file2.mkv" in inodes
        assert len(inodes) == 2
        # Sur Linux (runtime Docker), les inodes sont réels et non-zéro.
        # Sur Windows (dev), entry.stat(follow_symlinks=False) retourne st_ino=0.
        # On vérifie juste que les valeurs sont des entiers cohérents.
        assert isinstance(inodes["file1.mkv"], int)
        assert isinstance(inodes["sub/file2.mkv"], int)

    def test_scan_inodes_empty_dir(self, file_service):
        """_scan_inodes retourne un dict vide pour un dossier vide."""
        svc, tmpdir = file_service
        test_dir = tmpdir / "empty"
        test_dir.mkdir()

        inodes = svc._scan_inodes(str(test_dir))
        assert len(inodes) == 0

    def test_scan_inodes_nonexistent(self, file_service):
        """_scan_inodes retourne un dict vide pour un dossier inexistant."""
        svc, tmpdir = file_service

        inodes = svc._scan_inodes(str(tmpdir / "does_not_exist"))
        assert len(inodes) == 0

    def test_scan_inodes_used_for_source_and_destination(self, file_service):
        """_scan_inodes peut servir à la fois pour indexer source et destination."""
        svc, tmpdir = file_service
        # Créer source avec 3 fichiers
        source = tmpdir / "source"
        source.mkdir()
        (source / "ep01.mkv").write_bytes(b"1")
        (source / "ep02.mkv").write_bytes(b"2")
        sub = source / "extras"
        sub.mkdir()
        (sub / "behind.mkv").write_bytes(b"3")

        source_inodes = svc._scan_inodes(str(source))

        assert len(source_inodes) == 3
        assert "ep01.mkv" in source_inodes
        assert "ep02.mkv" in source_inodes
        assert "extras/behind.mkv" in source_inodes

        # Créer destination avec 1 fichier déjà hardlinké
        dest = tmpdir / "dest"
        dest.mkdir()
        os.link(source / "ep01.mkv", dest / "ep01.mkv")

        dest_inodes = svc._scan_inodes(str(dest))

        assert len(dest_inodes) == 1
        assert dest_inodes["ep01.mkv"] == source_inodes["ep01.mkv"]  # même inode


# ============================================================
# Tests sécurité
# ============================================================

class TestHardlinkSecurity:
    def test_destination_outside_hardlink_path(self, mock_hardlink_path):
        svc, tmpdir, hardlink_dir = mock_hardlink_path
        source = tmpdir / "movie.mkv"
        source.write_bytes(b"data")

        # Destination hors du hardlink_path configuré
        success, msg = svc.create_hardlink(
            str(source),
            str(tmpdir / "outside" / "movie.mkv")
        )
        assert not success
        assert "accès refusé" in msg.lower()

    def test_destination_inside_hardlink_path(self, mock_hardlink_path):
        svc, tmpdir, hardlink_dir = mock_hardlink_path
        source = tmpdir / "movie.mkv"
        source.write_bytes(b"data")

        success, msg = svc.create_hardlink(
            str(source),
            str(hardlink_dir / "Movie.2024.mkv")
        )
        assert success
        assert (hardlink_dir / "Movie.2024.mkv").exists()
