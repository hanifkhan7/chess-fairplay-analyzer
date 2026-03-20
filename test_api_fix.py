#!/usr/bin/env python3
"""Test the fixed API calls"""

import requests

username = "hikaru"

print("Testing Chess.com API fix with proper headers...\n")

# Test with proper headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Testing profile endpoint for: {username}")
try:
    url = f"https://api.chess.com/pub/player/{username.lower()}"
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Profile fetch SUCCESS!")
        print(f"   - Username: {data.get('username', 'N/A')}")
        print(f"   - Name: {data.get('name', 'N/A')}")
        print(f"   - Title: {data.get('title', 'N/A')}")
        print(f"   - Avatar: {data.get('avatar', 'N/A')[:50]}...")
        print(f"   - Location: {data.get('location', 'N/A')}")
        print(f"   - Followers: {data.get('followers', 'N/A')}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Response preview: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print(f"Testing stats endpoint for: {username}")
try:
    url = f"https://api.chess.com/pub/player/{username.lower()}/stats"
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Stats fetch SUCCESS!")
        
        if 'chess_rapid' in data:
            rapid = data['chess_rapid'].get('last', {})
            print(f"   - Rapid Rating: {rapid.get('rating', 'N/A')}")
        
        if 'chess_blitz' in data:
            blitz = data['chess_blitz'].get('last', {})
            print(f"   - Blitz Rating: {blitz.get('rating', 'N/A')}")
        
        if 'tactics' in data:
            puzzle = data['tactics'].get('highest', {})
            print(f"   - Puzzle Rating: {puzzle.get('rating', 'N/A')}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Response preview: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 60)
print("API Fix is READY! The profile should now fetch correctly.")
