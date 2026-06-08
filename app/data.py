import json
import random
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).parent.parent / "data" / "recipes.json"

def _load():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"recipes.json tidak ditemukan di {DATA_PATH}\n"
            "Salin file recipes.json ke folder data/ terlebih dahulu."
        )
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

RECIPES: list[dict] = _load()


def get_random(n: int = 6) -> list[dict]:
    return random.sample(RECIPES, min(n, len(RECIPES)))


def get_by_id(recipe_id: int) -> Optional[dict]:
    for r in RECIPES:
        if r["id"] == recipe_id:
            return r
    return None


def search(query: str, limit: int = 24) -> list[dict]:
    q = query.lower().strip()
    if not q:
        return []

    title_hits = []
    ingredient_hits = []

    for r in RECIPES:
        if q in r["title"].lower():
            title_hits.append(r)
        elif any(q in ing.lower() for ing in r["ingredients"]):
            ingredient_hits.append(r)

    return (title_hits + ingredient_hits)[:limit]


def get_stats() -> dict:
    return {
        "total": len(RECIPES),
        "avg_ingredients": round(
            sum(r["num_ingredients"] for r in RECIPES) / len(RECIPES), 1
        ),
        "avg_steps": round(
            sum(r["num_steps"] for r in RECIPES) / len(RECIPES), 1
        ),
    }
