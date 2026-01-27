#!/usr/bin/env python3
"""Test the new move tree builder"""

import chess
import chess.pgn
from io import StringIO
from chess_analyzer.move_tree import MoveTreeNode, MoveTreeBuilder, TreeVisualizer

print("Testing Move Tree Builder...\n")

# Test 1: MoveTreeNode creation
print("[TEST 1] MoveTreeNode creation...")
node = MoveTreeNode("e4")
node.add_game_result("1-0")
node.add_game_result("1-0")
node.add_game_result("0-1")
node.add_game_result("1/2-1/2")

assert node.games == 4, f"Expected 4 games, got {node.games}"
assert node.wins == 2, f"Expected 2 wins, got {node.wins}"
assert node.losses == 1, f"Expected 1 loss, got {node.losses}"
assert node.draws == 1, f"Expected 1 draw, got {node.draws}"
print(f"  [OK] Move: {node.move}")
print(f"  [OK] Games: {node.games}")
print(f"  [OK] Win Rate: {node.get_win_rate():.1f}%")
print(f"  [OK] Draw Rate: {node.get_draw_rate():.1f}%")
print(f"  [OK] Loss Rate: {node.get_loss_rate():.1f}%")

# Test 2: MoveTreeBuilder
print("\n[TEST 2] MoveTreeBuilder...")
builder = MoveTreeBuilder()

# Create a simple PGN game
pgn_string = """[Event "Test"]
[Site "?"]
[Date "2025.01.27"]
[White "TestPlayer"]
[Black "Opponent"]
[Result "1-0"]

1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 1-0
"""

pgn_io = StringIO(pgn_string)
game = chess.pgn.read_game(pgn_io)

if game:
    builder.add_game(game, white_perspective=True)
    root = builder.get_root()
    
    print(f"  [OK] Root node: {root.move}")
    print(f"  [OK] Children: {len(root.children)}")
    
    # Check first response
    if "e4" in root.children:
        e4_node = root.children["e4"]
        print(f"  [OK] 1.e4 found: {e4_node.games} games")
        print(f"  [OK] e4 children: {len(e4_node.children)}")
else:
    print("  [ERROR] Could not parse PGN")

# Test 3: TreeVisualizer ASCII
print("\n[TEST 3] TreeVisualizer ASCII output...")
visualizer = TreeVisualizer(root)
ascii_output = visualizer.to_ascii(max_depth=5)
print(ascii_output)

print("\n[SUCCESS] All move tree tests passed!")

