"""
Menu-driven user interface for Chess Fairplay Analyzer
"""
import os
from pathlib import Path
from datetime import datetime
import json
import csv

from .fetcher import fetch_player_games
from .reporter import generate_report


def main():
    print("\n" + "="*60)
    print("   CHESS FAIRPLAY ANALYZER v2.0")
    print("   Modern Detection of Computer Assistance in Chess")
    print("="*60 + "\n")
    
    while True:
        print("\nMAIN MENU")
        print("="*50)
        print("1. Analyze Player (Detect Suspicious Activity)")
        print("2. Download All Games (Export Game History)")
        print("3. Interactive Game Viewer (Coming v2)")
        print("4. Strength Profile (Coming v2)")
        print("5. Accuracy Report (Coming v2)")
        print("6. View Reports")
        print("7. Settings")
        print("8. Exit")
        print("="*50 + "\n")
        
        choice = input("Select option (1-8): ").strip()
        
        if choice == "1":
            _analyze_player()
        elif choice == "2":
            _download_games()
        elif choice == "3":
            print("\n[v2.0] Interactive Game Viewer - Coming Soon")
        elif choice == "4":
            print("\n[v2.0] Strength Profile - Coming Soon")
        elif choice == "5":
            print("\n[v2.0] Accuracy Report - Coming Soon")
        elif choice == "6":
            _view_reports()
        elif choice == "7":
            _settings()
        elif choice == "8":
            print("\nGoodbye!\n")
            break
        else:
            print("\nInvalid option!")


def _analyze_player():
    print("\n" + "-"*50)
    print("ANALYZE PLAYER")
    print("-"*50)
    
    username = input("Enter Chess.com username: ").strip()
    if not username:
        return
    
    try:
        games = int(input("Games to analyze (default 50): ") or "50")
        
        print(f"Fetching {games} games for {username}...")
        player_games = fetch_player_games(username, max_games=games)
        print(f"Retrieved {len(player_games)} games")
        
        print("Analyzing with Stockfish...")
        from .analyzer import ChessAnalyzer
        from .utils.helpers import load_config
        
        config = load_config()
        analyzer = ChessAnalyzer(config)
        results = analyzer.analyze_games(player_games)
        
        print(f"\nSuspicion Score: {results.suspicion_score:.1f}/100")
        print(f"Engine Correlation: {results.engine_correlation:.1f}%")
        print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
        
        save = input("\nSave report? (y/n): ").strip().lower()
        if save == "y":
            fmt = input("Format (html/json/text): ").strip() or "html"
            from .reporter import generate_report
            generate_report(results, f"report_{username}", fmt)
            print("Report saved!")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _download_games():
    print("\n" + "-"*50)
    print("DOWNLOAD ALL GAMES")
    print("-"*50)
    print("Coming Soon")
    input("Press Enter to continue...")


def _view_reports():
    print("\n" + "-"*50)
    print("VIEW REPORTS")
    print("-"*50)
    reports_dir = Path("reports")
    if reports_dir.exists():
        reports = list(reports_dir.glob("*"))
        if reports:
            for i, r in enumerate(reports, 1):
                print(f"{i}. {r.name}")
        else:
            print("No reports found")
    else:
        print("Reports directory not found")
    input("Press Enter to continue...")


def _settings():
    print("\nSettings - Coming Soon")
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
