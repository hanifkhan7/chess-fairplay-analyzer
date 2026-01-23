#!/usr/bin/env python3
"""Minimal test of _get_local_evaluations"""

print("1. Importing chess...")
import chess
import chess.pgn
from io import StringIO

print("2. Creating game...")
pgn_text = "1. e4 c5 2. Nf3 d6"
pgn = chess.pgn.read_game(StringIO(f"[White \"A\"]\\n[Black \"B\"]\\n\\n{pgn_text}"))
moves = list(pgn.mainline_moves())
print(f"   Moves: {len(moves)}")

print("3. Creating analyzer...")
import yaml
config = yaml.safe_load(open('config.yaml'))

print("4. Importing analyzer class...")
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer

print("5. Instantiating analyzer...")
analyzer = EnhancedPlayerAnalyzer(config)

print("6. Calling _get_local_evaluations...")
evals = analyzer._get_local_evaluations(pgn, moves)

print(f"7. Got {len(evals)} evaluations")
print("DONE")
