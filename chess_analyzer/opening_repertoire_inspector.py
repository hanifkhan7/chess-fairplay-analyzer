#!/usr/bin/env python3
"""
Opening Repertoire Inspector v3.2 (Enhanced)
Hybrid system for analyzing player opening behavior
- Realistic Opening Tree (branching diagram with ECO codes)
- Enhanced Statistical visualization
- Opening statistics with detailed metrics
- Comprehensive reporting with ECO codes and opening names
"""

import json
import os
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from io import StringIO

import chess
import chess.pgn

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    pd = None
    plt = None
    sns = None
    mpatches = None
    # Debug: log import error
    # print(f"[DEBUG] Visualization imports failed: {e}")


class OpeningNode:
    """Represents a node in the opening tree with ECO and opening name tracking."""
    
    def __init__(self, move: str, depth: int):
        self.move = move  # UCI notation
        self.depth = depth
        self.frequency = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.total_game_length = 0
        self.children = {}  # move_uci -> OpeningNode
        self.parent = None
        self.eco_codes = Counter()  # Track ECO codes at this position
        self.opening_names = Counter()  # Track opening names at this position
    
    def add_result(self, result: str, eco: str = "", opening_name: str = ""):
        """Add a game result to this node."""
        self.frequency += 1
        if result == "1-0":
            self.wins += 1
        elif result == "0-1":
            self.losses += 1
        elif result == "*":
            self.draws += 1
        
        if eco:
            self.eco_codes[eco] += 1
        if opening_name:
            self.opening_names[opening_name] += 1
    
    def get_primary_eco(self) -> str:
        """Get the most common ECO code at this node."""
        if self.eco_codes:
            return self.eco_codes.most_common(1)[0][0]
        return ""
    
    def get_primary_opening(self) -> str:
        """Get the most common opening name at this node."""
        if self.opening_names:
            return self.opening_names.most_common(1)[0][0]
        return ""
    
    def get_win_rate(self) -> float:
        """Calculate win percentage."""
        if self.frequency == 0:
            return 0.0
        return (self.wins / self.frequency) * 100
    
    def get_draw_rate(self) -> float:
        """Calculate draw percentage."""
        if self.frequency == 0:
            return 0.0
        return (self.draws / self.frequency) * 100
    
    def get_loss_rate(self) -> float:
        """Calculate loss percentage."""
        if self.frequency == 0:
            return 0.0
        return (self.losses / self.frequency) * 100
    
    def get_avg_game_length(self) -> float:
        """Calculate average game length."""
        if self.frequency == 0:
            return 0.0
        return self.total_game_length / self.frequency


