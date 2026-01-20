#!/usr/bin/env python3
"""Test analyzer with hardcoded values"""

print("START")

from chess_analyzer.fetcher import fetch_player_games
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
from chess_analyzer.utils.helpers import load_config

print("IMPORTS DONE")

games = fetch_player_games("hikaru", 5)
print(f"FETCHED {len(games)} GAMES")

config = load_config()
analyzer = EnhancedPlayerAnalyzer(config, use_lichess=True)

print("ANALYZER CREATED")

results = analyzer.analyze_games_fast(games, "hikaru", max_workers=4)

print("ANALYSIS DONE")

display_enhanced_analysis(results, "hikaru")

print("DISPLAY DONE")
