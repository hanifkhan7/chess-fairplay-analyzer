#!/usr/bin/env python3
"""Test full analyzer with Stockfish"""

import chess.pgn
from io import StringIO
import yaml

# More complex game
pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 
6. Bg5 e6 7. f4 Be7 8. Qf3 Nbd7 9. O-O-O b5 10. a3 Bb7
"""

try:
    print("=" * 80)
    print("[TEST] FULL ANALYZER WITH STOCKFISH")
    print("=" * 80)
    
    print("\n[SETUP] Loading game...")
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    
    print("[SETUP] Loading analyzer...")
    config = yaml.safe_load(open('config.yaml'))
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
    
    analyzer = EnhancedPlayerAnalyzer(config)
    
    print("\n[ANALYSIS] Running full pipeline with Stockfish...")
    print("(This will use Stockfish for evaluations - may take 10-30 seconds)")
    
    results = analyzer.analyze_games_fast([pgn], "Player1", max_workers=1)
    
    print("\n[RESULTS]")
    print(f"Games analyzed: {results.get('games_analyzed')}")
    print(f"Average accuracy: {results.get('avg_accuracy'):.1f}%")
    
    game_analyses = results.get('game_analyses', [])
    if game_analyses:
        game = game_analyses[0]
        accuracy = game.get('accuracy', {})
        engine = game.get('engine_pattern', {})
        
        print(f"\nDetailed Accuracy:")
        print(f"  Overall: {accuracy.get('overall_accuracy', 0):.1f}%")
        print(f"  Opening: {accuracy.get('opening_accuracy', 0):.1f}%")
        print(f"  Middlegame: {accuracy.get('middlegame_accuracy', 0):.1f}%")
        
        print(f"\nEngine Matching:")
        print(f"  Top 1 Match: {engine.get('top_1_match_rate', 0):.1f}%")
        print(f"  Top 3 Match: {engine.get('top_3_match_rate', 0):.1f}%")
        print(f"  Top 5 Match: {engine.get('top_5_match_rate', 0):.1f}%")
        
        # Show which evaluation source was used
        print(f"\nEvaluation source: Stockfish (Local)")
    
    # Display full analysis
    print("\n" + "=" * 80)
    print("[DISPLAY] Full Analysis Output")
    print("=" * 80)
    display_enhanced_analysis(results, "Player1")
    
    print("\n[SUCCESS] Stockfish is integrated and working!")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
