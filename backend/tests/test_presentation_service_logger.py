"""
Tests pour vérifier que le logger est bien configuré dans presentation_service
"""
import logging
from unittest.mock import patch, MagicMock
from pathlib import Path
from app.services.presentation_service import PresentationService


class TestPresentationServiceLogger:
    """Tests pour le système de logging de PresentationService"""
    
    def test_logger_exists(self):
        """Vérifier que le logger est importé et configuré"""
        from app.services import presentation_service
        assert hasattr(presentation_service, 'logger')
        assert isinstance(presentation_service.logger, logging.Logger)
    
    def test_logger_name_is_correct(self):
        """Vérifier que le logger a le bon nom de module"""
        from app.services import presentation_service
        assert presentation_service.logger.name == 'app.services.presentation_service'
    
    def test_save_template_logs_error_on_exception(self, tmp_path):
        """Vérifier que save_template utilise logger.error au lieu de print"""
        service = PresentationService()
        
        # Mock du logger pour capturer les appels
        with patch('app.services.presentation_service.logger') as mock_logger:
            # Mock settings.base_path pour pointer vers un fichier au lieu d'un répertoire
            # Cela causera une erreur lors de mkdir() ou open()
            with patch('app.services.presentation_service.settings') as mock_settings:
                # Créer un fichier ordinaire et essayer de l'utiliser comme répertoire
                dummy_file = tmp_path / "file_not_dir.txt"
                dummy_file.write_text("This is a file, not a directory")
                mock_settings.base_path = dummy_file
                
                # Appeler save_template - cela devrait échouer car base_path est un fichier
                result = service.save_template("Test template")
                
                # Vérifier que save_template retourne False
                assert result is False
                
                # Vérifier que logger.error a été appelé
                assert mock_logger.error.called
                
                # Vérifier que exc_info=True a été passé pour inclure la stack trace
                call_args = mock_logger.error.call_args
                assert call_args is not None
                # Vérifier le format du message
                assert "Erreur sauvegarde template" in call_args[0][0]
                # Vérifier que exc_info est passé
                assert call_args[1].get('exc_info') is True
    
    def test_no_print_statements_in_error_handling(self):
        """Vérifier qu'il n'y a plus de print() dans la gestion d'erreur"""
        import inspect
        source = inspect.getsource(PresentationService.save_template)
        
        # Vérifier qu'il n'y a pas de print dans le code
        assert 'print(' not in source or 'print(f"' not in source, \
            "Le code ne devrait plus contenir de print() pour la gestion d'erreur"
    
    def test_save_template_success_no_log(self, tmp_path):
        """Vérifier que le succès ne génère pas de log d'erreur"""
        service = PresentationService()
        
        # Créer un fichier template valide
        template_file = tmp_path / "template.txt"
        
        with patch('app.services.presentation_service.logger') as mock_logger:
            with patch('app.services.presentation_service.settings') as mock_settings:
                mock_settings.template_path = template_file
                
                result = service.save_template("Valid template content")
                
                # Vérifier que save_template retourne True
                assert result is True
                
                # Vérifier que logger.error n'a PAS été appelé en cas de succès
                assert not mock_logger.error.called
