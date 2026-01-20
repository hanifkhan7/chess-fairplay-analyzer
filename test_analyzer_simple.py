#!/usr/bin/env python3
"""Test analyzer with fresh load"""
import sys
import os

# Clean imports
for key in list(sys.modules.keys()):
    if 'chess_analyzer' in key:
        del sys.modules[key]

os.chdir('c:\\Users\\zaibi\\chess-fairplay-analyzer')

# Now import
from chess_analyzer.fetcher import fetch_player_games
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
from chess_analyzer.utils.helpers import load_config

username = "hikaru"
max_games = 3  # Use fewer games for quick test

print(f"[TEST] Fetching up to {max_games} games for {username}...")
games = fetch_player_games(username, max_games)
print(f"[TEST] Retrieved {len(games)} games")

if not games:
    print("[ERROR] No games retrieved")
    sys.exit(1)

print(f"\n[TEST] Initializing analyzer...")
config = load_config()
analyzer = EnhancedPlayerAnalyzer(config, use_lichess=True)

print(f"[TEST] Running analysis...")
try:
    results = analyzer.analyze_games_fast(games, username, max_workers=1)
    print(f"[TEST] Analysis complete. Results: {results}")
except Exception as e:
    print(f"[ERROR] Analysis failed: {e}")
    import traceback
    traceback.print_exc()
