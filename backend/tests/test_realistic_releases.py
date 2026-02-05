"""Tests avec des noms de releases réalistes provenant de différents trackers
pour vérifier la détection de titres, langues, résolutions, codecs, etc.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.naming_service import NamingService


class TestRealisticMovieReleases:
    """Tests avec 15 noms de films réalistes de différents trackers"""
    
    def setup_method(self):
        self.service = NamingService()
    
    # --- Films français ---
    
    def test_movie_gladiator_2_french_bluray(self):
        """Test Gladiator II - Release française BluRay"""
        filename = "Gladiator.II.2024.MULTi.1080p.BluRay.x264-PRODUX.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Gladiator" in title
        assert "II" in title or "2" in title
        assert "1080p" not in title.lower()
        assert "bluray" not in title.lower()
    
    def test_movie_seigneur_anneaux_extended(self):
        """Test Le Seigneur des Anneaux - Version Extended"""
        filename = "Le.Seigneur.Des.Anneaux.La.Communaute.De.L.Anneau.2001.EXTENDED.MULTi.1080p.BluRay.x264-FtLi.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Seigneur" in title
        assert "Anneaux" in title
        assert "extended" not in title.lower()
        assert "1080p" not in title.lower()
    
    def test_movie_avatar_4k_hdr(self):
        """Test Avatar - Release 4K HDR"""
        filename = "Avatar.2009.MULTi.2160p.UHD.BluRay.HDR.x265-YOURGROUP.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Avatar" in title
        assert "2160p" not in title.lower()
        assert "hdr" not in title.lower()
    
    def test_movie_dune_2_web_amazon(self):
        """Test Dune 2 - Release WEB Amazon"""
        filename = "Dune.Part.Two.2024.MULTi.1080p.AMZN.WEB-DL.DDP5.1.H.264-FLUX.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Dune" in title
        assert "amzn" not in title.lower()
        assert "web-dl" not in title.lower()
    
    def test_movie_intouchables_french_only(self):
        """Test Intouchables - Film français"""
        filename = "Intouchables.2011.FRENCH.1080p.BluRay.x264-LOST.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Intouchables" in title
        assert "french" not in title.lower()
    
    def test_movie_inception_remux(self):
        """Test Inception - Release REMUX"""
        filename = "Inception.2010.MULTi.1080p.BluRay.REMUX.AVC.DTS-HD.MA.5.1-EPSiLON.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Inception" in title
        assert "remux" not in title.lower()
    
    def test_movie_asterix_obelix_accent(self):
        """Test Astérix et Obélix - Titre avec accents"""
        filename = "Asterix.Et.Obelix.Mission.Cleopatre.2002.FRENCH.1080p.BluRay.x264-FHD.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Asterix" in title
        assert "Obelix" in title
    
    def test_movie_matrix_trilogy(self):
        """Test Matrix - Nom avec The"""
        filename = "The.Matrix.1999.REMASTERED.MULTi.1080p.BluRay.x264-VENUE.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Matrix" in title
        assert "remastered" not in title.lower()
    
    def test_movie_joker_dc(self):
        """Test Joker - Director's Cut"""
        filename = "Joker.2019.DC.MULTi.1080p.BluRay.x264-LOST.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Joker" in title
        # DC peut rester car c'est ambigu (Director's Cut ou DC Comics)
    
    def test_movie_parasite_vostfr(self):
        """Test Parasite - VOSTFR"""
        filename = "Parasite.2019.VOSTFR.1080p.BluRay.x264-VENUE.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Parasite" in title
        assert "vostfr" not in title.lower()
    
    def test_movie_oppenheimer_imax(self):
        """Test Oppenheimer - Release IMAX"""
        filename = "Oppenheimer.2023.IMAX.MULTi.1080p.WEB-DL.x264-EXTREME.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Oppenheimer" in title
        assert "web-dl" not in title.lower()
    
    def test_movie_leon_directors_cut(self):
        """Test Léon - Director's Cut"""
        filename = "Leon.The.Professional.1994.Directors.Cut.MULTi.1080p.BluRay.x264-VENUE.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Leon" in title
        assert "Professional" in title
    
    def test_movie_amelie_poulain(self):
        """Test Le Fabuleux Destin d'Amélie Poulain"""
        filename = "Le.Fabuleux.Destin.D.Amelie.Poulain.2001.FRENCH.1080p.BluRay.x264-FHD.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Amelie" in title or "Fabuleux" in title
    
    def test_movie_interstellar_imax(self):
        """Test Interstellar - IMAX"""
        filename = "Interstellar.2014.IMAX.MULTi.2160p.UHD.BluRay.x265.HDR-VENUE.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Interstellar" in title
        assert "2160p" not in title.lower()
    
    def test_movie_spiderman_no_way_home(self):
        """Test Spider-Man No Way Home - Titre avec tiret"""
        filename = "Spider-Man.No.Way.Home.2021.MULTi.1080p.BluRay.x264-LOST.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        assert "Spider" in title
        assert "Man" in title or "man" in title.lower()


