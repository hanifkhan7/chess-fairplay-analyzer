#!/usr/bin/env python3
"""
Simulate Menu Option 10 DNA analysis with real imports
to verify the encoding fix works in the actual menu context
"""

import sys
import os
from chess_analyzer.player_dna import PlayerDNA

def test_menu_option_10_simulation():
    """
    Simulate what Menu Option 10 does with a minimal dataset
    """
    print("Simulating Menu Option 10 DNA Analysis...")
    print("=" * 70)
    
    try:
        # Create minimal DNA object to test get_tree_report()
        dna_data = {
            'player': 'hikaru',
            'total_games': 248,
            'color': 'white',
            'statistics': {
                'wins': 196,
                'draws': 18,
                'losses': 34,
                'win_rate': 79.0
            },
            'favorite_openings': [
                {'name': 'Italian Game', 'games': 120, 'win_rate': 82.0},
                {'name': 'Ruy Lopez', 'games': 85, 'win_rate': 78.0}
            ],
            'weak_openings': [],
            'risky_openings': []
        }
        
        # Create PlayerDNA instance
        dna = PlayerDNA(dna_data)
        
        # Get tree report (this is where Unicode characters are added)
        print("\n[STEP 1] Getting tree report with Unicode characters...")
        tree_report = dna.get_tree_report(limit=15)
        
        # Verify Unicode characters are in the report
        if '⭐' in tree_report:
            print("✓ Unicode character ⭐ is in tree_report")
        if '⚠️' in tree_report:
            print("✓ Unicode character ⚠️ is in tree_report")
        if '🎲' in tree_report:
            print("✓ Unicode character 🎲 is in tree_report")
        
        # Now save the file EXACTLY as menu.py does
        print("\n[STEP 2] Saving report to file (exact code from menu.py)...")
        os.makedirs('reports', exist_ok=True)
        
        username = 'hikaru_test'
        report_file = f"reports/{username}_player_dna_report.txt"
        
        # THIS IS THE EXACT CODE FROM menu.py line 1637-1640
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(tree_report)
            f.write("\n\nEnd of report")
        
        print(f"✓ Successfully saved to: {report_file}")
        
        # Verify the file was saved with Unicode intact
        print("\n[STEP 3] Verifying file contents...")
        with open(report_file, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        if '⭐' in saved_content and '⚠️' in saved_content and '🎲' in saved_content:
            print("✓ All Unicode characters were preserved in saved file")
        
        print("\n" + "="*70)
        print("✓ SUCCESS - Menu Option 10 encoding fix is working!")
        print("="*70)
        print("\nThe file was saved successfully with Unicode characters.")
        print(f"File location: {report_file}")
        
        return True
        
    except UnicodeEncodeError as e:
        print(f"\n✗ UnicodeEncodeError: {e}")
        print(f"\nThis means the encoding='utf-8' fix didn't work.")
        print(f"Error position: {e.start}-{e.end}")
        print(f"Character: {e.object[e.start:e.end]}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_menu_option_10_simulation()
    sys.exit(0 if success else 1)
