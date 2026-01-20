#!/usr/bin/env python3
"""
Test Tournament Forensics with Real Lichess Data
"""

from chess_analyzer.tournament_forensics import analyze_tournament

print("\n" + "="*70)
print("TOURNAMENT FORENSICS - REAL LICHESS TOURNAMENT TEST")
print("="*70)

# Test with multiple Lichess tournament IDs
# These are examples - actual IDs may vary

test_tournaments = [
    "5N8Ny9oK",      # Sample Lichess tournament
    "perft2024",     # Sample format
]

for tournament_id in test_tournaments:
    print(f"\n[TEST] Attempting to analyze: {tournament_id}")
    print("-" * 70)
    
    result = analyze_tournament(tournament_id)
    
    if result.get('error'):
        print(f"Status: Tournament not found or error occurred")
        print(f"Error: {result['error']}")
        print("\nNote: This is expected if the tournament ID doesn't exist")
        print("To find real Lichess tournaments:")
        print("  1. Visit: https://lichess.org/tournament")
        print("  2. Find a concluded tournament")
        print("  3. Copy its ID from the URL")
        continue
    
    # If successful
    print(f"\n✅ TOURNAMENT ANALYSIS SUCCESSFUL")
    print(f"\nTournament: {result.get('tournament_name')}")
    print(f"Players: {result.get('total_players')}")
    
    summary = result.get('summary', {})
    print(f"Average ELO: {summary.get('average_elo')}")
    print(f"ELO Range: {summary.get('elo_range')}")
    
    anomalies = result.get('anomalies', [])
    print(f"\nAnomalies Detected: {len(anomalies)}")
    
    if anomalies:
        print("\n[FLAGGED RESULTS]")
        for i, anomaly in enumerate(anomalies[:5], 1):
            severity = anomaly.get('severity', 'UNKNOWN')
            emoji = '🚩' if severity == 'HIGH' else '⚠️'
            
            print(f"\n{emoji} #{anomaly.get('rank')}: {anomaly['player']} (ELO: {anomaly['elo']})")
            print(f"   {anomaly['description']}")
            if anomaly.get('probability_pct'):
                print(f"   Probability: {anomaly['probability_pct']:.1f}%")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nNote: To use this feature with your own tournaments:")
print("  1. Find a Lichess tournament at: https://lichess.org/tournament")
print("  2. Use the tournament ID in the menu")
print("  3. System will analyze standings for suspicious patterns")
print("\nFor Chess.com tournaments, use the 'Analyze Player' feature")
print("to check top finishers individually.")
print("="*70 + "\n")
