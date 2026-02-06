#!/usr/bin/env python3
"""Quick test of Feature 18 integration"""

print("[TEST] Checking Feature 18 imports...")

try:
    from chess_analyzer.interactive_simulator import InteractiveSimulator, OpponentMoveDatabase
    print("✓ Interactive Simulator imported")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    from chess_analyzer.menu import _interactive_opponent_simulator
    print("✓ Feature 18 function imported from menu")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

try:
    import chess
    print("✓ python-chess available")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

print("\n[SUCCESS] All Feature 18 dependencies verified!")
print("[READY] Feature 18 is ready for integration")
