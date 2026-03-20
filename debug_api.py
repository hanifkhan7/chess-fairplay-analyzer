#!/usr/bin/env python3
"""Debug Chess.com API response"""

import requests

username = "hikaru"

print("Testing Chess.com API with different approaches...\n")

# Test 1: Basic request
print("Test 1: Basic request")
try:
    url = f"https://api.chess.com/pub/player/{username.lower()}"
    response = requests.get(url, timeout=5)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Success! Got: {list(data.keys())[:5]}")
    else:
        print(f"  ❌ Failed")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 2: With User-Agent
print("Test 2: With User-Agent header")
try:
    url = f"https://api.chess.com/pub/player/{username.lower()}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=5)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Success! Got keys:")
        for key in list(data.keys())[:10]:
            print(f"     - {key}: {str(data[key])[:50]}")
    else:
        print(f"  ❌ Failed with {response.status_code}")
        print(f"     Response: {response.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 3: Stats endpoint with headers
print("Test 3: Stats endpoint with User-Agent")
try:
    url = f"https://api.chess.com/pub/player/{username.lower()}/stats"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=5)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ Success!")
        if 'chess_rapid' in data:
            print(f"     Rapid: {data['chess_rapid'].get('last', {}).get('rating', 'N/A')}")
    else:
        print(f"  ❌ Failed with {response.status_code}")
        print(f"     Response: {response.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "="*60)
print("Results saved to debug output above")
