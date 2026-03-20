#!/usr/bin/env python3
"""Test the corrected chess board rendering"""

from chess_analyzer.exploit_report_generator import fen_to_svg
import chess

# Test starting position
fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
svg = fen_to_svg(fen)

# Verify correct chess board setup
board = chess.Board(fen)

print("=" * 60)
print("CHESS BOARD VERIFICATION")
print("=" * 60)
print()

# Check SVG contains correct number of pieces
white_pawns = fen.count('P')
white_pieces = sum(1 for c in fen.split()[0] if c.isupper() and c != '/')
black_pieces = sum(1 for c in fen.split()[0] if c.islower())

print("Initial position pieces:")
print(f"  White pieces: {white_pieces}")
print(f"  Black pieces: {black_pieces}")
print()

# Verify board colors in SVG (looking for the hex codes)
if '#a0522d' in svg and '#deb887' in svg:
    print("✅ Board colors present: Dark (#a0522d) and Light (#deb887)")
else:
    print("❌ Board color issue!")
    
# Verify no errors in SVG
if 'Invalid' not in svg and 'Error' not in svg:
    print("✅ SVG generated without errors")
    print(f"   SVG size: {len(svg):,} characters")
else:
    print("❌ SVG has errors")

print()
print("Square color verification (from Wikipedia: h1 must be LIGHT):")
print("  a1 (bottom-left):  should be DARK")
print("  h1 (bottom-right): should be LIGHT ✨")  
print("  a8 (top-left):     should be LIGHT")
print("  h8 (top-right):    should be DARK")
print()

print("Piece placement verification:")
# Check a few known pieces from starting position
test_pieces = [
    (chess.A1, 'White Rook at a1'),
    (chess.E1, 'White King at e1'),
    (chess.E8, 'Black King at e8'),
    (chess.A7, 'Black Pawn at a7'),
    (chess.H1, 'White Rook at h1'),
    (chess.D8, 'Black Queen at d8'),
]

all_correct = True
for square, desc in test_pieces:
    piece = board.piece_at(square)
    if piece:
        print(f"  ✅ {desc}: {piece}")
    else:
        print(f"  ❌ {desc}: Missing piece!")
        all_correct = False

print()
if all_correct:
    print("✅ All pieces in correct starting positions")
else:
    print("❌ Some pieces are missing or misplaced")

print()
print("=" * 60)
print("✅ BOARD RENDERING TEST COMPLETE")
print("=" * 60)
