#!/usr/bin/env python3
"""
Quick verification test - no heavy imports, direct module testing.
"""

import sys
import os

# Direct test without package imports
print("\n" + "="*70)
print("QUICK VERIFICATION TEST")
print("="*70)

# Test 1: Check files exist
print("\nTEST 1: File Existence")
print("-" * 70)

files_to_check = [
    'chess_analyzer/player_dna.py',
    'chess_analyzer/ai_integration.py',
    'chess_analyzer/ai_menu_integration.py',
    'chess_analyzer/menu.py',
]

all_exist = True
for file in files_to_check:
    exists = os.path.exists(file)
    status = "✓" if exists else "✗"
    print(f"{status} {file}")
    if not exists:
        all_exist = False

if all_exist:
    print("\n✓ TEST 1 PASSED: All files exist")
else:
    print("\n✗ TEST 1 FAILED: Some files missing")
    sys.exit(1)

# Test 2: Python syntax check
print("\nTEST 2: Python Syntax")
print("-" * 70)

import py_compile

syntax_ok = True
for file in files_to_check:
    try:
        py_compile.compile(file, doraise=True)
        print(f"✓ {file} - syntax OK")
    except py_compile.PyCompileError as e:
        print(f"✗ {file} - syntax error: {e}")
        syntax_ok = False

if syntax_ok:
    print("\n✓ TEST 2 PASSED: All files have valid syntax")
else:
    print("\n✗ TEST 2 FAILED: Syntax errors detected")
    sys.exit(1)

# Test 3: Import key modules
print("\nTEST 3: Module Imports")
print("-" * 70)

try:
    # Add to path
    sys.path.insert(0, 'chess_analyzer')
    
    # Test basic imports
    print("Importing player_dna...")
    import player_dna
    print("✓ player_dna imported")
    
    print("Importing ai_integration...")
    import ai_integration
    print("✓ ai_integration imported")
    
    print("Importing ai_menu_integration...")
    import ai_menu_integration
    print("✓ ai_menu_integration imported")
    
    print("\n✓ TEST 3 PASSED: All key modules import successfully")

except Exception as e:
    print(f"\n✗ TEST 3 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify menu.py has AI integration
print("\nTEST 4: Menu Integration Check")
print("-" * 70)

try:
    with open('chess_analyzer/menu.py', 'r', encoding='utf-8', errors='ignore') as f:
        menu_content = f.read()
    
    checks = [
        ('ai_menu_integration', 'AI menu integration import'),
        ('AIReportGenerator', 'AI report generator'),
        ('prompt_for_ai', 'AI prompt function'),
        ('generate_ai_explanation', 'AI explanation generation'),
    ]
    
    all_good = True
    for check_str, desc in checks:
        if check_str in menu_content:
            print(f"✓ Found: {desc}")
        else:
            print(f"✗ Missing: {desc}")
            all_good = False
    
    if all_good:
        print("\n✓ TEST 4 PASSED: All AI integrations found in menu")
    else:
        print("\n✗ TEST 4 FAILED: Some integrations missing")
        sys.exit(1)

except Exception as e:
    print(f"\n✗ TEST 4 FAILED: {e}")
    sys.exit(1)

# Test 5: Verify fixes in player_dna
print("\nTEST 5: Player DNA Fix Check")
print("-" * 70)

try:
    with open('chess_analyzer/player_dna.py', 'r', encoding='utf-8', errors='ignore') as f:
        dna_content = f.read()
    
    checks = [
        ('isinstance(game_item, dict)', 'Dict format handling'),
        ('isinstance(game_item, chess.pgn.Game)', 'Game object handling'),
        ('List[', 'Fixed type annotation'),
    ]
    
    all_good = True
    for check_str, desc in checks:
        if check_str in dna_content:
            print(f"✓ Found: {desc}")
        else:
            print(f"✗ Missing: {desc}")
            all_good = False
    
    if all_good:
        print("\n✓ TEST 5 PASSED: DNA fixes verified")
    else:
        print("\n✗ TEST 5 FAILED: Some fixes missing")
        sys.exit(1)

except Exception as e:
    print(f"\n✗ TEST 5 FAILED: {e}")
    sys.exit(1)

# Test 6: Verify AI providers
print("\nTEST 6: AI Providers")
print("-" * 70)

try:
    # Check for provider classes
    providers = [
        'OpenAIProvider',
        'ClaudeProvider',
        'OllamaProvider',
        'DeepseekProvider',
    ]
    
    all_exist = True
    for provider in providers:
        if provider in ai_integration.__dict__:
            print(f"✓ {provider} defined")
        else:
            print(f"✗ {provider} missing")
            all_exist = False
    
    if all_exist:
        print("\n✓ TEST 6 PASSED: All providers implemented")
    else:
        print("\n✗ TEST 6 FAILED: Some providers missing")
        sys.exit(1)

except Exception as e:
    print(f"\n✗ TEST 6 FAILED: {e}")
    sys.exit(1)

# Summary
print("\n" + "="*70)
print("✓✓✓ ALL QUICK VERIFICATION TESTS PASSED ✓✓✓")
print("="*70)

print("\n✓ Player DNA fix is in place")
print("✓ AI integration module created and imports successfully")
print("✓ Menu integration code added")
print("✓ All 4 AI providers implemented")
print("✓ Syntax is valid throughout")

print("\nNext steps:")
print("1. Test in the actual menu system (Option 10)")
print("2. Create AI report with test data")
print("3. Verify full end-to-end workflow")

sys.exit(0)
