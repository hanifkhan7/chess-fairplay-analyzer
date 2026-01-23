#!/usr/bin/env python3
"""
Debug test to see what's happening with evaluation fetching
"""

import sys
sys.path.insert(0, 'chess_analyzer')

from analyzer_v3 import EnhancedPlayerAnalyzer
import requests
import json
import chess.pgn
from io import StringIO

# Initialize analyzer
config = {"api_key_lichess": ""}
analyzer = EnhancedPlayerAnalyzer(config, use_lichess=True)

# Get a real game to test with
print("=" * 80)
print("[DEBUG] EVALUATION FETCHING TEST")
print("=" * 80)

# Fetch a real game from Lichess
print("\n[STEP 1] Fetching test game from Lichess...")
games = []
try:
    url = "https://api.lichess.org/api/games/user/hikaru"
    headers = {"Accept": "application/x-ndjson"}
    response = requests.get(url, headers=headers, timeout=10, params={"max": 1})
    
    if response.status_code == 200:
        game_pgn = response.text.strip()
        pgn = chess.pgn.read_game(StringIO(game_pgn))
        if pgn:
            games.append(pgn)
            game_link = pgn.headers.get("Link", "")
            print(f"✓ Got game: {game_link}")
except Exception as e:
    print(f"✗ Failed: {e}")

if not games:
    print("No games fetched, creating test game...")
    pgn_text = """
[Event "Test Game"]
[Site "https://lichess.org/test"]
[Link "https://lichess.org/test1234567890"]
[Round "1"]
[White "Test1"]
[Black "Test2"]
[Result "*"]

1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 *
"""
    pgn = chess.pgn.read_game(StringIO(pgn_text))
    games = [pgn]

# Test with the game
if games:
    game = games[0]
    print(f"\n[STEP 2] Testing _get_lichess_evaluations()...")
    
    # Test extraction of game ID
    link = game.headers.get("Link", "")
    print(f"  Link header: {link}")
    
    game_id = link.split('/')[-1].split('?')[0]
    print(f"  Extracted game ID: {game_id}")
    
    if "lichess.org" in link and game_id and len(game_id) >= 8:
        print(f"  Valid Lichess link: YES")
        
        # Try to fetch from API
        url = f"https://lichess.org/api/games/{game_id}"
        headers = {"Accept": "application/json"}
        print(f"\n  Fetching from: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status code: {response.status_code}")
            
            if response.status_code == 200:
                game_data = response.json()
                print(f"  Response keys: {list(game_data.keys())}")
                
                # Check for analysis
                if 'analysis' in game_data:
                    analysis = game_data['analysis']
                    print(f"  Analysis field exists: {len(analysis)} items")
                    if analysis:
                        print(f"    First analysis item: {analysis[0]}")
                else:
                    print(f"  No 'analysis' field in response")
                    
                # Check for moves
                if 'moves' in game_data:
                    moves = game_data['moves']
                    print(f"  Moves field: {len(moves)} moves")
            else:
                print(f"  Error: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {e}")
    
    # Extract moves from game
    moves = []
    board = chess.Board()
    for move in game.mainline_moves():
        moves.append(move)
        board.push(move)
    
    print(f"\n[STEP 3] Testing evaluation methods...")
    print(f"  Total moves in game: {len(moves)}")
    
    # Test _get_evaluations (should use 3-tier system)
    evals = analyzer._get_evaluations(game, moves)
    print(f"  _get_evaluations() returned: {len(evals)} evaluations")
    
    if evals:
        print(f"    First evaluation: {evals[0]}")
        print(f"    Sample (every 5th): {[evals[i] for i in range(0, min(len(evals), 20), 5)]}")
        
        # Check for heuristic flag
        heuristic_count = sum(1 for e in evals if e.get('heuristic', False))
        print(f"    Heuristic evaluations: {heuristic_count}/{len(evals)}")
    
    # Test individual methods
    print(f"\n[STEP 4] Testing individual evaluation methods...")
    
    lichess_evals = analyzer._get_lichess_evaluations(game)
    print(f"  _get_lichess_evaluations(): {len(lichess_evals)} evals")
    
    local_evals = analyzer._get_local_evaluations(game, moves)
    print(f"  _get_local_evaluations(): {len(local_evals)} evals")
    
    heuristic_evals = analyzer._generate_heuristic_evaluations(game, moves)
    print(f"  _generate_heuristic_evaluations(): {len(heuristic_evals)} evals")
    if heuristic_evals:
        print(f"    First 5: {heuristic_evals[:5]}")

print("\n" + "=" * 80)
