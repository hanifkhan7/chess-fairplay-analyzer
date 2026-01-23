#!/usr/bin/env python3
"""Test local Stockfish evaluations"""

import chess.pgn
from io import StringIO
import yaml

pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 
6. Bg5 e6 7. f4 Be7 8. Qf3 Nbd7 9. O-O-O b5
"""

print("=" * 80)
print("[TEST] LOCAL STOCKFISH EVALUATION")
print("=" * 80)

try:
    print("\n[STEP 1] Loading game...")
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    moves = list(pgn.mainline_moves())
    print(f"Game loaded with {len(moves)} moves")
    
    print("\n[STEP 2] Initializing analyzer...")
    config = yaml.safe_load(open('config.yaml'))
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # Test each evaluation method directly
    print("\n[STEP 3] Testing Lichess API...")
    lichess_evals = analyzer._get_lichess_evaluations(pgn)
    print(f"Lichess evaluations: {len(lichess_evals)}")
    if lichess_evals:
        print(f"  Sample: {lichess_evals[0]}")
    
    print("\n[STEP 4] Testing Local Stockfish...")
    print("(Note: This may take 30-60 seconds if Stockfish is available)")
    
    import time
    start = time.time()
    stockfish_evals = analyzer._get_local_evaluations(pgn, moves)
    elapsed = time.time() - start
    
    print(f"Stockfish evaluations: {len(stockfish_evals)} in {elapsed:.1f}s")
    if stockfish_evals:
        print(f"  First 5 evaluations:")
        for i, e in enumerate(stockfish_evals[:5]):
            cp = e.get('centipawns', 'N/A')
            print(f"    Move {i+1}: CP={cp}")
        
        # Calculate move scores from stockfish evals
        scores = analyzer._calculate_move_scores(stockfish_evals)
        if scores:
            print(f"  Move scores calculated: {len(scores)}")
            print(f"  Score range: {min(scores):.1f} - {max(scores):.1f}")
            print(f"  Average score: {sum(scores)/len(scores):.1f}")
    else:
        print("  [WARNING] Stockfish returned no evaluations")
        print("  This might mean Stockfish is not installed or not configured")
    
    print("\n[STEP 5] Testing Heuristic Fallback...")
    heuristic_evals = analyzer._generate_heuristic_evaluations(pgn, moves)
    print(f"Heuristic evaluations: {len(heuristic_evals)}")
    if heuristic_evals:
        print(f"  First 5 evaluations:")
        for i, e in enumerate(heuristic_evals[:5]):
            cp = e.get('centipawns', 'N/A')
            print(f"    Move {i+1}: CP={cp}")
    
    print("\n[STEP 6] Testing 3-Tier System...")
    evals = analyzer._get_evaluations(pgn, moves)
    print(f"Total evaluations from 3-tier system: {len(evals)}")
    
    # Identify which tier was used
    has_stockfish = any(e.get('stockfish') for e in evals)
    has_heuristic = any(e.get('heuristic') for e in evals)
    
    if has_stockfish:
        print("  Source: Stockfish (Tier 2 - Local)")
    elif has_heuristic:
        print("  Source: Heuristic Fallback (Tier 3)")
    else:
        print("  Source: Lichess API (Tier 1)")
    
    # Calculate accuracy
    if evals:
        accuracy = analyzer._calculate_accuracy(evals, moves)
        print(f"  Calculated accuracy: {accuracy.overall_accuracy:.1f}%")
        print(f"    Opening: {accuracy.opening_accuracy:.1f}%")
        print(f"    Middlegame: {accuracy.middlegame_accuracy:.1f}%")
    
    print("\n" + "=" * 80)
    
    if has_stockfish:
        print("[SUCCESS] Stockfish is working correctly!")
    else:
        print("[INFO] Stockfish not available, using heuristic fallback")
        print("To enable Stockfish:")
        print("1. Download from https://stockfishchess.org")
        print("2. Extract to 'stockfish' folder in project root")
        print("3. Ensure file is: stockfish/stockfish-windows-x86-64.exe")
    
    print("=" * 80)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
