#!/usr/bin/env python3
"""
Test Tournament Forensics Analyzer
"""

from chess_analyzer.tournament_analyzer import TournamentAnalyzer

print("\n" + "="*70)
print("TOURNAMENT FORENSICS ANALYZER TEST")
print("="*70)

analyzer = TournamentAnalyzer()

# Test 1: ELO Probability Calculation
print("\n[TEST 1] ELO Probability Calculations")
print("-"*70)

test_cases = [
    (1600, 1600, "Equal rating"),
    (1600, 1800, "200 ELO disadvantage"),
    (1800, 1600, "200 ELO advantage"),
    (1200, 2000, "800 ELO disadvantage"),
    (2000, 1200, "800 ELO advantage"),
]

for player_elo, opponent_elo, description in test_cases:
    prob = analyzer.calculate_win_probability(player_elo, opponent_elo)
    print(f"  {player_elo} vs {opponent_elo:4d} ({description:20s}): {prob*100:5.1f}% win probability")

# Test 2: Tournament Win Probability
print("\n[TEST 2] Tournament Win Probability")
print("-"*70)

tournament_cases = [
    (1600, 1600, 10, "Equal rating, 10 games"),
    (1800, 1600, 10, "200 ELO advantage, 10 games"),
    (1600, 1600, 5, "Equal rating, 5 games"),
]

for player_elo, avg_opp_elo, num_games, description in tournament_cases:
    prob = analyzer.calculate_tournament_win_probability(player_elo, avg_opp_elo, num_games)
    print(f"  {description:35s}: {prob*100:6.2f}% tournament win probability")

# Test 3: Suspicious Result Detection
print("\n[TEST 3] Suspicious Result Detection")
print("-"*70)

# Mock tournament data
mock_tournament = {
    'results': [
        {
            'username': 'Player_A',
            'rating': 1600,
            'wins': 8,
            'losses': 2,
            'draws': 0
        },
        {
            'username': 'Player_B',
            'rating': 1400,
            'wins': 9,
            'losses': 1,
            'draws': 0
        },
        {
            'username': 'Player_C',
            'rating': 1800,
            'wins': 4,
            'losses': 6,
            'draws': 0
        },
    ],
    'avg_rating': 1600
}

suspicious = analyzer.flag_suspicious_results(mock_tournament)

if suspicious:
    print(f"  Found {len(suspicious)} suspicious result(s):\n")
    for result in suspicious:
        print(f"    Player: {result['player']}")
        print(f"      Rating: {result['elo']} ELO")
        print(f"      Expected wins: {result['expected_wins']:.1f}, Actual: {result['actual_wins']:.1f}")
        print(f"      Deviation: {result['deviation_percent']:+.1f}%")
        print(f"      Suspicion: {result['suspicion']} ({result['severity']})")
        print()
else:
    print("  No suspicious results in test data")

# Test 4: Fetch Tournament (will show available data)
print("\n[TEST 4] Tournament Data Fetching")
print("-"*70)

print("  Lichess tournaments (last 30 days):")
tournaments = analyzer.fetch_lichess_tournaments(days_back=30)
if tournaments:
    print(f"    Found {len(tournaments)} tournaments")
    for t in tournaments[:3]:
        print(f"      - {t.get('name')} ({t.get('speed')} {t.get('variant')})")
else:
    print("    No recent tournaments found (expected - API may be limited)")

print("\n" + "="*70)
print("✅ TOURNAMENT ANALYZER TESTS COMPLETE")
print("="*70 + "\n")
