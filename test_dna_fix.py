#!/usr/bin/env python3
"""
Test script to verify Player DNA fix works with different input formats.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from chess_analyzer.player_dna import build_player_dna, PlayerDNAProfile
import chess.pgn
from io import StringIO

# Sample PGN games
SAMPLE_PGNS = [
    """[Event "Chess.com"]
[White "hikaru"]
[Black "opponent1"]
[Result "1-0"]
[Opening "Ruy Lopez"]
[ECO "C60"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Na5 10. Bc2 c5 11. d4 Qc7 12. d5 cxd4 13. cxd4 1-0""",
    
    """[Event "Chess.com"]
[White "hikaru"]
[Black "opponent2"]
[Result "1/2-1/2"]
[Opening "Sicilian Defense"]
[ECO "B20"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1/2-1/2""",
    
    """[Event "Chess.com"]
[White "opponent3"]
[Black "hikaru"]
[Result "0-1"]
[Opening "Queen's Gambit"]
[ECO "D40"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Ne4 0-1""",
]

def test_with_dict_format():
    """Test with dictionary format (pgn string)"""
    print("\n" + "="*70)
    print("TEST 1: Dictionary format (pgn string)")
    print("="*70)
    
    games = [{'pgn': pgn} for pgn in SAMPLE_PGNS]
    
    print(f"Input: {len(games)} games as dicts with 'pgn' key")
    dna = build_player_dna('hikaru', games, color='white', min_games=1)
    
    print(f"Player: {dna.data['player']}")
    print(f"Total games: {dna.data['total_games']}")
    print(f"Color: {dna.data['color']}")
    
    if dna.data['total_games'] > 0:
        stats = dna.data['statistics']
        print(f"Record: {stats['wins']}W {stats['draws']}D {stats['losses']}L")
        print(f"Win rate: {stats['win_rate']:.1f}%")
        print("✓ TEST 1 PASSED")
        return True
    else:
        print("✗ TEST 1 FAILED: No games analyzed")
        return False


def test_with_game_objects():
    """Test with chess.pgn.Game objects"""
    print("\n" + "="*70)
    print("TEST 2: chess.pgn.Game objects")
    print("="*70)
    
    games = []
    for pgn in SAMPLE_PGNS:
        game = chess.pgn.read_game(StringIO(pgn))
        if game:
            games.append(game)
    
    print(f"Input: {len(games)} games as chess.pgn.Game objects")
    dna = build_player_dna('hikaru', games, color='white', min_games=1)
    
    print(f"Player: {dna.data['player']}")
    print(f"Total games: {dna.data['total_games']}")
    print(f"Color: {dna.data['color']}")
    
    if dna.data['total_games'] > 0:
        stats = dna.data['statistics']
        print(f"Record: {stats['wins']}W {stats['draws']}D {stats['losses']}L")
        print(f"Win rate: {stats['win_rate']:.1f}%")
        print("✓ TEST 2 PASSED")
        return True
    else:
        print("✗ TEST 2 FAILED: No games analyzed")
        return False


def test_favorite_openings():
    """Test favorite openings extraction"""
    print("\n" + "="*70)
    print("TEST 3: Favorite openings extraction")
    print("="*70)
    
    games = []
    for pgn in SAMPLE_PGNS:
        game = chess.pgn.read_game(StringIO(pgn))
        if game:
            games.append(game)
    
    dna = build_player_dna('hikaru', games, color='white', min_games=1)
    
    favorites = dna.data['favorite_openings']
    print(f"Found {len(favorites)} favorite openings:")
    for opening in favorites:
        print(f"  - {opening['name']}: {opening['games']} games, {opening['win_rate']}% win rate")
    
    if len(favorites) > 0:
        print("✓ TEST 3 PASSED")
        return True
    else:
        print("✗ TEST 3 FAILED: No openings extracted")
        return False


def test_both_colors():
    """Test with both white and black games"""
    print("\n" + "="*70)
    print("TEST 4: Both colors analysis")
    print("="*70)
    
    games = []
    for pgn in SAMPLE_PGNS:
        game = chess.pgn.read_game(StringIO(pgn))
        if game:
            games.append(game)
    
    dna = build_player_dna('hikaru', games, color='both', min_games=1)
    
    print(f"Player: {dna.data['player']}")
    print(f"Total games: {dna.data['total_games']}")
    print(f"Color: {dna.data['color']}")
    
    if dna.data['total_games'] > 0:
        stats = dna.data['statistics']
        print(f"Record: {stats['wins']}W {stats['draws']}D {stats['losses']}L")
        print(f"Win rate: {stats['win_rate']:.1f}%")
        print("✓ TEST 4 PASSED")
        return True
    else:
        print("✗ TEST 4 FAILED: No games analyzed")
        return False


def main():
    print("\n" + "="*70)
    print("PLAYER DNA FIX VERIFICATION TESTS")
    print("="*70)
    
    try:
        results = []
        results.append(test_with_dict_format())
        results.append(test_with_game_objects())
        results.append(test_favorite_openings())
        results.append(test_both_colors())
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        passed = sum(results)
        total = len(results)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("\n✓ ALL TESTS PASSED - DNA FIX IS WORKING")
            return 0
        else:
            print(f"\n✗ {total - passed} TEST(S) FAILED")
            return 1
    
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
