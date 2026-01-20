#!/usr/bin/env python3
"""Test the fixed platform detection and fetching"""

import sys
import os
sys.path.insert(0, '.')

# Suppress logging
os.environ['PYTHONWARNINGS'] = 'ignore'

print("Starting test...")

try:
    from chess_analyzer.dual_fetcher import detect_player_platforms
    print("Import successful")
    
    print("\nTesting Quantum-Chesss detection:")
    platforms = detect_player_platforms('Quantum-Chesss')
    print(f"Results: {platforms}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
