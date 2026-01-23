#!/usr/bin/env python3
"""Test analyzer with real Lichess games and proper evaluation"""

import yaml
import sys

try:
    print("="*80)
    print("[TEST] REAL GAME ANALYSIS WITH EVALUATIONS")
    print("="*80)
    
    # Load config
    config = yaml.safe_load(open('config.yaml'))
    
    # Fetch real games from Lichess
    print("\n[STEP 1] Fetching real games from Lichess...")
    from chess_analyzer.dual_fetcher import fetch_lichess_games
    
    username = 'Pap-G'
    games, count = fetch_lichess_games(username, 3, config)
    print(f"✓ Fetched {count} games from Lichess")
    
    if not games:
        print("✗ No games found. Trying Chess.com instead...")
        from chess_analyzer.fetcher import fetch_player_games
        games = fetch_player_games('hikaru', 3, config)
        print(f"✓ Fetched {len(games)} games from Chess.com")
    
    if not games:
        print("✗ Could not fetch any games")
        sys.exit(1)
    
    # Analyze games
    print("\n[STEP 2] Analyzing games with evaluations...")
    from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
    
    analyzer = EnhancedPlayerAnalyzer(config)
    results = analyzer.analyze_games_fast(games, username, max_workers=2)
    
    # Show results
    print(f"\n[RESULTS] Analysis Complete")
    print(f"  Games analyzed: {results.get('games_analyzed', 0)}")
    print(f"  Average accuracy: {results.get('avg_accuracy', 0):.1f}%")
    print(f"  Average engine match: {results.get('avg_engine_match_rate', 0):.1f}%")
    print(f"  Average suspicion score: {results.get('suspicion_score', 0):.1f}/100")
    
    # Show game details
    print(f"\n[GAMES] Individual Game Results")
    for i, game in enumerate(results.get('game_analyses', [])[:3], 1):
        print(f"\n  Game {i}:")
        print(f"    Accuracy: {game.get('accuracy', {}).get('overall_accuracy', 0):.1f}%")
        print(f"    Engine Match: {game.get('engine_pattern', {}).get('top_1_match_rate', 0):.1f}%")
        print(f"    Opponent: {game.get('opponent_elo', 0)} Elo")
        print(f"    Moves: {game.get('move_count', 0)}")
    
    print("\n" + "="*80)
    
    # Check if evaluations worked
    accuracy_values = [g.get('accuracy', {}).get('overall_accuracy', 0) for g in results.get('game_analyses', [])]
    if all(a == 0.0 for a in accuracy_values):
        print("[WARN] All accuracy values are 0.0 - evaluations not being fetched")
        print("  This might be because:")
        print("  1. Lichess API is not returning evaluation data")
        print("  2. StockfishEngine is not working properly")
        print("  3. Game links don't point to Lichess")
    else:
        print("[SUCCESS] Evaluations are being calculated correctly!")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
