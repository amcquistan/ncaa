# Design

## Overview

This project analyzes NCAA Division I football outcomes over a 10-season window and compares Nebraska’s loss profile against all other programs. The analysis is driven by the exact requirements in the project brief:

- Identify losses by 7 points or less where the losing team led earlier in the game.
- Identify losses where the losing team held the lead within the final 5 minutes.
- Compare Nebraska vs every other team across the same conditions.
- Produce both tabular results and graphical summaries.
- Use only observed, exact game data; no estimates or inferred values.

The system is designed as a small Python analytics workflow that reads historical game data, computes the required filters, aggregates the results, and exports a concise report for review.

## Design decisions

### 1. Use Python as the primary analytics stack

Python is the chosen implementation language because it provides a low-friction data analysis ecosystem for filtering, grouping, and plotting sports data. The project will use the local virtual environment in the repository root so dependency installation stays isolated and repeatable.

Recommended dependency approach:
- Python 3.x runtime managed locally via the repo .venv
- pandas for structured data operations
- numpy for numeric aggregation and comparisons
- matplotlib and seaborn for charts
- pytest for validation, if a test layer is added later

This keeps the project simple, transparent, and easy to run in a local workspace without introducing a heavier application framework.

### 2. Use a single-source data pipeline

The project will follow a straightforward data pipeline:

1. Load raw game-level results into a normalized table.
2. Standardize team names and season identifiers.
3. Compute loss condition flags.
4. Aggregate by team and season.
5. Compare Nebraska against all other teams.
6. Export tabular output and generated charts.

This pipeline is efficient because the analysis is entirely batch-oriented: one canonical dataset, one set of filters, and a deterministic aggregation process. It also minimizes the risk of inconsistent logic across multiple report views.

### 3. Define the exact loss conditions in code

The design includes explicit boolean flags for each required category so the logic remains auditable and easy to validate.

Loss condition A:
- game result is a loss
- margin of defeat is 7 points or less
- losing team had a lead at some point earlier in the game

Loss condition B:
- game result is a loss
- losing team still held a lead within the last 5 minutes of the game

These conditions are computed using the game’s score progression and lead status, not by approximating trends from season summaries.

### 4. Standardize reporting around Nebraska vs all others

The project compares Nebraska as a single team profile to the full population of all other Division I teams. To keep the output unbiased and consistent, the following rules apply:

- Nebraska is evaluated as a named team key in each season.
- All other teams are included in the comparison set for the same seasons.
- Aggregations are computed on the exact same filtered criteria for both groups.
- Report tables should include counts, not estimates.

This ensures the comparison is apples-to-apples and follows the requirement exactly.

### 5. Output both data and visuals

The reporting layer will generate:
- a tabular summary by team and metric
- a side-by-side comparison chart for Nebraska vs the rest of the field
- a chart per scenario that highlights the exact counts for each condition

The visualizations are intended to support interpretation, but the underlying tables remain the source of truth. No estimated or projected values will be developed for the report.

## Architecture

### High-level structure

The system can be organized as a small set of Python modules and artifacts:

- data_ingest.py: loads raw game results and normalizes fields
- metrics.py: defines loss-condition logic and seasonal aggregation
- compare.py: computes Nebraska vs all-other-teams comparisons
- report.py: builds tables and plots
- outputs/: stores generated CSV and PNG artifacts

This modular layout keeps the logic traceable and makes it easy to validate each stage of the pipeline independently.

### Data model

The core dataset should be modeled as a game-level row with the following normalized fields:

- season
- date
- home_team
- away_team
- home_score
- away_score
- winner
- loser
- margin
- lead_team_earlier
- lead_within_last_5_minutes
- is_loss_by_7_or_less
- is_loss_with_lead_in_final_5

These fields allow the system to derive the exact metrics without re-reading raw source files for every calculation.

### Execution flow

1. Load the canonical game dataset.
2. Filter to NCAA Division I games only.
3. Standardize school names and season years.
4. Compute the two loss-condition flags.
5. Group by team and season.
6. Build Nebraska-specific and all-other-team aggregates.
7. Generate tables and charts.
8. Save outputs in a reproducible report directory.

## Ambiguities and resolutions

### Ambiguity: What does “10 seasons” mean?

The requirements do not specify a starting year. To resolve this in a deterministic way, the design chooses the latest 10 complete seasons available in the source dataset, with the season label based on the actual competition year (for example, 2015-2024 if 2025 is not complete).

This avoids partial-season bias and keeps the analysis consistent over a stable time window.

### Ambiguity: What source system should provide the game data?

The project does not specify a scoreboard source. The design resolves this by using a canonical game-result dataset that can be loaded from a local CSV or a vetted sports data source. The analytics logic is independent of the source format as long as each row contains game result and lead-status fields.

### Ambiguity: How should Nebraska be separated from all other teams?

The design resolves this by treating Nebraska as a single comparison team and grouping all remaining schools into the “all other teams” cohort for each metric. No mixing between seasons or partial filters is allowed.

## Risks and considerations

- Data quality risk: some source feeds may not include lead timing or score history in a clean format.
- Normalization risk: team naming differences can cause duplicate team keys unless standardization is enforced.
- Comparison risk: if the dataset is incomplete for a season, the analysis may need to exclude that season from the 10-season window.
- Reporting risk: chart labels and tables must explicitly show that values are exact counts based on observed data only.

## Dependency and environment plan

The project is designed to run in the local repository virtual environment:

- create the environment at .venv
- install Python dependencies inside that environment
- execute the analysis scripts from the activated venv

This ensures the project remains isolated from the system Python and keeps the install path explicit for future reproduction.

## Success criteria

The design is successful when:

- the exact two loss conditions are computed correctly for all games in scope
- Nebraska’s totals are directly comparable with all other teams
- results are available in both tabular and graphical form
- no estimated or inferred values appear in the final report
