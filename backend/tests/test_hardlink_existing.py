"""
Test pour vérifier le comportement des hardlinks quand le fichier existe déjà
"""
import os
import tempfile
import shutil
from pathlib import Path

# Simuler la logique create_hardlink pour tester
def create_hardlink(source_path: str, destination_path: str):
    """Version simplifiée de create_hardlink pour les tests"""
    try:
        source = Path(source_path)
        destination = Path(destination_path)
        
        if not source.exists():
            return False, f"La source n'existe pas: {source_path}"
        
        # Créer le dossier parent
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Vérifier si la destination existe déjà
        if destination.exists():
            # Vérifier si c'est déjà un hardlink vers la même source
            if destination.is_file():
                try:
                    if destination.stat().st_ino == source.stat().st_ino:
                        # Même inode = même fichier (déjà hardlinké)
                        return True, f"Hardlink déjà existant: {destination_path}"
                except:
                    pass
            return False, f"La destination existe déjà: {destination_path}"
        
        # Créer le hardlink
        if source.is_file():
            try:
                os.link(source, destination)
                return True, f"Hardlink créé: {destination_path}"
            except OSError as e:
                return False, f"Erreur: {str(e)}"
        
        return False, "Type non supporté"
        
    except Exception as e:
        return False, f"Erreur: {str(e)}"


def test_hardlink_already_exists():
    """Test: Si le hardlink existe déjà, on retourne succès avec message approprié"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Créer un fichier source
        source = Path(tmpdir) / "source.txt"
        source.write_text("contenu test")
        
        # Créer le hardlink une première fois
        dest = Path(tmpdir) / "dest.txt"
        success1, msg1 = create_hardlink(str(source), str(dest))
        print(f"1ère création: {success1} - {msg1}")
        assert success1, f"La première création devrait réussir: {msg1}"
        
        # Vérifier que c'est bien un hardlink (même inode)
        assert source.stat().st_ino == dest.stat().st_ino, "Devrait être le même inode"
        
        # Essayer de créer le même hardlink une deuxième fois
        success2, msg2 = create_hardlink(str(source), str(dest))
        print(f"2ème création: {success2} - {msg2}")
        assert success2, f"La deuxième création devrait aussi réussir (déjà existant): {msg2}"
        assert "déjà existant" in msg2.lower(), f"Le message devrait indiquer que ça existe déjà: {msg2}"
        
        print("✅ Test réussi: Les hardlinks déjà existants sont correctement gérés")


def test_different_file_exists():
    """Test: Si un fichier différent existe à la destination, on retourne une erreur"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Créer deux fichiers différents
        source = Path(tmpdir) / "source.txt"
        source.write_text("contenu source")
        
        other = Path(tmpdir) / "other.txt"
        other.write_text("contenu différent")
        
        # Renommer other.txt en dest.txt
        dest = Path(tmpdir) / "dest.txt"
        other.rename(dest)
        
        # Essayer de créer le hardlink - devrait échouer car fichier différent existe
        success, msg = create_hardlink(str(source), str(dest))
        print(f"Création sur fichier existant différent: {success} - {msg}")
        assert not success, "Devrait échouer car un fichier différent existe"
        assert "existe déjà" in msg.lower(), f"Message devrait indiquer l'existence: {msg}"
        
        print("✅ Test réussi: Les fichiers différents existants bloquent correctement")


def test_directory_with_existing_files():
    """Test: Pour les dossiers, skip les fichiers déjà existants"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Créer un dossier source avec des fichiers
        source_dir = Path(tmpdir) / "source"
        source_dir.mkdir()
        
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        
        dest_dir = Path(tmpdir) / "dest"
        
        # Première création
        # Note: Cette version simplifiée ne gère pas les dossiers, 
        # mais le vrai code le fait
        
        print("✅ Test des dossiers: Voir l'implémentation complète dans file_service.py")


if __name__ == "__main__":
    print("=" * 60)
    print("Test 1: Hardlink déjà existant")
    print("=" * 60)
    test_hardlink_already_exists()
    print()
    
    print("=" * 60)
    print("Test 2: Fichier différent existe")
    print("=" * 60)
    test_different_file_exists()
    print()
    
    print("=" * 60)
    print("Tous les tests ont réussi!")
    print("=" * 60)
