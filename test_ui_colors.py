#!/usr/bin/env python3
"""Test the new professional UI with colors and ASCII art"""

from chess_analyzer.menu import (
    print_header, print_menu_item, print_divider,
    print_success, print_warning, print_error, print_info, Colors
)

if __name__ == "__main__":
    print_header()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Testing Color Functions:{Colors.END}\n")
    
    print_success("This is a success message - Feature working correctly!")
    print_warning("This is a warning message - Please review this")
    print_error("This is an error message - Something went wrong")
    print_info("This is an info message - Important information")
    
    print()
    print_divider()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}Sample Menu Items:{Colors.END}\n")
    
    print_menu_item("1", "Analyze Player", "(Detect Suspicious Activity)")
    print_menu_item("2", "Play Against Opponent", "(Interactive Opening Training)")
    print_menu_item("3", "Exploit Your Opponent", "(Opening & Style Analysis)")
    print_menu_item("12", "Head-to-Head Matchup", "(Detailed Matchup Report)")
    print_menu_item("15", "Exit", "(Close Application)")
    
    print()
    print_divider()
    
    print(f"\n{Colors.BOLD}🎯 Professional UI Theme Applied!{Colors.END}")
    print(f"{Colors.GREEN}✓ ASCII Detective Character Integrated{Colors.END}")
    print(f"{Colors.GREEN}✓ Color-Coded Messages{Colors.END}")
    print(f"{Colors.GREEN}✓ Professional Menu Design{Colors.END}")
    print()
