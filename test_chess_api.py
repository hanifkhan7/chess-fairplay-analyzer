#!/usr/bin/env python3
"""Test Chess.com API directly"""

import requests

# Use the exact usernames provided
usernames = ["41723R-HK", "rohan_asif", "Hassan_Tahirr", "hikaru"]

for username in usernames:
    print(f"\nTesting: {username}")
    # Chess.com API is case-insensitive, but let's test both
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            archives = data.get('archives', [])
            print(f"  Archives: {len(archives)}")
            if archives:
                print(f"  Latest: {archives[-1]}")
        else:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"  Exception: {e}")
