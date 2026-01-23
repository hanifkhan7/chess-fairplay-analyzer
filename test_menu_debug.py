#!/usr/bin/env python3
"""Test menu with Local Deep mode and debug logging"""

import sys
import os

# Simulate menu input
inputs = ["1", "hikaru", "3", "3", "2", "3", "3"]
input_index = 0

def mock_input(prompt=""):
    global input_index
    if input_index < len(inputs):
        value = inputs[input_index]
        print(prompt + value)
        input_index += 1
        return value
    return ""

# Mock the built-in input
import builtins
builtins.input = mock_input

# Now run the menu
from chess_analyzer.menu import main
try:
    main()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
