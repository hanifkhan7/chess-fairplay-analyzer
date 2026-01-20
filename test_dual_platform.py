#!/usr/bin/env python3
"""Test dual-platform game fetching"""
import sys
import os

print("[START]", flush=True)

os.chdir('c:\\Users\\zaibi\\chess-fairplay-analyzer')

from chess_analyzer.dual_fetcher import fetch_dual_platform_games
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
from chess_analyzer.utils.helpers import load_config

username = "hikaru"

print("\n" + "="*80)
print("[TEST] DUAL-PLATFORM ANALYZER TEST")
print("="*80)

# Test 1: Fetch from both platforms
print("\n[TEST1] Fetching from both Chess.com and Lichess...")
games, counts = fetch_dual_platform_games(username, max_games=10, platforms=['chess.com', 'lichess'])

print(f"[TEST1] Fetched {len(games)} total games")

if not games:
    print("[ERROR] No games fetched")
    sys.exit(1)

# Test 2: Analyze games
print("\n[TEST2] Analyzing games...", flush=True)
config = load_config()
analyzer = EnhancedPlayerAnalyzer(config, use_lichess=True, use_chess_com=True)

results = analyzer.analyze_games_fast(games, username, max_workers=4)
results['platform_breakdown'] = counts

# Test 3: Display results
print("\n[TEST3] Displaying results...\n")
display_enhanced_analysis(results, username)

print("\n[SUCCESS] Dual-platform test completed!")
