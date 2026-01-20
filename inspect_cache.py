import json

with open('cache/41723R-HK_games.json') as f:
    data = json.load(f)
    games = data.get('games', [])
    if games:
        g = games[0]
        print("First game type:", type(g))
        if isinstance(g, dict):
            print("Game keys:", list(g.keys())[:15])
            print("\nSample fields:")
            for key in ['result', 'opponent', 'opponent_elo', 'opening', 'pgn', 'eco', 'moves']:
                if key in g:
                    val = g[key]
                    if isinstance(val, str) and len(val) > 100:
                        print(f"  {key}: {val[:100]}...")
                    else:
                        print(f"  {key}: {val}")
