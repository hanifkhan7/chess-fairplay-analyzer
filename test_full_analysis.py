#!/usr/bin/env python3
"""Full test of analyzer v3.0 with real data"""
import sys
import os

os.chdir('c:\\Users\\zaibi\\chess-fairplay-analyzer')

from chess_analyzer.fetcher import fetch_player_games
from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer, display_enhanced_analysis
from chess_analyzer.utils.helpers import load_config

username = "hikaru"
max_games = 5

print(f"\n[TEST] Fetching up to {max_games} games for {username}...")
games = fetch_player_games(username, max_games)
print(f"[TEST] Retrieved {len(games)} games")

if not games:
    print("[ERROR] No games retrieved")
    sys.exit(1)

print(f"\n[TEST] Initializing analyzer...")
config = load_config()
analyzer = EnhancedPlayerAnalyzer(config, use_lichess=True)

print(f"[TEST] Running analysis with {len(games)} games...")
try:
    results = analyzer.analyze_games_fast(games, username, max_workers=4)
    print(f"\n[TEST] Analysis complete!\n")
    
    print("="*80)
    print(f"Results Summary:")
    print(f"  Games Analyzed: {results.get('games_analyzed', 0)}")
    print(f"  Suspicious Games: {results.get('suspicious_games', 0)}")
    print(f"  Suspicion Score: {results.get('suspicion_score', 0):.1f}/100")
    print(f"  Avg Engine Match: {results.get('avg_engine_match_rate', 0):.1f}%")
    print("="*80)
    
    print("\n[TEST] Displaying enhanced analysis...")
    display_enhanced_analysis(results, username)
    
except Exception as e:
    print(f"[ERROR] Analysis failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[TEST] COMPLETE")