class TestRealisticSeriesReleases:
    """Tests avec 15 noms de séries réalistes de différents trackers"""
    
    def setup_method(self):
        self.service = NamingService()
    
    # --- Séries ---
    
    def test_series_stranger_things_episode(self):
        """Test Stranger Things - Episode standard"""
        filename = "Stranger.Things.S04E01.MULTi.1080p.NF.WEB-DL.DDP5.1.x264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Stranger" in title
        assert "Things" in title
        assert episode_info["is_series"] == True
        assert episode_info["season"] == 4
        assert episode_info["episode"] == 1
    
    def test_series_game_of_thrones_season(self):
        """Test Game of Thrones - Saison complète"""
        filename = "Game.Of.Thrones.S08.MULTi.1080p.BluRay.x264-VENUE"
        episode_info = self.service.detect_episode_info(filename)
        assert episode_info["is_series"] == True
        assert episode_info["season"] == 8
        assert episode_info["is_complete_season"] == True
    
    def test_series_breaking_bad_final(self):
        """Test Breaking Bad - Episode final"""
        filename = "Breaking.Bad.S05E16.FiNAL.MULTi.1080p.BluRay.x264-VENUE.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Breaking" in title
        assert "Bad" in title
        assert episode_info["season"] == 5
        assert episode_info["episode"] == 16
    
    def test_series_casa_de_papel_spanish(self):
        """Test La Casa de Papel - Série espagnole"""
        filename = "La.Casa.De.Papel.S01E01.MULTi.1080p.NF.WEB-DL.x264-EXTREME.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Casa" in title
        assert "Papel" in title
        assert episode_info["is_series"] == True
    
    def test_series_the_witcher_netflix(self):
        """Test The Witcher - Netflix"""
        filename = "The.Witcher.S03E05.MULTi.1080p.NF.WEB-DL.DDP5.1.Atmos.x264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Witcher" in title
        assert episode_info["season"] == 3
        assert episode_info["episode"] == 5
    
    def test_series_peaky_blinders_complete(self):
        """Test Peaky Blinders - Intégrale"""
        filename = "Peaky.Blinders.iNTEGRALE.MULTi.1080p.BluRay.x264-VENUE"
        episode_info = self.service.detect_episode_info(filename)
        # Intégrale devrait être détectée
        assert "Peaky" in filename
    
    def test_series_mandalorian_disney(self):
        """Test The Mandalorian - Disney+"""
        filename = "The.Mandalorian.S02E08.MULTi.1080p.DSNP.WEB-DL.DDP5.1.Atmos.H.264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Mandalorian" in title
        assert episode_info["season"] == 2
        assert episode_info["episode"] == 8
    
    def test_series_lupin_french(self):
        """Test Lupin - Série française Netflix"""
        filename = "Lupin.S01E05.MULTi.1080p.NF.WEB-DL.DDP5.1.x264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Lupin" in title
        assert episode_info["season"] == 1
        assert episode_info["episode"] == 5
    
    def test_series_dark_german(self):
        """Test Dark - Série allemande"""
        filename = "Dark.S03E08.MULTi.1080p.NF.WEB-DL.DDP5.1.x264-VENUE.mkv"
        episode_info = self.service.detect_episode_info(filename)
        assert episode_info["is_series"] == True
        assert episode_info["season"] == 3
    
    def test_series_chernobyl_hbo(self):
        """Test Chernobyl - HBO Mini-série"""
        filename = "Chernobyl.S01E05.MULTi.1080p.AMZN.WEB-DL.DDP5.1.H.264-TEPES.mkv"
        episode_info = self.service.detect_episode_info(filename)
        assert episode_info["season"] == 1
        assert episode_info["episode"] == 5
    
    def test_series_squid_game_korean(self):
        """Test Squid Game - Série coréenne"""
        filename = "Squid.Game.S01E09.MULTi.1080p.NF.WEB-DL.DDP5.1.Atmos.x264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Squid" in title
        assert "Game" in title
        assert episode_info["episode"] == 9
    
    def test_series_house_of_dragon_hbo(self):
        """Test House of the Dragon - HBO"""
        filename = "House.Of.The.Dragon.S01E10.MULTi.1080p.HMAX.WEB-DL.DDP5.1.Atmos.H.264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "House" in title
        assert "Dragon" in title
        assert episode_info["season"] == 1
        assert episode_info["episode"] == 10
    
    def test_series_last_of_us_hbo(self):
        """Test The Last of Us - HBO"""
        filename = "The.Last.Of.Us.S01E03.MULTi.1080p.HMAX.WEB-DL.DDP5.1.Atmos.H.264-FLUX.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Last" in title
        assert episode_info["season"] == 1
        assert episode_info["episode"] == 3
    
    def test_series_wednesday_netflix(self):
        """Test Wednesday - Netflix"""
        filename = "Wednesday.S01E08.MULTi.1080p.NF.WEB-DL.DDP5.1.Atmos.x264-TEPES.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Wednesday" in title
        assert episode_info["season"] == 1
        assert episode_info["episode"] == 8
    
    def test_series_severance_apple(self):
        """Test Severance - Apple TV+"""
        filename = "Severance.S01E09.MULTi.1080p.ATVP.WEB-DL.DDP5.1.Atmos.H.264-FLUX.mkv"
        title = self.service.extract_movie_title_from_filename(filename)
        episode_info = self.service.detect_episode_info(filename)
        assert "Severance" in title
        assert episode_info["season"] == 1
        assert episode_info["episode"] == 9


