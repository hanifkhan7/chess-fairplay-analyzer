#!/usr/bin/env python
"""Quick test of H2H improvements with real players"""
import sys
sys.path.insert(0, '.')

from chess_analyzer.menu import _fetch_games
from chess_analyzer.dual_fetcher import fetch_player_info
from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer

config = {
    'DEFAULT_PLATFORM': 'lichess',
    'LICHESS_API_URL': 'https://lichess.org/api',
    'STOCKFISH_PATH': 'stockfish/stockfish-windows-x86-64.exe',
}

print("Testing Head-to-Head Analyzer with Real Players")
print("=" * 80)

# Use the players from the previous output
p1_name = "41723R-HK"
p2_name = "Hassan_Tahirr"
platform = "lichess"

print(f"\nFetching 50 games for {p1_name}...")
games1, counts1 = _fetch_games(p1_name, 50, [platform], config)
print(f"✓ Got {len(games1)} games for {p1_name}")

print(f"Fetching 50 games for {p2_name}...")
games2, counts2 = _fetch_games(p2_name, 50, [platform], config)
print(f"✓ Got {len(games2)} games for {p2_name}")

# Get player ratings
print(f"\nFetching player info...")
p1_info = fetch_player_info(p1_name, platform, config)
p2_info = fetch_player_info(p2_name, platform, config)

p1_elo = p1_info.get('rating') if p1_info and p1_info.get('rating') else None
p2_elo = p2_info.get('rating') if p2_info and p2_info.get('rating') else None

print(f"  {p1_name}: {p1_elo if p1_elo else 'API failed'}")
print(f"  {p2_name}: {p2_elo if p2_elo else 'API failed'}")

# Generate report
print(f"\nGenerating matchup report...")
analyzer = HeadToHeadAnalyzer()
report = analyzer.generate_matchup_report(p1_name, p1_elo, games1, p2_name, p2_elo, games2)

# Display
print("\n" + "=" * 80)
print("MATCHUP REPORT:")
print("=" * 80)
analyzer.display_matchup_report(report)

print("\n[TEST COMPLETE]")
