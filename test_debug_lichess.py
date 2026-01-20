#!/usr/bin/env python3
"""Debug Lichess fetch"""

from chess_analyzer.dual_fetcher import fetch_lichess_games

print("Testing fetch_lichess_games directly...")
try:
    games, count = fetch_lichess_games('Pap-G', 5)
    print(f"Result: {count} games, {len(games)} parsed")
    if games:
        print(f"First game: {games[0].headers.get('White')} vs {games[0].headers.get('Black')}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