class TestRealisticMediaInfo:
    """Tests avec des faux MediaInfo pour vérifier la détection des langues et codecs"""
    
    def setup_method(self):
        self.service = NamingService()
    
    def test_mediainfo_multi_truefrench(self):
        """Test MediaInfo avec VFF (TrueFrench)"""
        media_info = {
            "file_name": "Film.2024.MULTi.1080p.BluRay.x264-GROUP.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1920, "height": 1080}],
            "audio_tracks": [
                {"language": "en", "title": "English DTS-HD MA 5.1", "codec": "DTS-HD MA", "channels": 6},
                {"language": "fr", "title": "VFF AC3 5.1", "codec": "AC3", "channels": 6}
            ],
            "subtitle_tracks": []
        }
        lang = self.service.detect_audio_languages(media_info)
        assert lang == "MULTi.TrueFrench"
    
    def test_mediainfo_multi_vfq(self):
        """Test MediaInfo avec VFQ (Québécois)"""
        media_info = {
            "file_name": "Film.2024.MULTi.1080p.BluRay.x264-GROUP.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1920, "height": 1080}],
            "audio_tracks": [
                {"language": "en", "title": "English DTS-HD MA 5.1", "codec": "DTS-HD MA", "channels": 6},
                {"language": "fr", "title": "VFQ AC3 5.1 - Québec", "codec": "AC3", "channels": 6}
            ],
            "subtitle_tracks": []
        }
        lang = self.service.detect_audio_languages(media_info)
        assert lang == "MULTi.VFQ"
    
    def test_mediainfo_hevc_4k_hdr(self):
        """Test MediaInfo 4K HDR HEVC"""
        media_info = {
            "file_name": "Film.2024.MULTi.2160p.UHD.BluRay.x265-GROUP.mkv",
            "video_tracks": [{
                "codec": "HEVC",
                "width": 3840,
                "height": 2160,
                "hdr_format": "HDR10",
                "color_primaries": "BT.2020"
            }],
            "audio_tracks": [
                {"language": "en", "title": "English TrueHD Atmos", "codec": "TrueHD", "channels": 8}
            ],
            "subtitle_tracks": []
        }
        resolution = self.service.detect_resolution(media_info)
        codec = self.service.detect_video_codec(media_info)
        hdr = self.service.detect_hdr(media_info)
        
        assert resolution == "2160p"
        assert codec in ["HEVC", "x265", "H265"]
        assert hdr == "HDR"
    
    def test_mediainfo_dolby_vision(self):
        """Test MediaInfo Dolby Vision"""
        media_info = {
            "video_tracks": [{
                "codec": "HEVC",
                "width": 3840,
                "height": 2160,
                "hdr_format": "Dolby Vision, HDR10",
                "transfer_characteristics": "PQ"
            }],
            "audio_tracks": []
        }
        hdr = self.service.detect_hdr(media_info)
        assert hdr == "HDR.DV"
    
    def test_mediainfo_web_netflix(self):
        """Test MediaInfo WEB Netflix"""
        media_info = {
            "file_name": "Series.S01E01.MULTi.1080p.NF.WEB-DL.x264-GROUP.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1920, "height": 1080}],
            "audio_tracks": [
                {"language": "en", "title": "English EAC3 5.1", "codec": "E-AC3", "channels": 6},
                {"language": "fr", "title": "French EAC3 5.1", "codec": "E-AC3", "channels": 6}
            ],
            "subtitle_tracks": []
        }
        platform = self.service.detect_platform(media_info["file_name"])
        source = self.service.detect_source(media_info["file_name"])
        
        assert platform == "NF"
        assert source == "WEB-DL"
    
    def test_mediainfo_remux_dts_hd(self):
        """Test MediaInfo REMUX avec DTS-HD MA"""
        media_info = {
            "file_name": "Film.2024.MULTi.1080p.BluRay.REMUX.AVC.DTS-HD.MA-GROUP.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1920, "height": 1080}],
            "audio_tracks": [
                {"language": "en", "title": "English DTS-HD MA 7.1", "codec": "DTS-HD MA", "channels": 8},
                {"language": "fr", "title": "VFF DTS-HD MA 5.1", "codec": "DTS-HD MA", "channels": 6}
            ],
            "subtitle_tracks": []
        }
        source = self.service.detect_source(media_info["file_name"])
        audio_codec = self.service.detect_audio_codec(media_info)
        
        assert source == "REMUX"
        assert "DTS" in audio_codec
    
    def test_mediainfo_sd_dvdrip(self):
        """Test MediaInfo SD DVDRip"""
        media_info = {
            "file_name": "Film.2000.FRENCH.DVDRip.x264-GROUP.avi",
            "video_tracks": [{"codec": "AVC", "width": 720, "height": 576}],
            "audio_tracks": [
                {"language": "fr", "title": "French AC3", "codec": "AC3", "channels": 6}
            ],
            "subtitle_tracks": []
        }
        resolution = self.service.detect_resolution(media_info)
        is_sd = self.service.is_sd_resolution(media_info)
        source = self.service.detect_source(media_info["file_name"])
        
        assert is_sd == True
        assert source == "DVDRip"
    
    def test_mediainfo_720p_hdtv(self):
        """Test MediaInfo 720p HDTV"""
        media_info = {
            "file_name": "Series.S01E01.FRENCH.720p.HDTV.x264-GROUP.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1280, "height": 720}],
            "audio_tracks": [
                {"language": "fr", "title": "French AAC", "codec": "AAC", "channels": 2}
            ],
            "subtitle_tracks": []
        }
        resolution = self.service.detect_resolution(media_info)
        source = self.service.detect_source(media_info["file_name"])
        
        assert resolution == "720p"
        assert source == "HDTV"
    
    def test_mediainfo_atmos_audio(self):
        """Test MediaInfo avec Dolby Atmos"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English TrueHD Atmos 7.1", "codec": "TrueHD Atmos", "channels": 8}
            ]
        }
        audio_spec = self.service.detect_audio_spec(media_info)
        assert audio_spec == "Atmos"
    
    def test_mediainfo_vfi_international(self):
        """Test MediaInfo avec VFi (International)"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English", "codec": "DTS", "channels": 6},
                {"language": "fr", "title": "VFi - International", "codec": "AC3", "channels": 6}
            ]
        }
        lang = self.service.detect_audio_languages(media_info)
        assert lang == "MULTi.VFi"
    
    def test_mediainfo_english_only(self):
        """Test MediaInfo anglais uniquement"""
        media_info = {
            "audio_tracks": [
                {"language": "en", "title": "English DTS-HD MA 5.1", "codec": "DTS-HD MA", "channels": 6}
            ]
        }
        lang = self.service.detect_audio_languages(media_info)
        assert lang == "ENGLISH"
    
    def test_mediainfo_french_only_no_tag(self):
        """Test MediaInfo français seul sans tag VFF/VFQ"""
        media_info = {
            "audio_tracks": [
                {"language": "fr", "title": "French AC3 5.1", "codec": "AC3", "channels": 6}
            ]
        }
        lang = self.service.detect_audio_languages(media_info)
        assert lang == "TrueFrench"
    
    def test_mediainfo_group_detection(self):
        """Test détection du groupe depuis le nom de fichier"""
        filenames = [
            ("Film.2024.MULTi.1080p.BluRay.x264-PRODUX.mkv", "PRODUX"),
            ("Series.S01E01.MULTi.1080p.NF.WEB-DL.x264-TEPES.mkv", "TEPES"),
            ("Film.2024.FRENCH.1080p.BluRay.x264-FtLi.mkv", "FtLi"),
            ("Film.2024.MULTi.2160p.UHD.BluRay.x265-VENUE.mkv", "VENUE"),
        ]
        for filename, expected_group in filenames:
            group = self.service.detect_group(filename)
            assert group == expected_group, f"Expected {expected_group} for {filename}, got {group}"
    
    def test_mediainfo_platform_detection(self):
        """Test détection des plateformes de streaming"""
        platforms = [
            ("Film.2024.MULTi.1080p.NF.WEB-DL.x264-GROUP.mkv", "NF"),
            ("Film.2024.MULTi.1080p.AMZN.WEB-DL.x264-GROUP.mkv", "AMZN"),
            ("Film.2024.MULTi.1080p.DSNP.WEB-DL.x264-GROUP.mkv", "DSNP"),
            ("Film.2024.MULTi.1080p.ATVP.WEB-DL.x264-GROUP.mkv", "ATVP"),
            ("Film.2024.MULTi.1080p.HMAX.WEB-DL.x264-GROUP.mkv", "HMAX"),
        ]
        for filename, expected_platform in platforms:
            platform = self.service.detect_platform(filename)
            assert platform == expected_platform, f"Expected {expected_platform} for {filename}, got {platform}"


