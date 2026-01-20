#!/usr/bin/env python3
"""Comprehensive dual-platform test"""
import sys
import os

os.chdir('c:\\Users\\zaibi\\chess-fairplay-analyzer')

print("[TEST-START]")

# Test 1: Import check
print("\n[TEST1] Checking imports...")
try:
    from chess_analyzer.dual_fetcher import fetch_dual_platform_games
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
    from chess_analyzer.menu import _fetch_games
    print("[OK] All imports successful")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

# Test 2: Dual-fetch Chess.com only
print("\n[TEST2] Testing Chess.com fetch...")
try:
    games, counts = fetch_dual_platform_games('hikaru', max_games=3, platforms=['chess.com'])
    print(f"[OK] Chess.com: {len(games)} games")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 3: Analyze the games
print("\n[TEST3] Analyzing games...")
try:
    from chess_analyzer.utils.helpers import load_config
    config = load_config()
    analyzer = EnhancedPlayerAnalyzer(config, use_lichess=True, use_chess_com=True)
    
    if games:
        results = analyzer.analyze_games_fast(games, 'hikaru', max_workers=2)
        results['platform_breakdown'] = counts
        print(f"[OK] Analyzed {results.get('games_analyzed', 0)} games")
        
        # Test 4: Display results
        print("\n[TEST4] Displaying results:")
        display_enhanced_analysis(results, 'hikaru')
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST-COMPLETE]")
