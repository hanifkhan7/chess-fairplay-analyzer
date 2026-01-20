"""
Menu-driven user interface for Chess Fairplay Analyzer
"""
import os
from pathlib import Path
from datetime import datetime
import json
import csv
import zipfile
import io

from .fetcher import fetch_player_games
from .reporter import generate_report


def main():
    """Entry point for menu UI"""
    
    print("\n" + "="*60)
    print("   CHESS DETECTIVE v2.2.1")
    print("   Forensic Analysis of Player Behavior")
    print("="*60 + "\n")
    
    while True:
        print("\nMAIN MENU")
        print("="*50)
        print("1. Analyze Player (Detect Suspicious Activity)")
        print("2. Download All Games (Export Game History)")
        print("3. Exploit your opponent (Opening & Style Analysis)")
        print("4. Strength Profile (Skill Level Analysis)")
        print("5. Accuracy Report (Move Accuracy & Consistency)")
        print("6. Account Metrics Dashboard (Quick View)")
        print("7. Multi-Player Comparison")
        print("8. Fatigue Detection")
        print("9. Network Analysis")
        print("10. Opening Repertoire Inspector (NEW!)")
        print("11. View Reports")
        print("12. Settings")
        print("13. Exit")
        print("="*50 + "\n")
        
        choice = input("Select option (1-13): ").strip()
        
        if choice == "1":
            _analyze_player()
        elif choice == "2":
            _download_games()
        elif choice == "3":
            _player_brain()
        elif choice == "4":
            _strength_profile()
        elif choice == "5":
            _accuracy_report()
        elif choice == "6":
            _account_metrics_dashboard()
        elif choice == "7":
            _multi_player_comparison()
        elif choice == "8":
            _fatigue_detection()
        elif choice == "9":
            _network_analysis()
        elif choice == "10":
            _opening_repertoire_inspector()
        elif choice == "11":
            _view_reports()
        elif choice == "12":
            _settings()
        elif choice == "13":
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
        
        # Ask for analysis speed
        print("\nAnalysis Speed:")
        print("1. Fast (depth 12, ~40s per game)")
        print("2. Standard (depth 14, ~60s per game)")
        print("3. Thorough (depth 16, ~90s per game)")
        speed = input("Choose (1-3, default 2): ").strip() or "2"
        
        depth_map = {"1": 12, "2": 14, "3": 16}
        custom_depth = depth_map.get(speed, 14)
        
        print(f"\nFetching up to {games} games for {username}...")
        player_games = fetch_player_games(username, max_games=games)
        actual_count = len(player_games)
        status = "✓" if actual_count > 0 else "❌"
        msg = f"{status} Retrieved {actual_count} games"
        if actual_count < games:
            msg += f" (player has fewer than {games} total)"
        print(msg)
        
        from .analyzer import ChessAnalyzer
        from .utils.helpers import load_config
        
        config = load_config()
        analyzer = ChessAnalyzer(config)
        
        use_lichess = config.get('analysis', {}).get('use_lichess', False)
        depth = config.get('analysis', {}).get('engine_depth', 14)
        
        if use_lichess:
            engine_name = "Lichess API (cloud analysis)"
            time_estimate = "30-90 seconds per game"
        else:
            engine_name = f"Stockfish (depth={depth})"
            time_estimate = "1-5 minutes per game"
        
        print(f"\nAnalyzing with {engine_name}...")
        print(f"Estimated time: {time_estimate}...\n")
        results = analyzer.analyze_games(player_games)
        
        print(f"\n" + "="*50)
        print(f"ANALYSIS RESULTS for {username}")
        print("="*50)
        print(f"Games Analyzed: {results.games_analyzed}/{len(player_games)}")
        print(f"Suspicion Score: {results.suspicion_score:.1f}/100")
        print(f"Engine Correlation: {results.avg_engine_correlation:.1f}%")
        print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
        print(f"Suspicious Games: {results.suspicious_game_count}")
        print("="*50)
        
        save = input("\nSave report? (y/n): ").strip().lower()
        if save == "y":
            fmt = input("Format (html/json/text): ").strip() or "html"
            from .reporter import generate_report
            
            # Convert PlayerAnalysis dataclass to dictionary for reporter
            from dataclasses import asdict
            analysis_dict = asdict(results)
            
            generate_report(analysis_dict, f"report_{username}", fmt)
            print("Report saved!")
        
        # Offer to export suspicious games
        if results.suspicious_game_count > 0:
            export = input(f"\nExport {results.suspicious_game_count} suspicious games? (y/n): ").strip().lower()
            if export == "y":
                _export_suspicious_games(results, username, player_games)
    
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _download_games():
    print("\n" + "-"*50)
    print("DOWNLOAD ALL GAMES")
    print("-"*50)
    
    username = input("\nEnter Chess.com username: ").strip()
    if not username:
        return
    
    try:
        # Ask which games to download
        print("\nDownload Range:")
        print("1. Most recent games (newest first)")
        print("2. All games (from first ever played)")
        range_choice = input("Choose (1-2, default 1): ").strip() or "1"
        
        # Ask how many games
        print("\nNumber of Games:")
        print("1. All games")
        print("2. Specific amount")
        count_choice = input("Choose (1-2, default 1): ").strip() or "1"
        
        max_games = 0  # 0 means all
        if count_choice == "2":
            try:
                max_games = int(input("How many games? ").strip())
            except ValueError:
                print("Invalid number, using default (all games)")
                max_games = 0
        
        # Ask for export format
        print("\nExport Format:")
        print("1. Single PGN file")
        print("2. CSV file (metadata only)")
        print("3. JSON file (full data)")
        print("4. ZIP archive (PGN + JSON)")
        fmt_choice = input("Choose (1-4, default 1): ").strip() or "1"
        
        print(f"\nFetching up to {max_games} games for {username}...")
        games = fetch_player_games(username, max_games=max_games)
        actual_count = len(games)
        msg = f"✓ Retrieved {actual_count} games"
        if actual_count < max_games:
            msg += f" (player has fewer than {max_games} total)"
        print(msg)
        print(f"✓ Retrieved {len(games)} games")
        
        if not games:
            print("No games found")
            input("Press Enter to continue...")
            return
        
        # Determine sort order
        if range_choice == "2":
            # Oldest first (from first ever played)
            games.reverse()
        # else: most recent (default order from API)
        
        # Export
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if fmt_choice == "1":
            # PGN file
            filename = export_dir / f"{username}_games_{timestamp}.pgn"
            with open(filename, "w") as f:
                for i, game in enumerate(games):
                    if i > 0:
                        f.write("\n\n")
                    f.write(str(game))
            print(f"\n✓ Exported {len(games)} games to {filename.name}")
        
        elif fmt_choice == "2":
            # CSV file
            filename = export_dir / f"{username}_games_{timestamp}.csv"
            with open(filename, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "White", "Black", "Result", "Time Control", "Moves", "URL"])
                for game in games:
                    white = game.headers.get("White", "?")
                    black = game.headers.get("Black", "?")
                    result = game.headers.get("Result", "*")
                    time_control = game.headers.get("TimeControl", "?")
                    moves = len(list(game.mainline_moves()))
                    date = game.headers.get("Date", "?")
                    url = game.headers.get("Link", "")
                    writer.writerow([date, white, black, result, time_control, moves, url])
            print(f"\n✓ Exported {len(games)} games to {filename.name}")
        
        elif fmt_choice == "3":
            # JSON file
            filename = export_dir / f"{username}_games_{timestamp}.json"
            games_data = []
            for game in games:
                games_data.append({
                    "white": game.headers.get("White", "?"),
                    "black": game.headers.get("Black", "?"),
                    "result": game.headers.get("Result", "*"),
                    "date": game.headers.get("Date", "?"),
                    "time_control": game.headers.get("TimeControl", "?"),
                    "moves": len(list(game.mainline_moves())),
                    "url": game.headers.get("Link", ""),
                    "eco": game.headers.get("ECO", ""),
                })
            with open(filename, "w") as f:
                json.dump(games_data, f, indent=2)
            print(f"\n✓ Exported {len(games)} games to {filename.name}")
        
        elif fmt_choice == "4":
            # ZIP archive
            zip_filename = export_dir / f"{username}_games_{timestamp}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add PGN file
                pgn_data = ""
                for i, game in enumerate(games):
                    if i > 0:
                        pgn_data += "\n\n"
                    pgn_data += str(game)
                zf.writestr(f"{username}_games.pgn", pgn_data)
                
                # Add JSON summary
                games_data = []
                for game in games:
                    games_data.append({
                        "white": game.headers.get("White", "?"),
                        "black": game.headers.get("Black", "?"),
                        "result": game.headers.get("Result", "*"),
                        "date": game.headers.get("Date", "?"),
                        "time_control": game.headers.get("TimeControl", "?"),
                        "moves": len(list(game.mainline_moves())),
                    })
                summary = {
                    "username": username,
                    "total_games": len(games),
                    "download_date": timestamp,
                    "games": games_data
                }
                zf.writestr(f"{username}_data.json", json.dumps(summary, indent=2))
            
            print(f"\n✓ Exported to {zip_filename.name}")
            print(f"  Contents: PGN file + JSON data")
        
        else:
            print("Invalid choice.")
    
    except KeyboardInterrupt:
        print("\n\nDownload cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _player_brain():
    """Analyze player profile: openings, strengths, playing style - EXPLOIT YOUR OPPONENT."""
    
    username = input("\n\n🎯 EXPLOIT YOUR OPPONENT\n" + "-"*50 + "\nEnter Chess.com username: ").strip()
    if not username:
        return
    
    try:
        games_count = int(input("Games to analyze (default 50): ") or "50")
        
        print(f"\nFetching up to {games_count} games for {username}...")
        games = fetch_player_games(username, max_games=games_count)
        actual_count = len(games)
        msg = f"✓ Retrieved {actual_count} games"
        if actual_count < games_count:
            msg += f" (player has fewer than {games_count} total)"
        print(msg + "\n")
        
        if not games:
            print("No games found")
            input("Press Enter to continue...")
            return
        
        # Use enhanced exploit analyzer
        from .exploit import display_exploit_analysis
        display_exploit_analysis(games, username)
        
        
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")



def _strength_profile():
    """Analyze player's skill level and strength metrics."""
    print("\n" + "-"*50)
    print("STRENGTH PROFILE - SKILL LEVEL ANALYSIS")
    print("-"*50)
    
    username = input("\nEnter Chess.com username: ").strip()
    if not username:
        return
    
    try:
        games_count = int(input("Games to analyze (default 50): ") or "50")
        
        print(f"\nFetching up to {games_count} games for {username}...")
        games = fetch_player_games(username, max_games=games_count)
        actual_count = len(games)
        msg = f"✓ Retrieved {actual_count} games"
        if actual_count < games_count:
            msg += f" (player has fewer than {games_count} total)"
        print(msg + "\n")
        
        if not games:
            print("No games found")
            input("Press Enter to continue...")
            return
        
        # Collect strength metrics
        time_controls = {}
        avg_ratings_vs = {"white_opponents": [], "black_opponents": []}
        performance_by_rating = {}
        accuracy_metrics = []
        
        for game in games:
            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")
            time_control = game.headers.get("TimeControl", "unknown")
            result = game.headers.get("Result", "*")
            white_elo = game.headers.get("WhiteElo", "?")
            black_elo = game.headers.get("BlackElo", "?")
            move_count = len(list(game.mainline_moves()))
            
            # Determine player perspective
            is_player_white = white.lower() == username.lower()
            player_elo = int(white_elo) if is_player_white and white_elo != "?" else (int(black_elo) if black_elo != "?" else None)
            opponent_elo = int(black_elo) if is_player_white and black_elo != "?" else (int(white_elo) if white_elo != "?" else None)
            
            # Time control stats
            if time_control not in time_controls:
                time_controls[time_control] = {"wins": 0, "losses": 0, "draws": 0, "count": 0}
            
            time_controls[time_control]["count"] += 1
            if result == "1-0" and is_player_white:
                time_controls[time_control]["wins"] += 1
            elif result == "0-1" and not is_player_white:
                time_controls[time_control]["wins"] += 1
            elif result == "*":
                pass
            else:
                if (result == "0-1" and is_player_white) or (result == "1-0" and not is_player_white):
                    time_controls[time_control]["losses"] += 1
                else:
                    time_controls[time_control]["draws"] += 1
            
            # Rating stats
            if opponent_elo:
                if is_player_white:
                    avg_ratings_vs["white_opponents"].append(opponent_elo)
                else:
                    avg_ratings_vs["black_opponents"].append(opponent_elo)
                
                # Determine outcome
                if result == "1-0":
                    outcome = "win" if is_player_white else "loss"
                elif result == "0-1":
                    outcome = "loss" if is_player_white else "win"
                else:
                    outcome = "draw"
                
                # Performance by rating difference
                rating_bracket = f"{(opponent_elo // 100) * 100}-{(opponent_elo // 100) * 100 + 99}"
                if rating_bracket not in performance_by_rating:
                    performance_by_rating[rating_bracket] = {"wins": 0, "losses": 0, "draws": 0, "count": 0}
                
                performance_by_rating[rating_bracket]["count"] += 1
                if outcome == "win":
                    performance_by_rating[rating_bracket]["wins"] += 1
                elif outcome == "loss":
                    performance_by_rating[rating_bracket]["losses"] += 1
                else:
                    performance_by_rating[rating_bracket]["draws"] += 1
            
            # Game length metric (longer games = better decision making usually)
            accuracy_metrics.append(move_count)
        
        # Calculate statistics
        total_games = len(games)
        avg_game_length = sum(accuracy_metrics) / len(accuracy_metrics) if accuracy_metrics else 0
        
        avg_white_rating = sum(avg_ratings_vs["white_opponents"]) / len(avg_ratings_vs["white_opponents"]) if avg_ratings_vs["white_opponents"] else 0
        avg_black_rating = sum(avg_ratings_vs["black_opponents"]) / len(avg_ratings_vs["black_opponents"]) if avg_ratings_vs["black_opponents"] else 0
        
        # Display results
        print("\n" + "="*70)
        print(f"STRENGTH PROFILE for {username.upper()}")
        print("="*70)
        
        # Overall performance
        print(f"\n📈 OVERALL SKILL METRICS")
        print("-" * 70)
        print(f"  Total Games Analyzed: {total_games}")
        print(f"  Average Game Length: {avg_game_length:.1f} moves")
        if avg_white_rating > 0:
            print(f"  Avg Opponent Strength (as White): {avg_white_rating:.0f}")
        if avg_black_rating > 0:
            print(f"  Avg Opponent Strength (as Black): {avg_black_rating:.0f}")
        if avg_white_rating > 0 and avg_black_rating > 0:
            combined_avg = (avg_white_rating + avg_black_rating) / 2
            print(f"  Combined Average Opponent: {combined_avg:.0f}")
        
        # Performance by time control
        print(f"\n⏱️  PERFORMANCE BY TIME CONTROL")
        print("-" * 70)
        for tc in sorted(time_controls.keys()):
            stats = time_controls[tc]
            total = stats["count"]
            win_rate = (stats["wins"] / total * 100) if total > 0 else 0
            print(f"  {tc}:")
            print(f"    Games: {total} | W-L-D: {stats['wins']}-{stats['losses']}-{stats['draws']} | Win Rate: {win_rate:.1f}%")
        
        # Strength assessment
        print(f"\n💪 SKILL ASSESSMENT")
        print("-" * 70)
        
        # By time control strength
        best_tc = max(time_controls.items(), key=lambda x: (x[1]["wins"] / x[1]["count"] * 100 if x[1]["count"] > 0 else 0))
        worst_tc = min(time_controls.items(), key=lambda x: (x[1]["wins"] / x[1]["count"] * 100 if x[1]["count"] > 0 else 0))
        
        best_wr = (best_tc[1]["wins"] / best_tc[1]["count"] * 100) if best_tc[1]["count"] > 0 else 0
        worst_wr = (worst_tc[1]["wins"] / worst_tc[1]["count"] * 100) if worst_tc[1]["count"] > 0 else 0
        
        print(f"  ✓ Strongest in: {best_tc[0]} ({best_wr:.1f}% win rate)")
        print(f"  ! Weakest in: {worst_tc[0]} ({worst_wr:.1f}% win rate)")
        
        # Game length assessment
        if avg_game_length > 40:
            print(f"  ✓ Patient player (avg {avg_game_length:.0f} moves) - good endgame technique")
        elif avg_game_length > 25:
            print(f"  ✓ Balanced player (avg {avg_game_length:.0f} moves)")
        else:
            print(f"  ! Quick finishes (avg {avg_game_length:.0f} moves) - tactical rather than positional")
        
        # Opponent strength
        if avg_white_rating > 0 and avg_black_rating > 0:
            combined_avg = (avg_white_rating + avg_black_rating) / 2
            if combined_avg > 1800:
                print(f"  💎 Plays strong opposition (avg {combined_avg:.0f}) - high level")
            elif combined_avg > 1500:
                print(f"  ✓ Plays intermediate opponents (avg {combined_avg:.0f})")
            else:
                print(f"  📚 Plays varied opposition (avg {combined_avg:.0f})")
        
        # Performance consistency
        if len(time_controls) > 1:
            win_rates = []
            for tc_stats in time_controls.values():
                if tc_stats["count"] > 0:
                    wr = (tc_stats["wins"] / tc_stats["count"] * 100)
                    win_rates.append(wr)
            
            if win_rates:
                avg_wr = sum(win_rates) / len(win_rates)
                variance = sum((wr - avg_wr) ** 2 for wr in win_rates) / len(win_rates)
                std_dev = variance ** 0.5
                
                if std_dev < 10:
                    print(f"  ✓ Consistent across formats (std dev: {std_dev:.1f}%)")
                elif std_dev < 20:
                    print(f"  ~ Variable performance (std dev: {std_dev:.1f}%)")
                else:
                    print(f"  ! Inconsistent across formats (std dev: {std_dev:.1f}%)")
        
        # Overall rating level
        if avg_white_rating > 0:
            if avg_white_rating > 2200:
                level = "Super-GM Level (2200+)"
            elif avg_white_rating > 2000:
                level = "Grandmaster Level (2000-2200)"
            elif avg_white_rating > 1800:
                level = "International Master Level (1800-2000)"
            elif avg_white_rating > 1600:
                level = "Master Level (1600-1800)"
            elif avg_white_rating > 1400:
                level = "Expert Level (1400-1600)"
            elif avg_white_rating > 1200:
                level = "Intermediate (1200-1400)"
            else:
                level = "Beginner/Club Level (<1200)"
            
            print(f"\n  🎯 Estimated Level: {level}")
        
        print("\n" + "="*70)
        
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _accuracy_report():
    """Analyze player's move accuracy and consistency."""
    print("\n" + "-"*50)
    print("ACCURACY REPORT - MOVE ACCURACY & CONSISTENCY")
    print("-"*50)
    
    username = input("\nEnter Chess.com username: ").strip()
    if not username:
        return
    
    try:
        games_count = int(input("Games to analyze (default 30): ") or "30")
        
        print(f"\nFetching up to {games_count} games for {username}...")
        games = fetch_player_games(username, max_games=games_count)
        actual_count = len(games)
        msg = f"✓ Retrieved {actual_count} games"
        if actual_count < games_count:
            msg += f" (player has fewer than {games_count} total)"
        print(msg)
        print("Running accuracy analysis...")
        
        if not games:
            print("No games found")
            input("Press Enter to continue...")
            return
        
        # Import ChessAnalyzer for analysis
        from .analyzer import ChessAnalyzer
        from .utils.helpers import load_config
        
        config = load_config()
        analyzer = ChessAnalyzer(config)
        
        # Analyze all games at once
        results = analyzer.analyze_games(games)
        
        if not results or not results.game_analyses:
            print("Could not analyze games. Please try again.")
            input("Press Enter to continue...")
            return
        
        # Collect accuracy data from analysis results
        accuracy_by_phase = {"opening": [], "middlegame": [], "endgame": []}
        accuracy_by_result = {"win": [], "loss": [], "draw": []}
        accuracy_by_opponent = {}
        blunder_count = 0
        inaccuracy_count = 0
        game_accuracies = []
        accuracy_trends = []
        
        for game_analysis in results.game_analyses:
            if not game_analysis:
                continue
            
            game = game_analysis.game
            white = game.headers.get("White", "").lower()
            black = game.headers.get("Black", "").lower()
            result = game.headers.get("Result", "*")
            opponent_elo = game.headers.get("BlackElo" if white == username.lower() else "WhiteElo", "?")
            move_count = len(list(game.mainline_moves()))
            
            # Get accuracy from analysis
            accuracy = game_analysis.accuracy_score
            if accuracy > 0:
                game_accuracies.append(accuracy)
                accuracy_trends.append(accuracy)
                
                # Determine result outcome
                is_player_white = white == username.lower()
                if result == "1-0":
                    outcome = "win" if is_player_white else "loss"
                elif result == "0-1":
                    outcome = "loss" if is_player_white else "win"
                else:
                    outcome = "draw"
                
                accuracy_by_result[outcome].append(accuracy)
                
                # Phase accuracy
                if move_count <= 20:
                    phase = "opening"
                elif move_count <= 40:
                    phase = "middlegame"
                else:
                    phase = "endgame"
                
                accuracy_by_phase[phase].append(accuracy)
                
                # Opponent strength accuracy
                if opponent_elo != "?":
                    try:
                        elo_int = int(opponent_elo)
                        elo_bracket = f"{(elo_int // 100) * 100}-{(elo_int // 100) * 100 + 99}"
                        if elo_bracket not in accuracy_by_opponent:
                            accuracy_by_opponent[elo_bracket] = []
                        accuracy_by_opponent[elo_bracket].append(accuracy)
                    except:
                        pass
                
                # Count blunders and inaccuracies
                # (represented by low accuracy scores)
                if accuracy < 40:
                    blunder_count += 1
                elif accuracy < 65:
                    inaccuracy_count += 1
        
        if not game_accuracies:
            print("Could not extract accuracy data from games.")
            input("Press Enter to continue...")
            return
        
        # Calculate statistics
        overall_accuracy = sum(game_accuracies) / len(game_accuracies)
        best_game_accuracy = max(game_accuracies)
        worst_game_accuracy = min(game_accuracies)
        
        # Calculate phase accuracies
        phase_stats = {}
        for phase, accuracies in accuracy_by_phase.items():
            if accuracies:
                avg_acc = sum(accuracies) / len(accuracies)
                phase_stats[phase] = avg_acc
        
        # Calculate result-based accuracies
        result_stats = {}
        for result, accuracies in accuracy_by_result.items():
            if accuracies:
                avg_acc = sum(accuracies) / len(accuracies)
                result_stats[result] = avg_acc
        
        # Consistency (standard deviation)
        avg_acc = sum(game_accuracies) / len(game_accuracies)
        variance = sum((acc - avg_acc) ** 2 for acc in game_accuracies) / len(game_accuracies)
        consistency = variance ** 0.5  # Lower is more consistent
        
        # Display results
        print("\n" + "="*70)
        print(f"ACCURACY REPORT for {username.upper()}")
        print("="*70)
        
        print(f"\n🎯 OVERALL ACCURACY ({len(game_accuracies)} games analyzed)")
        print("-" * 70)
        print(f"  Average Accuracy: {overall_accuracy:.1f}%")
        print(f"  Best Game: {best_game_accuracy:.1f}%")
        print(f"  Worst Game: {worst_game_accuracy:.1f}%")
        print(f"  Consistency: {100 - consistency:.1f}% (lower variance = more consistent)")
        
        # Accuracy rating
        if overall_accuracy >= 80:
            rating = "🌟 Excellent - Few mistakes, strong play"
        elif overall_accuracy >= 70:
            rating = "✓ Very Good - Solid play with occasional errors"
        elif overall_accuracy >= 60:
            rating = "~ Good - Reasonable play with some inaccuracies"
        elif overall_accuracy >= 50:
            rating = "! Fair - Notable mistakes and blunders"
        else:
            rating = "✗ Poor - Frequent errors and tactical oversights"
        print(f"  Rating: {rating}")
        
        print(f"\n📊 ACCURACY BY GAME PHASE")
        print("-" * 70)
        if phase_stats:
            for phase in ["opening", "middlegame", "endgame"]:
                if phase in phase_stats:
                    acc = phase_stats[phase]
                    count = len(accuracy_by_phase[phase])
                    print(f"  {phase.upper()}: {acc:.1f}% ({count} games)")
            
            # Find strongest phase
            strongest_phase = max(phase_stats.items(), key=lambda x: x[1])
            weakest_phase = min(phase_stats.items(), key=lambda x: x[1])
            print(f"  💪 Strongest: {strongest_phase[0].upper()} ({strongest_phase[1]:.1f}%)")
            print(f"  📉 Weakest: {weakest_phase[0].upper()} ({weakest_phase[1]:.1f}%)")
        
        print(f"\n📈 ACCURACY BY GAME RESULT")
        print("-" * 70)
        if result_stats:
            for result in ["win", "loss", "draw"]:
                if result in result_stats:
                    acc = result_stats[result]
                    count = len(accuracy_by_result[result])
                    if count > 0:
                        print(f"  {result.upper()}S: {acc:.1f}% ({count} games)")
            
            # Performance pattern
            if "win" in result_stats and "loss" in result_stats and result_stats["win"] > 0 and result_stats["loss"] > 0:
                diff = result_stats["win"] - result_stats["loss"]
                if diff > 5:
                    print(f"  ✓ More accurate in wins (better decision making in winning positions)")
                elif diff < -5:
                    print(f"  ⚠ More accurate in losses (better defense, but still lost)")
                else:
                    print(f"  ~ Consistent accuracy across results")
        
        print(f"\n⚠️  ERROR ANALYSIS")
        print("-" * 70)
        print(f"  Blunders (accuracy <40%): {blunder_count}")
        print(f"  Inaccuracies (accuracy 40-65%): {inaccuracy_count}")
        print(f"  Games with errors: {blunder_count + inaccuracy_count}/{len(game_accuracies)}")
        
        if len(game_accuracies) > 0:
            error_rate = ((blunder_count + inaccuracy_count) / len(game_accuracies) * 100)
            print(f"  Error Rate: {error_rate:.1f}%")
        
        print(f"\n🔍 ACCURACY VS OPPONENT STRENGTH")
        print("-" * 70)
        if accuracy_by_opponent:
            for elo_bracket in sorted(accuracy_by_opponent.keys()):
                accuracies = accuracy_by_opponent[elo_bracket]
                avg_acc = sum(accuracies) / len(accuracies)
                print(f"  vs {elo_bracket}: {avg_acc:.1f}% ({len(accuracies)} games)")
        else:
            print("  (Insufficient opponent rating data)")
        
        print(f"\n💡 ACCURACY INSIGHTS")
        print("-" * 70)
        
        # Consistency insight
        if consistency < 10:
            print(f"  ✓ Very consistent player (low variance)")
        elif consistency < 15:
            print(f"  ✓ Generally consistent with minor fluctuations")
        elif consistency < 25:
            print(f"  ~ Variable performance (highs and lows)")
        else:
            print(f"  ! Highly inconsistent (significant performance swings)")
        
        # Trend analysis
        if len(accuracy_trends) >= 5:
            first_half = sum(accuracy_trends[:len(accuracy_trends)//2]) / (len(accuracy_trends)//2)
            second_half = sum(accuracy_trends[len(accuracy_trends)//2:]) / (len(accuracy_trends) - len(accuracy_trends)//2)
            improvement = second_half - first_half
            
            if improvement > 3:
                print(f"  📈 Improving trend (+{improvement:.1f}% better in recent games)")
            elif improvement < -3:
                print(f"  📉 Declining trend ({improvement:.1f}% worse in recent games)")
            else:
                print(f"  → Stable trend (no significant change)")
        
        # Recommendations
        print(f"\n📋 RECOMMENDATIONS")
        print("-" * 70)
        if overall_accuracy < 60:
            print(f"  • Focus on tactics training to reduce blunders")
            print(f"  • Slow down and calculate more carefully")
        
        if "endgame" in phase_stats and "opening" in phase_stats:
            if phase_stats["endgame"] < phase_stats["opening"] - 8:
                print(f"  • Practice endgame technique - accuracy drops in this phase")
        
        if consistency > 15:
            print(f"  • Work on consistency - reduce variance between games")
        
        if error_rate > 40:
            print(f"  • High error rate - consider playing slower time controls")
        
        print("\n" + "="*70)
        
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _account_metrics_dashboard():
    """Display Account Metrics Dashboard"""
    print("\n" + "-"*50)
    print("ACCOUNT METRICS DASHBOARD")
    print("-"*50)
    
    username = input("Enter Chess.com username: ").strip()
    if not username:
        return
    
    game_count = input("How many games to analyze? (default 100): ").strip()
    try:
        game_count = int(game_count) if game_count else 100
    except:
        game_count = 100
    
    try:
        print(f"\nFetching up to {game_count} games for {username}...")
        player_games = fetch_player_games(username, max_games=game_count)
        actual_count = len(player_games)
        msg = f"✓ Retrieved {actual_count} games"
        if actual_count < game_count:
            msg += f" (player has fewer than {game_count} total)"
        print(msg + "\n")
        
        if not player_games:
            print(f"No games found for {username}")
            input("\nPress Enter to continue...")
            return
        
        print(f"Retrieved {len(player_games)} games. Analyzing...")
        
        from .dashboard import display_dashboard_from_games
        display_dashboard_from_games(player_games, username)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _multi_player_comparison():
    """Compare statistics across multiple players"""
    print("\n" + "-"*50)
    print("MULTI-PLAYER COMPARISON")
    print("-"*50)
    
    print("\nEnter player usernames (comma-separated):")
    usernames_input = input("Usernames: ").strip()
    if not usernames_input:
        return
    
    usernames = [u.strip() for u in usernames_input.split(',')]
    if len(usernames) < 2:
        print("❌ Please enter at least 2 usernames")
        input("\nPress Enter to continue...")
        return
    
    game_count = input("Games per player to analyze? (default 100): ").strip()
    try:
        game_count = int(game_count) if game_count else 100
    except:
        game_count = 100
    
    try:
        from .comparison import compare_players_display
        compare_players_display(usernames, max_games=game_count)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _fatigue_detection():
    """Analyze fatigue patterns in a player's games"""
    print("\n" + "-"*50)
    print("FATIGUE DETECTION ANALYSIS")
    print("-"*50)
    
    username = input("Enter Chess.com username: ").strip()
    if not username:
        return
    
    game_count = input("Games to analyze? (default 100): ").strip()
    try:
        game_count = int(game_count) if game_count else 100
    except:
        game_count = 100
    
    try:
        print(f"\nFetching up to {game_count} games for {username}...")
        player_games = fetch_player_games(username, max_games=game_count)
        actual_count = len(player_games)
        
        if not player_games:
            print(f"No games found for {username}")
            input("\nPress Enter to continue...")
            return
        
        msg = f"Retrieved {actual_count} games"
        if actual_count < game_count:
            msg += f" (player has fewer than {game_count} total)"
        print(msg + ". Analyzing...")
        
        from .fatigue import display_fatigue_analysis
        display_fatigue_analysis(player_games, username)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _network_analysis():
    """Analyze player connection networks and opponent patterns"""
    print("\n" + "-"*50)
    print("NETWORK ANALYSIS")
    print("-"*50)
    
    username = input("Enter Chess.com username: ").strip()
    if not username:
        return
    
    game_count = input("Games to analyze? (default 100): ").strip()
    try:
        game_count = int(game_count) if game_count else 100
    except:
        game_count = 100
    
    try:
        print(f"\nFetching up to {game_count} games for {username}...")
        player_games = fetch_player_games(username, max_games=game_count)
        actual_count = len(player_games)
        
        if not player_games:
            print(f"No games found for {username}")
            input("\nPress Enter to continue...")
            return
        
        msg = f"Retrieved {actual_count} games"
        if actual_count < game_count:
            msg += f" (player has fewer than {game_count} total)"
        print(msg + ". Analyzing...")
        
        from .network import display_network_analysis
        display_network_analysis(player_games, username)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def _opening_repertoire_inspector():
    """Analyze opponent's opening repertoire and vulnerabilities"""
    print("\n" + "-"*50)
    print("🎯 OPENING REPERTOIRE INSPECTOR")
    print("-"*50)
    print("\nVisualize opponent's opening repertoire, patterns, and vulnerabilities")
    
    username = input("\nEnter Chess.com username: ").strip()
    if not username:
        return
    
    game_count = input("Games to analyze? (default 100, recommended 50-200): ").strip()
    try:
        game_count = int(game_count) if game_count else 100
    except:
        game_count = 100
    
    try:
        print(f"\nFetching up to {game_count} games for {username}...")
        player_games = fetch_player_games(username, max_games=game_count)
        actual_count = len(player_games)
        
        if not player_games:
            print(f"No games found for {username}")
            input("\nPress Enter to continue...")
            return
        
        msg = f"Retrieved {actual_count} games"
        if actual_count < game_count:
            msg += f" (player has fewer than {game_count} total)"
        print(msg + ". Building opening tree...\n")
        
        from .opening_tree import display_opening_tree_analysis
        display_opening_tree_analysis(player_games, username)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")
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
    """Configure application settings."""
    from .utils.helpers import load_config, save_config
    
    while True:
        print("\n" + "-"*50)
        print("SETTINGS")
        print("-"*50)
        print("1. Analysis Engine Settings")
        print("2. Cache Settings")
        print("3. Report Settings")
        print("4. Chess.com API Settings")
        print("5. View Current Configuration")
        print("6. Reset to Defaults")
        print("7. Back to Main Menu")
        print("-"*50)
        
        choice = input("Select option (1-7): ").strip()
        
        if choice == "1":
            _engine_settings()
        elif choice == "2":
            _cache_settings()
        elif choice == "3":
            _report_settings()
        elif choice == "4":
            _api_settings()
        elif choice == "5":
            _view_config()
        elif choice == "6":
            _reset_config()
        elif choice == "7":
            break
        else:
            print("Invalid option!")


def _engine_settings():
    """Configure analysis engine settings."""
    from .utils.helpers import load_config, save_config
    
    config = load_config()
    
    print("\n" + "-"*50)
    print("ENGINE SETTINGS")
    print("-"*50)
    
    current_depth = config.get('analysis', {}).get('engine_depth', 14)
    current_threads = config.get('analysis', {}).get('threads', 2)
    current_hash = config.get('analysis', {}).get('hash_size', 256)
    use_lichess = config.get('analysis', {}).get('use_lichess', False)
    
    print(f"\nCurrent Settings:")
    print(f"  Stockfish Depth: {current_depth}")
    print(f"  Threads: {current_threads}")
    print(f"  Hash Size: {current_hash} MB")
    print(f"  Use Lichess: {'Yes' if use_lichess else 'No'}")
    
    print("\nOptions:")
    print("1. Change Stockfish Depth")
    print("2. Change Thread Count")
    print("3. Change Hash Size")
    print("4. Toggle Lichess API")
    print("5. Back")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        try:
            depth = int(input(f"Enter depth (10-20, current: {current_depth}): "))
            if 10 <= depth <= 20:
                config['analysis']['engine_depth'] = depth
                save_config(config)
                print(f"✓ Depth changed to {depth}")
            else:
                print("Invalid depth! Must be between 10-20")
        except:
            print("Invalid input!")
    
    elif choice == "2":
        try:
            threads = int(input(f"Enter threads (1-8, current: {current_threads}): "))
            if 1 <= threads <= 8:
                config['analysis']['threads'] = threads
                save_config(config)
                print(f"✓ Threads changed to {threads}")
            else:
                print("Invalid threads! Must be between 1-8")
        except:
            print("Invalid input!")
    
    elif choice == "3":
        try:
            hash_size = int(input(f"Enter hash size in MB (64-1024, current: {current_hash}): "))
            if 64 <= hash_size <= 1024:
                config['analysis']['hash_size'] = hash_size
                save_config(config)
                print(f"✓ Hash size changed to {hash_size} MB")
            else:
                print("Invalid hash size! Must be between 64-1024")
        except:
            print("Invalid input!")
    
    elif choice == "4":
        new_value = not use_lichess
        config['analysis']['use_lichess'] = new_value
        save_config(config)
        status = "enabled" if new_value else "disabled"
        print(f"✓ Lichess API {status}")
        print(f"  Note: Lichess requires valid API token in config.yaml")
    
    input("\nPress Enter to continue...")


def _cache_settings():
    """Configure cache settings."""
    from .utils.helpers import load_config, save_config
    
    config = load_config()
    
    print("\n" + "-"*50)
    print("CACHE SETTINGS")
    print("-"*50)
    
    cache_enabled = config.get('chess_com', {}).get('cache_enabled', True)
    cache_dir = config.get('chess_com', {}).get('cache_dir', 'cache')
    
    print(f"\nCurrent Settings:")
    print(f"  Cache Enabled: {'Yes' if cache_enabled else 'No'}")
    print(f"  Cache Directory: {cache_dir}")
    
    print("\nOptions:")
    print("1. Toggle Cache")
    print("2. Clear Cache Files")
    print("3. Change Cache Directory")
    print("4. Back")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        new_value = not cache_enabled
        config['chess_com']['cache_enabled'] = new_value
        save_config(config)
        status = "enabled" if new_value else "disabled"
        print(f"✓ Cache {status}")
    
    elif choice == "2":
        cache_path = Path(cache_dir)
        if cache_path.exists():
            count = 0
            for file in cache_path.glob("*.json"):
                file.unlink()
                count += 1
            print(f"✓ Deleted {count} cache files")
        else:
            print(f"Cache directory not found: {cache_dir}")
    
    elif choice == "3":
        new_dir = input(f"Enter new cache directory (current: {cache_dir}): ").strip()
        if new_dir:
            config['chess_com']['cache_dir'] = new_dir
            save_config(config)
            Path(new_dir).mkdir(exist_ok=True)
            print(f"✓ Cache directory changed to {new_dir}")
    
    input("\nPress Enter to continue...")


def _report_settings():
    """Configure report settings."""
    from .utils.helpers import load_config, save_config
    
    config = load_config()
    
    print("\n" + "-"*50)
    print("REPORT SETTINGS")
    print("-"*50)
    
    report_format = config.get('report', {}).get('default_format', 'html')
    output_dir = config.get('report', {}).get('output_dir', 'reports')
    highlight = config.get('report', {}).get('highlight_suspicious', True)
    save_analysis = config.get('report', {}).get('save_analysis_data', True)
    
    print(f"\nCurrent Settings:")
    print(f"  Default Format: {report_format}")
    print(f"  Output Directory: {output_dir}")
    print(f"  Highlight Suspicious: {'Yes' if highlight else 'No'}")
    print(f"  Save Analysis Data: {'Yes' if save_analysis else 'No'}")
    
    print("\nOptions:")
    print("1. Change Default Format (html/json)")
    print("2. Change Output Directory")
    print("3. Toggle Highlight Suspicious")
    print("4. Toggle Save Analysis Data")
    print("5. Back")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        fmt = input("Enter format (html/json): ").strip().lower()
        if fmt in ['html', 'json']:
            config['report']['default_format'] = fmt
            save_config(config)
            print(f"✓ Default format changed to {fmt}")
        else:
            print("Invalid format!")
    
    elif choice == "2":
        new_dir = input(f"Enter output directory (current: {output_dir}): ").strip()
        if new_dir:
            config['report']['output_dir'] = new_dir
            save_config(config)
            Path(new_dir).mkdir(exist_ok=True)
            print(f"✓ Output directory changed to {new_dir}")
    
    elif choice == "3":
        config['report']['highlight_suspicious'] = not highlight
        save_config(config)
        status = "enabled" if not highlight else "disabled"
        print(f"✓ Highlight suspicious {status}")
    
    elif choice == "4":
        config['report']['save_analysis_data'] = not save_analysis
        save_config(config)
        status = "enabled" if not save_analysis else "disabled"
        print(f"✓ Save analysis data {status}")
    
    input("\nPress Enter to continue...")


def _api_settings():
    """Configure Chess.com API settings."""
    from .utils.helpers import load_config, save_config
    
    config = load_config()
    
    print("\n" + "-"*50)
    print("CHESS.COM API SETTINGS")
    print("-"*50)
    
    api_base = config.get('chess_com', {}).get('api_base', 'https://api.chess.com/pub/player')
    delay = config.get('chess_com', {}).get('request_delay', 1.0)
    max_games = config.get('chess_com', {}).get('max_games', 100)
    
    print(f"\nCurrent Settings:")
    print(f"  API Base URL: {api_base}")
    print(f"  Request Delay: {delay}s")
    print(f"  Max Games Per Request: {max_games}")
    
    print("\nOptions:")
    print("1. Change Request Delay")
    print("2. Change Max Games Per Request")
    print("3. Reset API to Defaults")
    print("4. Back")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        try:
            new_delay = float(input(f"Enter delay in seconds (0.5-5.0, current: {delay}): "))
            if 0.5 <= new_delay <= 5.0:
                config['chess_com']['request_delay'] = new_delay
                save_config(config)
                print(f"✓ Request delay changed to {new_delay}s")
            else:
                print("Invalid delay! Must be between 0.5-5.0")
        except:
            print("Invalid input!")
    
    elif choice == "2":
        try:
            new_max = int(input(f"Enter max games (10-500, current: {max_games}): "))
            if 10 <= new_max <= 500:
                config['chess_com']['max_games'] = new_max
                save_config(config)
                print(f"✓ Max games changed to {new_max}")
            else:
                print("Invalid value! Must be between 10-500")
        except:
            print("Invalid input!")
    
    elif choice == "3":
        config['chess_com']['api_base'] = 'https://api.chess.com/pub/player'
        config['chess_com']['request_delay'] = 1.0
        config['chess_com']['max_games'] = 100
        save_config(config)
        print("✓ API settings reset to defaults")
    
    input("\nPress Enter to continue...")


def _view_config():
    """Display current configuration."""
    from .utils.helpers import load_config
    
    config = load_config()
    
    print("\n" + "-"*50)
    print("CURRENT CONFIGURATION")
    print("-"*50)
    
    print("\n📊 Analysis Settings:")
    print(f"  Engine Depth: {config.get('analysis', {}).get('engine_depth', 14)}")
    print(f"  Threads: {config.get('analysis', {}).get('threads', 2)}")
    print(f"  Hash Size: {config.get('analysis', {}).get('hash_size', 256)} MB")
    print(f"  Use Lichess: {config.get('analysis', {}).get('use_lichess', False)}")
    
    print("\n🔗 Chess.com API:")
    print(f"  Request Delay: {config.get('chess_com', {}).get('request_delay', 1.0)}s")
    print(f"  Max Games: {config.get('chess_com', {}).get('max_games', 100)}")
    print(f"  Cache Enabled: {config.get('chess_com', {}).get('cache_enabled', True)}")
    print(f"  Cache Dir: {config.get('chess_com', {}).get('cache_dir', 'cache')}")
    
    print("\n📝 Report Settings:")
    print(f"  Default Format: {config.get('report', {}).get('default_format', 'html')}")
    print(f"  Output Dir: {config.get('report', {}).get('output_dir', 'reports')}")
    print(f"  Highlight Suspicious: {config.get('report', {}).get('highlight_suspicious', True)}")
    print(f"  Save Analysis Data: {config.get('report', {}).get('save_analysis_data', True)}")
    
    print("\n⚙️  Thresholds:")
    thresholds = config.get('analysis', {}).get('thresholds', {})
    print(f"  Engine Correlation: {thresholds.get('engine_correlation_red_flag', 92.0)}%")
    print(f"  Centipawn Loss: {thresholds.get('avg_centipawn_loss_red_flag', 15.0)}")
    print(f"  Accuracy Fluctuation: {thresholds.get('accuracy_fluctuation_red_flag', 25.0)}%")
    print(f"  Min Games: {thresholds.get('min_games_for_analysis', 5)}")
    
    input("\nPress Enter to continue...")


def _reset_config():
    """Reset configuration to defaults."""
    from .utils.helpers import save_config
    
    confirm = input("\n⚠️  Reset all settings to defaults? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        default_config = {
            'chess_com': {
                'api_base': 'https://api.chess.com/pub/player',
                'request_delay': 1.0,
                'max_games': 100,
                'cache_enabled': True,
                'cache_dir': 'cache'
            },
            'lichess': {
                'api_token': '',
                'username': '',
                'enabled': False
            },
            'analysis': {
                'use_lichess': False,
                'engine_depth': 14,
                'engine_path': 'stockfish/stockfish-windows-x86-64.exe',
                'threads': 2,
                'hash_size': 256,
                'thresholds': {
                    'engine_correlation_red_flag': 92.0,
                    'avg_centipawn_loss_red_flag': 15.0,
                    'accuracy_fluctuation_red_flag': 25.0,
                    'min_games_for_analysis': 5
                }
            },
            'report': {
                'default_format': 'html',
                'output_dir': 'reports',
                'include_all_games_data': False,
                'highlight_suspicious': True,
                'save_analysis_data': True
            },
            'logging': {
                'level': 'INFO',
                'log_file': ''
            }
        }
        save_config(default_config)
        print("✓ Configuration reset to defaults")
    else:
        print("Reset cancelled")
    
    input("\nPress Enter to continue...")


def _export_suspicious_games(results, username, all_games):
    """Export suspicious games to PGN and optionally ZIP them."""
    try:
        # Create exports directory
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)
        
        # Collect suspicious games
        suspicious_games = []
        for game_analysis in results.game_analyses:
            if game_analysis.is_suspicious:
                suspicious_games.append(game_analysis.game)
        
        if not suspicious_games:
            print("No suspicious games to export.")
            return
        
        # Export options
        print("\nExport Format:")
        print("1. PGN files (individual)")
        print("2. Single PGN file (all in one)")
        print("3. ZIP archive (PGN + JSON)")
        choice = input("Choose (1-3): ").strip()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if choice == "1":
            # Individual PGN files
            for i, game in enumerate(suspicious_games, 1):
                filename = export_dir / f"{username}_suspicious_{i:02d}.pgn"
                with open(filename, "w") as f:
                    f.write(str(game))
            print(f"\n✓ Exported {len(suspicious_games)} PGN files to exports/")
        
        elif choice == "2":
            # Single PGN file
            filename = export_dir / f"{username}_suspicious_games_{timestamp}.pgn"
            with open(filename, "w") as f:
                for i, game in enumerate(suspicious_games):
                    if i > 0:
                        f.write("\n\n")
                    f.write(str(game))
            print(f"\n✓ Exported to {filename.name}")
        
        elif choice == "3":
            # ZIP archive
            zip_filename = export_dir / f"{username}_suspicious_games_{timestamp}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add PGN file
                pgn_data = ""
                for i, game in enumerate(suspicious_games):
                    if i > 0:
                        pgn_data += "\n\n"
                    pgn_data += str(game)
                zf.writestr(f"{username}_suspicious_games.pgn", pgn_data)
                
                # Add JSON summary
                summary = {
                    "username": username,
                    "timestamp": timestamp,
                    "suspicious_count": len(suspicious_games),
                    "suspicion_score": results.suspicion_score,
                    "engine_correlation": results.avg_engine_correlation,
                }
                zf.writestr(f"{username}_summary.json", json.dumps(summary, indent=2))
            
            print(f"\n✓ Exported ZIP to {zip_filename.name}")
            print(f"  Contents: PGN file + JSON summary")
        
        else:
            print("Invalid choice.")
    
    except Exception as e:
        print(f"Error exporting games: {e}")


if __name__ == "__main__":
    main()
def _account_metrics():
    print("\n" + "-"*50)
    print("ACCOUNT METRICS - BEHAVIORAL ANALYSIS")
    print("-"*50)

    username = input("\nEnter Chess.com username: ").strip()
    if not username:
        return

    from .fetcher import fetch_player_games
    from .account_metrics import analyze_account_behavior

    games = fetch_player_games(username, max_games=100)

    if not games:
        print("No games found.")
        input("Press Enter to continue...")
        return

    metrics = analyze_account_behavior(games, username)

    print("\n" + "="*60)
    print(f"ACCOUNT METRICS FOR {username.upper()}")
    print("="*60)

    rp = metrics.get("rating_progression")
    if rp:
        print(f"\n📈 Rating Volatility:")
        print(f"  Avg Change: {rp['avg_change']:.1f}")
        print(f"  Max Change: {rp['max_change']}")
        print(f"  Suspicious Jumps: {'YES' if rp['suspicious'] else 'NO'}")

    tp = metrics.get("time_patterns")
    if tp:
        print(f"\n⏱️ Move Time Patterns:")
        print(f"  CV: {tp['coefficient_variation']:.1f}%")
        print(f"  Repeated Timing: {tp['common_time_percentage']:.1f}%")
        print(f"  Suspicious Consistency: {'YES' if tp['is_suspicious'] else 'NO'}")

    oa = metrics.get("opponent_strength_anomaly")
    if oa:
        print(f"\n🎯 Opponent Strength Anomaly Score: {oa:.1f}/100")

    gc = metrics.get("game_clustering")
    if gc:
        print(f"\n📆 Game Clustering:")
        print(f"  Max Games/Day: {gc['max_games_per_day']}")
        print(f"  Clustered: {'YES' if gc['is_clustered'] else 'NO'}")

    print("\n" + "="*60)
    input("\nPress Enter to continue...")
