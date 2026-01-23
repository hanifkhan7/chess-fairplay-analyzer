#!/usr/bin/env python3
"""Debug why evaluations are returning 0%"""

import sys
import json
from pathlib import Path
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
from chess_analyzer.dual_fetcher import fetch_dual_platform_games

# Load config
config_file = Path("config.yaml")
import yaml
with open(config_file) as f:
    config = yaml.safe_load(f) or {}

print("=" * 70)
print("EVALUATION PIPELINE DEBUG")
print("=" * 70)

# Test parameters
username = "hikaru"
games_to_fetch = 2
platforms = ["Chess.com", "Lichess"]
time_control = "Blitz"
depth = 24

# Update config with test depth
if 'analysis' not in config:
    config['analysis'] = {}
config['analysis']['engine_depth'] = depth
print(f"\n[CONFIG] Set engine_depth to: {depth}")

# Fetch games
print(f"\n[FETCH] Fetching {games_to_fetch} {time_control} games for {username}...")
try:
    player_games, platform_counts = fetch_dual_platform_games(
        username,
        max_games=games_to_fetch,
        platforms=platforms,
        time_control="blitz"
    )
    print(f"✓ Fetched {len(player_games)} games")
    print(f"  Platform breakdown: {platform_counts}")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

if not player_games:
    print("✗ No games fetched!")
    exit(1)

# Test analyzer with Local mode
print(f"\n[ANALYZE] Creating analyzer with use_lichess=False (Local Deep mode)...")
analyzer = EnhancedPlayerAnalyzer(
    config,
    use_lichess=False,  # Local Deep mode
    use_chess_com=True
)

print(f"  use_lichess: {analyzer.use_lichess}")
print(f"  engine_depth from config: {config.get('analysis', {}).get('engine_depth', 'NOT SET')}")

# Analyze first game
if player_games:
    game = player_games[0]
    print(f"\n[GAME] Testing on first game: {game.headers.get('White')} vs {game.headers.get('Black')}")
    
    # Test _get_evaluations directly
    import chess
    board = chess.Board()
    moves = []
    
    for move in game.mainline_moves():
        moves.append(move)
    
    print(f"  Moves in game: {len(moves)}")
    print(f"  First 5 moves: {[move.uci() for move in moves[:5]]}")
    
    print(f"\n[EVAL] Calling _get_evaluations()...")
    evaluations = analyzer._get_evaluations(game, moves)
    
    print(f"  Returned {len(evaluations)} evaluations")
    if evaluations:
        print(f"  First evaluation: {evaluations[0]}")
        print(f"  Second evaluation: {evaluations[1] if len(evaluations) > 1 else 'N/A'}")
    else:
        print("  ✗ NO EVALUATIONS RETURNED!")
        
        # Check which method was used
        print(f"\n[DEBUG] Checking evaluation methods...")
        
        # Try Lichess
        print(f"  Trying Lichess API...")
        lich_evals = analyzer._get_lichess_evaluations(game)
        print(f"    Result: {len(lich_evals)} evaluations")
        
        # Try Local
        print(f"  Trying Local Stockfish...")
        try:
            local_evals = analyzer._get_local_evaluations(game, moves)
            print(f"    Result: {len(local_evals)} evaluations")
            if not local_evals:
                print("    WARNING: Local evaluations are empty!")
        except Exception as e:
            print(f"    Error: {e}")
        
        # Try Heuristic
        print(f"  Trying Heuristic...")
        heur_evals = analyzer._generate_heuristic_evaluations(game, moves)
        print(f"    Result: {len(heur_evals)} evaluations")

print("\n" + "=" * 70)
