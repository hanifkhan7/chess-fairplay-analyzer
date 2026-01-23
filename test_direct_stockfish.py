#!/usr/bin/env python3
"""Direct test of _get_local_evaluations method"""

import chess
import chess.pgn
import io
import os

print("=" * 70)
print("DIRECT STOCKFISH INTEGRATION TEST")
print("=" * 70)

# Create a simple game
pgn_text = """
[Event "Test"]
[White "Test1"]
[Black "Test2"]
[Result "1-0"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6
"""

pgn_io = io.StringIO(pgn_text)
game = chess.pgn.read_game(pgn_io)

if not game:
    print("Error: Could not parse game")
    exit(1)

print("✓ Parsed test game")
print(f"  White: {game.headers.get('White')}")
print(f"  Black: {game.headers.get('Black')}")

# Extract moves
board = chess.Board()
moves = []
for move in game.mainline_moves():
    moves.append(move)

print(f"  Moves: {len(moves)}")
print(f"  First 5 moves: {[m.uci() for m in moves[:5]]}")

# Now test Stockfish directly
print("\n[STOCKFISH] Testing direct Stockfish integration...")

sf_paths = [
    "stockfish/stockfish-windows-x86-64.exe",
    "stockfish\\stockfish-windows-x86-64.exe",
]

sf_path = None
for path in sf_paths:
    if os.path.exists(path):
        sf_path = path
        break

if not sf_path:
    print(f"✗ Stockfish not found at:")
    for path in sf_paths:
        print(f"    {os.path.abspath(path)}")
    exit(1)

print(f"✓ Found Stockfish: {sf_path}")

# Test the actual _get_local_evaluations logic
evaluations = []

try:
    engine = None
    try:
        print("\n[ENGINE] Starting chess.engine.SimpleEngine...")
        engine = chess.engine.SimpleEngine.popen_uci(sf_path)
        print("✓ Engine started")
        
        board = chess.Board()
        depth = 16  # Start with standard depth
        
        time_limits = {
            16: 0.5,
            20: 1.0,
            24: 2.0,
            28: 4.0
        }
        time_per_move = time_limits.get(depth, 0.5)
        
        print(f"\n[ANALYZE] Analyzing with Depth {depth}, {time_per_move}s per move...")
        print(f"  Analyzing {len(moves[:10])} positions (limited to 10)...")
        
        for i, move in enumerate(moves[:10]):
            try:
                limits = chess.engine.Limit(depth=depth, time=time_per_move)
                info = engine.analyse(board, limits)
                
                if info and 'score' in info:
                    score = info['score']
                    cp = score.white().score(mate_score=10000)
                    
                    evaluations.append({
                        "centipawns": cp if cp is not None else 0,
                        "mate": None,
                        "stockfish": True
                    })
                    print(f"  Move {i+1}: {move.uci()} → {cp} cp ✓")
                else:
                    print(f"  Move {i+1}: {move.uci()} → No score")
                    evaluations.append({
                        "centipawns": 0,
                        "mate": None,
                        "stockfish": True
                    })
                
            except Exception as move_error:
                print(f"  Move {i+1}: {move.uci()} → Error: {move_error}")
                break
            
            board.push(move)
        
        print(f"\n✓ Got {len(evaluations)} evaluations")
        
    finally:
        if engine:
            try:
                engine.quit()
                print("✓ Engine closed")
            except:
                pass

except ImportError as e:
    print(f"✗ chess.engine not available: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
if evaluations:
    print("✓ SUCCESS: Stockfish returned evaluations")
else:
    print("✗ FAILURE: No evaluations returned")
