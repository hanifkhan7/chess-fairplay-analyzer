#!/usr/bin/env python3
"""Direct menu test with 2 games"""
import sys

print("\n" + "="*60)
print("   CHESS FAIRPLAY ANALYZER v2.0")
print("   Modern Detection of Computer Assistance in Chess")
print("="*60 + "\n")

try:
    from chess_analyzer.fetcher import fetch_player_games
    from chess_analyzer.analyzer import ChessAnalyzer
    from chess_analyzer.utils.helpers import load_config
    import time
    
    username = 'Salman_Ali_Khan'
    games_to_fetch = 2
    
    print(f"Fetching {games_to_fetch} games for {username}...")
    player_games = fetch_player_games(username, max_games=games_to_fetch)
    print(f"Retrieved {len(player_games)} games")
    
    print("\nLoading analyzer...")
    config = load_config()
    analyzer = ChessAnalyzer(config)
    
    engine_type = "Lichess API (FAST)" if config.get('analysis', {}).get('use_lichess', True) else "Local Stockfish"
    print(f"Analyzing with {engine_type}...")
    print("This should only take 30 seconds to 2 minutes...\n")
    
    start = time.time()
    results = analyzer.analyze_games(player_games)
    elapsed = time.time() - start
    
    print(f"\n" + "="*50)
    print(f"ANALYSIS RESULTS for {username}")
    print("="*50)
    print(f"Games Analyzed: {results.games_analyzed}/{len(player_games)}")
    print(f"Time Taken: {elapsed:.1f} seconds")
    print(f"Suspicion Score: {results.suspicion_score:.1f}/100")
    print(f"Engine Correlation: {results.avg_engine_correlation:.1f}%")
    print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
    print(f"Suspicious Games: {results.suspicious_game_count}")
    print("="*50)
    
    if elapsed < 120:
        print(f"\n✓ Lightning fast! ({elapsed/len(player_games):.0f}s per game average)")
    
except KeyboardInterrupt:
    print("\n\nAnalysis cancelled.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
