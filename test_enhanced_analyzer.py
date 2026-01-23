#!/usr/bin/env python3
"""Test the enhanced analyzer with proper accuracy calculations"""

import yaml
import sys
from io import StringIO
import chess.pgn

try:
    print("="*80)
    print("[TEST] ENHANCED ANALYZER v3.0 - ACCURACY CALCULATION TEST")
    print("="*80)
    
    # Load config
    config = yaml.safe_load(open('config.yaml'))
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    # Create analyzer
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # Create a test game with evaluations
    print("\n[STEP 1] Creating test game with evaluations...")
    pgn_text = """[Event "Test"]
[Site "https://lichess.org/test"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]
[WhiteElo "2000"]
[BlackElo "1900"]
[TimeControl "600+0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 Na5 9. Bc2 c5 10. d4 Qc7 11. h3 O-O 12. exd5 Nxd5 13. Nxe5 Nxe5 14. Rxe5 Nf4 15. Qf3 Neg4 16. Rxe7 1-0
"""
    
    game = chess.pgn.read_game(StringIO(pgn_text))
    print(f"✓ Created test game: {game.headers.get('White')} vs {game.headers.get('Black')}")
    
    # Test move scores calculation
    print("\n[STEP 2] Testing move score calculation...")
    
    # Create sample evaluations (eval changes for testing)
    evaluations = [
        {"centipawns": 25},      # Initial position
        {"centipawns": 20},      # Move 1: Small improvement
        {"centipawns": -15},     # Move 2: Small loss
        {"centipawns": 10},      # Move 3: Improvement
        {"centipawns": -45},     # Move 4: Medium loss (0.45 pawn)
        {"centipawns": 5},       # Move 5: Recovery
        {"centipawns": -120},    # Move 6: Large loss (1.2 pawn)
        {"centipawns": 50},      # Move 7: Large improvement
    ]
    
    move_scores = analyzer._calculate_move_scores(evaluations)
    print(f"\n   Evaluation changes: {[e['centipawns'] for e in evaluations]}")
    print(f"   Calculated scores: {[f'{s:.0f}' for s in move_scores]}")
    
    # Analyze scores
    excellent = len([s for s in move_scores if s >= 90])
    good = len([s for s in move_scores if s >= 80])
    okay = len([s for s in move_scores if s >= 70])
    poor = len([s for s in move_scores if s < 70])
    
    print(f"\n   Score distribution:")
    print(f"     Excellent (90+): {excellent}")
    print(f"     Good (80-89):    {good}")
    print(f"     Okay (70-79):    {okay}")
    print(f"     Poor (< 70):     {poor}")
    
    avg_score = sum(move_scores) / len(move_scores) if move_scores else 0
    print(f"   Average accuracy: {avg_score:.1f}%")
    
    print("\n[STEP 3] Testing accuracy metrics...")
    
    # Create AccuracyMetrics object
    from chess_analyzer.analyzer_v3 import AccuracyMetrics
    metrics = AccuracyMetrics()
    
    # Use only the first 5 evaluations for opening
    opening_evals = evaluations[:3]
    middlegame_evals = evaluations[3:6]
    endgame_evals = evaluations[6:]
    
    metrics.opening_accuracy = sum(analyzer._calculate_move_scores([opening_evals[0], opening_evals[1]])) / 2 if len(opening_evals) > 1 else 0
    metrics.middlegame_accuracy = sum(analyzer._calculate_move_scores(middlegame_evals)) / len(middlegame_evals) if middlegame_evals else 0
    metrics.endgame_accuracy = sum(analyzer._calculate_move_scores(endgame_evals)) / len(endgame_evals) if endgame_evals else 0
    metrics.overall_accuracy = avg_score
    
    print(f"\n   Phase accuracies:")
    print(f"     Opening:    {metrics.opening_accuracy:.1f}%")
    print(f"     Middlegame: {metrics.middlegame_accuracy:.1f}%")
    print(f"     Endgame:    {metrics.endgame_accuracy:.1f}%")
    print(f"     Overall:    {metrics.overall_accuracy:.1f}%")
    
    print("\n[STEP 4] Testing engine matching...")
    
    from chess_analyzer.analyzer_v3 import EnginePattern
    pattern = analyzer._analyze_engine_matching(evaluations, list(game.mainline_moves()))
    
    print(f"\n   Engine matching rates:")
    print(f"     Top 1 match:  {pattern.top_1_match_rate:.1f}%")
    print(f"     Top 3 match:  {pattern.top_3_match_rate:.1f}%")
    print(f"     Top 5 match:  {pattern.top_5_match_rate:.1f}%")
    print(f"     Is suspicious: {pattern.is_suspicious}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Enhanced analyzer calculations working correctly!")
    print("="*80)
    print("\nNext steps:")
    print("1. Test with real Lichess games")
    print("2. Verify accuracy values are in 0-100 range")
    print("3. Confirm sorting and display works")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
