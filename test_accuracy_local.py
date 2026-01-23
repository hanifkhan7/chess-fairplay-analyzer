#!/usr/bin/env python3
"""Debug test with local PGN to test accuracy calculation"""

import yaml
import sys
import chess.pgn
from io import StringIO

try:
    print("="*80)
    print("[DEBUG] ACCURACY CALCULATION TEST - LOCAL GAME")
    print("="*80)
    
    # Create a test PGN with real move patterns
    pgn_text = """[Event "Test"]
[Site "https://lichess.org/test123456"]
[Date "2024.01.01"]
[Round "-"]
[White "WhitePlayer"]
[Black "BlackPlayer"]
[WhiteElo "2500"]
[BlackElo "2400"]
[TimeControl "300+3"]
[Result "1-0"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Bg5 e6 7. f4 Be7
8. Qf3 Nbd7 9. O-O-O b5 10. a3 Bb7 11. Bxf6 Nxf6 12. Kb1 Rc8 13. g4 b4
14. axb4 Rxc3 15. bxc3 Qb6 16. Qg3 Qxb4+ 17. Kc1 h6 18. e5 dxe5 19. fxe5
Ng4 20. Bh5 Qd6 21. e6 fxe6 22. Qxg4 Qd5 23. Qxd5+ exd5 24. Bc6+ Kd8
25. Bxb7 a5 26. Bd5 a4 27. Nxe6+ Kd7 28. Nf4 a3 29. bxa3 d4 30. cxd4
Rc8+ 31. Kb1 Rc6 32. Bc4 Rc1+ 33. Kxc1 Kc6 34. Nd5 Kc5 35. Nxe7+ Kd5 1-0
"""
    
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    print("✓ Created test game from PGN")
    
    # Load config
    config = yaml.safe_load(open('config.yaml'))
    
    # Extract moves
    moves = list(pgn.mainline_moves())
    print(f"✓ Extracted {len(moves)} moves from game")
    
    # Get evaluations
    print("\n[STEP 1] Testing evaluation methods...")
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # Test the 3-tier system
    evaluations = analyzer._get_evaluations(pgn, moves)
    print(f"✓ Got {len(evaluations)} evaluations")
    
    if evaluations:
        print(f"  Sample evals (first 5): {evaluations[:5]}")
        print(f"  Sample evals (last 5): {evaluations[-5:]}")
        
        # Check for heuristic flag
        heuristic_count = sum(1 for e in evaluations if e.get('heuristic', False))
        print(f"  Heuristic evaluations: {heuristic_count}/{len(evaluations)}")
        
        # Check centipawn values
        cp_values = [e.get('centipawns', 0) for e in evaluations if e.get('centipawns') is not None]
        if cp_values:
            print(f"  CP values: min={min(cp_values)}, max={max(cp_values)}, mean={sum(cp_values)/len(cp_values):.0f}")
    
    # Calculate move scores
    print("\n[STEP 2] Testing move score calculation...")
    move_scores = analyzer._calculate_move_scores(evaluations)
    print(f"✓ Calculated {len(move_scores)} move scores")
    
    if move_scores:
        print(f"  Sample scores (first 5): {[f'{s:.0f}' for s in move_scores[:5]]}")
        print(f"  Sample scores (last 5): {[f'{s:.0f}' for s in move_scores[-5:]]}")
        avg_score = sum(move_scores) / len(move_scores)
        print(f"  Score range: {min(move_scores):.1f} - {max(move_scores):.1f}")
        print(f"  Average: {avg_score:.1f}")
        
        # Distribution
        excellent = sum(1 for s in move_scores if s >= 90)
        good = sum(1 for s in move_scores if 80 <= s < 90)
        okay = sum(1 for s in move_scores if 70 <= s < 80)
        poor = sum(1 for s in move_scores if s < 70)
        print(f"  Distribution: Excellent({excellent}) Good({good}) Okay({okay}) Poor({poor})")
    
    # Calculate accuracy
    print("\n[STEP 3] Testing accuracy calculation...")
    accuracy = analyzer._calculate_accuracy(evaluations, moves)
    print(f"✓ Accuracy metrics:")
    print(f"  Overall: {accuracy.overall_accuracy:.1f}%")
    print(f"  Opening: {accuracy.opening_accuracy:.1f}%")
    print(f"  Middlegame: {accuracy.middlegame_accuracy:.1f}%")
    print(f"  Endgame: {accuracy.endgame_accuracy:.1f}%")
    print(f"  Consistency StdDev: {accuracy.consistency_std_dev:.1f}")
    
    if accuracy.overall_accuracy == 0.0:
        print("\n  ⚠️ WARNING: Overall accuracy is 0.0%")
        print(f"     Evaluations length: {len(evaluations)}")
        print(f"     Move scores length: {len(move_scores)}")
        
    # Now test with the full analyze_games_fast
    print("\n[STEP 4] Testing full analysis pipeline...")
    results = analyzer.analyze_games_fast([pgn], "test_user", max_workers=1)
    
    print(f"✓ Results compiled:")
    print(f"  Games analyzed: {results.get('games_analyzed', 0)}")
    print(f"  Avg accuracy: {results.get('avg_accuracy', 0):.1f}%")
    
    # Check game analyses
    game_analyses = results.get('game_analyses', [])
    if game_analyses:
        game_data = game_analyses[0]
        print(f"\n  Game analysis accuracy field:")
        accuracy_field = game_data.get('accuracy', {})
        print(f"    Type: {type(accuracy_field)}")
        print(f"    Value: {accuracy_field}")
        
        if isinstance(accuracy_field, dict):
            print(f"    Overall: {accuracy_field.get('overall_accuracy', 'N/A')}%")
    
    print("\n" + "="*80)
    
    # Summary
    if results.get('avg_accuracy', 0) == 0.0:
        print("[FAIL] Analysis still showing 0.0% accuracy")
        print("  Debug needed in accuracy calculation pipeline")
    else:
        print(f"[SUCCESS] Accuracy is being calculated: {results.get('avg_accuracy', 0):.1f}%")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
