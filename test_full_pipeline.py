#!/usr/bin/env python3
"""Test full pipeline with display"""

import chess.pgn
from io import StringIO
from dataclasses import asdict

pgn_text = """[Event "Test"]
[Site "https://lichess.org/test123456"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1-0
"""

try:
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    print(f"Game loaded")
    
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    config = {}
    analyzer = EnhancedPlayerAnalyzer(config)
    
    print("\n[STEP 1] Analyzing single game...")
    analysis = analyzer._analyze_single_game(pgn, "Player1")
    print(f"Analysis object: {type(analysis)}")
    print(f"  Game ID: {analysis.game_id}")
    print(f"  Accuracy: {analysis.accuracy}")
    print(f"  Accuracy.overall_accuracy: {analysis.accuracy.overall_accuracy}%")
    
    print("\n[STEP 2] Converting to dict...")
    analysis_dict = asdict(analysis)
    print(f"Dict accuracy field: {analysis_dict.get('accuracy')}")
    
    print("\n[STEP 3] Compiling results...")
    results = analyzer._compile_analysis_results([analysis], "Player1")
    print(f"Results avg_accuracy: {results.get('avg_accuracy')}%")
    
    print("\n[STEP 4] Checking game_analyses...")
    game_analyses = results.get('game_analyses', [])
    if game_analyses:
        game = game_analyses[0]
        print(f"Game accuracy: {game.get('accuracy')}")
    
    print("\n✓ Test complete!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
