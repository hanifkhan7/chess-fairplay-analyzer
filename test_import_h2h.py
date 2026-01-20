#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("[TEST] Attempting import...", flush=True)

try:
    from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer
    print("[OK] Import successful")
    
    analyzer = HeadToHeadAnalyzer()
    print("[OK] HeadToHeadAnalyzer instantiated")
    
    print("[DONE] Basic import and instantiation works!")
    sys.exit(0)
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
