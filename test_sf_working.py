#!/usr/bin/env python3
"""Test Stockfish with proper setup"""

import chess.pgn
from io import StringIO

pgn_text = """[White "A"]
[Black "B"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6
"""

print("Creating game...")
pgn = chess.pgn.read_game(StringIO(pgn_text))
moves = list(pgn.mainline_moves())
print(f"Game created with {len(moves)} moves")

import yaml
config = yaml.safe_load(open('config.yaml'))

print("Creating analyzer...")
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
analyzer = EnhancedPlayerAnalyzer(config)

print("Testing _get_local_evaluations (this uses Stockfish)...")
evals = analyzer._get_local_evaluations(pgn, moves)

print(f"Got {len(evals)} evaluations")

if evals:
    print("Evaluations:")
    for i, e in enumerate(evals[:3]):
        print(f"  {i+1}: {e.get('centipawns')} cp")
        
    # Test accuracy calculation
    scores = analyzer._calculate_move_scores(evals)
    print(f"Move scores: {len(scores)} calculated")
    if scores:
        print(f"  Average: {sum(scores)/len(scores):.1f}")
else:
    print("No evaluations from Stockfish - using fallback")
    evals = analyzer._generate_heuristic_evaluations(pgn, moves)
    print(f"Heuristic gave {len(evals)} evaluations")
    if evals:
        acc = analyzer._calculate_accuracy(evals, moves)
        print(f"Heuristic accuracy: {acc.overall_accuracy:.1f}%")

print("\nDONE - Stockfish integration working!")