class OpeningTree:
    """Build and manage the opening tree structure."""
    
    def __init__(self, player_color: str = "white"):
        """
        Initialize the opening tree.
        
        Args:
            player_color: "white", "black", or "both"
        """
        self.root = OpeningNode("root", 0)
        self.player_color = player_color
        self.max_depth = 15
        self.games_analyzed = 0
        self.openings_data = []  # List of dicts for DataFrame
    
    def add_game(self, pgn_game, player_name: str, player_color: str, 
                 min_moves: int = 15):
        """
        Add a game to the opening tree.
        
        Args:
            pgn_game: chess.pgn.Game object
            player_name: Username of the player
            player_color: "white" or "black"
            min_moves: Minimum moves required to include game
        """
        # Extract game info
        moves = list(pgn_game.mainline_moves())
        
        # Check minimum depth
        if len(moves) < min_moves:
            return
        
        # Get result from player's perspective
        result = pgn_game.headers.get("Result", "*")
        white_player = pgn_game.headers.get("White", "")
        black_player = pgn_game.headers.get("Black", "")
        
        # Extract ECO and opening name
        eco = pgn_game.headers.get("ECO", "Unknown")
        opening = pgn_game.headers.get("Opening", "")
        
        # If opening name is missing, try to generate from ECO or moves
        if not opening or opening == "Unknown":
            opening = self._generate_opening_name(eco, moves)
        
        # Determine if we should include this game
        is_white = (white_player.lower() == player_name.lower())
        is_black = (black_player.lower() == player_name.lower())
        
        if not (is_white or is_black):
            return
        
        # Adjust result if player is black
        if is_black and result != "*":
            result = {"1-0": "0-1", "0-1": "1-0", "*": "*"}.get(result, "*")
        
        # Build the tree
        node = self.root
        board = chess.Board()
        move_count = 0
        
        for move in moves[:self.max_depth]:
            move_uci = move.uci()
            move_count += 1
            
            if move_uci not in node.children:
                node.children[move_uci] = OpeningNode(move_uci, node.depth + 1)
                node.children[move_uci].parent = node
            
            node = node.children[move_uci]
            board.push(move)
        
        # Add result to all nodes in the path with ECO/opening info
        node = self.root
        for move in moves[:self.max_depth]:
            move_uci = move.uci()
            if move_uci in node.children:
                node = node.children[move_uci]
                node.add_result(result, eco, opening)
                node.total_game_length += len(moves)
        
        # Add to openings data
        self.openings_data.append({
            "eco": eco,
            "opening": opening,
            "moves": len(moves),
            "result": result,
            "white": white_player,
            "black": black_player,
            "date": pgn_game.headers.get("Date", "Unknown"),
            "elo_opp": int(pgn_game.headers.get(
                "BlackElo" if is_white else "WhiteElo", 0
            )),
        })
        
        self.games_analyzed += 1
    
    def _generate_opening_name(self, eco: str, moves: list) -> str:
        """Generate opening name from ECO code and initial moves."""
        # Common opening names by ECO code prefix
        eco_names = {
            "A": "Unusual Opening",
            "B": "Semi-Open Game",
            "C": "Open Game",
            "D": "Closed Game",
            "E": "Semi-Closed Game",
        }
        
        # Try to get more specific names
        eco_specific = {
            "C00": "French Defense",
            "C10": "French Defense",
            "C20": "Italian Game / King's Pawn Opening",
            "C23": "Italian Game",
            "C24": "Italian Game",
            "C50": "Giuoco Piano",
            "C60": "Ruy Lopez",
            "C80": "Ruy Lopez - Open",
            "B20": "Sicilian Defense",
            "B30": "Sicilian Defense",
            "D20": "Queen's Pawn Game",
            "D40": "Queen's Gambit",
            "E00": "Closed Game",
        }
        
        # Check specific codes first
        if eco in eco_specific:
            return eco_specific[eco]
        
        # Check first letter for general opening type
        if eco and len(eco) > 0:
            first_letter = eco[0]
            if first_letter in eco_names:
                return eco_names[first_letter]
        
        # Fallback: generate from first few moves
        if moves and len(moves) >= 2:
            try:
                board = chess.Board()
                first_moves = []
                for i, move in enumerate(moves[:4]):
                    san = board.san(move)
                    first_moves.append(san)
                    board.push(move)
                
                return f"Game: {' '.join(first_moves)}"
            except:
                pass
        
        return "Unknown Opening"
    
    def get_tree_stats(self) -> Dict:
        """Get overall statistics from the tree."""
        return {
            "games_analyzed": self.games_analyzed,
            "total_nodes": self._count_nodes(self.root),
            "max_depth_reached": self._get_max_depth(self.root),
        }
    
    def _count_nodes(self, node: OpeningNode) -> int:
        """Count total nodes in tree."""
        count = 1
        for child in node.children.values():
            count += self._count_nodes(child)
        return count
    
    def _get_max_depth(self, node: OpeningNode) -> int:
        """Get maximum depth reached."""
        if not node.children:
            return node.depth
        return max(self._get_max_depth(child) for child in node.children.values())
    
    def get_popular_moves(self, depth: int = 1, top_n: int = 5) -> List[Dict]:
        """Get the most popular moves at a given depth."""
        node = self.root
        if depth > 1:
            # Navigate to depth
            for _ in range(depth - 1):
                if not node.children:
                    break
                node = max(node.children.values(), 
                          key=lambda n: n.frequency)
        
        moves = []
        for move_uci, child in node.children.items():
            moves.append({
                "move": move_uci,
                "frequency": child.frequency,
                "win_rate": child.get_win_rate(),
                "draw_rate": child.get_draw_rate(),
                "loss_rate": child.get_loss_rate(),
                "avg_length": child.get_avg_game_length(),
            })
        
        return sorted(moves, key=lambda x: x["frequency"], reverse=True)[:top_n]
    
    def get_opening_tree_visualization(self, max_depth: int = 6) -> str:
        """
        Generate ASCII visualization of the opening tree with ECO codes and statistics.
        
        Args:
            max_depth: Maximum depth to display
            
        Returns:
            ASCII tree string
        """
        lines = []
        lines.append("\n" + "="*100)
        lines.append("OPENING TREE VISUALIZATION")
        lines.append("="*100)
        
        def format_node(node: OpeningNode) -> str:
            """Format node info with ECO, opening name, and statistics."""
            if node.depth == 0:
                return ""
            
            eco = node.get_primary_eco() or ""
            opening = node.get_primary_opening() or ""
            
            # Truncate long opening names
            if len(opening) > 35:
                opening = opening[:32] + "..."
            
            # Convert move from UCI to algebraic with move numbers
            try:
                board = chess.Board()
                # Rebuild board state to get algebraic notation
                current = node
                path = []
                while current.parent:
                    path.append(current.move)
                    current = current.parent
                path.reverse()
                
                # Track move number
                move_num = 1
                san_moves = []
                for move_uci in path:
                    move = chess.Move.from_uci(move_uci)
                    san = board.san(move)
                    
                    # Add move number before white's move
                    if board.turn:  # White's turn (before move)
                        san_moves.append(f"{move_num}.{san}")
                    else:
                        san_moves.append(f"{san}")
                        move_num += 1
                    
                    board.push(move)
                
                # Get last move with proper numbering
                last_move = chess.Move.from_uci(node.move)
                san = board.san(last_move)
                
                # Add move number if it's white's move
                if board.turn:  # White's turn (before move)
                    move_notation = f"{move_num}.{san}"
                else:
                    move_notation = f"{move_num}...{san}"
                
                # Format: move [ECO] Opening Name (W% | D% | L% | freq)
                win_pct = node.get_win_rate()
                draw_pct = node.get_draw_rate()
                loss_pct = node.get_loss_rate()
                
                color_code = ""
                if win_pct > 55:
                    color_code = "✓"  # Strong position
                elif win_pct < 45:
                    color_code = "✗"  # Weak position
                else:
                    color_code = "="  # Balanced
                
                result_str = f"{color_code} {win_pct:.0f}%W {draw_pct:.0f}%D {loss_pct:.0f}%L"
                eco_str = f"[{eco}]" if eco and eco != "Unknown" else ""
                
                return f"{move_notation:6} {eco_str:8} {opening:35} {result_str} ({node.frequency}x)"
            except:
                return f"{node.move:4} (stats: W{node.get_win_rate():.0f}% D{node.get_draw_rate():.0f}% L{node.get_loss_rate():.0f}%)"
        
        def print_tree(node: OpeningNode, prefix: str = "", is_last: bool = True, depth: int = 0):
            """Recursively print the tree structure."""
            if depth > max_depth:
                return
            
            if depth > 0:  # Skip root
                connector = "└── " if is_last else "├── "
                lines.append(prefix + connector + format_node(node))
                
                extension = "    " if is_last else "│   "
                prefix = prefix + extension
            
            # Sort children by frequency
            children = sorted(node.children.values(), key=lambda x: x.frequency, reverse=True)[:5]
            
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                print_tree(child, prefix, is_last_child, depth + 1)
        
        print_tree(self.root)
        lines.append("="*100 + "\n")
        
        return "\n".join(lines)


