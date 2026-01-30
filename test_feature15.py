#!/usr/bin/env python3
"""Test Feature 15 - Anti-Repertoire Builder with proper config"""

import sys
sys.path.insert(0, '.')
import os

# Mock input for testing
class InputMock:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0
    
    def __call__(self, prompt=""):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"{prompt}{response}")
            return response
        return ""

# Test with sample data
import builtins
builtins.input = InputMock([
    "41723R-HK",      # opponent username
    "20",             # games to analyze
    "2",              # losses only
    "white",          # white pieces
    "n"               # don't open file
])

# Check if Stockfish is configured
stockfish_path = None
try:
    config_file = 'config.yaml'
    if os.path.exists(config_file):
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            stockfish_path = config.get('stockfish_path')
        if stockfish_path:
            print(f"[INFO] Stockfish path from config: {stockfish_path}\n")
except:
    pass

if not stockfish_path:
    print("[WARN] Stockfish path not found in config, test may fail")
    print("[INFO] Please configure stockfish_path in config.yaml\n")

# Now test the feature
from chess_analyzer.menu import _opponent_weakness_repertoire

try:
    print("Running Feature 15 test...\n")
    _opponent_weakness_repertoire()
    print("\n[SUCCESS] Feature 15 test completed")
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
