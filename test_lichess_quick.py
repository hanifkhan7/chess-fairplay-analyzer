#!/usr/bin/env python3
"""Quick test of Lichess API with just the imports and basic check."""

import yaml
import sys

try:
    print("Loading config...")
    config = yaml.safe_load(open('config.yaml'))
    
    print("Config loaded successfully")
    print(f"  use_lichess: {config.get('analysis', {}).get('use_lichess')}")
    print(f"  lichess token: {config.get('lichess', {}).get('api_token', 'NOT SET')[:20]}...")
    print()
    
    print("Importing fetcher...")
    from chess_analyzer.fetcher import fetch_player_games
    print("✓ Fetcher imported")
    
    print("Importing analyzer...")
    from chess_analyzer.analyzer import ChessAnalyzer
    print("✓ Analyzer imported")
    
    print("Fetching 1 game from hikaru...")
    games = fetch_player_games('hikaru', max_games=1, config=config)
    print(f"✓ Fetched {len(games)} game(s)")
    
    if games:
        game = games[0]
        print(f"  Game: {game.headers.get('White')} vs {game.headers.get('Black')}")
        print(f"  Moves: {len(list(game.mainline_moves()))}")
    
    print("\nCreating analyzer (this will use Lichess)...")
    analyzer = ChessAnalyzer(config)
    engine_type = type(analyzer.engine_manager).__name__
    print(f"✓ Analyzer created with engine: {engine_type}")
    
    if engine_type == 'LichessAnalyzer':
        print("✓ Successfully using Lichess API!")
    elif engine_type == 'StockfishManager':
        print("⚠ Fell back to Stockfish (Lichess failed to initialize)")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ All checks passed!")
