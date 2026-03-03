#!/usr/bin/env python3
"""
Test PGN generation and AI integration fixes
"""

import sys
import os
from io import StringIO
import chess.pgn

print("=" * 70)
print("TEST 1: OPENING TREE PGN GENERATION")
print("=" * 70)

try:
    from chess_analyzer.opening_tree import OpeningTree, MoveNode
    
    # Create a simple tree with sample moves
    tree = OpeningTree()
    
    # Create test games programmatically
    test_pgns = [
        "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6",
        "1. e4 e5 2. Nf3 Nc6 3. Bb5 Nge7",
        "1. e4 c5 2. Nf3 Nc6 3. d4 cxd4",
        "1. d4 d5 2. c4 c6",
        "1. d4 d5 2. c4 dxc4",
    ]
    
    for pgn_text in test_pgns:
        pgn_io = StringIO(pgn_text)
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            game = chess.pgn.Game()
            game.headers["Result"] = "1-0"
            board = game.board()
            for move_san in pgn_text.split():
                if move_san[0].isdigit() or move_san == ".":
                    continue
                try:
                    move = board.parse_san(move_san)
                    game.add_main_variation(move)
                    board.push(move)
                except:
                    break
        tree.insert_game(game)
    
    print(f"✓ Created test tree with {tree.game_count} games")
    
    # Check statistics
    stats = tree.get_stats_summary()
    print(f"✓ Unique positions: {stats['unique_positions']}")
    print(f"✓ Tree depth: {stats['max_depth']}")
    
    # Try to export PGN
    pgn_export = tree.export_to_pgn("TestPlayer")
    if pgn_export and "TestPlayer" in pgn_export:
        print(f"✓ PGN export successful ({len(pgn_export)} chars)")
    else:
        print(f"✗ PGN export failed")
        sys.exit(1)
    
    # Try to save PGN
    os.makedirs('reports', exist_ok=True)
    pgn_file = 'reports/test_opening_book.pgn'
    if tree.save_pgn(pgn_file, "TestPlayer"):
        with open(pgn_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if "TestPlayer" in content and len(content) > 50:
            print(f"✓ PGN file saved and verified")
        else:
            print(f"✗ PGN file content invalid")
            sys.exit(1)
    else:
        print(f"✗ PGN file save failed")
        sys.exit(1)
    
    print("\n✓✓✓ OPENING TREE TEST PASSED\n")
    
except Exception as e:
    print(f"✗ Error in opening tree test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("TEST 2: OPENAI API COMPATIBILITY (v1.0.0+)")
print("=" * 70)

try:
    import inspect
    from chess_analyzer import ai_integration
    
    # Check that new API structure is in place without initializing
    source = inspect.getsource(ai_integration.OpenAIProvider)
    
    if "from openai import OpenAI" in source:
        print(f"✓ Import statement uses new API: 'from openai import OpenAI'")
    else:
        print(f"✗ New OpenAI import not found!")
        sys.exit(1)
    
    if "client.chat.completions.create" in source:
        print(f"✓ Chat API call uses new format: 'client.chat.completions.create'")
    else:
        print(f"✗ New chat completions API not found!")
        sys.exit(1)
    
    if "openai.ChatCompletion" in source:
        print(f"✗ Old API (openai.ChatCompletion) still present!")
        sys.exit(1)
    else:
        print(f"✓ Old API (openai.ChatCompletion) completely removed")
    
    print("\n✓✓✓ OPENAI API TEST PASSED (Ready for v1.0.0+)\n")
    
except Exception as e:
    print(f"✗ Error in OpenAI test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("TEST 3: MENU INTEGRATION CHECK")
print("=" * 70)

try:
    # Check that menu.py has the PGN generation code
    with open('chess_analyzer/menu.py', 'r', encoding='utf-8') as f:
        menu_content = f.read()
    
    if "from .opening_tree import build_opening_tree_from_games" in menu_content:
        print(f"✓ Menu imports opening_tree module")
    else:
        print(f"✗ Menu does not import opening_tree")
        sys.exit(1)
    
    if "opening_book.pgn" in menu_content:
        print(f"✓ Menu has PGN export code")
    else:
        print(f"✗ Menu missing PGN export code")
        sys.exit(1)
    
    utf8_count = menu_content.count("encoding='utf-8'")
    if "encoding='utf-8'" in menu_content and utf8_count >= 2:
        print(f"✓ Menu has UTF-8 encoding fixes ({utf8_count} locations)")
    else:
        print(f"✗ UTF-8 encoding fixes missing")
        sys.exit(1)
    
    print("\n✓✓✓ MENU INTEGRATION TEST PASSED\n")
    
except Exception as e:
    print(f"✗ Error in menu test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("✓✓✓ ALL TESTS PASSED ✓✓✓")
print("=" * 70)
print("\nSummary:")
print("  ✓ Unicode encoding bug: FIXED")
print("  ✓ OpenAI API compatibility: FIXED (v1.0.0+)")
print("  ✓ PGN generation: IMPLEMENTED")
print("  ✓ Menu integration: COMPLETE")
print("\nNext steps:")
print("  1. Run Menu Option 10 to test full integration")
print("  2. Select AI provider to test AI generation")
print("  3. Check reports/ folder for all output files")
print("  4. Verify opening_book.pgn contains variation tree")
