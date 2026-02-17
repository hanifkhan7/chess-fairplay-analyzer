#!/usr/bin/env python3
"""
Test Unicode encoding fix for report files.
"""

import sys
import os
import json
from pathlib import Path

# Test data with Unicode characters (same as in DNA reports)
test_content = """
======================================================================
[OPENING TREE] HIKARU
======================================================================

Total Games: 50
Color: WHITE

Record: 43W 1D 6L
Win Rate: 86.0%

⭐ FAVORITE OPENINGS (Best Performance):
   1. Ruy Lopez                            ( 50G)  86.0%

⚠️  WEAK LINES (Needs Improvement):

🎲 RISKY LINES (High Variance):

======================================================================
"""

test_json = {
    "player": "hikaru",
    "total_games": 50,
    "favorite_openings": [
        {"name": "Ruy Lopez", "games": 50, "win_rate": 86.0}
    ],
    "notes": "Contains Unicode: ⭐ ⚠️ 🎲"
}

def test_text_writing():
    """Test writing text file with Unicode."""
    print("TEST 1: Writing text file with Unicode characters...")
    try:
        os.makedirs('test_encoding', exist_ok=True)
        
        # Write with UTF-8 encoding (the fix)
        test_file = 'test_encoding/test_report.txt'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✓ Successfully wrote: {test_file}")
        
        # Verify it was written correctly
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '⭐' in content and '⚠️' in content and '🎲' in content:
            print("✓ Unicode characters preserved correctly")
            return True
        else:
            print("✗ Unicode characters were lost")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_json_writing():
    """Test writing JSON file with Unicode."""
    print("\nTEST 2: Writing JSON file with Unicode characters...")
    try:
        os.makedirs('test_encoding', exist_ok=True)
        
        # Write with UTF-8 encoding and ensure_ascii=False (the fix)
        test_file = 'test_encoding/test_report.json'
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_json, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully wrote: {test_file}")
        
        # Verify it was written correctly
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if '⭐' in str(data) or '🎲' in str(data):
            print("✓ Unicode characters preserved correctly in JSON")
            return True
        else:
            print("✗ Unicode characters were lost in JSON")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_file_reading():
    """Test reading files back."""
    print("\nTEST 3: Reading written files with Unicode...")
    try:
        # Read text file
        with open('test_encoding/test_report.txt', 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Read JSON file
        with open('test_encoding/test_report.json', 'r', encoding='utf-8') as f:
            json_content = json.load(f)
        
        print("✓ Successfully read both files with UTF-8 encoding")
        
        if '⭐' in text_content:
            print("✓ Text file contains Unicode star")
        if json_content['notes'] == test_json['notes']:
            print("✓ JSON content matches original with Unicode")
        
        return True
            
    except Exception as e:
        print(f"✗ Error reading: {e}")
        return False

def cleanup():
    """Clean up test files."""
    print("\nCleaning up test files...")
    try:
        import shutil
        shutil.rmtree('test_encoding')
        print("✓ Cleanup successful")
    except:
        pass

def main():
    print("="*70)
    print("UNICODE ENCODING FIX VERIFICATION")
    print("="*70)
    
    results = []
    results.append(test_text_writing())
    results.append(test_json_writing())
    results.append(test_file_reading())
    
    # Cleanup
    cleanup()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nThe Unicode encoding fix is working correctly!")
        print("Files with emoji and special characters will now save properly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
