#!/usr/bin/env python3
"""Test the Chess.com profile fetching and HTML generation"""

from chess_analyzer.exploit_report_generator import ExploitReportGenerator
import json

# Create generator instance
gen = ExploitReportGenerator()

# Test fetching profile for a public player
test_username = "hikaru"

print("=" * 70)
print("TESTING CHESS.COM PROFILE FETCHING")
print("=" * 70)
print()

# Test profile fetch
print(f"Fetching profile for: {test_username}")
profile = gen._fetch_chesscom_profile(test_username)

if profile:
    print(f"✅ Profile fetched successfully")
    print(f"   - Name: {profile.get('name', 'N/A')}")
    print(f"   - Location: {profile.get('location', 'N/A')}")
    print(f"   - Title: {profile.get('title', 'N/A')}")
    print(f"   - Followers: {profile.get('followers', 'N/A')}")
    print(f"   - Avatar: {'Yes' if profile.get('avatar') else 'No'}")
else:
    print(f"❌ Profile fetch failed")

print()

# Test stats fetch
print(f"Fetching stats for: {test_username}")
stats = gen._fetch_chesscom_stats(test_username)

if stats:
    print(f"✅ Stats fetched successfully")
    if 'chess_rapid' in stats:
        rapid_rating = stats['chess_rapid'].get('last', {}).get('rating', 'N/A')
        print(f"   - Rapid Rating: {rapid_rating}")
    if 'chess_blitz' in stats:
        blitz_rating = stats['chess_blitz'].get('last', {}).get('rating', 'N/A')
        print(f"   - Blitz Rating: {blitz_rating}")
    if 'tactics' in stats:
        puzzle_rating = stats['tactics'].get('highest', {}).get('rating', 'N/A')
        print(f"   - Puzzle Rating: {puzzle_rating}")
else:
    print(f"❌ Stats fetch failed")

print()
print("=" * 70)
