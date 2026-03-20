from chess_analyzer.exploit_report_generator import fen_to_svg

fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
svg = fen_to_svg(fen)

print("White piece color (#f0f0f0):", "#f0f0f0" in svg)
print("Black piece color (#333333):", "#333333" in svg)
print("Board light color (#deb887):", "#deb887" in svg)
print("Board dark color (#a0522d):", "#a0522d" in svg)

if "#f0f0f0" in svg and "#333333" in svg:
    print("\n✅ PIECE COLORS FIXED!")
else:
    print("\n❌ Issue detected")
