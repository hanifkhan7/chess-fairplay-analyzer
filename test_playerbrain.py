#!/usr/bin/env python3
"""Test PlayerBrain with small sample."""

from chess_analyzer.fetcher import fetch_player_games
import yaml

config = yaml.safe_load(open('config.yaml'))
games = fetch_player_games('rohan_asif', max_games=2, config=config)

username = 'rohan_asif'
openings = {}

print(f"Fetched {len(games)} games\n")

for game in games:
    white = game.headers.get('White', '').lower()
    black = game.headers.get('Black', '').lower()
    result = game.headers.get('Result', '*')
    eco = game.headers.get('ECO', 'Unknown')
    opening = game.headers.get('Opening', 'Unknown')
    move_count = len(list(game.mainline_moves()))
    
    is_player_white = white == username.lower()
    if result == '1-0':
        outcome = 'win' if is_player_white else 'loss'
    elif result == '0-1':
        outcome = 'loss' if is_player_white else 'win'
    else:
        outcome = 'draw'
    
    opening_key = f'{eco}: {opening}'
    if opening_key not in openings:
        openings[opening_key] = {'wins': 0, 'losses': 0, 'draws': 0, 'count': 0, 'moves': []}
    
    openings[opening_key]['count'] += 1
    openings[opening_key]['moves'].append(move_count)
    if outcome == 'win':
        openings[opening_key]['wins'] += 1
    elif outcome == 'loss':
        openings[opening_key]['losses'] += 1
    else:
        openings[opening_key]['draws'] += 1

print('🏛️ OPENINGS PLAYED:', len(openings), 'different')
print('-' * 70)
sorted_openings = sorted(openings.items(), key=lambda x: x[1]['count'], reverse=True)
for i, (eco_name, stats) in enumerate(sorted_openings, 1):
    total = stats['count']
    win_rate = (stats['wins'] / total * 100) if total > 0 else 0
    avg_moves = sum(stats['moves']) / len(stats['moves'])
    print(f"  {i}. {eco_name}")
    print(f"     {total}x | W-L-D: {stats['wins']}-{stats['losses']}-{stats['draws']} | Win Rate: {win_rate:.1f}% | Avg Moves: {avg_moves:.0f}")
