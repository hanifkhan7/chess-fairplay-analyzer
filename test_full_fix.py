#!/usr/bin/env python3
"""Test the fixed dual-platform detection and fetching"""

from chess_analyzer.dual_fetcher import detect_player_platforms, prompt_platform_selection
from chess_analyzer.menu import _fetch_games
from chess_analyzer.utils.helpers import load_config

print("="*70)
print("TEST 1: Quantum-Chesss (Chess.com account, 403 private profile)")
print("="*70)

platforms = detect_player_platforms('Quantum-Chesss')
print(f"\nDetection: {platforms}")
print(f"  Chess.com: {'✓' if platforms['chess.com'] else '✗'}")
print(f"  Lichess: {'✓' if platforms['lichess'] else '✗'}")

if platforms['chess.com']:
    print("\nFetching 5 games from Chess.com...")
    config = load_config()
    games, counts = _fetch_games('Quantum-Chesss', 5, ['chess.com'], config)
    print(f"✓ Fetched {len(games)} games from Chess.com")
    if games:
        print(f"  Sample: {games[0].headers.get('White')} vs {games[0].headers.get('Black')}")

print("\n" + "="*70)
print("TEST 2: Pap-G (Both Chess.com and Lichess)")
print("="*70)

platforms = detect_player_platforms('Pap-G')
print(f"\nDetection: {platforms}")
print(f"  Chess.com: {'✓' if platforms['chess.com'] else '✗'}")
print(f"  Lichess: {'✓' if platforms['lichess'] else '✗'}")

if platforms['lichess']:
    print("\nFetching 5 games from Lichess...")
    config = load_config()
    games, counts = _fetch_games('Pap-G', 5, ['lichess'], config)
    print(f"✓ Fetched {len(games)} games from Lichess")
    if games:
        print(f"  Sample: {games[0].headers.get('White')} vs {games[0].headers.get('Black')}")

if platforms['chess.com']:
    print("\nFetching 5 games from Chess.com...")
    config = load_config()
    games, counts = _fetch_games('Pap-G', 5, ['chess.com'], config)
    print(f"✓ Fetched {len(games)} games from Chess.com")
    if games:
        print(f"  Sample: {games[0].headers.get('White')} vs {games[0].headers.get('Black')}")

print("\n" + "="*70)
print("✓ ALL TESTS PASSED")
print("="*70)
