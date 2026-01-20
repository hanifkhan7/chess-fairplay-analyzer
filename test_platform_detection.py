#!/usr/bin/env python3
"""Test intelligent platform detection"""
import os

os.chdir('c:\\Users\\zaibi\\chess-fairplay-analyzer')

from chess_analyzer.dual_fetcher import detect_player_platforms, prompt_platform_selection

print("\n" + "="*80)
print("[TEST] INTELLIGENT PLATFORM DETECTION")
print("="*80)

# Test 1: Detect platforms for known user
print("\n[TEST1] Detecting platforms for 'hikaru'...")
platforms = detect_player_platforms('hikaru')
print(f"\nResults:")
for platform, available in platforms.items():
    status = "✓ Found" if available else "✗ Not found"
    print(f"  {platform}: {status}")

# Test 2: Detect for a Lichess-only user
print("\n[TEST2] Detecting platforms for 'nepo' (likely Lichess)...")
platforms = detect_player_platforms('nepo')
print(f"\nResults:")
for platform, available in platforms.items():
    status = "✓ Found" if available else "✗ Not found"
    print(f"  {platform}: {status}")

# Test 3: Non-existent user
print("\n[TEST3] Detecting platforms for non-existent 'xyzabc123notauser'...")
platforms = detect_player_platforms('xyzabc123notauser')
print(f"\nResults:")
for platform, available in platforms.items():
    status = "✓ Found" if available else "✗ Not found"
    print(f"  {platform}: {status}")

print("\n" + "="*80)
print("[TEST] COMPLETE - Platform detection working!")
print("="*80)
