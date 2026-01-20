import requests
import json

# Try with pgnInJson parameter
headers = {'Accept': 'application/x-ndjson'}
url = 'https://lichess.org/api/games/user/Pap-G'
params = {'max': 1, 'sort': 'dateDesc', 'pgnInJson': 'true'}

response = requests.get(url, headers=headers, params=params, timeout=5)
print(f"Status: {response.status_code}")

first_line = response.text.strip().split('\n')[0]
game = json.loads(first_line)
print(f"Keys: {list(game.keys())}")
print(f"Has 'pgn': {'pgn' in game}")

if 'pgn' in game:
    print(f"PGN content: {game['pgn'][:200]}")
