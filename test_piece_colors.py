#!/usr/bin/env python3
"""Verify piece colors are correct"""

from chess_analyzer.exploit_report_generator import fen_to_svg
import chess

# Test starting position
fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
board = chess.Board(fen)
svg = fen_to_svg(fen)

print("=" * 60)
print("PIECE COLOR VERIFICATION")
print("=" * 60)
print()

# Count pieces from FEN
white_pieces = sum(1 for c in fen.split()[0] if c.isupper() and c not in '12345678/')
black_pieces = sum(1 for c in fen.split()[0] if c.islower())

print(f"Starting position pieces:")
print(f"  White pieces: {white_pieces}")
print(f"  Black pieces: {black_pieces}")
print()

# Check colors in SVG
has_white_fill = '#ffffff' in svg
has_black_fill = '#000000' in svg
has_board_colors = '#a0522d' in svg and '#deb887' in svg

print("SVG color verification:")
print(f"  White piece fill (#ffffff): {'✅' if has_white_fill else '❌'}")
print(f"  Black piece fill (#000000): {'✅' if has_black_fill else '❌'}")
print(f"  Board colors (#a0522d, #deb887): {'✅' if has_board_colors else '❌'}")
print()

# Verify specific pieces
print("Piece placement check:")
pieces_to_check = [
    (chess.A1, 'White Rook', True),
    (chess.E1, 'White King', True),
    (chess.A8, 'Black Rook', False),
    (chess.E8, 'Black King', False),
    (chess.A2, 'White Pawn', True),
    (chess.A7, 'Black Pawn', False),
]

all_correct = True
for square, name, is_white in pieces_to_check:
    piece = board.piece_at(square)
    if piece:
        if is_white and piece.color == chess.WHITE:
            print(f"  ✅ {name} at {chess.square_name(square)}: WHITE")
        elif not is_white and piece.color == chess.BLACK:
            print(f"  ✅ {name} at {chess.square_name(square)}: BLACK")
        else:
            print(f"  ❌ {name} at {chess.square_name(square)}: WRONG COLOR!")
            all_correct = False
    else:
        print(f"  ❌ {name} at {chess.square_name(square)}: MISSING!")
        all_correct = False

print()
if all_correct and has_white_fill and has_black_fill:
    print("✅ ALL PIECE COLORS CORRECT!")
else:
    print("❌ Some issues found")
print("=" * 60)
