#!/usr/bin/env python3
"""Quick test to see if Stockfish can start"""

import sys
import os

print("[TEST] Stockfish Availability Check")
print("=" * 60)

try:
    # Check if stockfish executable exists
    sf_path = "stockfish/stockfish-windows-x86-64.exe"
    
    if os.path.exists(sf_path):
        print(f"[OK] Stockfish found at: {sf_path}")
        
        # Try to import and start it
        print("\n[TEST] Attempting to import chess.engine...")
        import chess.engine
        print("[OK] chess.engine imported")
        
        print("\n[TEST] Attempting to start Stockfish...")
        try:
            engine = chess.engine.SimpleEngine.popen_uci(sf_path)
            print("[OK] Stockfish started successfully!")
            
            # Try a quick analysis
            import chess
            board = chess.Board()
            
            print("\n[TEST] Running quick analysis on starting position...")
            info = engine.analyse(board, chess.engine.Limit(depth=10))
            
            if info:
                score = info.get('score')
                if score:
                    cp = score.white().score(mate_score=10000)
                    print(f"[OK] Analysis successful!")
                    print(f"     Starting position evaluation: {cp} centipawns")
            
            engine.quit()
            print("\n[SUCCESS] Stockfish is working!")
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze: {e}")
            sys.exit(1)
    else:
        print(f"[ERROR] Stockfish not found at: {sf_path}")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
