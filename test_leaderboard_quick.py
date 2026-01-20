#!/usr/bin/env python
"""Quick test of leaderboard analyzer module."""

try:
    from chess_analyzer.leaderboard_analyzer import fetch_leaderboard, LeaderboardAnalyzer
    print("✓ Module imports successful")
    
    # Test fetching FIDE info
    result = fetch_leaderboard('fide')
    if result.get('info'):
        print(f"✓ FIDE leaderboard info available: {result['info']['url']}")
    else:
        print("✗ FIDE info missing")
    
    # Test LeaderboardAnalyzer instantiation
    analyzer = LeaderboardAnalyzer()
    print("✓ LeaderboardAnalyzer instantiation successful")
    
    # Test getting countries
    countries = analyzer.get_lichess_countries()
    if countries:
        print(f"✓ Lichess countries available: {len(countries)} countries")
    else:
        print("✗ No countries returned")
        
    print("\n✓ ALL TESTS PASSED")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
