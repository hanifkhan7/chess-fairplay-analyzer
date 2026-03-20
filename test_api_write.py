#!/usr/bin/env python3
"""Test Chess.com API and write output to file"""

import requests

username = "hikaru"

try:
    print("Fetching profile...", flush=True)
    url = f"https://api.chess.com/pub/player/{username.lower()}"
    response = requests.get(url, timeout=10)
    
    with open('api_test_output.txt', 'w') as f:
        f.write(f"Status Code: {response.status_code}\n")
        if response.status_code == 200:
            data = response.json()
            f.write(f"✅ Profile received\n")
            f.write(f"Name: {data.get('name', 'N/A')}\n")
            f.write(f"Title: {data.get('title', 'N/A')}\n")
            f.write(f"Location: {data.get('location', 'N/A')}\n")
            f.write(f"Avatar: {data.get('avatar', 'N/A')[:50]}\n")
        else:
            f.write(f"❌ Failed to fetch profile\n")
            
        f.write("\n---\n\n")
        
        # Try stats
        stats_url = f"https://api.chess.com/pub/player/{username.lower()}/stats"
        stats_response = requests.get(stats_url, timeout=10)
        f.write(f"Stats Status Code: {stats_response.status_code}\n")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            f.write(f"✅ Stats received\n")
            rapid = stats.get('chess_rapid', {})
            f.write(f"Rapid: {rapid.get('last', {}).get('rating', 'N/A')}\n")
            
    print("Done! Check api_test_output.txt")
    
except Exception as e:
    with open('api_test_output.txt', 'w') as f:
        f.write(f"ERROR: {str(e)}\n")
    print(f"Error: {e}")
