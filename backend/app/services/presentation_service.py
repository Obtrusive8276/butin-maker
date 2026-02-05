from pathlib import Path
from typing import Optional
from ..config import settings


class PresentationService:
    
    DEFAULT_TEMPLATE = """[center]
[img]{poster_url}[/img]

[size=6][color=#eab308][b]{title}[/b][/color][/size]

[b]Note :[/b] {rating}/10
[b]Genre :[/b] {genre}

[quote]{synopsis}[/quote]

[color=#eab308][b]--- DÉTAILS ---[/b][/color]

[b]Qualité :[/b] {quality}
[b]Format :[/b] {format}
[b]Codec Vidéo :[/b] {video_codec}
[b]Codec Audio :[/b] {audio_codec}
[b]Langues :[/b] {languages}
[b]Sous-titres :[/b] {subtitles}
[b]Taille :[/b] {size}


[i]Généré par La Cale Uploader[/i]
[/center]"""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        template_path = settings.base_path / "templates" / "presentation_template.txt"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        return self.DEFAULT_TEMPLATE
    
    def generate_presentation(self, data: dict) -> str:
        template = self.template
        
        replacements = {
            "{poster_url}": data.get("poster_url", ""),
            "{title}": data.get("title", "Titre"),
            "{rating}": str(data.get("rating", "N/A")),
            "{genre}": data.get("genre", ""),
            "{synopsis}": data.get("synopsis", ""),
            "{quality}": data.get("quality", ""),
            "{format}": data.get("format", ""),
            "{video_codec}": data.get("video_codec", ""),
            "{audio_codec}": data.get("audio_codec", ""),
            "{languages}": data.get("languages", ""),
            "{subtitles}": data.get("subtitles", "Aucun"),
            "{size}": data.get("size", ""),
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))
        
        return result
    
    def get_template(self) -> str:
        return self.template
    
    def save_template(self, template: str) -> bool:
        try:
            template_dir = settings.base_path / "templates"
            template_dir.mkdir(parents=True, exist_ok=True)
            
            template_path = template_dir / "presentation_template.txt"
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(template)
            
            self.template = template
            return True
        except Exception as e:
            print(f"Erreur sauvegarde template: {e}")
            return False


presentation_service = PresentationService()
