#!/usr/bin/env python3
"""Minimal test of _analyze_single_game"""
import sys
import os

print("[START]", flush=True)

import chess
import chess.pgn
from io import StringIO

print("[IMPORTS]", flush=True)

os.chdir('c:\\Users\\zaibi\\chess-fairplay-analyzer')

print("[CHDIR]", flush=True)

from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
from chess_analyzer.utils.helpers import load_config

print("[LOADED ANALYZER]", flush=True)

# Create a simple game
pgn_text = """[Event "Casual Rapid game"]
[Site "https://lichess.org/aJk9Zj0O"]
[Date "2024.01.01"]
[Round "-"]
[White "hikaru"]
[Black "enemy"]
[Result "1-0"]
[UTCDate "2024.01.01"]
[UTCTime "12:00:00"]
[WhiteElo "2800"]
[BlackElo "1800"]
[TimeControl "600+0"]

1. e4 e5 2. Nf3 Nc6 1-0"""

print("[GAME TEXT READY]", flush=True)

pgn = chess.pgn.read_game(StringIO(pgn_text))
print(f"[GAME PARSED]: {pgn}", flush=True)

config = load_config()
print(f"[CONFIG LOADED]", flush=True)

analyzer = EnhancedPlayerAnalyzer(config, use_lichess=False)
print(f"[ANALYZER CREATED]", flush=True)

print("[TEST] Analyzing single game...", flush=True)
try:
    result = analyzer._analyze_single_game(pgn, "hikaru")
    print(f"[TEST] Success! Result: {result}", flush=True)
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("[END]", flush=True)
