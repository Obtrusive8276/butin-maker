"""Tests unitaires pour le service de nommage"""
import pytest
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.naming_service import NamingService


class TestNamingService:
    """Tests pour NamingService"""
    
    def setup_method(self):
        self.service = NamingService()
    
    # Tests sanitize_title
    def test_sanitize_title_basic(self):
        """Test nettoyage basique du titre"""
        result = self.service.sanitize_title("Mon Film")
        assert result == "Mon.Film"
    
    def test_sanitize_title_accents(self):
        """Test suppression des accents"""
        result = self.service.sanitize_title("L'été meurtrier")
        assert "e" in result.lower()
        assert "é" not in result
        assert "è" not in result
    
    def test_sanitize_title_special_chars(self):
        """Test suppression des caractères spéciaux"""
        result = self.service.sanitize_title("Film: Le Retour!")
        assert ":" not in result
        assert "!" not in result
    
    def test_sanitize_title_apostrophe(self):
        """Test remplacement des apostrophes par des points"""
        result = self.service.sanitize_title("L'homme")
        assert "'" not in result
    
    def test_sanitize_title_removes_extension(self):
        """Test suppression de l'extension"""
        result = self.service.sanitize_title("Film.mkv")
        assert ".mkv" not in result.lower()
    
    def test_sanitize_title_multiple_spaces(self):
        """Test remplacement des espaces multiples"""
        result = self.service.sanitize_title("Film   Test")
        assert "..." not in result
    
    # Tests extract_movie_title_from_filename
    def test_extract_title_simple(self):
        """Test extraction du titre simple"""
        result = self.service.extract_movie_title_from_filename("Iznogoud.2005.FRENCH.1080p.WEB-DL.H264.mkv")
        assert "Iznogoud" in result
        assert "2005" not in result
        assert "1080p" not in result.lower()
    
    def test_extract_title_with_group(self):
        """Test extraction avec groupe de release"""
        result = self.service.extract_movie_title_from_filename("Film.2020.1080p.BluRay.x264-GROUP")
        assert "GROUP" not in result
        assert "-" not in result or result.count("-") == 0
    
    def test_extract_title_with_parentheses(self):
        """Test extraction avec année entre parenthèses (format: Title (YYYY))"""
        result = self.service.extract_movie_title_from_filename("The Onion Movie (2008).mkv")
        assert result == "The.Onion.Movie", f"Attendu: 'The.Onion.Movie', Obtenu: '{result}'"
        assert "2008" not in result
        assert "(" not in result
        assert ")" not in result
    
    def test_extract_title_with_parentheses_no_extension(self):
        """Test extraction avec parenthèses sans extension"""
        result = self.service.extract_movie_title_from_filename("The Onion Movie (2008)")
        assert result == "The.Onion.Movie", f"Attendu: 'The.Onion.Movie', Obtenu: '{result}'"
    
    def test_extract_title_multi_word(self):
        """Test extraction titre multi-mots (Le Seigneur des Anneaux)"""
        result = self.service.extract_movie_title_from_filename(
            "Le.Seigneur.Des.Anneaux.2001.FRENCH.1080p.BluRay.x264-GROUP.mkv"
        )
        # Le titre doit contenir les mots du film (avec points)
        assert "Seigneur" in result
        assert "Anneaux" in result
        # Les tags techniques doivent être supprimés
        assert "1080p" not in result.lower()
        assert "bluray" not in result.lower()
        assert "GROUP" not in result
    
    # Tests detect_episode_info
    def test_detect_episode_s01e01(self):
        """Test détection S01E01"""
        result = self.service.detect_episode_info("Series.S01E05.1080p.mkv")
        assert result["is_series"] == True
        assert result["season"] == 1
        assert result["episode"] == 5
    
    def test_detect_episode_season_only(self):
        """Test détection saison seule"""
        result = self.service.detect_episode_info("Series.S02.Complete")
        assert result["is_series"] == True
        assert result["season"] == 2
        assert result["is_complete_season"] == True
    
    def test_detect_episode_movie(self):
        """Test non-détection pour un film"""
        result = self.service.detect_episode_info("Movie.2020.1080p.mkv")
        assert result["is_series"] == False
        assert result["season"] is None
        assert result["episode"] is None
    
    # Tests format_episode_tag
    def test_format_episode_tag_standard(self):
        """Test formatage S01E01"""
        result = self.service.format_episode_tag(season=1, episode=5)
        assert result == "S01E05"
    
    def test_format_episode_tag_final(self):
        """Test formatage épisode final"""
        result = self.service.format_episode_tag(season=1, episode=10, is_final_episode=True)
        assert result == "S01E10.FiNAL"
    
    def test_format_episode_tag_complete_season(self):
        """Test formatage saison complète"""
        result = self.service.format_episode_tag(season=2, is_complete_season=True)
        assert result == "S02"
    
    def test_format_episode_tag_integrale(self):
        """Test formatage intégrale"""
        result = self.service.format_episode_tag(is_complete_series=True)
        assert result == "iNTEGRALE"
    
    # Tests detect_resolution
    def test_detect_resolution_1080p_standard(self):
        """Test détection 1080p standard"""
        media_info = {"video_tracks": [{"width": 1920, "height": 1080}]}
        result = self.service.detect_resolution(media_info)
        assert result == "1080p"
    
    def test_detect_resolution_1080p_scope(self):
        """Test détection 1080p pour film scope (hauteur réduite)"""
        media_info = {"video_tracks": [{"width": 1920, "height": 816}]}
        result = self.service.detect_resolution(media_info)
        assert result == "1080p"
    
    def test_detect_resolution_4k(self):
        """Test détection 4K"""
        media_info = {"video_tracks": [{"width": 3840, "height": 2160}]}
        result = self.service.detect_resolution(media_info)
        assert result == "2160p"
    
    def test_detect_resolution_720p(self):
        """Test détection 720p"""
        media_info = {"video_tracks": [{"width": 1280, "height": 720}]}
        result = self.service.detect_resolution(media_info)
        assert result == "720p"
    
    def test_detect_resolution_no_tracks(self):
        """Test sans pistes vidéo"""
        media_info = {"video_tracks": []}
        result = self.service.detect_resolution(media_info)
        assert result == "Unknown"
    
    # Tests detect_video_codec
    def test_detect_video_codec_hevc(self):
        """Test détection HEVC"""
        media_info = {"video_tracks": [{"codec": "HEVC"}]}
        result = self.service.detect_video_codec(media_info)
        assert result in ["HEVC", "H265", "x265"]
    
    def test_detect_video_codec_h264(self):
        """Test détection H264"""
        media_info = {"video_tracks": [{"codec": "AVC"}]}
        result = self.service.detect_video_codec(media_info)
        assert result in ["H264", "x264", "AVC"]


