import re
from pathlib import Path
from typing import Optional, Dict, Any
import shutil


class NamingService:
    """Service pour renommer les fichiers selon la nomenclature La Cale"""
    
    # Mapping des codecs vidéo selon La Cale
    VIDEO_CODECS = {
        "hevc": "HEVC", "h.265": "H265", "h265": "H265", "x265": "x265",
        "avc": "H264", "h.264": "H264", "h264": "H264", "x264": "x264",
        "vp9": "VP9", "av1": "AV1", "vc-1": "VC-1", "vc1": "VC-1",
        "mpeg": "MPEG", "x266": "x266", "vvc": "VVC"
    }
    
    # Mapping des codecs audio selon La Cale
    AUDIO_CODECS = {
        "dts-hd ma": "DTS-HD.MA", "dts-hd master": "DTS-HD.MA",
        "dts-hd hr": "DTS-HD.HR", "dts-hd high": "DTS-HD.HR",
        "dts:x": "DTS-X", "dts-x": "DTS-X", "dtsx": "DTS-X",
        "dts": "DTS",
        "truehd": "TrueHD", "true hd": "TrueHD",
        "atmos": "Atmos",
        "e-ac-3": "EAC3", "eac3": "EAC3", "ddp": "DDP", "dolby digital plus": "DDP",
        "ac-3": "AC3", "ac3": "AC3", "dd": "DD", "dolby digital": "DD",
        "ac-4": "AC4", "ac4": "AC4",
        "aac": "AAC", "he-aac": "HE-AAC",
        "flac": "FLAC", "mp3": "MP3", "opus": "OPUS"
    }
    
    # Mapping des sources selon La Cale (ordre important: plus spécifique d'abord)
    SOURCES = {
        "remux": "REMUX",  # REMUX avant BluRay car contient souvent "BluRay.REMUX"
        "bluray": "BluRay", "blu-ray": "BluRay", "bdrip": "BluRay",
        "web-dl": "WEB-DL", "webdl": "WEB-DL",
        "webrip": "WEBRip",
        "hdtv": "HDTV",
        "dvdrip": "DVDRip", "dvd": "DVDRip",
        "full": "FULL", "complete": "COMPLETE",
        "hdlight": "HDLight", "4klight": "4KLight"
    }
    
    # Mapping des résolutions
    RESOLUTIONS = {
        "3840": "2160p", "2160": "2160p", "4k": "2160p",
        "1920": "1080p", "1080": "1080p",
        "1280": "720p", "720": "720p",
        "576": None, "480": None  # SD = pas de résolution affichée
    }
    
    # Seuils pour détection par hauteur (pour films avec bandes noires)
    RESOLUTION_HEIGHT_THRESHOLDS = [
        (2160, "2160p"),   # 4K
        (800, "1080p"),    # 1080p avec bandes (ex: 816px)
        (700, "720p"),     # 720p standard
    ]
    
    # Plateformes (pour WEB sources) - inclut les abréviations courtes
    PLATFORMS = {
        # Abréviations courtes (prioritaires)
        ".nf.": "NF", ".amzn.": "AMZN", ".dsnp.": "DSNP", ".atvp.": "ATVP",
        ".hmax.": "HMAX", ".pmtp.": "PMTP", ".adn.": "ADN", ".cr.": "CR",
        # Noms complets
        "netflix": "NF", "amazon": "AMZN", "prime": "AMZN",
        "disney": "DSNP", "apple": "ATVP", "itunes": "iT",
        "hbo": "HMAX", "max": "MAX", "paramount": "PMTP",
        "hulu": "HULU", "peacock": "PCOK", "starz": "STARZ",
        "crave": "CRAVE", "stan": "STAN", "mubi": "MUBI",
        "crunchyroll": "CR", "bravia": "BCORE"
    }
    
    # Dynamic Range
    HDR_TYPES = {
        "dolby vision": "DV", "dovi": "DV", "dv": "DV",
        "hdr10+": "HDR10Plus", "hdr10plus": "HDR10Plus",
        "hdr10": "HDR", "hdr": "HDR",
        "hlg": "HLG", "sdr": "SDR"
    }
    
    # Caractères à remplacer/supprimer
    CHAR_REPLACEMENTS = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a", "ä": "a",
        "ù": "u", "û": "u", "ü": "u",
        "ô": "o", "ö": "o",
        "î": "i", "ï": "i",
        "ç": "c",
        "'": ".", "'": ".",
        ":": "", ";": "", ",": "",
        "{": "", "}": "", "[": "", "]": "",
        "!": "", "?": ""
    }
    
    # Patterns pour détecter saison/épisode
    EPISODE_PATTERNS = [
        r'[Ss](\d{1,2})[Ee](\d{1,2})',           # S01E01
        r'[Ss](\d{1,2})\.?[Ee](\d{1,2})',        # S01.E01
        r'(\d{1,2})x(\d{1,2})',                   # 1x01
        r'[Ss]aison\s*(\d{1,2}).*[Ee]pisode\s*(\d{1,2})',  # Saison 1 Episode 1
        r'[Ss]eason\s*(\d{1,2}).*[Ee]pisode\s*(\d{1,2})',  # Season 1 Episode 1
    ]
    
    SEASON_ONLY_PATTERNS = [
        r'[Ss]aison\s*(\d{1,2})',    # Saison 1
        r'[Ss]eason\s*(\d{1,2})',    # Season 1
        r'[Ss](\d{1,2})(?![Ee])',    # S01 (sans E après)
    ]
    
    def sanitize_title(self, title: str) -> str:
        """Nettoie le titre selon les règles La Cale
        
        Règles:
        - Première lettre de chaque mot en majuscule
        - Pas d'accents, apostrophes, cédilles
        - Pas de caractères spéciaux ,;}{][
        - Espaces remplacés par des points
        - Supprime les extensions de fichier
        """
        # Supprimer l'extension si présente
        title = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v|ts|m2ts)$', '', title, flags=re.IGNORECASE)
        
        # Remplacer les caractères accentués et spéciaux
        for char, replacement in self.CHAR_REPLACEMENTS.items():
            title = title.replace(char, replacement)
            title = title.replace(char.upper(), replacement.upper())
        
        # Supprimer les caractères interdits
        title = re.sub(r'[<>"/\\|?*]', '', title)
        
        # Supprimer les tags communs du titre (langues, résolutions, codecs, etc.)
        common_tags = ['french', 'vff', 'vfq', 'vostfr', 'multi', '1080p', '720p', '2160p', '4k', 
                       'h264', 'h265', 'x264', 'x265', 'hevc', 'avc', 'bluray', 'web-dl', 'webdl', 
                       'webrip', 'hdtv', 'dvdrip', 'remux', 'ac3', 'aac', 'dts', 'hdma']
        title_lower = title.lower()
        for tag in common_tags:
            title = re.sub(r'\.' + tag + r'\b', '', title, flags=re.IGNORECASE)
            title = re.sub(r'\b' + tag + r'\.', '', title, flags=re.IGNORECASE)
        
        # Remplacer les espaces par des points
        title = re.sub(r'\s+', '.', title.strip())
        
        # Supprimer les points multiples
        title = re.sub(r'\.+', '.', title)
        
        # Mettre la première lettre de chaque mot en majuscule
        parts = title.split('.')
        parts = [p.capitalize() if p.islower() else p for p in parts if p]
        title = '.'.join(parts)
        
        # Supprimer le point final s'il existe
        title = title.rstrip('.')
        
        return title
    
    def extract_movie_title_from_filename(self, filename: str) -> str:
        """Extrait le titre du film depuis le nom de fichier en supprimant tous les tags
        
        Ex: Iznogoud.2005.FRENCH.1080p.WEB-DL.H264.mkv -> Iznogoud
        
        Stratégie: Trouver l'année (19xx ou 20xx) et couper avant, sinon supprimer les tags connus.
        """
        # Supprimer l'extension
        name = Path(filename).stem if '.' in filename else filename
        
        # Supprimer le groupe à la fin (tiret suivi de lettres/chiffres)
        name = re.sub(r'-[A-Za-z0-9]+$', '', name)
        
        # Stratégie 1: Chercher l'année (format .YYYY.) et couper avant
        year_match = re.search(r'\.((19|20)\d{2})\.', name)
        if year_match:
            # Prendre tout ce qui est avant l'année
            title = name[:year_match.start()]
            # Nettoyer les points
            title = title.strip('.')
            if title:
                return title
        
        # Stratégie 1b: Chercher l'année avec parenthèses (format (YYYY)) et couper avant
        year_match = re.search(r'\s*\((19|20)\d{2}\)', name)
        if year_match:
            # Prendre tout ce qui est avant l'année
            title = name[:year_match.start()]
            # Nettoyer les espaces et remplacer par des points
            title = title.strip()
            # Remplacer les espaces par des points pour la cohérence
            title = title.replace(' ', '.')
            if title:
                return title
        
        # Stratégie 2: Chercher l'année à la fin (.YYYY)
        year_match = re.search(r'\.((19|20)\d{2})$', name)
        if year_match:
            title = name[:year_match.start()]
            title = title.strip('.')
            if title:
                return title
        
        # Stratégie 2.5: Chercher les tags de saison/épisode et couper avant
        season_match = re.search(r'\.S\d{1,2}(E\d{1,2})?\.?', name, re.IGNORECASE)
        if season_match:
            title = name[:season_match.start()]
            title = title.strip('.')
            if title:
                return title
        
        # Stratégie 3: Pas d'année trouvée, supprimer les tags connus
        # Liste des tags techniques à supprimer (avec point avant)
        tags_to_remove = [
            # Saisons/Episodes
            r'\.S\d{1,2}E\d{1,2}\b', r'\.S\d{1,2}\b', r'\.\d{1,2}x\d{1,2}\b',
            # Résolutions
            r'\.\d{3,4}p\b', r'\.[24]k\b', r'\.uhd\b',
            # Codecs vidéo
            r'\.h\.?264\b', r'\.h\.?265\b', r'\.x264\b', r'\.x265\b',
            r'\.hevc\b', r'\.avc\b', r'\.av1\b',
            # Codecs audio
            r'\.ac3\b', r'\.aac\b', r'\.dts[^a-z]*', r'\.truehd\b',
            r'\.atmos\b', r'\.eac3\b', r'\.ddp?\d*\.?\d*\b', r'\.flac\b',
            # Sources
            r'\.web-dl\b', r'\.webdl\b', r'\.webrip\b', r'\.web\b',
            r'\.bluray\b', r'\.blu-ray\b', r'\.bdrip\b', r'\.brrip\b',
            r'\.hdtv\b', r'\.dvdrip\b', r'\.remux\b', r'\.hdlight\b',
            # Langues
            r'\.french\b', r'\.vff\b', r'\.vfq\b', r'\.vostfr\b', r'\.subfrench\b',
            r'\.multi\b', r'\.english\b', r'\.eng\b', r'\.vo\b', r'\.vf\b',
            r'\.truefrench\b', r'\.vfi\b',
            # HDR/Dynamic
            r'\.hdr10plus\b', r'\.hdr10\b', r'\.hdr\b', r'\.dv\b', r'\.hlg\b', r'\.sdr\b',
            # Éditions
            r'\.dc\b', r'\.extended\b', r'\.remastered\b', r'\.unrated\b',
            r'\.final\.cut\b', r'\.directors?\.?cut\b', r'\.theatrical\b',
            r'\.imax\b', r'\.proper\b', r'\.repack\b', r'\.rerip\b', r'\.custom\b',
            # Plateformes
            r'\.nf\b', r'\.amzn\b', r'\.dsnp\b', r'\.atvp\b', r'\.hmax\b',
            r'\.pmtp\b', r'\.adn\b', r'\.cr\b',
        ]
        
        result = name
        for pattern in tags_to_remove:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        # Nettoyer les points multiples et les points de début/fin
        result = re.sub(r'\.+', '.', result)
        result = result.strip('.')
        
        return result
    
    def detect_episode_info(self, filename: str) -> Dict[str, Any]:
        result = {
            "is_series": False,
            "season": None,
            "episode": None,
            "is_complete_season": False
        }
        
        # Chercher S01E01 patterns
        for pattern in self.EPISODE_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                result["is_series"] = True
                result["season"] = int(match.group(1))
                result["episode"] = int(match.group(2))
                return result
        
        # Chercher saison seule (dossier complet)
        for pattern in self.SEASON_ONLY_PATTERNS:
            match = re.search(pattern, filename)
            if match:
                result["is_series"] = True
                result["season"] = int(match.group(1))
                result["is_complete_season"] = True
                return result
        
        return result
    
    def format_episode_tag(
        self, 
        season: Optional[int] = None, 
        episode: Optional[int] = None,
        is_complete_season: bool = False,
        is_complete_series: bool = False,
        is_final_episode: bool = False,
        episode_only: bool = False
    ) -> str:
        """Formate le tag de saison/épisode selon les règles La Cale
        
        Formats:
        - S##E## : Episode spécifique (S01E01)
        - S##E##.FiNAL : Episode final
        - E## : Episode seul sans saison (E01)
        - S## : Saison complète (S01)
        - iNTEGRALE ou COMPLETE : Série complète
        """
        if is_complete_series:
            return "iNTEGRALE"
        
        if season is not None and episode is not None:
            tag = f"S{season:02d}E{episode:02d}"
            if is_final_episode:
                tag += ".FiNAL"
            return tag
        
        if episode_only and episode is not None:
            tag = f"E{episode:02d}"
            if is_final_episode:
                tag += ".FiNAL"
            return tag
        
        if season is not None and is_complete_season:
            return f"S{season:02d}"
        
        if season is not None:
            return f"S{season:02d}"
        
        return ""
    
    def detect_resolution(self, media_info: Dict[str, Any]) -> str:
        """Détecte la résolution depuis MediaInfo
        
        Prend en compte les films avec bandes noires (hauteur < 1080 mais largeur = 1920)
        """
        video_tracks = media_info.get("video_tracks", [])
        if not video_tracks:
            return "Unknown"
        
        height = video_tracks[0].get("height", 0)
        width = video_tracks[0].get("width", 0)
        
        # D'abord essayer de matcher par largeur (plus fiable pour les films avec bandes)
        if width >= 3840:
            return "2160p"
        elif width >= 1920:
            return "1080p"
        elif width >= 1280:
            return "720p"
        
        # Fallback sur la hauteur avec seuils ajustés
        for min_height, res_name in self.RESOLUTION_HEIGHT_THRESHOLDS:
            if height >= min_height:
                return res_name
        
        return f"{height}p" if height else "Unknown"
    
    def detect_video_codec(self, media_info: Dict[str, Any]) -> str:
        """Détecte le codec vidéo depuis MediaInfo"""
        video_tracks = media_info.get("video_tracks", [])
        if not video_tracks:
            return "Unknown"
        
        codec = video_tracks[0].get("codec", "")
        
        for codec_key, codec_value in self.VIDEO_CODECS.items():
            if codec_key.lower() in codec.lower():
                return codec_value
        
        return codec or "Unknown"
    
    def detect_audio_codec(self, media_info: Dict[str, Any]) -> str:
        """Détecte le codec audio depuis MediaInfo"""
        audio_tracks = media_info.get("audio_tracks", [])
        if not audio_tracks:
            return "Unknown"
        
        codec = audio_tracks[0].get("codec", "")
        channels = audio_tracks[0].get("channels", "")
        
        detected_codec = codec
        for codec_key, codec_value in self.AUDIO_CODECS.items():
            if codec_key.lower() in codec.lower():
                detected_codec = codec_value
                break
        
        # Ajouter les canaux (5.1, 7.1, etc.)
        if channels:
            if "7.1" in str(channels) or channels == 8:
                detected_codec += ".7.1"
            elif "5.1" in str(channels) or channels == 6:
                detected_codec += ".5.1"
            elif "2.0" in str(channels) or channels == 2:
                detected_codec += ".2.0"
        
        return detected_codec
    
    def detect_audio_languages(self, media_info: Dict[str, Any]) -> str:
        """Détecte les langues audio et retourne le tag approprié
        
        Logique:
        - Si plusieurs langues avec français: MULTi.VFQ (canadien) ou MULTi.TrueFrench (France)
        - Si une seule langue française: VFQ ou TrueFrench selon le type
        - Détection basée sur le titre de la piste audio (vfq, vff, truefrench, quebec, etc.)
        """
        audio_tracks = media_info.get("audio_tracks", [])
        if not audio_tracks:
            return ""
        
        has_french = False
        has_english = False
        has_other = False
        french_type = None  # "VFQ" (canadien) ou "TrueFrench" (France)
        
        for track in audio_tracks:
            lang = (track.get("language") or "").lower()
            title = (track.get("title") or "").lower()
            
            # Détecter le type de français
            if "vfq" in title or "quebec" in title or "québec" in title or "canadien" in title:
                has_french = True
                french_type = "VFQ"
            elif "vff" in title or "truefrench" in title or "true french" in title or "france" in title:
                has_french = True
                french_type = "TrueFrench"
            elif "vfi" in title or "international" in title:
                has_french = True
                french_type = "VFi"
            elif "vf" in title or lang in ["fr", "fra", "fre", "french"]:
                has_french = True
                # Si pas de type spécifique détecté, on met TrueFrench par défaut
                if french_type is None:
                    french_type = "TrueFrench"
            
            # Détecter l'anglais
            if "vo" in title or "english" in title or lang in ["en", "eng", "english"]:
                has_english = True
            
            # Détecter autres langues
            if lang and lang not in ["fr", "fra", "fre", "french", "en", "eng", "english", "und", "zxx"]:
                has_other = True
        
        # Déterminer le tag final
        num_languages = sum([has_french, has_english, has_other])
        
        if num_languages > 1:
            # Multi-langues
            if has_french and french_type:
                return f"MULTi.{french_type}"
            return "MULTi"
        elif has_french and french_type:
            # Une seule langue française
            return french_type
        elif has_english:
            return "ENGLISH"
        
        return ""
    
    def detect_source(self, filename: str) -> str:
        """Détecte la source depuis le nom de fichier
        
        Utilise des word boundaries regex pour éviter les faux positifs
        par substring (ex: 'dvd' dans 'dvdscr').
        """
        filename_lower = filename.lower()
        
        for source_key, source_value in self.SOURCES.items():
            # Les clés avec des points (ex: ".nf.") matchent déjà précisément
            # Pour les autres, utiliser des word boundaries regex
            if '.' in source_key:
                if source_key in filename_lower:
                    return source_value
            else:
                if re.search(r'(?<![a-z])' + re.escape(source_key) + r'(?![a-z])', filename_lower):
                    return source_value
        
        return "Unknown"
    
    def detect_hdr(self, media_info: Dict[str, Any]) -> Optional[str]:
        """Détecte le type HDR depuis MediaInfo"""
        video_tracks = media_info.get("video_tracks", [])
        if not video_tracks:
            return None
        
        video = video_tracks[0]
        hdr_format = (video.get("hdr_format") or "").lower()
        color_primaries = (video.get("color_primaries") or "").lower()
        transfer = (video.get("transfer_characteristics") or "").lower()
        
        # Vérifier Dolby Vision
        if "dolby vision" in hdr_format or "dovi" in hdr_format:
            # Vérifier si HDR10 aussi présent (combo)
            if "hdr10" in hdr_format or "hdr" in transfer:
                return "HDR.DV"
            return "DV"
        
        # Vérifier HDR10+
        if "hdr10+" in hdr_format or "hdr10plus" in hdr_format:
            return "HDR10Plus"
        
        # Vérifier HDR10
        if "hdr10" in hdr_format or "hdr" in hdr_format:
            return "HDR"
        
        # Vérifier via les caractéristiques de transfert
        if "pq" in transfer or "smpte 2084" in transfer:
            return "HDR"
        if "hlg" in transfer:
            return "HLG"
        
        # Vérifier BT.2020
        if "bt.2020" in color_primaries or "rec.2020" in color_primaries:
            return "HDR"
        
        return None
    
    def detect_platform(self, filename: str) -> Optional[str]:
        """Détecte la plateforme de streaming depuis le nom de fichier
        
        Utilise des word boundaries regex pour éviter les faux positifs
        par substring (ex: 'max' dans 'maximum', 'prime' dans 'primed').
        """
        filename_lower = filename.lower()
        
        for platform_key, platform_value in self.PLATFORMS.items():
            # Les clés avec des points (ex: ".nf.") matchent déjà précisément
            if '.' in platform_key:
                if platform_key in filename_lower:
                    return platform_value
            else:
                if re.search(r'(?<![a-z])' + re.escape(platform_key) + r'(?![a-z])', filename_lower):
                    return platform_value
        
        return None
    
    def detect_audio_spec(self, media_info: Dict[str, Any]) -> Optional[str]:
        """Détecte les spécifications audio (Atmos, etc.)"""
        audio_tracks = media_info.get("audio_tracks", [])
        if not audio_tracks:
            return None
        
        for track in audio_tracks:
            codec = (track.get("codec") or "").lower()
            title = (track.get("title") or "").lower()
            
            if "atmos" in codec or "atmos" in title:
                return "Atmos"
            if "auro" in codec or "auro3d" in title:
                return "Auro3D"
        
        return None
    
    def detect_language_info(self, media_info: Dict[str, Any]) -> Optional[str]:
        """Détecte les infos de langue (VFF, VFQ, etc.)"""
        audio_tracks = media_info.get("audio_tracks", [])
        if not audio_tracks:
            return None
        
        has_vff = False
        has_vfq = False
        has_ad = False
        
        for track in audio_tracks:
            title = (track.get("title") or "").lower()
            
            if "vff" in title or "truefrench" in title or "true french" in title:
                has_vff = True
            if "vfq" in title or "quebec" in title or "québec" in title:
                has_vfq = True
            if "audio description" in title or "ad " in title:
                has_ad = True
        
        parts = []
        if has_vff and has_vfq:
            parts.append("VF2")
        elif has_vff:
            parts.append("VFF")
        elif has_vfq:
            parts.append("VFQ")
        
        if has_ad:
            parts.append("WiTH.AD")
        
        return ".".join(parts) if parts else None
    
    def is_sd_resolution(self, media_info: Dict[str, Any]) -> bool:
        """Vérifie si la résolution est SD (pas de tag résolution)"""
        video_tracks = media_info.get("video_tracks", [])
        if not video_tracks:
            return True
        
        height = video_tracks[0].get("height", 0)
        return height < 720
    
    def detect_group(self, filename: str) -> Optional[str]:
        """Détecte le nom du groupe depuis le nom de fichier
        
        Le groupe est généralement après le dernier tiret dans le nom.
        Ex: Gladiator.II.2024.FRENCH.1080p.BluRay.x264-PRODUX -> PRODUX
        """
        # Supprimer l'extension
        name = Path(filename).stem if '.' in filename else filename
        
        # Suffixes qui ne sont PAS des groupes (sources, codecs, etc.)
        non_group_suffixes = {
            "dl", "rip", "hd", "ma", "hr", "x", "plus",  # Parties de WEB-DL, WEBRip, DTS-HD MA, etc.
            "264", "265", "266",  # Parties de x264, x265, H264, etc.
            "ac3", "aac", "dts", "flac", "mp3",  # Codecs audio
            "1080p", "720p", "2160p", "480p", "576p",  # Résolutions
            "french", "multi", "vostfr", "vff", "vfq",  # Langues
        }
        
        # Chercher le pattern -GROUP à la fin
        match = re.search(r'-([A-Za-z0-9]+)$', name)
        if match:
            potential_group = match.group(1)
            # Vérifier que ce n'est pas un suffixe connu
            if potential_group.lower() not in non_group_suffixes:
                return potential_group
        
        return None
    
    def generate_release_name(
        self,
        title: str,
        year: Optional[str],
        media_info: Dict[str, Any],
        source: Optional[str] = None,
        group: Optional[str] = None,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        is_complete_season: bool = False,
        is_complete_series: bool = False,
        is_final_episode: bool = False,
        episode_only: bool = False,
        content_type: str = "movie",
        edition: Optional[str] = None,
        info: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """Génère le nom de release selon la nomenclature La Cale
        
        Structure Films:
        - SD: Titre.Année.Langue.Source.CodecVidéo-Team
        - HD: Titre.Année.Langue.Résolution.Source.CodecVidéo-Team
        - HDR: Titre.Année.Langue.Dynamic.Résolution.Source.CodecVidéo-Team
        
        Structure Séries:
        - SD: Titre.SaisonEpisode.Langue.Source.CodecVidéo-Team
        - HD: Titre.SaisonEpisode.Langue.Résolution.Source.CodecVidéo-Team
        - Saison: Titre.S##.Langue.Source.CodecVidéo-Team
        - Intégrale: Titre.iNTEGRALE.Langue.Source.CodecVidéo-Team
        
        Le groupe est détecté automatiquement depuis le nom de fichier source.
        """
        
        parts = []
        filename = media_info.get("file_name", "")
        
        # Détecter le groupe depuis le fichier source si non fourni
        if not group:
            group = self.detect_group(filename) or "NOTAG"
        is_sd = self.is_sd_resolution(media_info)
        
        # 1. Titre (nettoyé selon les règles)
        clean_title = self.sanitize_title(title)
        parts.append(clean_title)
        
        # 2. Pour les séries: Tag S01E01 / Pour les films: Année
        if content_type == "tv":
            episode_tag = self.format_episode_tag(
                season=season,
                episode=episode,
                is_complete_season=is_complete_season,
                is_complete_series=is_complete_series,
                is_final_episode=is_final_episode,
                episode_only=episode_only
            )
            if episode_tag:
                parts.append(episode_tag)
            # Année optionnelle pour les séries
            if year:
                parts.append(year)
        elif year:
            parts.append(year)
        
        # 3. Info (REPACK, PROPER, CUSTOM) - facultatif
        if info:
            parts.append(info.upper())
        
        # 4. Edition (DC, EXTENDED, REMASTERED, etc.) - facultatif
        if edition:
            parts.append(edition)
        
        # 5. Langue principale (manuelle ou auto-détectée)
        if language:
            # Langue fournie manuellement - utiliser telle quelle
            parts.append(language)
        else:
            # Auto-détection de la langue
            languages = self.detect_audio_languages(media_info)
            if languages:
                parts.append(languages)
        
        # 7. Dynamic (HDR, DV, etc.) - seulement si présent
        hdr = self.detect_hdr(media_info)
        if hdr:
            parts.append(hdr)
        
        # 8. Résolution (sauf pour SD)
        if not is_sd:
            resolution = self.detect_resolution(media_info)
            if resolution and resolution != "Unknown":
                parts.append(resolution)
        
        # 9. Plateforme (pour WEB) - facultatif
        platform = self.detect_platform(filename)
        if platform:
            parts.append(platform)
        
        # 10. Source
        if source:
            parts.append(source)
        else:
            detected_source = self.detect_source(filename)
            if detected_source != "Unknown":
                parts.append(detected_source)
        
        # 11. Codec Vidéo
        video_codec = self.detect_video_codec(media_info)
        if video_codec and video_codec != "Unknown":
            parts.append(video_codec)
        
        # 12. Groupe (avec tiret)
        release_name = ".".join(parts) + f"-{group}"
        
        return release_name
    
    def rename_file(
        self,
        source_path: str,
        new_name: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Renomme un fichier"""
        source = Path(source_path)
        
        if not source.exists():
            return {"success": False, "error": "Fichier source non trouvé"}
        
        # Conserver l'extension
        extension = source.suffix
        new_filename = f"{new_name}{extension}"
        new_path = source.parent / new_filename
        
        if dry_run:
            return {
                "success": True,
                "old_path": str(source),
                "new_path": str(new_path),
                "old_name": source.name,
                "new_name": new_filename,
                "dry_run": True
            }
        
        try:
            shutil.move(str(source), str(new_path))
            return {
                "success": True,
                "old_path": str(source),
                "new_path": str(new_path),
                "old_name": source.name,
                "new_name": new_filename
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


naming_service = NamingService()
