#!/usr/bin/env python3
"""Test just the Lichess analyzer import"""
import sys
import time

try:
    print("1. Testing Lichess analyzer import...")
    from chess_analyzer.lichess_analyzer import LichessAnalyzer
    print("   OK")
    
    print("2. Creating Lichess analyzer instance...")
    analyzer = LichessAnalyzer()
    print("   OK")
    
    print("3. Fetching a game...")
    from chess_analyzer.fetcher import fetch_player_games
    games = fetch_player_games('Salman_Ali_Khan', max_games=1)
    print(f"   OK - Got {len(games)} game(s)")
    
    if games:
        print("4. Starting Lichess analysis (this should be fast)...")
        start = time.time()
        result = analyzer.analyze_game(games[0])
        elapsed = time.time() - start
        
        print(f"   Completed in {elapsed:.1f} seconds")
        print(f"\n   Analysis result keys: {list(result.keys())}")
        if 'error' in result:
            print(f"   ERROR: {result['error']}")
        else:
            print(f"   Positions analyzed: {len(result.get('positions', []))}")
            print(f"   Engine correlation: {result.get('engine_correlation', 0):.1f}%")
            print("\n✓ Lichess analyzer working!")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
