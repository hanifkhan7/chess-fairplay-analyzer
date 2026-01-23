#!/usr/bin/env python3
"""Simple accuracy test"""

import chess.pgn
from io import StringIO

print("Starting accuracy test...")

pgn_text = """[Event "Test"]
[Site "https://lichess.org/test123456"]
[White "Player1"]
[Black "Player2"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1-0
"""

try:
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    print(f"Game loaded: {pgn.headers.get('Event', 'N/A')}")
    
    moves = list(pgn.mainline_moves())
    print(f"Moves: {len(moves)}")
    
    # Import analyzer
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    print("Initializing analyzer...")
    config = {}
    analyzer = EnhancedPlayerAnalyzer(config)
    
    print("Getting evaluations...")
    evals = analyzer._get_evaluations(pgn, moves)
    print(f"Evaluations: {len(evals)}")
    
    print("Calculating move scores...")
    scores = analyzer._calculate_move_scores(evals)
    print(f"Scores: {len(scores)}, values: {scores}")
    
    print("Calculating accuracy...")
    accuracy = analyzer._calculate_accuracy(evals, moves)
    print(f"Accuracy: {accuracy.overall_accuracy}%")
    
    print("\n✓ Test complete!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
