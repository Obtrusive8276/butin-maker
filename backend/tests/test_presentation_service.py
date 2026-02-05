"""Tests unitaires pour le service de présentation"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.presentation_service import PresentationService


class TestPresentationService:
    """Tests pour PresentationService"""
    
    def setup_method(self):
        self.service = PresentationService()
    
    def test_generate_presentation_basic(self):
        """Test génération basique de présentation"""
        data = {
            "title": "Mon Film",
            "rating": 8.5,
            "genre": "Action",
            "synopsis": "Un film d'action.",
            "quality": "1080p",
            "format": "MKV",
            "video_codec": "H264",
            "audio_codec": "AC3",
            "languages": "French",
            "subtitles": "Aucun",
            "size": "4.5 GB",
            "poster_url": "https://example.com/poster.jpg"
        }
        
        result = self.service.generate_presentation(data)
        
        assert "Mon Film" in result
        assert "8.5" in result
        assert "Action" in result
        assert "1080p" in result
        assert "MKV" in result
    
    def test_generate_presentation_missing_fields(self):
        """Test génération avec champs manquants"""
        data = {"title": "Film Test"}
        
        result = self.service.generate_presentation(data)
        
        assert "Film Test" in result
        assert "{title}" not in result
    
    def test_generate_presentation_empty_data(self):
        """Test génération avec données vides"""
        data = {}
        
        result = self.service.generate_presentation(data)
        
        # Doit retourner le template avec valeurs par défaut
        assert "Titre" in result or "{title}" not in result
    
    def test_get_template(self):
        """Test récupération du template"""
        template = self.service.get_template()
        
        assert isinstance(template, str)
        assert len(template) > 0
        assert "{title}" in template or "[b]" in template
    
    def test_template_has_required_placeholders(self):
        """Test que le template contient les placeholders requis"""
        template = self.service.get_template()
        
        required_placeholders = [
            "{title}", "{rating}", "{genre}", "{synopsis}",
            "{quality}", "{format}", "{video_codec}", "{audio_codec}",
            "{languages}", "{subtitles}", "{size}"
        ]
        
        for placeholder in required_placeholders:
            assert placeholder in template, f"Placeholder manquant: {placeholder}"
    
    def test_generate_presentation_bbcode_format(self):
        """Test que la présentation contient du BBCode valide"""
        data = {"title": "Test", "rating": 7}
        
        result = self.service.generate_presentation(data)
        
        # Vérifier la présence de balises BBCode
        assert "[" in result and "]" in result
        # Vérifier que les balises sont fermées
        assert result.count("[b]") == result.count("[/b]")
        assert result.count("[center]") == result.count("[/center]")


class TestPresentationServiceTemplate:
    """Tests pour la gestion du template"""
    
    def setup_method(self):
        self.service = PresentationService()
    
    def test_default_template_exists(self):
        """Test que le template par défaut existe"""
        assert hasattr(self.service, 'DEFAULT_TEMPLATE')
        assert len(self.service.DEFAULT_TEMPLATE) > 0
    
    def test_default_template_valid_bbcode(self):
        """Test que le template par défaut a un BBCode valide"""
        template = self.service.DEFAULT_TEMPLATE
        
        # Vérifier les balises ouvrantes/fermantes
        assert template.count("[center]") == template.count("[/center]")
        assert template.count("[b]") == template.count("[/b]")
        assert template.count("[quote]") == template.count("[/quote]")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
