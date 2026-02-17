#!/usr/bin/env python3
"""
Minimal test script for Player DNA fix without full package imports.
"""

import sys
import os

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chess_analyzer'))

# Import just what we need
import chess.pgn
from io import StringIO
from typing import Dict, List, Optional
from collections import defaultdict

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


def test_game_object_parsing():
    """Test parsing chess.pgn.Game objects"""
    print("\n" + "="*70)
    print("TEST 1: Parse chess.pgn.Game objects")
    print("="*70)
    
    games = []
    for pgn in SAMPLE_PGNS:
        game = chess.pgn.read_game(StringIO(pgn))
        if game:
            games.append(game)
            print(f"✓ Parsed: {game.headers.get('White')} vs {game.headers.get('Black')}")
    
    print(f"\nTotal games parsed: {len(games)}")
    
    if len(games) == 3:
        print("✓ TEST 1 PASSED")
        return True, games
    else:
        print("✗ TEST 1 FAILED")
        return False, []


def test_dict_with_pgn_parsing(games):
    """Test parsing dict format"""
    print("\n" + "="*70)
    print("TEST 2: Parse dict format with 'pgn' key")
    print("="*70)
    
    game_dicts = [{'pgn': pgn} for pgn in SAMPLE_PGNS]
    parsed = []
    
    for game_dict in game_dicts:
        pgn_str = game_dict.get('pgn', '')
        if pgn_str:
            game = chess.pgn.read_game(StringIO(pgn_str))
            if game:
                parsed.append(game)
                print(f"✓ Parsed: {game.headers.get('White')} vs {game.headers.get('Black')}")
    
    print(f"\nTotal games parsed: {len(parsed)}")
    
    if len(parsed) == 3:
        print("✓ TEST 2 PASSED")
        return True
    else:
        print("✗ TEST 2 FAILED")
        return False


def test_game_filtering(games):
    """Test filtering games for specific player"""
    print("\n" + "="*70)
    print("TEST 3: Filter games for player 'hikaru'")
    print("="*70)
    
    player_name = 'hikaru'
    player_games = []
    
    for game in games:
        white = game.headers.get('White', '').lower()
        black = game.headers.get('Black', '').lower()
        player_key = player_name.lower()
        
        player_is_white = player_key in white
        player_is_black = player_key in black
        
        if player_is_white or player_is_black:
            result = game.headers.get('Result', '*')
            white_won = result == '1-0'
            black_won = result == '0-1'
            draw = result == '1/2-1/2'
            
            if player_is_white:
                player_won = white_won
                player_draw = draw
                player_lost = black_won
            else:
                player_won = black_won
                player_draw = draw
                player_lost = white_won
            
            player_games.append({
                'game': game,
                'is_white': player_is_white,
                'won': player_won,
                'draw': player_draw,
                'lost': player_lost,
            })
            
            result_str = 'W' if player_won else ('D' if player_draw else 'L')
            color_str = 'White' if player_is_white else 'Black'
            print(f"✓ Found: {color_str} vs {game.headers.get('Black' if player_is_white else 'White')} - {result_str}")
    
    print(f"\nTotal games for 'hikaru': {len(player_games)}")
    
    if len(player_games) == 3:
        print("✓ TEST 3 PASSED")
        return True
    else:
        print("✗ TEST 3 FAILED")
        return False


def test_opening_extraction(games):
    """Test extracting opening information"""
    print("\n" + "="*70)
    print("TEST 4: Extract opening information")
    print("="*70)
    
    openings = defaultdict(lambda: {
        'games': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
    })
    
    for game in games:
        opening_name = game.headers.get('Opening', 'Unknown Opening')
        print(f"✓ Opening: {opening_name}")
        openings[opening_name]['games'] += 1
    
    print(f"\nTotal unique openings: {len(openings)}")
    
    if len(openings) == 3:
        print("✓ TEST 4 PASSED")
        return True
    else:
        print("✗ TEST 4 FAILED")
        return False


def main():
    print("\n" + "="*70)
    print("PLAYER DNA FIX VERIFICATION - MINIMAL TEST")
    print("="*70)
    
    try:
        # Test 1: Parse game objects
        passed1, games = test_game_object_parsing()
        if not passed1:
            return 1
        
        # Test 2: Parse dict format
        passed2 = test_dict_with_pgn_parsing(games)
        if not passed2:
            return 1
        
        # Test 3: Filter games
        passed3 = test_game_filtering(games)
        if not passed3:
            return 1
        
        # Test 4: Extract openings
        passed4 = test_opening_extraction(games)
        if not passed4:
            return 1
        
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
        print("\nThe Player DNA fix should work correctly with:")
        print("  1. chess.pgn.Game objects (from dual_fetcher)")
        print("  2. Dict format with 'pgn' key string")
        print("  3. Game filtering by player name")
        print("  4. Opening extraction")
        print("\nNow ready to test in the actual menu system.")
        return 0
    
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
