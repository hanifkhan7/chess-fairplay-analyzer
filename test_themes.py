#!/usr/bin/env python3
"""Test theme support in exploit report generator"""

from chess_analyzer.exploit_report_generator import fen_to_svg

# Test different themes
themes = ['chesscom', 'lichess', 'chessbase', 'blue', 'green']
test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

print("Testing fen_to_svg with different themes:")
for theme in themes:
    svg = fen_to_svg(test_fen, board_theme=theme)
    if 'Invalid' in svg:
        print(f"  ❌ {theme}: Failed")
    else:
        # Check if we have the specific colors in SVG
        has_light_color = theme in ['chesscom', 'lichess', 'chessbase', 'blue', 'green']
        print(f"  ✅ {theme}: Success (SVG generated with {len(svg)} chars)")

print("\nTheme colors used:")
themes_def = {
    'chesscom': {'light': '#eeeed2', 'dark': '#769656'},
    'lichess': {'light': '#f0d9b5', 'dark': '#b58863'},
    'chessbase': {'light': '#f0e6d2', 'dark': '#a67c52'},
    'blue': {'light': '#d4e3e8', 'dark': '#5a8ebc'},
    'green': {'light': '#e8f0d0', 'dark': '#6ba043'}
}

for theme, colors in themes_def.items():
    print(f"  {theme}: Light={colors['light']}, Dark={colors['dark']}")

# Verify theme colors are in generated SVG
print("\nVerifying theme colors in SVG:")
for theme, colors in themes_def.items():
    svg = fen_to_svg(test_fen, board_theme=theme)
    has_light = colors['light'] in svg
    has_dark = colors['dark'] in svg
    if has_light and has_dark:
        print(f"  ✅ {theme}: Colors correctly embedded")
    else:
        print(f"  ❌ {theme}: Colors missing - Light:{has_light}, Dark:{has_dark}")
