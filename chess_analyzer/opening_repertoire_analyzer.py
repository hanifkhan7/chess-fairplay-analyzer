"""
Opening Repertoire Analyzer - Hybrid System
Combines opening trees with statistical analysis for fair-play research.

Features:
- Move-by-move opening tree with branching diagrams
- Statistical X-Y visual graphs (win rates, performance)
- Export to CSV and PDF reports
"""

import chess.pgn
import pandas as pd
from collections import defaultdict, Counter
from io import StringIO
from typing import Dict, List, Tuple, Set
import json
from datetime import datetime


class OpeningNode:
    """Represents a single move in the opening tree"""
    
    def __init__(self, move: str, fen: str = None):
        self.move = move
        self.fen = fen
        self.frequency = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.avg_game_length = 0
        self.game_lengths = []
        self.children = {}  # move -> OpeningNode
        self.parent = None
    
    def record_game(self, result: str, game_length: int):
        """Record a game result at this node"""
        self.frequency += 1
        self.game_lengths.append(game_length)
        self.avg_game_length = sum(self.game_lengths) / len(self.game_lengths)
        
        if result == 'win':
            self.wins += 1
        elif result == 'loss':
            self.losses += 1
        elif result == 'draw':
            self.draws += 1
    
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.frequency == 0:
            return 0.0
        return (self.wins / self.frequency) * 100
    
    def loss_rate(self) -> float:
        """Calculate loss rate percentage"""
        if self.frequency == 0:
            return 0.0
        return (self.losses / self.frequency) * 100
    
    def draw_rate(self) -> float:
        """Calculate draw rate percentage"""
        if self.frequency == 0:
            return 0.0
        return (self.draws / self.frequency) * 100
    
    def get_visual_representation(self, depth: int = 0, is_last: bool = True) -> str:
        """Generate ASCII tree representation"""
        indent = "    " * depth
        branch = "└── " if is_last else "├── "
        
        # Color code by performance (simplified: uses win rate)
        win_pct = self.win_rate()
        if win_pct >= 60:
            marker = "[GREEN]"  # Favorable
        elif win_pct >= 45:
            marker = "[YELLOW]"  # Neutral
        else:
            marker = "[RED]"  # Unfavorable
        
        result = f"{indent}{branch}{self.move} {marker} ({self.frequency} games, {win_pct:.1f}% wins)\n"
        
        # Add children
        children_list = list(self.children.values())
        for i, child in enumerate(children_list):
            is_last_child = (i == len(children_list) - 1)
            result += child.get_visual_representation(depth + 1, is_last_child)
        
        return result


