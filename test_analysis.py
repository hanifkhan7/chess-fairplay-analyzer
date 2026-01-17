#!/usr/bin/env python3
"""Quick test of analysis functionality"""
import sys
import traceback

try:
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.utils.helpers import load_config
    
    print("Loading config...")
    config = load_config()
    
    print("Fetching 2 games for rohan_asif...")
    games = fetch_player_games('rohan_asif', max_games=2)
    print(f"Got {len(games)} games")
    
    print("Initializing analyzer...")
    analyzer = ChessAnalyzer(config)
    
    print("Analyzing games...")
    results = analyzer.analyze_games(games)
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"Avg Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
    print(f"Games analyzed: {results.games_analyzed}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
