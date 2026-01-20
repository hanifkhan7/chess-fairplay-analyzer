import requests
import json

# Test Lichess games fetch for Pap-G
print('Testing Lichess games fetch for Pap-G:')
url = 'https://lichess.org/api/games/user/pap-g'
headers = {'Accept': 'application/x-ndjson'}
params = {
    'max': 50,
    'perfType': 'blitz,bullet,rapid,classical',
    'sort': 'dateDesc'
}

response = requests.get(url, headers=headers, params=params, timeout=10)
print(f'Status: {response.status_code}')
print(f'Response length: {len(response.text)} characters')
print(f'Lines: {len(response.text.strip().split(chr(10)))}')

# Count games
lines = response.text.strip().split('\n')
games = 0
for line in lines:
    if line.strip():
        games += 1

print(f'Non-empty lines (games): {games}')

if games > 0:
    print('\nFirst game (raw):', lines[0][:200])

print('\n' + '='*60)
print('\nNow testing WITHOUT perfType filter:')
params2 = {
    'max': 50,
    'sort': 'dateDesc'
}

response2 = requests.get(url, headers=headers, params=params2, timeout=10)
print(f'Status: {response2.status_code}')

lines2 = response2.text.strip().split('\n')
games2 = 0
for line in lines2:
    if line.strip():
        games2 += 1

print(f'Non-empty lines (games): {games2}')
