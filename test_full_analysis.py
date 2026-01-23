#!/usr/bin/env python3
"""Test full analysis with Stockfish evaluations"""

import json
import yaml
import chess.pgn
import io
from pathlib import Path
from dataclasses import asdict

print("=" * 70)
print("FULL ANALYSIS TEST - STOCKFISH DEPTH 24")
print("=" * 70)

# Load config
config_file = Path("config.yaml")
with open(config_file) as f:
    config = yaml.safe_load(f) or {}

# Set Depth 24
if 'analysis' not in config:
    config['analysis'] = {}
config['analysis']['engine_depth'] = 24

# Load cached games
games_file = Path("cache/hikaru_games.json")
with open(games_file) as f:
    games_data = json.load(f)

print(f"\n[SETUP] Loaded {len(games_data['games'])} cached games")
print(f"        engine_depth = 24")

# Analyze first 2 games only (for speed)
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer

analyzer = EnhancedPlayerAnalyzer(
    config,
    use_lichess=False,
    use_chess_com=True
)

games_to_analyze = []
for game_data in games_data['games'][:2]:  # Only first 2 games
    pgn_io = io.StringIO(game_data['pgn'])
    game = chess.pgn.read_game(pgn_io)
    if game:
        games_to_analyze.append(game)

print(f"\n[ANALYZE] Analyzing {len(games_to_analyze)} games...")
print("          (This will take several minutes with Depth 24)")

# Analyze games
results = analyzer.analyze_games_fast(games_to_analyze, "hikaru", max_workers=1)

print(f"\n[RESULTS]")
print(f"  Total games analyzed: {results.get('total_games_analyzed', 0)}")
print(f"  Average engine match: {results.get('average_engine_match', 0):.1f}%")
print(f"  Average accuracy: {results.get('average_accuracy', 0):.1f}%")
print(f"  Average blunder rate: {results.get('average_blunder_rate', 0):.1f}%")

if results.get('analyses'):
    first_game = results['analyses'][0]
    print(f"\n[FIRST GAME]")
    print(f"  ID: {first_game.get('game_id', 'N/A')}")
    print(f"  Accuracy: {first_game.get('accuracy', {}).get('overall_accuracy', 0):.1f}%")
    print(f"  Engine Match: {first_game.get('engine_pattern', {}).get('top_1_match_rate', 0):.1f}%")
    print(f"  Suspicion Score: {first_game.get('suspicion_score', 0):.1f}/100")

print("\n" + "=" * 70)
