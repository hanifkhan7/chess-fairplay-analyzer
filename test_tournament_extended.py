#!/usr/bin/env python3
"""Test Tournament Inspector with more games to find head-to-head matchups"""

from chess_analyzer.tournament_inspector import TournamentInspector

print("=" * 80)
print("TOURNAMENT INSPECTOR - EXTENDED TEST")
print("=" * 80)

inspector = TournamentInspector()

# Test with real usernames and more games
players = ["41723R-HK", "rohan_asif", "Hassan_Tahirr"]
max_games = 50  # More games = higher chance of head-to-head

print(f"\nFetching most recent {max_games} games for each player...")

all_games = {}
successful_players = []

for player in players:
    print(f"\n[{player.upper()}]")
    games = inspector.fetch_recent_games(player, max_games)
    
    if games:
        all_games[player] = games
        successful_players.append(player)
        print(f"[OK] Got {len(games)} games")
    else:
        print(f"[ERROR] Failed to fetch games")

if len(successful_players) >= 2:
    print(f"\n\n[ANALYSIS] Analyzing head-to-head between: {', '.join(successful_players)}")
    results = inspector.analyze_head_to_head(successful_players, all_games)
    inspector.display_results(results)
else:
    print(f"\n[ERROR] Could only fetch for {len(successful_players)} players (need at least 2)")

print("\n" + "=" * 80)
