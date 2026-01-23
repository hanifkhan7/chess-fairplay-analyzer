#!/usr/bin/env python3
"""Test Multi-Player Comparison with IQ estimates"""

from chess_analyzer.comparison import compare_players_display

print("\n" + "="*90)
print("MULTI-PLAYER COMPARISON WITH CHESS IQ TEST")
print("="*90)

# Test with real players
players = ["rohan_asif", "Hassan_Tahirr"]
max_games = 30

print(f"\nComparing {len(players)} players using {max_games} games each...")
print(f"Players: {', '.join(players)}\n")

try:
    compare_players_display(players, max_games=max_games)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*90)
