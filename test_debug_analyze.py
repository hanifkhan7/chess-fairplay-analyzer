#!/usr/bin/env python3

print("START")

import chess.pgn
from io import StringIO
import yaml

print("1. Imports OK")

pgn_text = """[Event "Test"]
[White "A"]
[Black "B"]

1. e4 c5 2. Nf3 d6
"""

pgn = chess.pgn.read_game(StringIO(pgn_text))
print(f"2. Game created: {pgn is not None}")

config = yaml.safe_load(open('config.yaml'))
print("3. Config loaded")

from chess_analyzer.analyzer_v3 import EnhancedPlayerAnalyzer
print("4. Analyzer imported")

analyzer = EnhancedPlayerAnalyzer(config)
print("5. Analyzer created")

print("6. Calling analyze_games_fast...")
try:
    results = analyzer.analyze_games_fast([pgn], "TestUser", max_workers=1)
    print("7. analyze_games_fast returned")
    print(f"   Results: {results}")
except Exception as e:
    print(f"7. ERROR in analyze_games_fast: {e}")
    import traceback
    traceback.print_exc()

print("END")
