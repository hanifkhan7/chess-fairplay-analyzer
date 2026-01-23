#!/usr/bin/env python3
"""Test Stockfish with different depth levels to show accuracy improvement"""

import chess.pgn
from io import StringIO
import yaml
import time

# Test game
pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2700"]
[BlackElo "2600"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 
6. Bg5 e6 7. f4 Be7 8. Qf3 Nbd7 9. O-O-O b5
"""

try:
    print("="*80)
    print("[TEST] STOCKFISH DEPTH COMPARISON")
    print("="*80)
    print("\nTesting move evaluation accuracy at different Stockfish depths...")
    
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    moves = list(pgn.mainline_moves())
    
    config = yaml.safe_load(open('config.yaml'))
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    # Test different depths
    depths_to_test = [16, 20, 24]
    results = {}
    
    for depth in depths_to_test:
        print(f"\n[DEPTH {depth}] Analyzing with Stockfish depth {depth}...")
        
        # Update config with depth
        config['analysis']['engine_depth'] = depth
        analyzer = EnhancedPlayerAnalyzer(config)
        
        start = time.time()
        evals = analyzer._get_local_evaluations(pgn, moves)
        elapsed = time.time() - start
        
        if evals:
            scores = analyzer._calculate_move_scores(evals)
            accuracy = analyzer._calculate_accuracy(evals, moves)
            
            print(f"  Time: {elapsed:.1f}s")
            print(f"  Evaluations: {len(evals)}")
            print(f"  Move Scores: {[f'{s:.0f}' for s in scores[:5]]} ...")
            print(f"  Accuracy: {accuracy.overall_accuracy:.1f}%")
            print(f"  Opening: {accuracy.opening_accuracy:.1f}%")
            print(f"  Middlegame: {accuracy.middlegame_accuracy:.1f}%")
            
            results[depth] = {
                'time': elapsed,
                'accuracy': accuracy.overall_accuracy,
                'evals': len(evals)
            }
        else:
            print("  [ERROR] Stockfish returned no evaluations")
    
    # Summary
    print("\n" + "="*80)
    print("[SUMMARY] Depth Comparison")
    print("="*80)
    
    if results:
        print("\nDepth | Time    | Accuracy | Evaluations")
        print("-" * 50)
        for depth in sorted(results.keys()):
            r = results[depth]
            print(f"{depth:5d} | {r['time']:7.1f}s | {r['accuracy']:8.1f}% | {r['evals']:11d}")
        
        print("\n[RECOMMENDATION]")
        print("For Super GMs like Hikaru:")
        print("  Use Depth 20 (30-60s per game)")
        print("  Balances accuracy with reasonable analysis time")
        print()
        print("For Ultra-precise analysis:")
        print("  Use Depth 24 (2-5 min per game)")
        print("  For detecting subtle assistance")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
