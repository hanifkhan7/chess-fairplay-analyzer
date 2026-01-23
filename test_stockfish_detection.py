#!/usr/bin/env python3
"""Test if Stockfish is being detected and used"""

import os
import chess
import chess.engine
from pathlib import Path

print("=" * 60)
print("STOCKFISH DETECTION TEST")
print("=" * 60)

# Check if Stockfish exists
sf_paths = [
    "stockfish/stockfish-windows-x86-64.exe",
    "stockfish\\stockfish-windows-x86-64.exe",
]

print("\n[CHECK] Looking for Stockfish...")
sf_path = None
for path in sf_paths:
    print(f"  Checking: {path}")
    if os.path.exists(path):
        sf_path = path
        print(f"  ✓ Found!")
        break
    else:
        print(f"  ✗ Not found")

if not sf_path:
    print("\n[ERROR] Stockfish not found!")
    print("Paths checked:")
    for path in sf_paths:
        full_path = os.path.abspath(path)
        print(f"  - {full_path}")
        exists = os.path.exists(full_path)
        print(f"    Exists: {exists}")
    exit(1)

print(f"\n[FOUND] Stockfish at: {sf_path}")
print(f"[ABSOLUTE] Full path: {os.path.abspath(sf_path)}")

# Try to initialize engine
print("\n[ENGINE] Initializing chess.engine.SimpleEngine...")
try:
    engine = chess.engine.SimpleEngine.popen_uci(sf_path)
    print("✓ Engine started successfully")
    
    # Test analysis
    print("\n[TEST] Running test analysis at Depth 24...")
    board = chess.Board()
    
    # Make a few opening moves
    board.push_san("e4")
    board.push_san("c5")
    board.push_san("Nf3")
    
    print("  Position: Sicilian Defense")
    print(f"  Board: {board.fen()}")
    
    # Analyze with Depth 24
    limits = chess.engine.Limit(depth=24, time=2.0)
    print(f"  Limits: Depth 24, Time 2.0s")
    
    info = engine.analyse(board, limits)
    print(f"\n✓ Analysis completed")
    print(f"  Info keys: {list(info.keys())}")
    if 'score' in info:
        score = info['score']
        cp = score.white().score(mate_score=10000)
        print(f"  Score: {cp} centipawns")
        print(f"  Depth reached: {info.get('depth', 'unknown')}")
    
    engine.quit()
    print("\n[SUCCESS] Stockfish is working correctly!")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
