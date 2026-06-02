import random as rnd
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import data

app = FastAPI(title="Masak Bareng Gue")

BASE_DIR = Path(__file__).parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR.parent / "static"),
    name="static",
)
templates = Jinja2Templates(directory=BASE_DIR / "templates")

_emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\u200d"                  # zero width joiner
    "\uFE0F"                  # variation selector
    "\u2763-\u2764"           # heart symbols
    "]+",
    flags=re.UNICODE,
)

templates.env.filters["strip_emoji"] = lambda s: _emoji_pattern.sub("", s).strip()


# ── HTML routes ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured": data.get_random(6),
        "stats": data.get_stats(),
    })


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = ""):
    results = data.search(q) if q.strip() else []
    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q,
        "results": results,
    })


@app.get("/recipe/{recipe_id}", response_class=HTMLResponse)
async def recipe_detail(request: Request, recipe_id: int):
    recipe = data.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Resep tidak ditemukan")
    return templates.TemplateResponse("recipe.html", {
        "request": request,
        "recipe": recipe,
    })


# ── JSON API (untuk testing & future use) ────────────────────────────────────

@app.get("/api/random")
async def api_random():
    return rnd.choice(data.RECIPES)


@app.get("/api/search")
async def api_search(q: str = ""):
    return data.search(q)


@app.get("/api/recipe/{recipe_id}")
async def api_recipe(recipe_id: int):
    recipe = data.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Resep tidak ditemukan")
    return recipe


@app.get("/api/stats")
async def api_stats():
    return data.get_stats()
