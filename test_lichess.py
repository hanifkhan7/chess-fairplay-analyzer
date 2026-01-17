#!/usr/bin/env python3
"""Test Lichess API analysis - should be MUCH faster"""
import sys

try:
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.utils.helpers import load_config
    
    print("Loading config...")
    config = load_config()
    print(f"Using Lichess: {config.get('analysis', {}).get('use_lichess', True)}")
    
    print("\nFetching 1 game for Salman_Ali_Khan...")
    games = fetch_player_games('Salman_Ali_Khan', max_games=1)
    print(f"Got {len(games)} games\n")
    
    print("Initializing analyzer...")
    analyzer = ChessAnalyzer(config)
    
    print("Analyzing game with Lichess API...\n")
    import time
    start = time.time()
    results = analyzer.analyze_games(games)
    elapsed = time.time() - start
    
    print(f"\n{'='*50}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*50}")
    print(f"Time taken: {elapsed:.1f} seconds")
    print(f"Games Analyzed: {results.games_analyzed}")
    print(f"Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
    print(f"Risk Level: {results.risk_level}")
    
    if elapsed < 60:
        print("\n✓ LIGHTNING FAST! Lichess API is working great!")
    else:
        print(f"\n✓ Analysis complete in {elapsed:.0f} seconds")
    
except KeyboardInterrupt:
    print("\n\nInterrupted by user.")
    sys.exit(0)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