class TestNamingServiceLanguages:
    """Tests pour la détection des langues audio"""
    
    def setup_method(self):
        self.service = NamingService()
    
    def test_detect_multi_vfq(self):
        """Test détection MULTi.VFQ (anglais + français canadien)"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English"},
                {"language": "fr", "title": "VFQ - Québec"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "MULTi.VFQ"
    
    def test_detect_multi_truefrench(self):
        """Test détection MULTi.TrueFrench (anglais + français de France)"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English"},
                {"language": "fr", "title": "VFF - TrueFrench"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "MULTi.TrueFrench"
    
    def test_detect_single_vfq(self):
        """Test détection VFQ seul (français canadien uniquement)"""
        media_info = {
            "audio_tracks": [
                {"language": "fr", "title": "VFQ"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "VFQ"
    
    def test_detect_single_truefrench(self):
        """Test détection TrueFrench seul"""
        media_info = {
            "audio_tracks": [
                {"language": "fr", "title": "TrueFrench"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "TrueFrench"
    
    def test_detect_french_default_truefrench(self):
        """Test que français sans indication = TrueFrench par défaut"""
        media_info = {
            "audio_tracks": [
                {"language": "fr", "title": "French"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "TrueFrench"
    
    def test_detect_english_only(self):
        """Test détection anglais seul"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "ENGLISH"
    
    def test_detect_multi_without_french(self):
        """Test MULTi sans français (anglais + autre)"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English"},
                {"language": "de", "title": "German"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "MULTi"
    
    def test_detect_multi_french_english_from_nfo(self):
        """Test détection MULTi avec French + English (cas réel NFO The Onion Movie)
        
        Bug rapporté: Le système génère 'TrueFrench' au lieu de 'MULTi'
        quand il y a 2 pistes audio (French + English) sans titre spécifique VFF/VFQ
        """
        media_info = {
            "audio_tracks": [
                {"language": "fr", "title": "Stereo"},  # Piste 1: French sans tag VFF/VFQ
                {"language": "en", "title": "Surround"}  # Piste 2: English
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        # Devrait être MULTi.TrueFrench car French + English
        assert result == "MULTi.TrueFrench", f"Attendu: MULTi.TrueFrench, Obtenu: {result}"
    
    def test_detect_multi_three_languages(self):
        """Test détection MULTi avec 3 langues (French + English + Spanish)"""
        media_info = {
            "audio_tracks": [
                {"language": "fr", "title": "French"},
                {"language": "en", "title": "English"},
                {"language": "es", "title": "Spanish"}
            ]
        }
        result = self.service.detect_audio_languages(media_info)
        assert result == "MULTi.TrueFrench"


class TestNamingServiceCodecs:
    """Tests pour les mappings de codecs"""
    
    def setup_method(self):
        self.service = NamingService()
    
    def test_video_codecs_mapping(self):
        """Test que tous les codecs vidéo sont mappés"""
        assert "hevc" in self.service.VIDEO_CODECS
        assert "x264" in self.service.VIDEO_CODECS
        assert "av1" in self.service.VIDEO_CODECS
    
    def test_audio_codecs_mapping(self):
        """Test que tous les codecs audio sont mappés"""
        assert "dts" in self.service.AUDIO_CODECS
        assert "truehd" in self.service.AUDIO_CODECS
        assert "aac" in self.service.AUDIO_CODECS
    
    def test_sources_mapping(self):
        """Test que toutes les sources sont mappées"""
        assert "bluray" in self.service.SOURCES
        assert "web-dl" in self.service.SOURCES
        assert "remux" in self.service.SOURCES
    
    def test_platforms_mapping(self):
        """Test que toutes les plateformes sont mappées"""
        assert "netflix" in self.service.PLATFORMS
        assert "amazon" in self.service.PLATFORMS
        assert "disney" in self.service.PLATFORMS


class TestExtractTitleForSeries:
    """Tests pour l'extraction de titre des séries (sans S01/E01)"""
    
    def setup_method(self):
        self.service = NamingService()
    
    def test_extract_title_series_s01(self):
        """Test extraction titre série avec S01"""
        result = self.service.extract_movie_title_from_filename("Bluey.S01.MULTi.1080p.WEB.x264-GROUP")
        assert result == "Bluey"
        assert "S01" not in result
    
    def test_extract_title_series_s01e01(self):
        """Test extraction titre série avec S01E01"""
        result = self.service.extract_movie_title_from_filename("Stranger.Things.S01E01.MULTi.1080p.NF.WEB.x264-GROUP")
        assert result == "Stranger.Things"
        assert "S01" not in result
        assert "E01" not in result
    
    def test_extract_title_game_of_thrones(self):
        """Test extraction Game of Thrones"""
        result = self.service.extract_movie_title_from_filename("Game.of.Thrones.S01.1080p.BluRay.x264-GROUP")
        assert result == "Game.of.Thrones"
        assert "S01" not in result
    
    def test_extract_title_series_with_year(self):
        """Test extraction série avec année (année prioritaire)"""
        result = self.service.extract_movie_title_from_filename("House.of.the.Dragon.2022.S01E01.1080p.WEB.x264")
        # L'année est prioritaire, donc coupe avant 2022
        assert "House" in result
        assert "Dragon" in result
        assert "2022" not in result
    
    def test_extract_title_series_lowercase_s(self):
        """Test extraction avec s minuscule"""
        result = self.service.extract_movie_title_from_filename("Breaking.Bad.s05e16.1080p.BluRay")
        assert result == "Breaking.Bad"
        assert "s05" not in result.lower()
    
    def test_extract_title_series_double_digit_season(self):
        """Test extraction avec saison à deux chiffres"""
        result = self.service.extract_movie_title_from_filename("Supernatural.S15E20.1080p.WEB")
        assert result == "Supernatural"
        assert "S15" not in result
    
    def test_extract_title_movie_unchanged(self):
        """Test que les films ne sont pas affectés"""
        result = self.service.extract_movie_title_from_filename("Gladiator.II.2024.MULTi.1080p.BluRay.x264-GROUP")
        assert result == "Gladiator.II"
        assert "2024" not in result
    
    def test_extract_title_the_witcher(self):
        """Test The Witcher"""
        result = self.service.extract_movie_title_from_filename("The.Witcher.S03.1080p.NF.WEB.x264")
        assert result == "The.Witcher"
        assert "S03" not in result
    
    def test_extract_title_wednesday(self):
        """Test Wednesday"""
        result = self.service.extract_movie_title_from_filename("Wednesday.S01E08.FiNAL.MULTi.1080p.NF.WEB.x264")
        assert result == "Wednesday"
        assert "S01" not in result
        assert "E08" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
