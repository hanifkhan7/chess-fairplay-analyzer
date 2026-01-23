#!/usr/bin/env python3
"""Final verification test with Stockfish"""

import chess.pgn
from io import StringIO
import yaml

pgn_text = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 
6. Bg5 e6 7. f4 Be7 8. Qf3 Nbd7 9. O-O-O b5
"""

try:
    print("[SETUP] Loading game and analyzer...")
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    config = yaml.safe_load(open('config.yaml'))
    
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
    analyzer = EnhancedPlayerAnalyzer(config)
    
    print("[ANALYSIS] Running full analyzer with Stockfish...")
    results = analyzer.analyze_games_fast([pgn], "Player1", max_workers=1)
    
    print("\n[RESULTS]")
    print(f"Games analyzed: {results.get('games_analyzed')}")
    print(f"Average accuracy: {results.get('avg_accuracy'):.1f}%")
    
    # Display full output
    print("\n[DISPLAY]")
    display_enhanced_analysis(results, "Player1")
    
    print("\n[SUCCESS] Test complete - Stockfish integration working!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()


    import traceback
    traceback.print_exc()
    sys.exit(1)
