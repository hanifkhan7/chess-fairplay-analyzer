#!/usr/bin/env python3
"""Quick test with just 2 games"""
import sys

try:
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.utils.helpers import load_config
    
    print("Loading config...")
    config = load_config()
    print(f"Stockfish depth set to: {config.get('analysis', {}).get('engine_depth', 18)}")
    
    print("\nFetching 2 games for Salman_Ali_Khan...")
    games = fetch_player_games('Salman_Ali_Khan', max_games=2)
    print(f"Got {len(games)} games\n")
    
    print("Initializing analyzer...")
    analyzer = ChessAnalyzer(config)
    
    print("Analyzing games (this takes 2-5 minutes)...\n")
    results = analyzer.analyze_games(games)
    
    print(f"\n{'='*50}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*50}")
    print(f"Games Analyzed: {results.games_analyzed}")
    print(f"Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
    print(f"Risk Level: {results.risk_level}")
    
except KeyboardInterrupt:
    print("\n\nInterrupted by user.")
    sys.exit(0)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
