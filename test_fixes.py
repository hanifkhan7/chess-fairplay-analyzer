#!/usr/bin/env python3
"""Test the fixed platform detection and fetching"""

import sys
sys.path.insert(0, '.')

from chess_analyzer.dual_fetcher import detect_player_platforms, prompt_platform_selection
from chess_analyzer.fetcher import fetch_player_games
from chess_analyzer.dual_fetcher import fetch_lichess_games

print("="*60)
print("TEST 1: Platform detection for Quantum-Chesss")
print("="*60)
platforms = detect_player_platforms('Quantum-Chesss')
print(f"\nDetection Results:")
print(f"  Chess.com: {'✓ Found' if platforms['chess.com'] else '✗ Not found'}")
print(f"  Lichess: {'✓ Found' if platforms['lichess'] else '✗ Not found'}")

print("\n" + "="*60)
print("TEST 2: Fetching games from Chess.com for Quantum-Chesss")
print("="*60)
try:
    games = fetch_player_games('Quantum-Chesss', 10)
    print(f"\n✓ Fetched {len(games)} games from Chess.com")
    if len(games) > 0:
        print(f"  First game: {games[0].headers.get('White', 'Unknown')} vs {games[0].headers.get('Black', 'Unknown')}")
except Exception as e:
    print(f"\n✗ Error fetching: {e}")

print("\n" + "="*60)
print("TEST 3: Platform detection for Pap-G")
print("="*60)
platforms = detect_player_platforms('Pap-G')
print(f"\nDetection Results:")
print(f"  Chess.com: {'✓ Found' if platforms['chess.com'] else '✗ Not found'}")
print(f"  Lichess: {'✓ Found' if platforms['lichess'] else '✗ Not found'}")

print("\n" + "="*60)
print("TEST 4: Fetching games from Lichess for Pap-G")
print("="*60)
try:
    games, count = fetch_lichess_games('Pap-G', 10)
    print(f"\n✓ Fetched {count} games from Lichess")
    if len(games) > 0:
        print(f"  First game: {games[0].headers.get('White', 'Unknown')} vs {games[0].headers.get('Black', 'Unknown')}")
except Exception as e:
    print(f"\n✗ Error fetching: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
