#!/usr/bin/env python3
"""Test Feature 10 - Opening Repertoire Inspector"""

import sys
sys.path.insert(0, '.')

from chess_analyzer.menu import _opening_repertoire_inspector

# Simulate user inputs
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

# Mock input
import builtins
builtins.input = InputMock([
    "hikaru",      # username
    "yes",         # from lichess
    "y",           # generate D3
    "n"            # open browser
])

try:
    _opening_repertoire_inspector()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
