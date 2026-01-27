"""Test MoveTreeBuilder class"""

import chess.pgn
import io
from chess_analyzer.move_tree_builder import MoveTreeBuilder

# Test with sample PGN
pgn_text = """[Event "Test1"]
[Site "Test"]
[White "Player1"]
[Black "Opponent"]
[Result "1-0"]
[ECO "C45"]

1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.b4 Bxb4 1-0

[Event "Test2"]
[Site "Test"]
[White "Player1"]
[Black "Opponent"]
[Result "0-1"]
[ECO "C45"]

1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.c3 Nf6 0-1

[Event "Test3"]
[Site "Test"]
[White "Opponent"]
[Black "Player1"]
[Result "1/2-1/2"]
[ECO "D50"]

1.d4 d5 2.c4 e6 3.Nc3 Nf6 1/2-1/2
"""

print("[TEST] MoveTreeBuilder")
print("=" * 50)

games = []
for pgn in pgn_text.split('\n\n[Event'):
    if pgn.strip():
        if not pgn.startswith('[Event'):
            pgn = '[Event' + pgn
        pgn_file = io.StringIO(pgn)
        game = chess.pgn.read_game(pgn_file)
        if game:
            games.append(game)

print(f"Games loaded: {len(games)}")

# Test with opponent as Black
builder = MoveTreeBuilder(games, "Opponent")
print(f"\nTree Stats:")
print(f"  Positions: {builder.get_total_positions()}")
print(f"  Depth: {builder.get_tree_depth()}")
print(f"  Total nodes: {sum(1 for _ in builder.to_dict())}")

# Test root children
root = builder.get_root()
print(f"\nRoot moves: {list(root.children.keys())}")

if root.children:
    first_move = list(root.children.keys())[0]
    first_child = root.children[first_move]
    print(f"\nFirst move '{first_move}':")
    print(f"  Games: {first_child.games}")
    print(f"  Win rate: {first_child.get_win_rate():.1f}%")
    print(f"  ECO: {first_child.eco_code}")
    print(f"  Opening: {first_child.opening_name}")

# Test to_dict
tree_dict = builder.to_dict()
print(f"\nTree dict keys: {list(tree_dict.keys())}")
print(f"Opponent: {tree_dict['opponent']}")
print(f"Color filter: {tree_dict['color_filter']}")
print(f"Depth: {tree_dict['depth']}")
print(f"Positions: {tree_dict['positions']}")

# Test save
import tempfile
import os
temp_dir = tempfile.gettempdir()
json_path = os.path.join(temp_dir, 'test_tree.json')
builder.save_json(json_path)
print(f"\n✓ JSON saved successfully to {json_path}")

# Test with color filter
builder_white = MoveTreeBuilder(games, "Opponent", "white")
print(f"\nWith white filter: {builder_white.get_total_positions()} positions")

builder_black = MoveTreeBuilder(games, "Opponent", "black")
print(f"With black filter: {builder_black.get_total_positions()} positions")

print("\n✓ All MoveTreeBuilder tests passed!")
