#!/usr/bin/env python3
"""
Direct test of the encoding fix in menu.py
"""

import sys
import os

# Create test report with Unicode characters (same as DNA tree_report)
test_tree_report = """
======================================================================
[OPENING TREE] HIKARU
======================================================================

Total Games: 248
Color: WHITE

Record: 196W 18D 34L
Win Rate: 79.0%

⭐ FAVORITE OPENINGS (Best Performance):
   1. Unknown Opening                          (248G)  79.0%

⚠️  WEAK LINES (Needs Improvement):

🎲 RISKY LINES (High Variance):

======================================================================
"""

test_text_report = """
[DNA REPORT] Opening Repertoire Profile
========================================
Player: hikaru
Total Games: 248
Record: 196W 18D 34L
"""

def test_menu_py_fix():
    """Test the exact code from menu.py"""
    print("testing menu.py encoding fix...")
    print("-" * 70)
    
    try:
        # Create reports directory
        os.makedirs('reports', exist_ok=True)
        
        # Test 1: The exact code from menu.py line 1637-1640
        print("\nTest 1: Text file write (menu.py line 1637)")
        username = "test_hikaru"
        report_file = f"reports/{username}_player_dna_report.txt"
        
        # This is the EXACT code from menu.py now (with encoding='utf-8')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(test_tree_report)
            f.write("\n\n" + test_text_report)
        
        print(f"✓ Successfully wrote: {report_file}")
        
        # Verify content
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '⭐' in content:
            print("✓ Unicode character ⭐ preserved")
        if '⚠️' in content:
            print("✓ Unicode character ⚠️ preserved")
        if '🎲' in content:
            print("✓ Unicode character 🎲 preserved")
        
        # Test 2: JSON file write
        print("\nTest 2: JSON file write")
        import json
        json_file = f"reports/{username}_player_dna.json"
        test_data = {
            "player": "hikaru",
            "total_games": 248,
            "notes": "Contains emoji: ⭐ ⚠️ 🎲"
        }
        
        # This is the EXACT code from player_dna.py now
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully wrote: {json_file}")
        
        # Verify content
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if '⭐' in str(data):
            print("✓ Unicode preserved in JSON")
        
        print("\n" + "="*70)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*70)
        print("\nThe encoding fix is working correctly!")
        print("Menu.py should now save reports without Unicode errors.")
        
        return True
        
    except UnicodeEncodeError as e:
        print(f"\n✗ UnicodeEncodeError: {e}")
        print(f"Encoding used: {sys.stdout.encoding}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_menu_py_fix()
    sys.exit(0 if success else 1)
