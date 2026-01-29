#!/usr/bin/env python3
"""Test Feature 15 - Anti-Repertoire Builder"""

import sys
sys.path.insert(0, '.')

from chess_analyzer.opponent_repertoire_builder import OpponentRepertoireBuilder
import chess.pgn
from io import StringIO

# Create some sample games
pgn_text = '''[Event "Test"]
[Site "?"]
[Date "2024.01.01"]
[Round "?"]
[White "TestPlayer"]
[Black "hikaru"]
[Result "0-1"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. cxd5 exd5 5. Bg5 c6 6. Qc2 Be7 7. O-O-O O-O 8. Bxf6 Bxf6 *

[Event "Test"]
[Site "?"]
[Date "2024.01.02"]
[Round "?"]
[White "TestPlayer"]
[Black "hikaru"]
[Result "0.5-0.5"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Bg5 e6 7. f4 Be7 *
'''

games = []
pgn_io = StringIO(pgn_text)
while True:
    game = chess.pgn.read_game(pgn_io)
    if game is None:
        break
    games.append(game)

print(f"Loaded {len(games)} sample games\n")

# Test the builder
print("Testing OpponentRepertoireBuilder...")
builder = OpponentRepertoireBuilder(
    opponent_name="hikaru",
    games=games,
    color="white",
    loss_filter="loss"
)

print(f"✓ Builder created with {len(builder.games)} games")

# Generate PGN
output_file = "reports/test_anti_repertoire.pgn"
builder.generate_pgn(output_file)
print(f"✓ PGN generated: {output_file}")

# Check file was created
import os
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        content = f.read()
    print(f"✓ File created, size: {len(content)} bytes")
    print(f"\nFirst 500 chars of PGN:")
    print(content[:500])
else:
    print("✗ File not created")