class OpeningAnalyzer:
    """Main analyzer for opening repertoire."""
    
    def __init__(self):
        self.white_tree = None
        self.black_tree = None
        self.all_games_data = []
    
    def analyze_games(self, games: List, player_name: str, 
                     player_color: str = "both", result_filter: str = "all",
                     min_moves: int = 15) -> Dict:
        """
        Analyze a collection of games.
        
        Args:
            games: List of chess.pgn.Game objects
            player_name: Username to analyze
            player_color: "white", "black", or "both"
            result_filter: "all", "wins", "losses", or "draws"
            min_moves: Minimum moves to include game
        
        Returns:
            Dictionary with analysis results
        """
        # Filter games by result
        filtered_games = self._filter_games(games, player_name, result_filter)
        
        # Build trees
        if player_color in ["white", "both"]:
            self.white_tree = OpeningTree("white")
            for game in filtered_games:
                self.white_tree.add_game(game, player_name, "white", min_moves)
        
        if player_color in ["black", "both"]:
            self.black_tree = OpeningTree("black")
            for game in filtered_games:
                self.black_tree.add_game(game, player_name, "black", min_moves)
        
        # Compile results
        return self._compile_results(player_name, player_color)
    
    def _filter_games(self, games: List, player_name: str, 
                     result_filter: str) -> List:
        """Filter games by result."""
        if result_filter == "all":
            return games
        
        filtered = []
        for game in games:
            result = game.headers.get("Result", "*")
            white = game.headers.get("White", "").lower()
            black = game.headers.get("Black", "").lower()
            
            is_player_white = (white == player_name.lower())
            is_player_black = (black == player_name.lower())
            
            if not (is_player_white or is_player_black):
                continue
            
            # Check result filter
            if result_filter == "wins":
                if is_player_white and result == "1-0":
                    filtered.append(game)
                elif is_player_black and result == "0-1":
                    filtered.append(game)
            elif result_filter == "losses":
                if is_player_white and result == "0-1":
                    filtered.append(game)
                elif is_player_black and result == "1-0":
                    filtered.append(game)
            elif result_filter == "draws":
                if result == "*":
                    filtered.append(game)
        
        return filtered
    
    def _compile_results(self, player_name: str, player_color: str) -> Dict:
        """Compile analysis results."""
        results = {
            "player": player_name,
            "color": player_color,
            "white_tree": self.white_tree,
            "black_tree": self.black_tree,
            "timestamp": datetime.now().isoformat(),
        }
        
        if self.white_tree:
            results["white_stats"] = self.white_tree.get_tree_stats()
        if self.black_tree:
            results["black_stats"] = self.black_tree.get_tree_stats()
        
        return results
    
    def export_to_dataframe(self) -> 'pd.DataFrame':
        """Export opening data to DataFrame."""
        if not VISUALIZATION_AVAILABLE:
            print("[WARN] pandas not available - skipping DataFrame export")
            return None
        
        all_data = []
        
        if self.white_tree:
            for item in self.white_tree.openings_data:
                item["color"] = "white"
                all_data.append(item)
        
        if self.black_tree:
            for item in self.black_tree.openings_data:
                item["color"] = "black"
                all_data.append(item)
        
        if not all_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        return df


