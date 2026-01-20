#!/usr/bin/env python3
"""Quick test of analyzer v3.0 with debugging"""

import sys
sys.path.insert(0, 'c:\\Users\\zaibi\\chess-fairplay-analyzer')

from chess_analyzer.fetcher import fetch_player_games
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer

username = "hikaru"
games_to_fetch = 5

print(f"Fetching {games_to_fetch} games for {username}...")
games = fetch_player_games(username, games_to_fetch)
print(f"✓ Fetched {len(games)} games")

analyzer = EnhancedPlayerAnalyzer()
print("\nAnalyzing games...")
results = analyzer.analyze_games_fast(games, username, analysis_mode=1)

print(f"\nResults: {results}")
