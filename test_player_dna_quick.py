#!/usr/bin/env python
"""Quick test of player_dna module"""

try:
    from chess_analyzer.player_dna import (
        PlayerDNAProfile, 
        build_player_dna, 
        generate_player_dna_report
    )
    print("✓ PlayerDNAProfile class imports successfully")
    print("✓ build_player_dna function imports successfully")
    print("✓ generate_player_dna_report function imports successfully")
    
    # Test profile creation
    test_data = {
        'player': 'TestPlayer',
        'total_games': 100,
        'color': 'white',
        'statistics': {
            'wins': 60,
            'draws': 20,
            'losses': 20,
            'win_rate': 60.0
        },
        'favorite_openings': [
            {'name': 'Sicilian Defense', 'games': 30, 'win_rate': 65.0},
            {'name': 'Queen\'s Gambit', 'games': 25, 'win_rate': 60.0},
        ],
        'weak_openings': [
            {'name': 'French Defense', 'games': 15, 'win_rate': 45.0},
        ],
        'risky_openings': [
            {'name': 'King\'s Indian Attack', 'games': 10, 'draw_rate': 50.0, 'win_rate': 40.0},
        ]
    }
    
    # Create profile
    profile = PlayerDNAProfile(test_data)
    print(f"✓ Created profile: {profile}")
    
    # Test methods
    report = profile.get_tree_report(limit=5)
    print(f"✓ get_tree_report() works - {len(report)} chars")
    
    stats = profile.get_statistics()
    print(f"✓ get_statistics() works - {stats['win_rate']}%")
    
    favorites = profile.get_favorite_openings()
    print(f"✓ get_favorite_openings() works - {len(favorites)} openings")
    
    print("\n✓✓✓ All tests passed! ✓✓✓")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
