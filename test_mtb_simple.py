#!/usr/bin/env python
"""Simple test for MoveTreeBuilder"""

print("[TEST] MoveTreeBuilder - Simple Test")
print("=" * 50)

try:
    import chess.pgn
    print("✓ chess.pgn imported")
except Exception as e:
    print(f"✗ Failed to import chess.pgn: {e}")
    exit(1)

try:
    from chess_analyzer.move_tree_builder import MoveTreeBuilder
    print("✓ MoveTreeBuilder imported")
except Exception as e:
    print(f"✗ Failed to import MoveTreeBuilder: {e}")
    exit(1)

try:
    import io
    pgn_text = """[Event "Test"]
[White "Player1"]
[Black "Opponent"]
[Result "1-0"]
[ECO "C45"]

1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 1-0
"""
    pgn_file = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_file)
    print(f"✓ Game parsed: {game.headers.get('Event')}")
    
    builder = MoveTreeBuilder([game], "Opponent")
    print(f"✓ Tree built: {builder.get_total_positions()} positions")
    print(f"✓ Tree depth: {builder.get_tree_depth()}")
    
    print("\n✓ All tests passed!")
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