class OpeningRepertoireAnalyzer:
    """Hybrid Opening Analysis System"""
    
    def __init__(self, games: List[chess.pgn.Game], player_name: str = None):
        """
        Initialize analyzer with games
        
        Args:
            games: List of chess.pgn.Game objects
            player_name: Name of the player being analyzed
        """
        self.games = games
        self.player_name = player_name or "Unknown"
        self.white_tree = None
        self.black_tree = None
        self.opening_stats = {}
        self.filtered_games = []
    
    def filter_games(self, 
                    color: str = "both",
                    min_depth: int = 15,
                    results: List[str] = None) -> List[Tuple]:
        """
        Filter games by criteria
        
        Args:
            color: 'white', 'black', or 'both'
            min_depth: Minimum number of moves
            results: ['wins', 'losses', 'draws'] or None for all
        
        Returns:
            List of (game, player_color, game_result) tuples
        """
        filtered = []
        
        for game in self.games:
            # Get move count
            move_count = len(list(game.mainline_moves()))
            if move_count < min_depth:
                continue
            
            # Determine player's color and result
            white_player = game.headers.get('White', '').lower()
            black_player = game.headers.get('Black', '').lower()
            player_name_lower = self.player_name.lower()
            
            is_white = white_player == player_name_lower
            is_black = black_player == player_name_lower
            
            if not (is_white or is_black):
                continue
            
            # Filter by color
            if color == 'white' and not is_white:
                continue
            elif color == 'black' and not is_black:
                continue
            
            # Determine result
            result_str = game.headers.get('Result', '*')
            if is_white:
                if result_str == '1-0':
                    game_result = 'win'
                elif result_str == '0-1':
                    game_result = 'loss'
                else:
                    game_result = 'draw'
            else:  # is_black
                if result_str == '0-1':
                    game_result = 'win'
                elif result_str == '1-0':
                    game_result = 'loss'
                else:
                    game_result = 'draw'
            
            # Filter by results
            if results and game_result not in results:
                continue
            
            player_color = 'white' if is_white else 'black'
            filtered.append((game, player_color, game_result, move_count))
        
        self.filtered_games = filtered
        return filtered
    
    def extract_eco_and_opening(self, game: chess.pgn.Game) -> Tuple[str, str]:
        """Extract ECO code and opening name from game"""
        eco = game.headers.get('ECO', 'Unknown')
        opening = game.headers.get('Opening', 'Unknown Opening')
        return eco, opening
    
    def build_opening_trees(self, max_depth: int = 15):
        """
        Build separate opening trees for White and Black
        
        Args:
            max_depth: Maximum moves to include in tree
        """
        self.white_tree = OpeningNode("root")
        self.black_tree = OpeningNode("root")
        
        opening_stats = defaultdict(lambda: {
            'frequency': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'games': [],
            'white_stats': {'wins': 0, 'losses': 0, 'draws': 0, 'freq': 0},
            'black_stats': {'wins': 0, 'losses': 0, 'draws': 0, 'freq': 0}
        })
        
        for game, player_color, game_result, move_count in self.filtered_games:
            # Select appropriate tree
            tree = self.white_tree if player_color == 'white' else self.black_tree
            
            # Extract opening info
            eco, opening_name = self.extract_eco_and_opening(game)
            opening_key = f"{eco}: {opening_name}"
            
            # Walk the opening tree
            board = chess.Board()
            current_node = tree
            move_counter = 0
            
            for move in game.mainline_moves():
                if move_counter >= max_depth:
                    break
                
                move_san = board.san(move)
                
                # Create child node if needed
                if move_san not in current_node.children:
                    current_node.children[move_san] = OpeningNode(move_san, board.fen())
                
                current_node = current_node.children[move_san]
                board.push(move)
                move_counter += 1
            
            # Record result at final node
            current_node.record_game(game_result, move_count)
            
            # Update opening statistics
            opening_stats[opening_key]['frequency'] += 1
            opening_stats[opening_key]['games'].append({
                'result': game_result,
                'move_count': move_count,
                'eco': eco
            })
            
            if game_result == 'win':
                opening_stats[opening_key]['wins'] += 1
            elif game_result == 'loss':
                opening_stats[opening_key]['losses'] += 1
            else:
                opening_stats[opening_key]['draws'] += 1
            
            # Color-specific stats
            if player_color == 'white':
                opening_stats[opening_key]['white_stats']['freq'] += 1
                if game_result == 'win':
                    opening_stats[opening_key]['white_stats']['wins'] += 1
                elif game_result == 'loss':
                    opening_stats[opening_key]['white_stats']['losses'] += 1
                else:
                    opening_stats[opening_key]['white_stats']['draws'] += 1
            else:
                opening_stats[opening_key]['black_stats']['freq'] += 1
                if game_result == 'win':
                    opening_stats[opening_key]['black_stats']['wins'] += 1
                elif game_result == 'loss':
                    opening_stats[opening_key]['black_stats']['losses'] += 1
                else:
                    opening_stats[opening_key]['black_stats']['draws'] += 1
        
        self.opening_stats = dict(opening_stats)
    
    def get_opening_summary(self) -> pd.DataFrame:
        """Generate opening statistics as DataFrame"""
        data = []
        
        for opening, stats in self.opening_stats.items():
            total = stats['frequency']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            loss_rate = (stats['losses'] / total * 100) if total > 0 else 0
            draw_rate = (stats['draws'] / total * 100) if total > 0 else 0
            
            data.append({
                'Opening': opening,
                'Frequency': total,
                'Wins': stats['wins'],
                'Losses': stats['losses'],
                'Draws': stats['draws'],
                'Win_Rate_%': round(win_rate, 1),
                'Loss_Rate_%': round(loss_rate, 1),
                'Draw_Rate_%': round(draw_rate, 1),
                'White_Freq': stats['white_stats']['freq'],
                'White_Wins': stats['white_stats']['wins'],
                'Black_Freq': stats['black_stats']['freq'],
                'Black_Wins': stats['black_stats']['wins']
            })
        
        df = pd.DataFrame(data)
        return df.sort_values('Frequency', ascending=False)
    
    def display_tree(self, color: str = 'white', max_display_depth: int = 5):
        """
        Display opening tree as ASCII art
        
        Args:
            color: 'white' or 'black'
            max_display_depth: Maximum depth to display
        """
        tree = self.white_tree if color == 'white' else self.black_tree
        
        print(f"\n{'='*70}")
        print(f"OPENING TREE - {color.upper()} (Max Depth: {max_display_depth})")
        print(f"{'='*70}")
        print(f"Frequency shows how many games reached this position")
        print(f"[GREEN]=Favorable (60%+ wins), [YELLOW]=Neutral, [RED]=Unfavorable\n")
        
        # Recursively display with depth limit
        def print_tree(node, depth=0):
            if depth > max_display_depth:
                return
            if node != tree:  # Skip root
                print(node.get_visual_representation(depth, True).rstrip())
            for child in node.children.values():
                print_tree(child, depth + 1)
        
        print_tree(tree)
    
    def get_statistics_summary(self) -> Dict:
        """Get overall statistics"""
        total_games = len(self.filtered_games)
        if total_games == 0:
            return {}
        
        wins = sum(1 for _, _, result, _ in self.filtered_games if result == 'win')
        losses = sum(1 for _, _, result, _ in self.filtered_games if result == 'loss')
        draws = sum(1 for _, _, result, _ in self.filtered_games if result == 'draw')
        
        return {
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': round(wins / total_games * 100, 1),
            'loss_rate': round(losses / total_games * 100, 1),
            'draw_rate': round(draws / total_games * 100, 1),
            'unique_openings': len(self.opening_stats)
        }
    
    def export_to_csv(self, filename: str) -> bool:
        """Export opening statistics to CSV"""
        try:
            df = self.get_opening_summary()
            df.to_csv(filename, index=False)
            print(f"[OK] Exported to: {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] CSV export failed: {e}")
            return False
    
    def export_to_pdf(self, filename: str) -> bool:
        """Export full report to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.units import inch
            from datetime import datetime
            
            pdf = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30
            )
            story.append(Paragraph("Opening Repertoire Analysis Report", title_style))
            story.append(Spacer(1, 12))
            
            # Metadata
            meta_data = [
                f"Player: {self.player_name}",
                f"Games Analyzed: {len(self.filtered_games)}",
                f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            for line in meta_data:
                story.append(Paragraph(line, styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Statistics Summary
            stats = self.get_statistics_summary()
            if stats:
                story.append(Paragraph("Performance Summary", styles['Heading2']))
                summary_data = [
                    ['Metric', 'Value'],
                    ['Total Games', str(stats['total_games'])],
                    ['Wins', f"{stats['wins']} ({stats['win_rate']}%)"],
                    ['Losses', f"{stats['losses']} ({stats['loss_rate']}%)"],
                    ['Draws', f"{stats['draws']} ({stats['draw_rate']}%)"],
                    ['Unique Openings', str(stats['unique_openings'])]
                ]
                
                summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 20))
            
            # Opening Statistics Table
            story.append(PageBreak())
            story.append(Paragraph("Opening Statistics (Top 10)", styles['Heading2']))
            
            df = self.get_opening_summary().head(10)
            table_data = [['Opening', 'Freq', 'W%', 'L%', 'D%']]
            for _, row in df.iterrows():
                table_data.append([
                    row['Opening'][:40],
                    str(row['Frequency']),
                    str(row['Win_Rate_%']),
                    str(row['Loss_Rate_%']),
                    str(row['Draw_Rate_%'])
                ])
            
            opening_table = Table(table_data, colWidths=[3.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
            opening_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(opening_table)
            
            # Disclaimers
            story.append(Spacer(1, 20))
            disclaimer = (
                "<b>Disclaimer:</b> This report is intended for fair-play research, coaching analysis, and "
                "independent review. The analysis detects patterns but does not constitute accusation or evidence "
                "of wrongdoing."
            )
            story.append(Paragraph(disclaimer, styles['Normal']))
            
            pdf.build(story)
            print(f"[OK] PDF report generated: {filename}")
            return True
        
        except ImportError:
            print("[WARN] reportlab not installed. Install with: pip install reportlab")
            return False
        except Exception as e:
            print(f"[ERROR] PDF export failed: {e}")
            return False


def analyze_opening_repertoire(games: List, player_name: str, 
                               color: str = 'both',
                               min_depth: int = 15,
                               results: List[str] = None) -> OpeningRepertoireAnalyzer:
    """
    Main function to analyze opening repertoire
    
    Args:
        games: List of chess.pgn.Game objects
        player_name: Player username
        color: 'white', 'black', or 'both'
        min_depth: Minimum move count
        results: ['wins', 'losses', 'draws'] or None for all
    
    Returns:
        OpeningRepertoireAnalyzer instance with results
    """
    analyzer = OpeningRepertoireAnalyzer(games, player_name)
    
    # Filter games
    analyzer.filter_games(color=color, min_depth=min_depth, results=results)
    
    if not analyzer.filtered_games:
        print("[WARN] No games matched the filter criteria")
        return analyzer
    
    # Build trees
    analyzer.build_opening_trees()
    
    return analyzer
