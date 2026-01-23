#!/usr/bin/env python3
"""Debug test to see what accuracy values are being calculated"""

import yaml
import sys
import json

try:
    print("="*80)
    print("[DEBUG] ACCURACY CALCULATION TEST")
    print("="*80)
    
    # Load config
    config = yaml.safe_load(open('config.yaml'))
    
    # Fetch real games from Lichess
    print("\n[STEP 1] Fetching real games from Lichess...")
    from chess_analyzer.dual_fetcher import fetch_lichess_games
    
    username = 'Pap-G'
    games, count = fetch_lichess_games(username, 1, config)
    print(f"✓ Fetched {count} games from Lichess")
    
    if not games:
        print("✗ Could not fetch games")
        sys.exit(1)
    
    game = games[0]
    
    # Extract moves manually
    import chess
    moves = list(game.mainline_moves())
    print(f"✓ Extracted {len(moves)} moves from game")
    
    # Get evaluations
    print("\n[STEP 2] Testing evaluation methods...")
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    analyzer = EnhancedPlayerAnalyzer(config)
    
    # Test the 3-tier system
    evaluations = analyzer._get_evaluations(game, moves)
    print(f"✓ Got {len(evaluations)} evaluations")
    print(f"  Sample evals: {evaluations[:5]}")
    
    # Check for heuristic flag
    heuristic_count = sum(1 for e in evaluations if e.get('heuristic', False))
    print(f"  Heuristic evaluations: {heuristic_count}/{len(evaluations)}")
    
    # Calculate move scores
    print("\n[STEP 3] Testing move score calculation...")
    move_scores = analyzer._calculate_move_scores(evaluations)
    print(f"✓ Calculated {len(move_scores)} move scores")
    if move_scores:
        print(f"  Sample scores: {move_scores[:10]}")
        print(f"  Score range: {min(move_scores):.1f} - {max(move_scores):.1f}")
        print(f"  Average: {sum(move_scores)/len(move_scores):.1f}")
    
    # Calculate accuracy
    print("\n[STEP 4] Testing accuracy calculation...")
    accuracy = analyzer._calculate_accuracy(evaluations, moves)
    print(f"✓ Accuracy metrics:")
    print(f"  Overall: {accuracy.overall_accuracy:.1f}%")
    print(f"  Opening: {accuracy.opening_accuracy:.1f}%")
    print(f"  Middlegame: {accuracy.middlegame_accuracy:.1f}%")
    print(f"  Endgame: {accuracy.endgame_accuracy:.1f}%")
    print(f"  Consistency: {accuracy.consistency_std_dev:.1f}")
    
    # Now test with the full analyze_games_fast
    print("\n[STEP 5] Testing full analysis pipeline...")
    results = analyzer.analyze_games_fast(games, username, max_workers=1)
    
    print(f"✓ Results compiled:")
    print(f"  Games analyzed: {results.get('games_analyzed', 0)}")
    print(f"  Avg accuracy: {results.get('avg_accuracy', 0):.1f}%")
    
    # Check game analyses
    game_analyses = results.get('game_analyses', [])
    if game_analyses:
        game = game_analyses[0]
        print(f"\n  Game analysis details:")
        print(f"    Type of 'accuracy': {type(game.get('accuracy'))}")
        print(f"    Accuracy value: {game.get('accuracy')}")
        
        if isinstance(game.get('accuracy'), dict):
            acc = game['accuracy']
            print(f"    Overall accuracy: {acc.get('overall_accuracy', 'N/A')}")
        else:
            print(f"    (Not a dict, need to debug)")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
