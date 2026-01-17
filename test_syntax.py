#!/usr/bin/env python3
"""Quick test - just import and check syntax"""
import sys

try:
    print("Testing imports...")
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.engine import StockfishManager
    from chess_analyzer.fetcher import fetch_player_games
    print("SUCCESS: All imports work!")
    
    print("\nTesting ChessAnalyzer instantiation...")
    from chess_analyzer.utils.helpers import load_config
    config = load_config()
    analyzer = ChessAnalyzer(config)
    print("SUCCESS: ChessAnalyzer created!")
    
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll basic tests passed!")
