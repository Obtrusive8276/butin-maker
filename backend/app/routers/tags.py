from fastapi import APIRouter
from pathlib import Path
import json
from ..config import settings

router = APIRouter(prefix="/tags", tags=["tags"])


def load_tags_data():
    # Priorité: /app/data/tags_data.json (volume Docker)
    tags_file = Path("/app/data/tags_data.json")
    if not tags_file.exists():
        # Fallback: à côté du code source
        tags_file = settings.base_path.parent / "tags_data.json"
    if not tags_file.exists():
        tags_file = settings.data_path / "tags_data.json"
    
    if tags_file.exists():
        with open(tags_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"quaiprincipalcategories": []}


@router.get("/")
async def get_all_tags():
    data = load_tags_data()
    return data


@router.get("/categories")
async def get_categories():
    data = load_tags_data()
    categories = data.get("quaiprincipalcategories", [])
    return [{"name": cat["name"], "slug": cat["slug"]} for cat in categories]


@router.get("/category/{slug}")
async def get_category(slug: str):
    data = load_tags_data()
    categories = data.get("quaiprincipalcategories", [])
    
    for cat in categories:
        if cat["slug"] == slug:
            return cat
    
    return {"error": "Catégorie non trouvée"}


@router.get("/subcategories/{category_slug}")
async def get_subcategories(category_slug: str):
    data = load_tags_data()
    categories = data.get("quaiprincipalcategories", [])
    
    for cat in categories:
        if cat["slug"] == category_slug:
            subcats = cat.get("emplacementsouscategorie", [])
            if subcats:
                return [{"name": sub["name"], "slug": sub["slug"]} for sub in subcats]
            return []
    
    return []
