#!/usr/bin/env python3
import os
sf_path = "stockfish/stockfish-windows-x86-64.exe"
print("Checking:", sf_path)
print("Exists:", os.path.exists(sf_path))

if os.path.exists(sf_path):
    print("Starting Stockfish test...")
    import chess.engine
    import chess
    
    engine = chess.engine.SimpleEngine.popen_uci(sf_path)
    board = chess.Board()
    info = engine.analyse(board, chess.engine.Limit(depth=8))
    
    score = info.get('score')
    if score:
        cp = score.white().score(mate_score=10000)
        print(f"Stockfish evaluation: {cp} cp")
    
    engine.quit()
    print("SUCCESS!")
