"""
Test suite untuk Masak Bareng Gue API.

Jalankan: pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Homepage ──────────────────────────────────────────────────────────────────

class TestHomepage:
    def test_returns_200(self):
        res = client.get("/")
        assert res.status_code == 200

    def test_contains_recipe_content(self):
        res = client.get("/")
        assert "resep" in res.text.lower()

    def test_contains_search_form(self):
        res = client.get("/")
        assert "<form" in res.text


# ── Search page ───────────────────────────────────────────────────────────────

class TestSearchPage:
    def test_search_page_returns_200(self):
        res = client.get("/search?q=ayam")
        assert res.status_code == 200

    def test_search_shows_query(self):
        res = client.get("/search?q=rendang")
        assert "rendang" in res.text.lower()

    def test_empty_search_returns_200(self):
        res = client.get("/search?q=")
        assert res.status_code == 200


# ── API: Search ───────────────────────────────────────────────────────────────

class TestApiSearch:
    def test_returns_list(self):
        res = client.get("/api/search?q=ayam")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_common_query_has_results(self):
        res = client.get("/api/search?q=ayam")
        assert len(res.json()) > 0

    def test_nonsense_query_returns_empty(self):
        res = client.get("/api/search?q=xyzabc999notearecipe")
        assert res.json() == []

    def test_result_has_required_fields(self):
        res = client.get("/api/search?q=tempe")
        assert len(res.json()) > 0
        recipe = res.json()[0]
        for field in ["id", "title", "ingredients", "steps", "num_ingredients", "num_steps"]:
            assert field in recipe, f"Field '{field}' tidak ada di response"

    def test_search_by_ingredient(self):
        res = client.get("/api/search?q=bawang+merah")
        assert len(res.json()) > 0

    def test_result_count_within_limit(self):
        res = client.get("/api/search?q=ayam")
        assert len(res.json()) <= 24


# ── API: Random ───────────────────────────────────────────────────────────────

class TestApiRandom:
    def test_returns_200(self):
        res = client.get("/api/random")
        assert res.status_code == 200

    def test_returns_single_recipe(self):
        res = client.get("/api/random")
        recipe = res.json()
        assert "title" in recipe
        assert "ingredients" in recipe
        assert "steps" in recipe

    def test_different_results_on_repeated_calls(self):
        ids = {client.get("/api/random").json()["id"] for _ in range(10)}
        assert len(ids) > 1, "10 panggilan random seharusnya return lebih dari 1 resep berbeda"


# ── API: Recipe detail ────────────────────────────────────────────────────────

class TestApiRecipeDetail:
    def _get_valid_id(self) -> int:
        return client.get("/api/random").json()["id"]

    def test_valid_id_returns_200(self):
        res = client.get(f"/api/recipe/{self._get_valid_id()}")
        assert res.status_code == 200

    def test_invalid_id_returns_404(self):
        res = client.get("/api/recipe/999999")
        assert res.status_code == 404

    def test_recipe_has_all_fields(self):
        recipe = client.get(f"/api/recipe/{self._get_valid_id()}").json()
        for field in ["id", "title", "ingredients", "steps", "num_ingredients", "num_steps"]:
            assert field in recipe

    def test_ingredients_is_list(self):
        recipe = client.get(f"/api/recipe/{self._get_valid_id()}").json()
        assert isinstance(recipe["ingredients"], list)
        assert len(recipe["ingredients"]) > 0

    def test_steps_is_list(self):
        recipe = client.get(f"/api/recipe/{self._get_valid_id()}").json()
        assert isinstance(recipe["steps"], list)
        assert len(recipe["steps"]) > 0


# ── API: Stats ────────────────────────────────────────────────────────────────

class TestApiStats:
    def test_returns_200(self):
        res = client.get("/api/stats")
        assert res.status_code == 200

    def test_has_required_fields(self):
        stats = client.get("/api/stats").json()
        assert "total" in stats
        assert "avg_ingredients" in stats
        assert "avg_steps" in stats

    def test_total_is_3000(self):
        stats = client.get("/api/stats").json()
        assert stats["total"] == 3000

    def test_averages_are_positive(self):
        stats = client.get("/api/stats").json()
        assert stats["avg_ingredients"] > 0
        assert stats["avg_steps"] > 0


# ── Recipe detail page ────────────────────────────────────────────────────────

class TestRecipeDetailPage:
    def test_valid_id_returns_200(self):
        recipe_id = client.get("/api/random").json()["id"]
        res = client.get(f"/recipe/{recipe_id}")
        assert res.status_code == 200

    def test_invalid_id_returns_404(self):
        res = client.get("/recipe/999999")
        assert res.status_code == 404

    def test_page_contains_ingredients(self):
        recipe_id = client.get("/api/random").json()["id"]
        res = client.get(f"/recipe/{recipe_id}")
        assert "bahan" in res.text.lower()

    def test_page_contains_steps(self):
        recipe_id = client.get("/api/random").json()["id"]
        res = client.get(f"/recipe/{recipe_id}")
        assert "cara memasak" in res.text.lower()
