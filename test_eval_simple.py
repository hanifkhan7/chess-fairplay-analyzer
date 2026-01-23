#!/usr/bin/env python3
"""Test evaluation pipeline with cached game"""

import json
import yaml
import chess.pgn
import io
from pathlib import Path

print("=" * 70)
print("EVALUATION PIPELINE TEST - USING CACHED GAME")
print("=" * 70)

# Load config
config_file = Path("config.yaml")
with open(config_file) as f:
    config = yaml.safe_load(f) or {}

# Set Depth 24 for testing
if 'analysis' not in config:
    config['analysis'] = {}
config['analysis']['engine_depth'] = 24

print(f"\n[CONFIG] engine_depth = {config['analysis']['engine_depth']}")

# Load cached games
games_file = Path("cache/hikaru_games.json")
with open(games_file) as f:
    games_data = json.load(f)

print(f"\n[GAMES] Loaded {len(games_data['games'])} cached games")

# Get first game
first_game = games_data['games'][0]
pgn_text = first_game['pgn']

print(f"\n[GAME] Parsing first game PGN...")
pgn_io = io.StringIO(pgn_text)
game = chess.pgn.read_game(pgn_io)

if not game:
    print("ERROR: Could not parse game")
    exit(1)

# Extract moves
moves = []
for move in game.mainline_moves():
    moves.append(move)

print(f"  White: {game.headers.get('White')}")
print(f"  Black: {game.headers.get('Black')}")
print(f"  Moves: {len(moves)}")

# Test analyzer
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer

print(f"\n[ANALYZER] Creating analyzer with use_lichess=False...")
analyzer = EnhancedPlayerAnalyzer(
    config,
    use_lichess=False,  # Local Deep mode
    use_chess_com=True
)

print(f"  use_lichess: {analyzer.use_lichess}")
print(f"  engine_depth: {config.get('analysis', {}).get('engine_depth')}")

# Test _get_evaluations
print(f"\n[EVAL] Calling _get_evaluations()...")
import sys
evaluations = analyzer._get_evaluations(game, moves)

print(f"\n[RESULT] Got {len(evaluations)} evaluations for {len(moves)} moves")
if evaluations:
    print(f"  First: {evaluations[0]}")
    print(f"  Second: {evaluations[1] if len(evaluations) > 1 else 'N/A'}")
    print(f"  Last: {evaluations[-1] if evaluations else 'N/A'}")
else:
    print("  ERROR: No evaluations!")

print("\n" + "=" * 70)
