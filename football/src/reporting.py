from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def save_summary_chart(close_game_worst: pd.DataFrame, late_lead_worst: pd.DataFrame, output_path: str | Path) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 7))

    plot_configs = [
        (
            axes[0],
            close_game_worst.sort_values("avg_losses_per_season", ascending=True),
            "Worst teams: close-game losses\n(≤7 points, losing team led earlier)",
        ),
        (
            axes[1],
            late_lead_worst.sort_values("avg_losses_per_season", ascending=True),
            "Worst teams: losses with lead\ninside final 5 minutes",
        ),
    ]

    for ax, metric_df, title in plot_configs:
        ax.barh(metric_df["team"], metric_df["avg_losses_per_season"], color="#c0392b")
        ax.set_title(title)
        ax.set_xlabel("Average losses per season")
        ax.set_ylabel("Team")

    plt.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return str(output_path)


def _markdown_table(df: pd.DataFrame) -> str:
    header = "| Rank | Team | Avg losses per season | Raw losses |\n|---:|---|---:|---:|"
    lines = [header]
    for index, row in df.reset_index(drop=True).iterrows():
        lines.append(
            f"| {index + 1} | {row['team']} | {row['avg_losses_per_season']:.2f} | {int(row['raw_losses'])} |"
        )
    return "\n".join(lines)


def save_markdown_report(
    close_game_worst: pd.DataFrame, late_lead_worst: pd.DataFrame, chart_path: str | Path, output_path: str | Path
) -> str:
    chart_path = Path(chart_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    markdown = f"""# Worst teams by season-average loss metrics

This analysis reports the 10 worst teams for each required loss metric, based on average losses per season across the selected 10-season window.

## Metric 1: losses by 7 points or fewer after leading earlier

{_markdown_table(close_game_worst)}

## Metric 2: losses while still leading in the final 5 minutes

{_markdown_table(late_lead_worst)}

## Chart

![Worst teams by metric]({chart_path.name})

## Metric definitions

- The first metric measures the average number of losses by 7 points or less in which the losing team led earlier in the game.
- The second metric measures the average number of losses in which the losing team still held the lead within the final 5 minutes.

## Methodology

- Filtered to NCAA Division I football losses across the most recent full 10-season window.
- Used exact game result data and score progression for the required loss definitions.
- Ranked teams by average losses per season for each metric independently.
- No estimates or inferred values were used.
"""

    output_path.write_text(markdown, encoding="utf-8")
    return str(output_path)
