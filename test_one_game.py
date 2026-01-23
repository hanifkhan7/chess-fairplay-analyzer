#!/usr/bin/env python3
"""Test analysis of just 1 game with Depth 24"""

import json
import yaml
import chess.pgn
import io
from pathlib import Path

print("=" * 70)
print("SINGLE GAME ANALYSIS - STOCKFISH DEPTH 24")
print("=" * 70)

# Load config
config_file = Path("config.yaml")
with open(config_file) as f:
    config = yaml.safe_load(f) or {}

if 'analysis' not in config:
    config['analysis'] = {}
config['analysis']['engine_depth'] = 24

# Load cached game
games_file = Path("cache/hikaru_games.json")
with open(games_file) as f:
    games_data = json.load(f)

# Use first game only
first_game_data = games_data['games'][0]
pgn_io = io.StringIO(first_game_data['pgn'])
game = chess.pgn.read_game(pgn_io)

print(f"\n[GAME] {game.headers.get('White')} vs {game.headers.get('Black')}")
print(f"       Time Control: {first_game_data['time_control']} seconds")

# Analyze just this one game
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer

analyzer = EnhancedPlayerAnalyzer(config, use_lichess=False, use_chess_com=True)
result = analyzer.analyze_games_fast([game], "hikaru", max_workers=1)

print(f"\n[ANALYSIS COMPLETE]")
print(f"  Games Analyzed: {result.get('total_games_analyzed', 0)}")
print(f"  Average Accuracy: {result.get('average_accuracy', 0):.1f}%")
print(f"  Average Engine Match: {result.get('average_engine_match', 0):.1f}%")
print(f"  Average Blunder Rate: {result.get('average_blunder_rate', 0):.1f}%")

if result.get('analyses'):
    analysis = result['analyses'][0]
    print(f"\n[DETAILED METRICS]")
    print(f"  Game ID: {analysis.get('game_id', 'N/A')}")
    print(f"  Opening Accuracy: {analysis.get('accuracy', {}).get('opening_accuracy', 0):.1f}%")
    print(f"  Middlegame Accuracy: {analysis.get('accuracy', {}).get('middlegame_accuracy', 0):.1f}%")
    print(f"  Endgame Accuracy: {analysis.get('accuracy', {}).get('endgame_accuracy', 0):.1f}%")
    print(f"  Overall Accuracy: {analysis.get('accuracy', {}).get('overall_accuracy', 0):.1f}%")
    print(f"  Engine Match Rate (Top 1): {analysis.get('engine_pattern', {}).get('top_1_match_rate', 0):.1f}%")
    print(f"  Suspicion Score: {analysis.get('suspicion_score', 0):.1f}/100")
    print(f"  Is Suspicious: {analysis.get('is_suspicious', False)}")

print("\n" + "=" * 70)
