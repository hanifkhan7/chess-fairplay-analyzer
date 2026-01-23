#!/usr/bin/env python3
"""Debug evaluations in real pipeline"""

import yaml
import sys

try:
    print("[TEST] REAL GAME EVALUATION DEBUG")
    print("=" * 70)
    
    # Load config
    config = yaml.safe_load(open('config.yaml'))
    
    # Fetch real games from Lichess
    print("[STEP 1] Fetching real games from Lichess...")
    from chess_analyzer.dual_fetcher import fetch_lichess_games
    
    username = 'Pap-G'
    games, count = fetch_lichess_games(username, 1, config)
    
    if not games:
        print("No games fetched - trying cached games...")
        # Use test game
        import chess.pgn
        from io import StringIO
        pgn_text = """[Event "Test"]
[Site "https://lichess.org/test12345678"]
[White "Player1"]
[Black "Player2"]
[WhiteElo "2500"]
[BlackElo "2400"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Bg5 e6 7. f4
"""
        pgn = chess.pgn.read_game(StringIO(pgn_text))
        games = [pgn]
        print("Using test game")
    
    print("[SUCCESS] Got " + str(len(games)) + " game(s)")
    
    # Now manually test each step
    game = games[0]
    
    print()
    print("[STEP 2] Testing _analyze_single_game...")
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # Call _analyze_single_game directly
    analysis = analyzer._analyze_single_game(game, username)
    
    if analysis:
        print("[SUCCESS] Analysis completed")
        print("  Accuracy overall: " + str(analysis.accuracy.overall_accuracy) + "%")
        print("  Engine match: " + str(analysis.engine_pattern.top_1_match_rate) + "%")
        print("  Move count: " + str(analysis.move_count))
    else:
        print("[ERROR] Analysis returned None")
    
    print()
    print("[STEP 3] Testing full analyze_games_fast...")
    results = analyzer.analyze_games_fast(games, username, max_workers=1)
    
    print("[SUCCESS] Results compiled")
    print("  Games analyzed: " + str(results.get('games_analyzed')))
    print("  Avg accuracy: " + str(results.get('avg_accuracy')) + "%")
    
    # Check individual game
    game_analyses = results.get('game_analyses', [])
    if game_analyses:
        game_result = game_analyses[0]
        accuracy_dict = game_result.get('accuracy', {})
        print("  First game accuracy dict: " + str(accuracy_dict))
        if isinstance(accuracy_dict, dict):
            print("  Overall accuracy from dict: " + str(accuracy_dict.get('overall_accuracy')) + "%")
    
    print()
    print("[DONE] Test complete")
    
except Exception as e:
    print("[ERROR] " + str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)
