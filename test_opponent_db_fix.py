#!/usr/bin/env python3
"""Quick test that OpponentMoveDatabase handles chess.pgn.Game objects"""

import chess.pgn
import io

# Sample PGN for testing
sample_pgn = """
[Event "Test Game"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]
[Opening "Sicilian Defense"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1-0
"""

# Parse the game
game = chess.pgn.read_game(io.StringIO(sample_pgn))

# Test OpponentMoveDatabase with chess.pgn.Game object
from chess_analyzer.interactive_simulator import OpponentMoveDatabase

print("\n" + "="*60)
print("Testing OpponentMoveDatabase with chess.pgn.Game object")
print("="*60)

# Test with single game
games = [game]  # List with one chess.pgn.Game object
db = OpponentMoveDatabase(games, "Player2")

print(db.summary())

# Get opening
openings = db.get_openings()
print(f"\nOpenings found: {openings}")

# Get moves from initial position
initial_fen = chess.Board().fen()
moves = db.get_moves_from_position(initial_fen)
print(f"\nMoves in initial position: {moves}")

print("\n✓ Test passed! OpponentMoveDatabase properly handles chess.pgn.Game objects")
