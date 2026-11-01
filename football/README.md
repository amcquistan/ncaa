# NCAA Football Loss Analysis

This project uses the College Football Data API to analyze loss patterns for NCAA Division I football over the most recent 10 complete seasons.

## Setup

1. Create a local environment file from the example:
   - cp .env.example .env
2. Add your CFBD API key to `.env`.
3. Activate the repo-local virtual environment:
   - source .venv/bin/activate
4. Install dependencies:
   - python -m pip install -r requirements.txt

## Run

```bash
source .venv/bin/activate
python main.py
```

This script fetches the latest 10 seasons of game data, computes the requested loss conditions, and prints a Nebraska-vs-all-other-teams summary.
