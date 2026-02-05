from fastapi import APIRouter, Query
from typing import Optional
from ..services.tmdb_service import tmdb_service
from ..services.naming_service import naming_service

router = APIRouter(prefix="/tmdb", tags=["tmdb"])


@router.get("/status")
async def get_tmdb_status():
    """Vérifie si la clé API TMDB est configurée."""
    has_key = tmdb_service.has_api_key()
    return {
        "configured": has_key,
        "message": "Clé API TMDB configurée" if has_key else "Aucune clé API TMDB configurée. Veuillez la renseigner dans les paramètres."
    }


@router.get("/search")
async def search(
    query: str = Query(..., description="Terme de recherche"),
    type: Optional[str] = Query(None, description="Type: movie, tv, ou null pour les deux")
):
    """Recherche sur TMDB (films et séries)"""
    if type == "movie":
        results = await tmdb_service.search_movie(query)
    elif type == "tv":
        results = await tmdb_service.search_tv(query)
    else:
        results = await tmdb_service.search_multi(query)
    
    return {"results": results}


@router.get("/movie/{movie_id}")
async def get_movie(movie_id: int):
    """Récupère les détails d'un film"""
    details = await tmdb_service.get_movie_details(movie_id)
    if not details:
        return {"error": "Film non trouvé"}
    return details


@router.get("/tv/{tv_id}")
async def get_tv(tv_id: int):
    """Récupère les détails d'une série"""
    details = await tmdb_service.get_tv_details(tv_id)
    if not details:
        return {"error": "Série non trouvée"}
    return details


@router.post("/generate-name")
async def generate_release_name(
    title: str = Query(...),
    year: Optional[str] = Query(None),
    media_info: dict = None,
    source: Optional[str] = Query(None),
    group: Optional[str] = Query(None, description="Groupe/Team (détecté auto si non fourni)"),
    content_type: str = Query("movie"),
    season: Optional[int] = Query(None),
    episode: Optional[int] = Query(None),
    is_complete_season: bool = Query(False),
    is_complete_series: bool = Query(False),
    is_final_episode: bool = Query(False),
    episode_only: bool = Query(False),
    edition: Optional[str] = Query(None),
    info: Optional[str] = Query(None),
    language: Optional[str] = Query(None, description="Langue manuelle (ex: MULTi.TrueFrench, VFQ)")
):
    """Génère un nom de release selon la nomenclature La Cale
    
    Structure Films:
    - SD: Titre.Année.Langue.Source.CodecVidéo-Team
    - HD: Titre.Année.Langue.Résolution.Source.CodecVidéo-Team
    
    Structure Séries:
    - Episode: Titre.S##E##.Langue.Résolution.Source.CodecVidéo-Team
    - Saison: Titre.S##.Langue.Résolution.Source.CodecVidéo-Team
    - Intégrale: Titre.iNTEGRALE.Langue.Résolution.Source.CodecVidéo-Team
    """
    if not media_info:
        media_info = {}
    
    # Debug log
    print(f"[DEBUG] Generate release name:")
    print(f"  - title: {title}")
    print(f"  - language param: {language}")
    print(f"  - audio_tracks: {media_info.get('audio_tracks', [])}")
    
    release_name = naming_service.generate_release_name(
        title=title,
        year=year,
        media_info=media_info,
        source=source,
        group=group,
        season=season,
        episode=episode,
        is_complete_season=is_complete_season,
        is_complete_series=is_complete_series,
        is_final_episode=is_final_episode,
        episode_only=episode_only,
        content_type=content_type,
        edition=edition,
        info=info,
        language=language
    )
    
    print(f"  - generated: {release_name}")
    
    return {"release_name": release_name}


@router.get("/detect-episode")
async def detect_episode(filename: str = Query(..., description="Nom du fichier ou dossier")):
    """Détecte les informations de saison/épisode depuis un nom de fichier"""
    info = naming_service.detect_episode_info(filename)
    return info


@router.get("/extract-title")
async def extract_title(filename: str = Query(..., description="Nom du fichier")):
    """Extrait le titre du film depuis le nom de fichier en supprimant tous les tags"""
    clean_title = naming_service.extract_movie_title_from_filename(filename)
    # Remplacer les points par des espaces pour la recherche TMDB
    search_title = clean_title.replace('.', ' ')
    return {"original_filename": filename, "extracted_title": search_title}


@router.get("/search-from-filename")
async def search_from_filename(
    filename: str = Query(..., description="Nom du fichier"),
    type: Optional[str] = Query("movie", description="Type: movie ou tv")
):
    """Extrait le titre depuis le nom de fichier et fait une recherche TMDB"""
    # Extraire le titre propre
    clean_title = naming_service.extract_movie_title_from_filename(filename)
    
    # Faire la recherche TMDB
    if type == "movie":
        results = await tmdb_service.search_movie(clean_title)
    else:
        results = await tmdb_service.search_tv(clean_title)
    
    return {
        "original_filename": filename,
        "extracted_title": clean_title,
        "results": results
    }


@router.post("/rename")
async def rename_file(
    source_path: str,
    new_name: str,
    dry_run: bool = True
):
    """Renomme un fichier (dry_run=true pour prévisualiser)"""
    result = naming_service.rename_file(
        source_path=source_path,
        new_name=new_name,
        dry_run=dry_run
    )
    return result