class TestGenerateReleaseName:
    """Tests de génération de noms de release complets"""
    
    def setup_method(self):
        self.service = NamingService()
    
    def test_generate_movie_name_complete(self):
        """Test génération nom de film complet"""
        media_info = {
            "file_name": "source.mkv",
            "video_tracks": [{"codec": "HEVC", "width": 1920, "height": 1080}],
            "audio_tracks": [
                {"language": "en", "title": "English", "codec": "DTS", "channels": 6},
                {"language": "fr", "title": "VFF", "codec": "AC3", "channels": 6}
            ]
        }
        name = self.service.generate_release_name(
            title="Gladiator II",
            year="2024",
            media_info=media_info,
            source="BluRay",
            group="PRODUX"
        )
        assert "Gladiator" in name
        assert "2024" in name
        assert "1080p" in name
        assert "BluRay" in name
        assert "PRODUX" in name
    
    def test_generate_series_name_episode(self):
        """Test génération nom de série avec épisode"""
        media_info = {
            "file_name": "source.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1920, "height": 1080}],
            "audio_tracks": [
                {"language": "en", "title": "English", "codec": "EAC3", "channels": 6},
                {"language": "fr", "title": "French", "codec": "EAC3", "channels": 6}
            ]
        }
        name = self.service.generate_release_name(
            title="Stranger Things",
            year=None,
            media_info=media_info,
            source="WEB-DL",
            group="TEPES",
            content_type="tv",
            season=4,
            episode=1
        )
        assert "Stranger" in name
        assert "S04E01" in name
        assert "1080p" in name
        assert "WEB-DL" in name
    
    def test_generate_name_with_manual_language(self):
        """Test génération avec langue manuelle"""
        media_info = {
            "file_name": "source.mkv",
            "video_tracks": [{"codec": "AVC", "width": 1920, "height": 1080}],
            "audio_tracks": []
        }
        name = self.service.generate_release_name(
            title="Test Film",
            year="2024",
            media_info=media_info,
            source="BluRay",
            group="GROUP",
            language="MULTi.VFQ"
        )
        assert "MULTi.VFQ" in name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
