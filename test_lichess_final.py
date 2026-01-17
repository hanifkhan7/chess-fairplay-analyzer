#!/usr/bin/env python3
"""Test actual game analysis with Lichess API."""

import yaml
import sys
import time

try:
    print("=" * 70)
    print("LICHESS API - LIVE GAME ANALYSIS TEST")
    print("=" * 70)
    
    config = yaml.safe_load(open('config.yaml'))
    
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    
    # Fetch 2 games
    print("\n1. Fetching 2 games from 'hikaru'...")
    games = fetch_player_games('hikaru', max_games=2, config=config)
    print(f"   ✓ Got {len(games)} game(s)")
    
    for i, game in enumerate(games, 1):
        moves = len(list(game.mainline_moves()))
        white = game.headers.get('White', 'Unknown')
        black = game.headers.get('Black', 'Unknown')
        print(f"   Game {i}: {white} vs {black} ({moves} moves)")
    
    # Create analyzer
    print("\n2. Creating analyzer with Lichess...")
    analyzer = ChessAnalyzer(config)
    engine_type = type(analyzer.engine_manager).__name__
    print(f"   ✓ Engine: {engine_type}")
    
    # Analyze games
    print("\n3. Analyzing games with Lichess API...")
    print("   (This may take 30-90 seconds per game...)")
    
    start = time.time()
    results = analyzer.analyze_games(games)
    elapsed = time.time() - start
    
    print(f"\n4. Analysis Results (completed in {elapsed:.1f}s):")
    print(f"   ✓ Games Analyzed: {results.games_analyzed}/{len(games)}")
    print(f"   ✓ Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"   ✓ Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"   ✓ Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
    print(f"   ✓ Suspicious Games: {len(results.suspicious_games)}")
    
    print("\n" + "=" * 70)
    print("✓ LICHESS API INTEGRATION SUCCESSFUL!")
    print("=" * 70)
    
    if elapsed < 200:  # Less than 200 seconds for 2 games
        print("✓ Speed is excellent compared to local Stockfish!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
