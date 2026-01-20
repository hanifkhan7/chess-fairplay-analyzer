#!/usr/bin/env python
"""Test game conversion from actual Lichess fetch"""
import sys
sys.path.insert(0, '.')

from chess_analyzer.menu import _fetch_games
from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer
import chess.pgn

config = {
    'DEFAULT_PLATFORM': 'lichess',
}

# Fetch a small number of games
print("Fetching 5 games from Lichess for hikaru...")
games, counts = _fetch_games('hikaru', 5, ['lichess'], config)

print(f"Got {len(games)} games")
if games:
    g = games[0]
    print(f"\nFirst game type: {type(g)}")
    print(f"Is chess.pgn.Game: {isinstance(g, chess.pgn.Game)}")
    
    if isinstance(g, chess.pgn.Game):
        print(f"Headers: {dict(g.headers)}")
        print(f"\nTesting conversion...")
        analyzer = HeadToHeadAnalyzer()
        game_dict = analyzer._convert_game_to_dict(g)
        print(f"Converted game:")
        for key in ['result', 'opponent', 'opponent_elo', 'opening', 'moves']:
            print(f"  {key}: {game_dict.get(key)}")
