#!/usr/bin/env python3
"""Minimal test without cache"""

import chess.pgn
from io import StringIO

pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 1-0
"""

print("1. Loading PGN...")
pgn = chess.pgn.read_game(StringIO(pgn_text))

print("2. Creating analyzer...")
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
analyzer = EnhancedPlayerAnalyzer({})

print("3. Getting moves...")
moves = list(pgn.mainline_moves())
print(f"   Moves: {len(moves)}")

print("4. Getting evaluations...")
evals = analyzer._get_evaluations(pgn, moves)
print(f"   Evals: {len(evals)}")

print("5. Calculating move scores...")
scores = analyzer._calculate_move_scores(evals)
print(f"   Scores: {len(scores)}")

print("6. Calculating accuracy...")
accuracy = analyzer._calculate_accuracy(evals, moves)
print(f"   Overall: {accuracy.overall_accuracy}%")

print("\n✓ Done!")
