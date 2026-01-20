import requests
import json

headers = {'Accept': 'application/x-ndjson'}
url = 'https://lichess.org/api/games/user/Pap-G'
params = {'max': 1, 'sort': 'dateDesc'}

response = requests.get(url, headers=headers, params=params, timeout=5)
print(f"Status: {response.status_code}")
print(f"Response text ({len(response.text)} chars):")
print(response.text[:500])

print("\n\nParsing first line:")
first_line = response.text.strip().split('\n')[0]
game = json.loads(first_line)
print(f"Keys: {list(game.keys())}")
print(f"Has 'pgn': {'pgn' in game}")

# Try different key names
if 'pgn' not in game:
    print("\nLooking for PGN in different fields:")
    for key in ['pgnTrunc', 'moves', 'game', 'pgn_text']:
        if key in game:
            print(f"  Found in '{key}': {str(game[key])[:100]}")
