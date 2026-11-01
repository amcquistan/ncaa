from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd

from src.data_client import ApiError, fetch_games_for_years, fetch_plays_for_years


def latest_complete_seasons(window_size: int = 10) -> List[int]:
    """Return the most recent 10 seasons available in the data source."""
    current_year = datetime.now().year
    latest = current_year - 1
    return list(range(latest - window_size + 1, latest + 1))


def normalize_team_name(team: str | None) -> str:
    if team is None:
        return ""
    return team.strip().lower().replace("&", "and").replace(".", "")


def _clock_minutes(clock_obj: Any) -> int:
    if not isinstance(clock_obj, dict):
        return 0
    minutes = clock_obj.get("minutes")
    if minutes is None:
        return 0
    return int(minutes)


def detect_team_lead_earlier(plays: List[Dict[str, Any]], losing_team: str) -> bool:
    losing_team_norm = normalize_team_name(losing_team)

    for play in plays:
        if not isinstance(play, dict):
            continue

        offense = normalize_team_name(play.get("offense"))
        defense = normalize_team_name(play.get("defense"))
        offense_score = play.get("offenseScore")
        defense_score = play.get("defenseScore")

        if not offense or offense_score is None or defense_score is None:
            continue

        if offense == losing_team_norm and int(offense_score) > int(defense_score):
            return True
        if defense == losing_team_norm and int(defense_score) > int(offense_score):
            return True

    return False


def detect_team_lead_in_last_five_minutes(plays: List[Dict[str, Any]], losing_team: str) -> bool:
    losing_team_norm = normalize_team_name(losing_team)

    for play in plays:
        if not isinstance(play, dict):
            continue

        period = play.get("period")
        clock = play.get("clock")
        if period is None or not isinstance(clock, dict):
            continue

        offense = normalize_team_name(play.get("offense"))
        defense = normalize_team_name(play.get("defense"))
        offense_score = play.get("offenseScore")
        defense_score = play.get("defenseScore")

        if offense_score is None or defense_score is None:
            continue

        is_final_five = (int(period) == 4 and _clock_minutes(clock) <= 5) or (int(period) > 4)
        if not is_final_five:
            continue

        if offense == losing_team_norm and int(offense_score) > int(defense_score):
            return True
        if defense == losing_team_norm and int(defense_score) > int(offense_score):
            return True

    return False


def classify_games(games: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    games_by_id = {int(game.get("id")): game for game in games if isinstance(game, dict) and game.get("id") is not None}

    season_years = sorted({int(game["season"]) for game in games_by_id.values()})
    plays_by_game: Dict[int, List[Dict[str, Any]]] = {}

    for year in season_years:
        for week in range(1, 19):
            try:
                from src.data_client import fetch_plays_for_year_week
                week_plays = fetch_plays_for_year_week(year, week)
            except (ApiError, Exception):
                week_plays = []
            for play in week_plays:
                if not isinstance(play, dict):
                    continue
                game_id = play.get("gameId")
                if game_id is None:
                    continue
                plays_by_game.setdefault(int(game_id), []).append(play)

    for game in games_by_id.values():
        home_team = game.get("homeTeam")
        away_team = game.get("awayTeam")
        home_score = game.get("homePoints")
        away_score = game.get("awayPoints")
        season = game.get("season")

        if home_team is None or away_team is None or home_score is None or away_score is None or season is None:
            continue

        winner = home_team if int(home_score) > int(away_score) else away_team
        loser = away_team if int(home_score) > int(away_score) else home_team
        margin = abs(int(home_score) - int(away_score))

        row = {
            "season": int(season),
            "game_id": int(game["id"]),
            "home_team": home_team,
            "away_team": away_team,
            "home_score": int(home_score),
            "away_score": int(away_score),
            "winner": winner,
            "loser": loser,
            "margin": margin,
        }

        plays = plays_by_game.get(row["game_id"], [])
        row["lead_earlier_for_loser"] = detect_team_lead_earlier(plays, loser)
        row["lead_in_last_5_for_loser"] = detect_team_lead_in_last_five_minutes(plays, loser)
        row["loss_by_7_or_less_with_earlier_lead"] = row["margin"] <= 7 and row["lead_earlier_for_loser"]
        row["loss_with_lead_in_last_5"] = row["lead_in_last_5_for_loser"]
        rows.append(row)

    return rows


def build_comparison_df(classified_games: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(classified_games)
    if df.empty:
        return df

    df["is_loss"] = True
    df["is_loss_by_7_or_less_with_earlier_lead"] = df["margin"].le(7) & df["lead_earlier_for_loser"]
    df["is_loss_with_lead_in_last_5"] = df["lead_in_last_5_for_loser"]
    return df


def summarize_by_team(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["team", "season", "losses", "loss_by_7_or_less_with_earlier_lead", "loss_with_lead_in_last_5"])

    records = []
    for team_name, team_df in df.groupby("loser"):
        team_records = {
            "team": team_name,
            "season": team_df["season"].max(),
            "losses": len(team_df),
            "loss_by_7_or_less_with_earlier_lead": int(team_df["is_loss_by_7_or_less_with_earlier_lead"].sum()),
            "loss_with_lead_in_last_5": int(team_df["is_loss_with_lead_in_last_5"].sum()),
        }
        records.append(team_records)
    return pd.DataFrame(records)


def neb_vs_all_others(df: pd.DataFrame, team_name: str = "Nebraska") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "comparison_group",
            "teams_in_sample",
            "avg_close_game_losses_per_team",
            "avg_late_game_lead_losses_per_team",
            "raw_close_game_losses",
            "raw_late_game_lead_losses",
        ])

    team_metrics = (
        df.groupby("loser")
        .agg(
            raw_close_game_losses=("is_loss_by_7_or_less_with_earlier_lead", "sum"),
            raw_late_game_lead_losses=("is_loss_with_lead_in_last_5", "sum"),
        )
        .reset_index()
    )

    neb_subset = team_metrics[team_metrics["loser"].str.lower() == team_name.lower()]
    other_subset = team_metrics[team_metrics["loser"].str.lower() != team_name.lower()]

    rows: List[Dict[str, Any]] = []

    if not neb_subset.empty:
        neb_row = neb_subset.iloc[0]
        rows.append({
            "comparison_group": "Nebraska",
            "teams_in_sample": 1,
            "avg_close_game_losses_per_team": float(neb_row["raw_close_game_losses"]),
            "avg_late_game_lead_losses_per_team": float(neb_row["raw_late_game_lead_losses"]),
            "raw_close_game_losses": int(neb_row["raw_close_game_losses"]),
            "raw_late_game_lead_losses": int(neb_row["raw_late_game_lead_losses"]),
        })

    if not other_subset.empty:
        rows.append({
            "comparison_group": "All other teams (avg/team)",
            "teams_in_sample": int(len(other_subset)),
            "avg_close_game_losses_per_team": float(other_subset["raw_close_game_losses"].mean()),
            "avg_late_game_lead_losses_per_team": float(other_subset["raw_late_game_lead_losses"].mean()),
            "raw_close_game_losses": int(other_subset["raw_close_game_losses"].sum()),
            "raw_late_game_lead_losses": int(other_subset["raw_late_game_lead_losses"].sum()),
        })

    return pd.DataFrame(rows)
