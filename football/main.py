from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis import build_comparison_df, classify_games, latest_complete_seasons, neb_vs_all_others
from src.data_client import ApiError, fetch_games_for_years
from src.reporting import save_markdown_report, save_summary_chart


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Nebraska loss trends against all other NCAA Division I teams.")
    parser.add_argument(
        "--years",
        nargs="*",
        type=int,
        help="Season years to query. Defaults to the latest 10 complete seasons.",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refetch the dataset from the CFBD API and overwrite the local cache.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    years = args.years if args.years else latest_complete_seasons(window_size=10)
    print(f"[Progress] Starting Nebraska comparison for seasons: {years}")

    try:
        games = fetch_games_for_years(years, refresh=args.refresh)
    except ApiError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"[Progress] Retrieved {len(games)} games. Classifying results...")
    classified = classify_games(games)

    print("[Progress] Building team-level comparison metrics...")
    comparison_df = build_comparison_df(classified)
    summary = neb_vs_all_others(comparison_df, team_name="Nebraska")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print(f"[Progress] Writing outputs to {output_dir}...")
    chart_path = save_summary_chart(summary, output_dir / "nebraska_vs_all_others.png")
    report_path = save_markdown_report(summary, chart_path, output_dir / "analysis_report.md")

    print("\n[Progress] Final comparison summary:")
    print(summary.to_string(index=False))
    print(f"\nChart saved to: {chart_path}")
    print(f"Markdown report saved to: {report_path}")


if __name__ == "__main__":
    main()