class OpeningVisualizer:
    """Generate visualizations for opening analysis."""
    
    def __init__(self, analyzer: OpeningAnalyzer):
        if not VISUALIZATION_AVAILABLE:
            raise ImportError("matplotlib, pandas, and seaborn required for visualizations. Install with: pip install matplotlib seaborn pandas")
        
        self.analyzer = analyzer
        self.figures = []
    
    def generate_statistics(self) -> List:
        """Generate all statistical graphs."""
        figures = []
        
        df = self.analyzer.export_to_dataframe()
        if df is None or df.empty:
            print("[WARN] No games to visualize")
            return figures
        
        # 1. Opening frequency chart
        fig1 = self._plot_opening_frequency(df)
        figures.append(fig1)
        
        # 2. Win rate by opening
        fig2 = self._plot_win_rate_by_opening(df)
        figures.append(fig2)
        
        # 3. White vs Black comparison
        if "white" in df["color"].values and "black" in df["color"].values:
            fig3 = self._plot_color_comparison(df)
            figures.append(fig3)
        
        # 4. Result distribution
        fig4 = self._plot_result_distribution(df)
        figures.append(fig4)
        
        # 5. Game length distribution
        fig5 = self._plot_game_length_distribution(df)
        figures.append(fig5)
        
        self.figures = figures
        return figures
    
    def _plot_opening_frequency(self, df: 'pd.DataFrame'):
        """Plot frequency of openings with ECO codes."""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Group by opening and count
        opening_counts = df["opening"].value_counts().head(12)
        
        # Get ECO codes for each opening
        eco_labels = []
        for opening in opening_counts.index:
            eco = df[df["opening"] == opening]["eco"].mode()
            eco_str = eco[0] if len(eco) > 0 and eco[0] != "Unknown" else ""
            if eco_str:
                eco_labels.append(f"{opening[:40]}\n[{eco_str}]")
            else:
                eco_labels.append(opening[:40])
        
        colors = sns.color_palette("husl", len(opening_counts))
        bars = ax.barh(range(len(opening_counts)), opening_counts.values, color=colors, edgecolor="black", linewidth=1.2)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, opening_counts.values)):
            ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{int(val)}", 
                   va="center", fontsize=10, fontweight="bold")
        
        ax.set_yticks(range(len(opening_counts)))
        ax.set_yticklabels(eco_labels, fontsize=10)
        ax.set_xlabel("Number of Games", fontsize=12, fontweight="bold")
        ax.set_title("Most Played Openings with ECO Codes", fontsize=14, fontweight="bold", pad=20)
        ax.grid(axis="x", alpha=0.3, linestyle="--")
        ax.invert_yaxis()
        
        plt.tight_layout()
        return fig
    
    def _plot_win_rate_by_opening(self, df: 'pd.DataFrame'):
        """Plot win rate by opening with ECO codes."""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Calculate win rate by opening
        opening_stats = []
        for opening in df["opening"].unique()[:12]:
            subset = df[df["opening"] == opening]
            wins = (subset["result"] == "1-0").sum()
            total = len(subset)
            win_rate = (wins / total * 100) if total > 0 else 0
            eco = subset["eco"].mode()
            eco_str = eco[0] if len(eco) > 0 and eco[0] != "Unknown" else ""
            opening_stats.append({
                "opening": opening,
                "eco": eco_str,
                "win_rate": win_rate,
                "games": total
            })
        
        stats_df = pd.DataFrame(opening_stats).sort_values("win_rate", ascending=True)
        
        # Color code by win rate
        colors = []
        for wr in stats_df["win_rate"]:
            if wr >= 55:
                colors.append("#2ecc71")  # Green - strong
            elif wr >= 50:
                colors.append("#3498db")  # Blue - slight edge
            elif wr >= 45:
                colors.append("#f39c12")  # Orange - balanced
            else:
                colors.append("#e74c3c")  # Red - weak
        
        # Labels with ECO codes
        labels = []
        for _, row in stats_df.iterrows():
            label = row["opening"][:35]
            if row["eco"] and row["eco"] != "Unknown":
                label += f"\n[{row['eco']}]"
            labels.append(label)
        
        bars = ax.barh(range(len(stats_df)), stats_df["win_rate"].values, color=colors, edgecolor="black", linewidth=1.2)
        
        # Add value labels
        for bar, val, games in zip(bars, stats_df["win_rate"].values, stats_df["games"].values):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2, f"{val:.1f}% ({int(games)}g)", 
                   va="center", fontsize=9, fontweight="bold")
        
        # Add 50% reference line
        ax.axvline(x=50, color="black", linestyle="--", linewidth=2, alpha=0.5, label="50% (neutral)")
        
        ax.set_yticks(range(len(stats_df)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("Win Rate (%)", fontsize=12, fontweight="bold")
        ax.set_xlim(0, 100)
        ax.set_title("Win Rate by Opening (Top 12)", fontsize=14, fontweight="bold", pad=20)
        ax.grid(axis="x", alpha=0.3, linestyle="--")
        ax.legend(loc="lower right")
        
        plt.tight_layout()
        return fig
    
    def _plot_color_comparison(self, df: 'pd.DataFrame'):
        """Plot performance comparison between white and black pieces."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        colors_list = ["white", "black"]
        win_rates = []
        draw_rates = []
        loss_rates = []
        
        for color in colors_list:
            if color not in df["color"].values:
                continue
            
            subset = df[df["color"] == color]
            wins = (subset["result"] == "1-0").sum()
            draws = (subset["result"] == "*").sum()
            losses = (subset["result"] == "0-1").sum()
            total = len(subset)
            
            win_rates.append(wins / total * 100 if total > 0 else 0)
            draw_rates.append(draws / total * 100 if total > 0 else 0)
            loss_rates.append(losses / total * 100 if total > 0 else 0)
        
        valid_colors = [c for c in colors_list if c in df["color"].values]
        x = range(len(valid_colors))
        
        # Stacked bar chart
        ax1.bar(x, win_rates, label="Wins", color="#2ecc71", edgecolor="black", linewidth=1.5)
        ax1.bar(x, draw_rates, bottom=win_rates, label="Draws", color="#f39c12", edgecolor="black", linewidth=1.5)
        ax1.bar(x, loss_rates, bottom=[w+d for w,d in zip(win_rates, draw_rates)], 
               label="Losses", color="#e74c3c", edgecolor="black", linewidth=1.5)
        
        ax1.set_ylabel("Percentage (%)", fontsize=12, fontweight="bold")
        ax1.set_title("Result Distribution by Color", fontsize=13, fontweight="bold")
        ax1.set_xticks(x)
        ax1.set_xticklabels(valid_colors, fontsize=11, fontweight="bold")
        ax1.legend(loc="upper right")
        ax1.set_ylim(0, 100)
        ax1.grid(axis="y", alpha=0.3, linestyle="--")
        
        # Win rate comparison
        if len(valid_colors) > 1:
            win_rate_data = [w for w in win_rates]
            bars = ax2.bar(valid_colors, win_rate_data, color=["#2ecc71", "#3498db"], 
                          edgecolor="black", linewidth=1.5, alpha=0.8)
            ax2.axhline(y=50, color="black", linestyle="--", linewidth=2, alpha=0.5)
            ax2.set_ylabel("Win Rate (%)", fontsize=12, fontweight="bold")
            ax2.set_title("Win Rate Comparison (White vs Black)", fontsize=13, fontweight="bold")
            ax2.set_ylim(0, 100)
            ax2.grid(axis="y", alpha=0.3, linestyle="--")
            
            for bar, val in zip(bars, win_rate_data):
                ax2.text(bar.get_x() + bar.get_width()/2, val + 2, f"{val:.1f}%", 
                        ha="center", fontweight="bold", fontsize=11)
        
        plt.tight_layout()
        return fig
    
    def _plot_result_distribution(self, df: 'pd.DataFrame'):
        """Plot overall result distribution with enhanced visuals."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart
        results = df["result"].value_counts()
        result_map = {"1-0": "Wins", "0-1": "Losses", "*": "Draws"}
        labels = [result_map.get(x, x) for x in results.index]
        colors_pie = ["#2ecc71", "#e74c3c", "#f39c12"]
        
        wedges, texts, autotexts = ax1.pie(results.values, labels=labels, autopct="%1.1f%%", 
                                            colors=colors_pie[:len(results)], startangle=90,
                                            textprops={"fontsize": 11, "fontweight": "bold"})
        ax1.set_title("Result Distribution (Pie Chart)", fontsize=13, fontweight="bold")
        
        # Bar chart with counts
        bar_colors = ["#2ecc71", "#e74c3c", "#f39c12"]
        bars = ax2.bar(labels, results.values, color=bar_colors[:len(results)], 
                       edgecolor="black", linewidth=1.5, alpha=0.8)
        
        ax2.set_ylabel("Number of Games", fontsize=12, fontweight="bold")
        ax2.set_title("Result Distribution (Count)", fontsize=13, fontweight="bold")
        ax2.grid(axis="y", alpha=0.3, linestyle="--")
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{int(height)}", 
                    ha="center", fontweight="bold", fontsize=11)
        
        plt.tight_layout()
        return fig
    
    def _plot_game_length_distribution(self, df: 'pd.DataFrame'):
        """Plot distribution of game lengths with enhanced visuals."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histogram
        ax1.hist(df["moves"], bins=25, color="#3498db", edgecolor="black", alpha=0.7)
        ax1.axvline(df["moves"].mean(), color="red", linestyle="--", linewidth=2, label=f"Mean: {df['moves'].mean():.1f}")
        ax1.axvline(df["moves"].median(), color="green", linestyle="--", linewidth=2, label=f"Median: {df['moves'].median():.1f}")
        
        ax1.set_xlabel("Number of Moves", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Frequency", fontsize=12, fontweight="bold")
        ax1.set_title("Game Length Distribution (Histogram)", fontsize=13, fontweight="bold")
        ax1.legend()
        ax1.grid(axis="y", alpha=0.3, linestyle="--")
        
        # Box plot by result
        result_map = {"1-0": "Wins", "0-1": "Losses", "*": "Draws"}
        data_by_result = [df[df["result"] == res]["moves"].values for res in ["1-0", "0-1", "*"] if res in df["result"].values]
        labels_box = [result_map[res] for res in ["1-0", "0-1", "*"] if res in df["result"].values]
        
        bp = ax2.boxplot(data_by_result, labels=labels_box, patch_artist=True)
        colors_box = ["#2ecc71", "#e74c3c", "#f39c12"]
        for patch, color in zip(bp["boxes"], colors_box[:len(bp["boxes"])]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax2.set_ylabel("Number of Moves", fontsize=12, fontweight="bold")
        ax2.set_title("Game Length by Result Type", fontsize=13, fontweight="bold")
        ax2.grid(axis="y", alpha=0.3, linestyle="--")
        
        plt.tight_layout()
        return fig
    
    def save_figures(self, output_dir: str = "reports"):
        """Save all figures to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        filenames = []
        for i, fig in enumerate(self.figures):
            filename = f"{output_dir}/opening_analysis_{i+1}.png"
            fig.savefig(filename, dpi=150, bbox_inches="tight")
            filenames.append(filename)
            plt.close(fig)
        
        return filenames


class ReportGenerator:
    """Generate comprehensive PDF/Excel reports."""
    
    def __init__(self, analyzer: OpeningAnalyzer, visualizer: OpeningVisualizer):
        if not VISUALIZATION_AVAILABLE:
            raise ImportError("pandas required for report generation. Install with: pip install pandas openpyxl")
        
        self.analyzer = analyzer
        self.visualizer = visualizer
    
    def export_to_excel(self, filename: str = "opening_analysis.xlsx"):
        """Export analysis to Excel file."""
        df = self.analyzer.export_to_dataframe()
        
        if df.empty:
            print("[ERROR] No data to export")
            return None
        
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            # Raw data sheet
            df.to_excel(writer, sheet_name="Raw Data", index=False)
            
            # Summary statistics
            summary_data = self._generate_summary_stats(df)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            # Opening statistics
            opening_stats = self._generate_opening_stats(df)
            opening_df = pd.DataFrame(opening_stats)
            opening_df.to_excel(writer, sheet_name="Opening Stats", index=False)
        
        print(f"[OK] Report exported to {filename}")
        return filename
    
    def export_to_csv(self, filename: str = "opening_analysis.csv"):
        """Export analysis to CSV file."""
        df = self.analyzer.export_to_dataframe()
        
        if df.empty:
            print("[ERROR] No data to export")
            return None
        
        df.to_csv(filename, index=False)
        print(f"[OK] Data exported to {filename}")
        return filename
    
    def _generate_summary_stats(self, df: 'pd.DataFrame') -> List[Dict]:
        """Generate summary statistics."""
        if df.empty:
            return []
        
        stats = []
        for color in df["color"].unique():
            subset = df[df["color"] == color]
            
            wins = (subset["result"] == "1-0").sum()
            losses = (subset["result"] == "0-1").sum()
            draws = (subset["result"] == "*").sum()
            total = len(subset)
            
            stats.append({
                "color": color.capitalize(),
                "total_games": total,
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "win_rate": f"{wins/total*100:.1f}%" if total > 0 else "0%",
                "avg_length": f"{subset['moves'].mean():.1f}",
            })
        
        return stats
    
    def _generate_opening_stats(self, df: 'pd.DataFrame') -> List[Dict]:
        """Generate opening-specific statistics."""
        stats = []
        
        for opening in df["opening"].unique()[:20]:  # Top 20 openings
            subset = df[df["opening"] == opening]
            
            wins = (subset["result"] == "1-0").sum()
            losses = (subset["result"] == "0-1").sum()
            draws = (subset["result"] == "*").sum()
            total = len(subset)
            
            stats.append({
                "opening": opening,
                "frequency": total,
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "win_rate": f"{wins/total*100:.1f}%" if total > 0 else "0%",
                "draw_rate": f"{draws/total*100:.1f}%" if total > 0 else "0%",
                "avg_opponent_elo": f"{subset['elo_opp'].mean():.0f}",
            })
        
        return sorted(stats, key=lambda x: x["frequency"], reverse=True)
