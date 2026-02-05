"""
Test unitaire pour reproduire le bug de détection MULTi
Exécutez ce script pour vérifier que la détection fonctionne correctement.
"""

# Copiez-collez simplement la méthode detect_audio_languages ici pour tester
def detect_audio_languages(media_info):
    """Détecte les langues audio et retourne le tag approprié"""
    audio_tracks = media_info.get("audio_tracks", [])
    if not audio_tracks:
        return ""
    
    has_french = False
    has_english = False
    has_other = False
    french_type = None
    
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


# Test 1: The Onion Movie (French + English sans tags VFF/VFQ)
print("=" * 60)
print("Test 1: The Onion Movie (French + English)")
print("=" * 60)
media_info_1 = {
    "audio_tracks": [
        {"language": "fr", "title": "Stereo"},
        {"language": "en", "title": "Surround"}
    ]
}
result_1 = detect_audio_languages(media_info_1)
expected_1 = "MULTi.TrueFrench"
print(f"Pistes audio: {media_info_1['audio_tracks']}")
print(f"Résultat: {result_1}")
print(f"Attendu: {expected_1}")
print(f"✅ Test réussi!" if result_1 == expected_1 else f"❌ Test échoué!")
print()

# Test 2: Multi avec VFQ
print("=" * 60)
print("Test 2: Multi avec VFQ (FR Canada + EN)")
print("=" * 60)
media_info_2 = {
    "audio_tracks": [
        {"language": "fr", "title": "VFQ"},
        {"language": "en", "title": "English"}
    ]
}
result_2 = detect_audio_languages(media_info_2)
expected_2 = "MULTi.VFQ"
print(f"Pistes audio: {media_info_2['audio_tracks']}")
print(f"Résultat: {result_2}")
print(f"Attendu: {expected_2}")
print(f"✅ Test réussi!" if result_2 == expected_2 else f"❌ Test échoué!")
print()

# Test 3: French uniquement
print("=" * 60)
print("Test 3: French uniquement (pas de MULTi)")
print("=" * 60)
media_info_3 = {
    "audio_tracks": [
        {"language": "fr", "title": "French"}
    ]
}
result_3 = detect_audio_languages(media_info_3)
expected_3 = "TrueFrench"
print(f"Pistes audio: {media_info_3['audio_tracks']}")
print(f"Résultat: {result_3}")
print(f"Attendu: {expected_3}")
print(f"✅ Test réussi!" if result_3 == expected_3 else f"❌ Test échoué!")
print()

# Test 4: Trois langues
print("=" * 60)
print("Test 4: Trois langues (FR + EN + ES)")
print("=" * 60)
media_info_4 = {
    "audio_tracks": [
        {"language": "fr", "title": "French"},
        {"language": "en", "title": "English"},
        {"language": "es", "title": "Spanish"}
    ]
}
result_4 = detect_audio_languages(media_info_4)
expected_4 = "MULTi.TrueFrench"
print(f"Pistes audio: {media_info_4['audio_tracks']}")
print(f"Résultat: {result_4}")
print(f"Attendu: {expected_4}")
print(f"✅ Test réussi!" if result_4 == expected_4 else f"❌ Test échoué!")
print()

# Résumé
print("=" * 60)
print("RÉSUMÉ")
print("=" * 60)
tests = [
    (result_1 == expected_1, "The Onion Movie (FR+EN)"),
    (result_2 == expected_2, "Multi VFQ (FR+EN)"),
    (result_3 == expected_3, "French only"),
    (result_4 == expected_4, "Three languages (FR+EN+ES)"),
]
passed = sum(1 for t, _ in tests if t)
total = len(tests)
print(f"Tests réussis: {passed}/{total}")
if passed == total:
    print("🎉 Tous les tests passent! La logique de détection est correcte.")
else:
    print("⚠️  Certains tests ont échoué.")
