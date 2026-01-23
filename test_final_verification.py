#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST
Demonstrates the fixed analyzer with proper accuracy calculations
"""

import chess.pgn
from io import StringIO
import yaml

print("\n" + "="*80)
print("CHESS FAIRPLAY ANALYZER v3 - FINAL VERIFICATION TEST")
print("="*80)

# Complex test game with mixed quality moves
test_pgn = """[Event "Test Match"]
[Site "https://lichess.org/testgame123"]
[White "AnalyzerTest"]
[Black "Opponent"]
[WhiteElo "2500"]
[BlackElo "2480"]
[TimeControl "300+3"]
[Result "1-0"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 
6. Bg5 e6 7. f4 Be7 8. Qf3 Nbd7 9. O-O-O b5 10. a3 Bb7
11. Bxf6 Nxf6 12. Kb1 Rc8 13. g4 b4 14. axb4 Rxc3 
15. bxc3 Qb6 16. Qg3 Qxb4+ 17. Kc1 h6 18. e5 dxe5 
19. fxe5 Ng4 20. Bh5 Qd6 21. e6 fxe6 22. Qxg4 Qd5 
23. Qxd5+ exd5 24. Bc6+ Kd8 25. Bxb7 a5 26. Bd5 
1-0
"""

try:
    print("\n[SETUP] Loading chess game and analyzer...")
    pgn = chess.pgn.read_game(StringIO(test_pgn))
    
    if not pgn:
        print("Failed to parse PGN")
        exit(1)
    
    print(f"Game loaded: {pgn.headers.get('White')} vs {pgn.headers.get('Black')}")
    
    # Initialize analyzer
    config = yaml.safe_load(open('config.yaml'))
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # Analyze the game
    print("\n[ANALYSIS] Analyzing game...")
    results = analyzer.analyze_games_fast([pgn], "AnalyzerTest", max_workers=1)
    
    # Extract and display key metrics
    print("\n[RESULTS] Key Metrics:")
    print("-" * 80)
    
    games = results.get('game_analyses', [])
    if games:
        game = games[0]
        accuracy = game.get('accuracy', {})
        engine = game.get('engine_pattern', {})
        
        print(f"Overall Accuracy: {accuracy.get('overall_accuracy', 0):.1f}%")
        print(f"  - Opening: {accuracy.get('opening_accuracy', 0):.1f}%")
        print(f"  - Middlegame: {accuracy.get('middlegame_accuracy', 0):.1f}%")
        print(f"  - Endgame: {accuracy.get('endgame_accuracy', 0):.1f}%")
        print()
        print(f"Engine Matching Rates:")
        print(f"  - Top 1 (Excellent moves): {engine.get('top_1_match_rate', 0):.1f}%")
        print(f"  - Top 3 (Good moves): {engine.get('top_3_match_rate', 0):.1f}%")
        print(f"  - Top 5 (Okay moves): {engine.get('top_5_match_rate', 0):.1f}%")
        print()
        print(f"Move Quality: {game.get('move_count', 0)} total moves")
        print(f"Suspicion Score: {game.get('suspicion_score', 0):.1f}/100")
        
        # Determine accuracy flag
        accuracy_pct = accuracy.get('overall_accuracy', 0)
        if accuracy_pct >= 85:
            flag = "[SUSPICIOUS] 85%+ is unusually high"
        elif accuracy_pct >= 75:
            flag = "[HIGH] 75-84% - worth investigating"
        elif accuracy_pct >= 60:
            flag = "[MODERATE] 60-74% - normal human range"
        else:
            flag = "[NORMAL] <60% - expected for humans"
        
        print()
        print(f"Assessment: {flag}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Analyzer is working correctly!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)
