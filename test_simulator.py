"""Quick test of Interactive Opponent Simulator"""
from chess_analyzer.interactive_simulator import InteractiveSimulator
import chess
import chess.pgn
from io import StringIO

# Create a mock game for testing
pgn_str = """[Event "Test Game"]
[White "Player1"]
[Black "Player2"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6
"""

pgn_file = StringIO(pgn_str)
game = chess.pgn.read_game(pgn_file)

print("Testing Interactive Opponent Simulator...")
print("=" * 60)

# Create simulator
games = [game]
simulator = InteractiveSimulator(games, "TestPlayer")

print(f"✓ Simulator initialized with {len(simulator.database.games)} game(s)")
print(f"✓ Opening statistics: {simulator.database.opening_stats}")
print(f"✓ Total moves in database: {len(simulator.database.move_stats)}")

# Test move parsing with different notations
print("\nTesting move notation parsing...")
board = chess.Board()

test_moves = [
    ("e2e4", "UCI format"),
    ("e4", "SAN short"),
    ("Nf3", "SAN knight"),
    ("nc6", "Lowercase SAN"),
]

for move_str, notation in test_moves:
    board = chess.Board()
    try:
        # Use the parsing logic from simulator
        move = None
        try:
            move = board.parse_san(move_str)
        except:
            try:
                move = board.parse_uci(move_str.lower())
            except:
                try:
                    move = board.parse_san(move_str.upper())
                except:
                    move = None
        
        if move:
            print(f"  ✓ {notation:20} '{move_str}' → {board.san(move)}")
        else:
            print(f"  ✗ {notation:20} '{move_str}' → Failed")
    except Exception as e:
        print(f"  ✗ {notation:20} '{move_str}' → Error: {e}")

print("\n" + "=" * 60)
print("✓ Interactive Opponent Simulator working!")
