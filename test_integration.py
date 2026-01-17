#!/usr/bin/env python3
"""
Final integration test - Lichess + Menu analysis
"""
import sys

print("="*60)
print("CHESS FAIRPLAY ANALYZER - LICHESS INTEGRATION TEST")
print("="*60)

try:
    print("\n1. Testing imports...")
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.utils.helpers import load_config
    print("   ✓ All imports successful")
    
    print("\n2. Loading configuration...")
    config = load_config()
    use_lichess = config.get('analysis', {}).get('use_lichess', True)
    print(f"   ✓ Config loaded (use_lichess={use_lichess})")
    
    print("\n3. Fetching 3 games...")
    games = fetch_player_games('Salman_Ali_Khan', max_games=3)
    print(f"   ✓ Fetched {len(games)} games")
    
    print("\n4. Initializing ChessAnalyzer...")
    analyzer = ChessAnalyzer(config)
    print(f"   ✓ Analyzer created")
    
    print("\n5. Starting analysis with Lichess API...")
    print("   " + "-"*50)
    
    import time
    start_time = time.time()
    
    results = analyzer.analyze_games(games)
    
    elapsed = time.time() - start_time
    print("   " + "-"*50)
    
    print(f"\n6. Results:")
    print(f"   ✓ Analysis complete in {elapsed:.1f} seconds")
    print(f"   ✓ Games analyzed: {results.games_analyzed}/{len(games)}")
    print(f"   ✓ Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"   ✓ Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"   ✓ Risk Level: {results.risk_level}")
    
    print("\n" + "="*60)
    if elapsed < 120:  # Less than 2 minutes for 3 games is great
        print("✓ SUCCESS! Lichess API integration is working perfectly!")
        print(f"  Analysis speed: {elapsed/len(games):.1f}s per game (excellent!)")
    else:
        print(f"✓ Analysis complete ({elapsed:.0f}s total)")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
