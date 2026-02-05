from pymediainfo import MediaInfo as MI
from pathlib import Path
from typing import Optional, List, Tuple
from ..models.media import MediaInfo, VideoTrack, AudioTrack, SubtitleTrack, NFOData
from ..config import settings


class MediaInfoService:
    
    def analyze_file(self, file_path: str) -> Optional[MediaInfo]:
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            media_info = MI.parse(file_path)
            
            video_tracks = []
            audio_tracks = []
            subtitle_tracks = []
            container = None
            duration = None
            
            def safe_duration(d):
                """Convertit la durée en secondes de manière sécurisée"""
                if d is None:
                    return None
                try:
                    return float(d) / 1000
                except (TypeError, ValueError):
                    return None
            
            for track in media_info.tracks:
                if track.track_type == "General":
                    container = track.format
                    duration = safe_duration(track.duration)
                
                elif track.track_type == "Video":
                    video_tracks.append(VideoTrack(
                        codec=track.format,
                        width=track.width,
                        height=track.height,
                        bitrate=track.bit_rate,
                        framerate=float(track.frame_rate) if track.frame_rate else None,
                        duration=safe_duration(track.duration),
                        hdr=track.hdr_format if hasattr(track, 'hdr_format') else None
                    ))
                
                elif track.track_type == "Audio":
                    audio_tracks.append(AudioTrack(
                        codec=track.format,
                        channels=track.channel_s,
                        bitrate=track.bit_rate,
                        language=track.language,
                        title=track.title
                    ))
                
                elif track.track_type == "Text":
                    subtitle_tracks.append(SubtitleTrack(
                        codec=track.format,
                        language=track.language,
                        title=track.title,
                        forced=bool(track.forced) if hasattr(track, 'forced') else False
                    ))
            
            return MediaInfo(
                file_path=file_path,
                file_name=path.name,
                file_size=path.stat().st_size,
                container=container,
                duration=duration,
                video_tracks=video_tracks,
                audio_tracks=audio_tracks,
                subtitle_tracks=subtitle_tracks
            )
        except Exception as e:
            print(f"Erreur MediaInfo: {e}")
            return None
    
    def generate_nfo(self, file_path: str, release_name: str = None) -> Tuple[bool, Optional[NFOData]]:
        try:
            media_info = MI.parse(file_path)
            
            text_output = MI.parse(file_path, output="STRING", full=False)
            
            path = Path(file_path)
            
            # Déterminer le nom à afficher dans le NFO
            if release_name:
                # Utiliser le release_name avec l'extension du fichier original
                display_name = release_name + path.suffix
                nfo_filename = release_name + ".nfo"
            else:
                display_name = path.name
                nfo_filename = path.stem + ".nfo"
            
            # Remplacer le chemin complet par le nom de release dans le contenu
            # Le NFO contient "Complete name : /chemin/complet/fichier.mkv"
            # On veut "Complete name : ReleaseName.mkv"
            text_output = text_output.replace(file_path, display_name)
            # Aussi remplacer les chemins Windows potentiels
            text_output = text_output.replace(file_path.replace('/', '\\'), display_name)
            
            nfo_path = settings.output_path / nfo_filename
            
            with open(nfo_path, "w", encoding="utf-8") as f:
                f.write(text_output)
            
            return True, NFOData(
                file_path=str(nfo_path),
                content=text_output
            )
        except Exception as e:
            print(f"Erreur génération NFO: {e}")
            return False, None
    
    def get_raw_mediainfo(self, file_path: str) -> Optional[str]:
        try:
            return MI.parse(file_path, output="STRING", full=True)
        except Exception as e:
            return None


mediainfo_service = MediaInfoService()
