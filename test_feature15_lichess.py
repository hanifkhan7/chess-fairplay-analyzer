#!/usr/bin/env python3
"""Test Feature 15 - Anti-Repertoire Builder with Lichess"""

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

# Test with Lichess player (lowercase username, no hyphens)
import builtins
builtins.input = InputMock([
    "thinkingknight",  # Lichess username (lowercase)
    "30",              # games to analyze
    "2",               # losses only
    "white",           # white pieces
    "n"                # don't open file
])

# Now test the feature
from chess_analyzer.menu import _opponent_weakness_repertoire

try:
    print("Running Feature 15 test with Lichess...\n")
    _opponent_weakness_repertoire()
    print("\n[SUCCESS] Feature 15 test completed")
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
