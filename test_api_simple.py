#!/usr/bin/env python3
"""Test Lichess API connectivity"""

print("Testing Lichess API...")
import requests

username = 'Pap-G'
url = f'https://lichess.org/api/games/user/{username}'
headers = {'Accept': 'application/x-ndjson'}
params = {'max': 5, 'sort': 'dateDesc'}

try:
    response = requests.get(url, headers=headers, params=params, timeout=5)
    if response.status_code == 200:
        lines = len(response.text.strip().split('\n'))
        print(f"✓ Lichess API works - fetched {lines} games for {username}")
    else:
        print(f"✗ Error: Status {response.status_code}")
except Exception as e:
    print(f"✗ Connection error: {e}")
