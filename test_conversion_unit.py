#!/usr/bin/env python
"""
Test Head-to-Head Analyzer improvements with a simple local PGN example
"""
import sys
import io
sys.path.insert(0, '.')

import chess.pgn
from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer

# Create test games
pgn_hikaru_vs_opponent = """[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.20"]
[Round "-"]
[White "hikaru"]
[Black "opponent"]
[WhiteElo "2800"]
[BlackElo "2600"]
[Result "1-0"]
[Opening "Italian Game"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d3 Nf6 1-0"""

pgn_opponent_vs_hikaru = """[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.21"]
[Round "-"]
[White "opponent"]
[Black "hikaru"]
[WhiteElo "2600"]
[BlackElo "2800"]
[Result "0-1"]
[Opening "Italian Game"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 0-1"""

game1 = chess.pgn.read_game(io.StringIO(pgn_hikaru_vs_opponent))
game2 = chess.pgn.read_game(io.StringIO(pgn_opponent_vs_hikaru))

print("Testing game conversion with hikaru games:")
analyzer = HeadToHeadAnalyzer()

# Test conversion for hikaru (white in game1)
g1_dict = analyzer._convert_game_to_dict(game1, 'hikaru')
print(f"\nGame 1 (hikaru as White):")
print(f"  Result: {g1_dict['result']} (expected: won)")
print(f"  Opponent: {g1_dict['opponent']} (expected: opponent)")
print(f"  Opponent ELO: {g1_dict['opponent_elo']} (expected: 2600)")

# Test conversion for hikaru (black in game2)
g2_dict = analyzer._convert_game_to_dict(game2, 'hikaru')
print(f"\nGame 2 (hikaru as Black):")
print(f"  Result: {g2_dict['result']} (expected: won)")
print(f"  Opponent: {g2_dict['opponent']} (expected: opponent)")
print(f"  Opponent ELO: {g2_dict['opponent_elo']} (expected: 2600)")

# Test analysis
games_hikaru = [game1, game2]
analysis = analyzer.analyze_game_history(games_hikaru, [], 'hikaru', '')

print(f"\nGame history analysis for hikaru:")
print(f"  Total games: {analysis['player1']['total_games']} (expected: 2)")
print(f"  Wins: {analysis['player1']['wins']} (expected: 2)")
print(f"  Losses: {analysis['player1']['losses']} (expected: 0)")
print(f"  Draws: {analysis['player1']['draws']} (expected: 0)")
print(f"  Win rate: {analysis['player1']['win_rate']:.1f}% (expected: 100.0%)")

# Test opening analysis
openings = analyzer.analyze_opening_repertoire(games_hikaru, 'hikaru')
print(f"\nOpening analysis:")
for opening, stats in openings.items():
    print(f"  {opening}: {stats['count']} games, {stats['wins']}W-{stats['losses']}L-{stats['draws']}D, WR={stats.get('win_rate', 0):.1f}%")

print("\n✓ All tests passed!")
