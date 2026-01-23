#!/usr/bin/env python3
"""Auto-run menu with Local Deep mode for testing"""

import subprocess
import sys

# Menu inputs:
# Player: hikaru
# Games: 5
# Platform: 3 (Both)
# Time control: 2 (Blitz)
# Mode: 3 (Local Deep)
# Depth: 3 (Very Deep - Depth 24)

menu_inputs = """hikaru
5
3
2
3
3
"""

print("=" * 70)
print("RUNNING MENU WITH LOCAL DEEP MODE (Depth 24)")
print("=" * 70)
print("\nInputs:")
print("  Player: hikaru")
print("  Games: 5")
print("  Platforms: Both")
print("  Time control: Blitz")
print("  Mode: Local Deep (Stockfish)")
print("  Depth: Very Deep (24)")
print("\n" + "=" * 70)
print()

# Run menu with piped input
proc = subprocess.Popen(
    [sys.executable, "run_menu.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

stdout, stderr = proc.communicate(input=menu_inputs)

print("STDOUT:")
print(stdout)
print("\n" + "=" * 70)
print("STDERR (Debug Output):")
print("=" * 70)
print(stderr)
print()
