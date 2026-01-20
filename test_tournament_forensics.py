#!/usr/bin/env python3
"""Test the new tournament forensics feature"""

from chess_analyzer.tournament_forensics import analyze_tournament

print("\n" + "="*70)
print("TOURNAMENT FORENSICS ANALYSIS TEST")
print("="*70)

# Test 1: Test with a known Lichess tournament
print("\n[TEST 1] Lichess Tournament Analysis")
print("-"*70)

# Using a sample Lichess tournament ID
tournament_id = "5N8Ny9oK"

print(f"Analyzing tournament: {tournament_id}")
result = analyze_tournament(tournament_id)

if result.get('error'):
    print(f"Error: {result['error']}")
    print("(This is expected if the tournament doesn't exist)")
else:
    print(f"\n✓ Tournament: {result.get('tournament_name')}")
    print(f"✓ Players: {result.get('total_players')}")
    print(f"✓ Anomalies Found: {len(result.get('anomalies', []))}")
    
    if result.get('anomalies'):
        print("\nTop Anomalies:")
        for anomaly in result.get('anomalies', [])[:3]:
            print(f"  🚩 {anomaly['player']} (ELO: {anomaly['elo']})")
            print(f"     {anomaly['description']}")

print("\n" + "="*70)
print("Test Complete!")
print("="*70)
