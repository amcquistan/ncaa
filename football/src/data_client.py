from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests

from src.config import API_BASE_URL, CFBD_API_KEY

CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"


class ApiError(RuntimeError):
    """Raised when the College Football Data API request fails."""


def _request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if not CFBD_API_KEY:
        raise ApiError(
            "CFBD_API_KEY is not configured. Add it to the .env file or export it in the shell."
        )

    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {CFBD_API_KEY}"}
    response = requests.get(url, params=params, headers=headers, timeout=60)
    if response.status_code != 200:
        raise ApiError(
            f"College Football Data API request failed for {endpoint}: "
            f"{response.status_code} {response.text[:200]}"
        )

    payload = response.json()
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    return [payload]


def fetch_games_for_year(year: int) -> List[Dict[str, Any]]:
    params = {
        "year": year,
        "seasonType": "both",
    }
    return _request("/games", params)


def fetch_plays_for_year_week(year: int, week: int) -> List[Dict[str, Any]]:
    return _request("/plays", {"year": int(year), "week": int(week)})


def fetch_plays_for_years(years: Iterable[int], max_weeks: int = 18) -> List[Dict[str, Any]]:
    all_plays: List[Dict[str, Any]] = []
    for year in years:
        for week in range(1, max_weeks + 1):
            plays = fetch_plays_for_year_week(int(year), week)
            all_plays.extend(plays)
            time.sleep(0.05)
    return all_plays


def _cache_key_for_years(years: Iterable[int]) -> str:
    unique_years = sorted({int(year) for year in years})
    return "games_" + "_".join(str(year) for year in unique_years) + ".json"


def load_cached_games_for_years(years: Iterable[int]) -> Optional[List[Dict[str, Any]]]:
    cache_file = CACHE_DIR / _cache_key_for_years(years)
    if not cache_file.exists():
        return None

    try:
        with cache_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None

    if not isinstance(payload, list):
        return None
    return payload


def save_cached_games_for_years(years: Iterable[int], games: List[Dict[str, Any]]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / _cache_key_for_years(years)
    with cache_file.open("w", encoding="utf-8") as handle:
        json.dump(games, handle, indent=2)
    return cache_file


def fetch_games_for_years(years: Iterable[int], refresh: bool = False) -> List[Dict[str, Any]]:
    normalized_years = sorted({int(year) for year in years})

    if not refresh:
        cached_games = load_cached_games_for_years(normalized_years)
        if cached_games is not None:
            print(f"[Progress] Using cached local dataset for seasons: {normalized_years}")
            return cached_games
        print(f"[Progress] Cached dataset not found for seasons: {normalized_years}. Fetching from source...")

    if refresh:
        print(f"[Progress] Refreshing cached data for seasons: {normalized_years} from CFBD API...")

    all_games: List[Dict[str, Any]] = []
    for year in normalized_years:
        print(f"[Progress] Fetching game data from CFBD API for year {year}...")
        games = fetch_games_for_year(int(year))
        all_games.extend(games)
        time.sleep(0.25)

    save_cached_games_for_years(normalized_years, all_games)
    print(f"[Progress] Saved {len(all_games)} games to cache at {CACHE_DIR / _cache_key_for_years(normalized_years)}")
    return all_games
