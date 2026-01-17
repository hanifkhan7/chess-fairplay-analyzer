#!/usr/bin/env python3
"""Test Stockfish analysis at depth 14 - faster version"""
import sys
import time

print("\n" + "="*60)
print("CHESS FAIRPLAY ANALYZER - STOCKFISH TEST")
print("="*60)

try:
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.utils.helpers import load_config
    
    print("\n1. Loading config...")
    config = load_config()
    depth = config.get('analysis', {}).get('engine_depth', 14)
    print(f"   Stockfish depth: {depth}")
    print(f"   Use Lichess: {config.get('analysis', {}).get('use_lichess', False)}")
    
    print("\n2. Fetching 3 games for Quantum-Chesss...")
    games = fetch_player_games('Quantum-Chesss', max_games=3)
    print(f"   Retrieved {len(games)} games")
    
    print("\n3. Creating analyzer...")
    analyzer = ChessAnalyzer(config)
    
    print("\n4. Starting analysis...")
    print("   " + "-"*50)
    start = time.time()
    
    results = analyzer.analyze_games(games)
    
    elapsed = time.time() - start
    print("   " + "-"*50)
    
    print(f"\n5. RESULTS:")
    print(f"   Time: {elapsed:.1f} seconds ({elapsed/len(games):.0f}s per game)")
    print(f"   Games analyzed: {results.games_analyzed}")
    print(f"   Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"   Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"   Avg CPL: {results.avg_centipawn_loss:.1f}")
    print(f"   Risk Level: {results.risk_level}")
    
    print("\n" + "="*60)
    print("✓ SUCCESS - Stockfish analysis is working!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
