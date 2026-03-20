#!/usr/bin/env python3
"""Direct test of Chess.com profile fetching without menu imports"""

import requests
import json

def fetch_chesscom_profile(username):
    """Fetch Chess.com player profile data"""
    try:
        url = f"https://api.chess.com/pub/player/{username.lower()}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[ERROR] {e}")
    return {}

def fetch_chesscom_stats(username):
    """Fetch Chess.com player stats"""
    try:
        url = f"https://api.chess.com/pub/player/{username.lower()}/stats"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[ERROR] {e}")
    return {}

print("=" * 70)
print("TESTING CHESS.COM PROFILE API")
print("=" * 70)
print()

test_username = "hikaru"
print(f"Testing with username: {test_username}")
print()

# Test profile
print("1. Fetching profile...")
profile = fetch_chesscom_profile(test_username)
if profile:
    print(f"   ✅ Profile received")
    print(f"      - Name: {profile.get('name', 'N/A')}")
    print(f"      - Title: {profile.get('title', 'N/A')}")
    print(f"      - Location: {profile.get('location', 'N/A')}")
    print(f"      - Followers: {profile.get('followers', 0)}")
    print(f"      - Avatar: {'✓' if profile.get('avatar') else '✗'}")
else:
    print(f"   ❌ Failed")

print()

# Test stats
print("2. Fetching stats...")
stats = fetch_chesscom_stats(test_username)
if stats:
    print(f"   ✅ Stats received")
    
    # Extract ratings
    rapid = stats.get('chess_rapid', {})
    blitz = stats.get('chess_blitz', {})
    puzzle = stats.get('tactics', {})
    
    print(f"      - Rapid: {rapid.get('last', {}).get('rating', 'N/A')}")
    print(f"      - Blitz: {blitz.get('last', {}).get('rating', 'N/A')}")
    print(f"      - Puzzle: {puzzle.get('highest', {}).get('rating', 'N/A')}")
else:
    print(f"   ❌ Failed")

print()
print("=" * 70)
print("✅ API INTEGRATION TEST COMPLETE")
print("=" * 70)
