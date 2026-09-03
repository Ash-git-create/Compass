"""One-command setup for Compass on a fresh clone.

Usage:
    python -m scripts.setup

Requires:
    - alpine_sales_actuals.parquet and alpine_statistical_forecast.parquet in
      data/alpine-manufacturing-gmbh/source-data/. Both are gitignored and are
      not distributed with this repository, so this script only runs if you
      already hold them. The committed data/fva_base.parquet and
      data/headline_stats.json are the outputs of a previous run, so the app
      works without them.
    - ANTHROPIC_API_KEY in the environment (only needed at runtime, not setup).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

print("=== Compass setup ===")
print()

# Step 1 — Init DB and seed hierarchy
print("[1/2] Initialising DuckDB and seeding hierarchy...")
from compass.store import init_db, seed_hierarchy

init_db()
n = seed_hierarchy()
print(f"      OK — {n:,} hierarchy rows seeded")

# Step 2 — Precompute FVA cache files
print()
print("[2/2] Building FVA cache (fva_base, headline_stats, replay_chart)...")
from compass.fva import get_headline_stats, get_replay_chart_data
import pandas as pd, json

stats = get_headline_stats()
(ROOT / "data" / "headline_stats.json").write_text(
    json.dumps(stats, indent=2, default=str), encoding="utf-8"
)
print(f"      headline_stats.json: wape_machine={stats['wape_machine']:.1%}  wape_planner={stats['wape_planner']:.1%}")

chart = get_replay_chart_data()
chart.to_parquet(ROOT / "data" / "replay_chart_cache.parquet", index=False)
print(f"      replay_chart_cache.parquet: {len(chart)} cycles")

print()
print("Setup complete. Run: streamlit run app/main.py")
