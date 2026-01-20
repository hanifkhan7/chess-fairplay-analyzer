import requests
import chess.pgn
import json
from io import StringIO

username = 'Pap-G'
max_games = 10

try:
    url = 'https://lichess.org/api/games/user/{}'.format(username)
    headers = {'Accept': 'application/x-ndjson'}
    params = {
        'max': min(max_games, 300),
        'perfType': 'blitz,bullet,rapid,classical',
        'sort': 'dateDesc'
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response length: {len(response.text)} chars")
    
    if response.status_code != 200:
        print(f"Error: {response.text[:200]}")
    else:
        games = []
        game_count = 0
        
        for i, line in enumerate(response.text.strip().split('\n')):
            if not line.strip():
                continue
            
            try:
                game_data = json.loads(line)
                pgn = game_data.get('pgn', '')
                
                print(f"Line {i}: PGN length={len(pgn) if pgn else 0}")
                
                if pgn:
                    game = chess.pgn.read_game(StringIO(pgn))
                    if game:
                        games.append(game)
                        game_count += 1
                        print(f"  ✓ Parsed game {game_count}")
                        
                        if game_count >= max_games:
                            break
                            
            except (json.JSONDecodeError, Exception) as e:
                print(f"Line {i}: Error parsing - {type(e).__name__}: {str(e)[:100]}")
                continue
        
        print(f"\nSuccess: Parsed {game_count} games")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
