#!/usr/bin/env python
"""
Test the menu UI
"""
import sys
sys.path.insert(0, '.')

try:
    from chess_analyzer.menu import MenuUI
    print("✓ MenuUI imported successfully")
    
    menu = MenuUI()
    print("✓ MenuUI initialized successfully")
    
    menu.print_header()
    menu.print_menu()
    print("✓ Menu printed successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
