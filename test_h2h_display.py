#!/usr/bin/env python
"""
Simple test to verify Head-to-Head Analyzer displays correctly
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer

def test_display_format():
    """Test that the display function formats output correctly"""
    print("=" * 80)
    print("TEST: Head-to-Head Display Format")
    print("=" * 80)
    
    analyzer = HeadToHeadAnalyzer()
    
    # Create a test report matching the actual structure
    test_report = {
        'players': {
            'player1': {'name': 'rohan_asif', 'elo': 1650, 'games': 50},
            'player2': {'name': 'Hassan_Tahirr', 'elo': 1680, 'games': 50}
        },
        'elo_probability': (0.45, 0.55),
        'performance_probability': (0.52, 0.48),
        'h2h_games': {
            'total_games': 5,
            'player1_wins': 2,
            'player2_wins': 2,
            'draws': 1,
            'games': [
                {
                    'result': 'W',
                    'opponent': 'Hassan_Tahirr',
                    'opening': 'Sicilian Defense',
                    'date': '2024-01-15'
                },
                {
                    'result': 'L',
                    'opponent': 'Hassan_Tahirr',
                    'opening': 'Ruy Lopez',
                    'date': '2024-01-10'
                }
            ],
            'openings': {
                'Sicilian Defense': {'games': 2, 'player1_wins': 1, 'player2_wins': 1},
                'Ruy Lopez': {'games': 3, 'player1_wins': 1, 'player2_wins': 2}
            }
        },
        'h2h_probability': (0.40, 0.60),
        'combined_probability': (0.46, 0.54),
        'prediction': 'Hassan_Tahirr',
        'confidence': 54.0,
        'history_analysis': {
            'player1': {
                'wins': 27, 'losses': 18, 'draws': 5,
                'win_rate': 54.0, 'avg_accuracy': 76.3
            },
            'player2': {
                'wins': 28, 'losses': 16, 'draws': 6,
                'win_rate': 56.0, 'avg_accuracy': 78.1
            }
        },
        'suspicious_activity': {
            'player1': [],
            'player2': []
        }
    }
    
    print("\n[INFO] Testing display format with test report...")
    print("[INFO] This should show:")
    print("  - Individual player stats boxes")
    print("  - Comparison analysis")
    print("  - H2H games with opening stats")
    print("  - Final prediction")
    
    try:
        analyzer.display_matchup_report(test_report)
        print("\n✓ Display test successful!")
        return True
    except Exception as e:
        print(f"\n✗ Display test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("[START] Testing display format...", flush=True)
    success = test_display_format()
    print("\n" + "=" * 80)
    if success:
        print("✓ DISPLAY FORMAT TEST PASSED")
    else:
        print("✗ DISPLAY FORMAT TEST FAILED")
    print("=" * 80)
    sys.exit(0 if success else 1)
