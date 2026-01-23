#!/usr/bin/env python3
"""Quick Stockfish test with progress"""

import chess.pgn
from io import StringIO
import sys

pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Player2"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4
"""

print("1. Loading...")
sys.stdout.flush()

pgn = chess.pgn.read_game(StringIO(pgn_text))
moves = list(pgn.mainline_moves())

print(f"2. Loaded {len(moves)} moves")
sys.stdout.flush()

import yaml
config = yaml.safe_load(open('config.yaml'))

print("3. Importing analyzer...")
sys.stdout.flush()

from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
analyzer = EnhancedPlayerAnalyzer(config)

print("4. Testing local evaluations...")
sys.stdout.flush()

evals = analyzer._get_local_evaluations(pgn, moves)

print(f"5. Got {len(evals)} evaluations from Stockfish")
sys.stdout.flush()

if evals:
    print("Stockfish evaluations:")
    for i, e in enumerate(evals[:3]):
        print(f"  Move {i+1}: {e.get('centipawns')} cp")
    
    scores = analyzer._calculate_move_scores(evals)
    print(f"Move scores: {[f'{s:.0f}' for s in scores]}")
    
    acc = analyzer._calculate_accuracy(evals, moves)
    print(f"Accuracy: {acc.overall_accuracy:.1f}%")
else:
    print("No evaluations returned")

print("\nDONE")
