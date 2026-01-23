#!/usr/bin/env python3
"""Test Stockfish integration with analyzer"""

import chess.pgn
from io import StringIO
import yaml

pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6
"""

try:
    print("=" * 80)
    print("[TEST] STOCKFISH INTEGRATION")
    print("=" * 80)
    
    print("\n[STEP 1] Loading game and config...")
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    moves = list(pgn.mainline_moves())
    config = yaml.safe_load(open('config.yaml'))
    
    print(f"Game loaded with {len(moves)} moves")
    
    print("\n[STEP 2] Testing Stockfish evaluations directly...")
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # This will try to use Stockfish
    print("(Running Stockfish analysis - this takes a few seconds...)")
    stockfish_evals = analyzer._get_local_evaluations(pgn, moves)
    
    print(f"Stockfish returned {len(stockfish_evals)} evaluations")
    
    if stockfish_evals:
        print("\nStockfish Evaluations (first 5):")
        for i, e in enumerate(stockfish_evals[:5]):
            cp = e.get('centipawns', 0)
            print(f"  Move {i+1}: {cp} cp")
        
        # Calculate move scores
        scores = analyzer._calculate_move_scores(stockfish_evals)
        print(f"\nMove Scores ({len(scores)} total):")
        print(f"  Range: {min(scores):.1f} - {max(scores):.1f}")
        print(f"  Average: {sum(scores)/len(scores):.1f}")
        
        # Calculate accuracy
        accuracy = analyzer._calculate_accuracy(stockfish_evals, moves)
        print(f"\nAccuracy Metrics:")
        print(f"  Overall: {accuracy.overall_accuracy:.1f}%")
        
        print(f"\n[SUCCESS] Stockfish is working and returning proper evaluations!")
    else:
        print("\n[WARNING] Stockfish returned empty list")
        print("Trying fallback to heuristic...")
        heur_evals = analyzer._generate_heuristic_evaluations(pgn, moves)
        print(f"Heuristic returned {len(heur_evals)} evaluations")
        
        if heur_evals:
            accuracy = analyzer._calculate_accuracy(heur_evals, moves)
            print(f"Heuristic accuracy: {accuracy.overall_accuracy:.1f}%")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
