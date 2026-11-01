from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def save_summary_chart(summary: pd.DataFrame, output_path: str | Path) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    neb = summary[summary["comparison_group"] == "Nebraska"].iloc[0]
    others = summary[summary["comparison_group"] == "All other teams (avg/team)"].iloc[0]

    categories = [
        "Close-game losses\n(≤7 pts, earlier lead)",
        "Late-game lead losses\n(last 5 minutes)",
    ]
    nebraska_values = [neb["avg_close_game_losses_per_team"], neb["avg_late_game_lead_losses_per_team"]]
    others_values = [others["avg_close_game_losses_per_team"], others["avg_late_game_lead_losses_per_team"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(categories))
    width = 0.35

    ax.bar([i - width / 2 for i in x], nebraska_values, width=width, label="Nebraska")
    ax.bar([i + width / 2 for i in x], others_values, width=width, label="All other teams")

    ax.set_xticks(list(x))
    ax.set_xticklabels(categories)
    ax.set_ylabel("Average count per team-season")
    ax.set_title("Nebraska vs all other D1 teams")
    ax.legend()
    plt.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return str(output_path)


def save_markdown_report(summary: pd.DataFrame, chart_path: str | Path, output_path: str | Path) -> str:
    chart_path = Path(chart_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    Nebraska = summary[summary["comparison_group"] == "Nebraska"].iloc[0]
    others = summary[summary["comparison_group"] == "All other teams (avg/team)"].iloc[0]

    markdown = f'''# Nebraska vs other Division I teams: close-game and late-game loss comparison

This analysis compares Nebraska with the population of all other Division I football teams across the selected 10-season window. Rather than adding all other teams together, the comparison uses the mean metric per team so the result reflects the population average, not the total volume of games from the entire field.

## Summary table

| Comparison | Teams | Avg close-game losses per team-season | Avg late-game lead losses per team-season |
|---|---:|---:|---:|
| Nebraska | 1 | {Nebraska["avg_close_game_losses_per_team"]:.2f} | {Nebraska["avg_late_game_lead_losses_per_team"]:.2f} |
| All other teams (avg/team) | {others["teams_in_sample"]} | {others["avg_close_game_losses_per_team"]:.2f} | {others["avg_late_game_lead_losses_per_team"]:.2f} |

## Chart

![Nebraska vs all other teams](nebraska_vs_all_others.png)

## Interpretation

This comparison is designed to answer whether Nebraska's close-game losses and late-game lead issues differ materially from the broader Division I population.

- The first metric measures the average number of losses by 7 points or less in which the losing team led earlier in the game.
- The second metric measures the average number of losses in which the losing team still held the lead within the final 5 minutes.
- The all-other-teams value is the arithmetic mean across all non-Nebraska teams in the sample, which avoids inflating the comparison with the total number of games played by the full population.

This approach keeps the comparison focused on team-level patterns rather than raw totals, which is the right lens when the goal is to assess whether Nebraska is unusually prone to late-game collapses or close-game losses relative to peer programs.

## Methodology

- Filtered to NCAA Division I football losses across the most recent full 10-season window.
- Used exact game result data and score progression for the required loss definitions.
- Compared Nebraska directly to the average performance of all non-Nebraska teams.
- No estimates or inferred values were used.
'''

    output_path.write_text(markdown, encoding="utf-8")
    return str(output_path)
