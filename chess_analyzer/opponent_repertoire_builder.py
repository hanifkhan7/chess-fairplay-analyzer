"""Build anti-repertoires against specific opponents based on their weaknesses."""

import chess
import chess.pgn
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import re
import subprocess
import os
from datetime import datetime


@dataclass
class WeakPosition:
    """Position where opponent struggled."""
    fen: str
    move: str
    eval_drop: float  # How much eval dropped (positive = opponent got worse)
    game_result: str  # 'loss', 'draw', 'win'
    opening_name: str
    variations: List[str] = None
    
    def __post_init__(self):
        if self.variations is None:
            self.variations = []


class OpponentRepertoireBuilder:
    """Build specialized repertoire against a specific opponent."""
    
    def __init__(self, opponent_name: str, games: List[chess.pgn.Game], 
                 color: str = 'white', loss_filter: Optional[str] = None):
        """
        Initialize opponent repertoire builder.
        
        Args:
            opponent_name: Name of opponent to prepare against
            games: List of PGN games where opponent is the opponent
            color: 'white' or 'black' - what color we played
            loss_filter: 'loss', 'draw', 'win', or None for all
        """
        self.opponent_name = opponent_name.lower()
        self.games = games
        self.color = color
        self.loss_filter = loss_filter
        self.weak_positions: List[WeakPosition] = []
        self.repertoire_lines: Dict[str, List[str]] = defaultdict(list)
        self._filter_games()
        
    def _filter_games(self):
        """Filter games by result type."""
        if self.loss_filter:
            filtered = []
            for game in self.games:
                result = game.headers.get('Result', '*')
                
                # Determine our result from our color
                if self.color.lower() == 'white':
                    our_result = result.split('-')[0] if '-' in result else result
                else:  # black
                    our_result = result.split('-')[1] if '-' in result else result
                
                # Map result to filter
                if self.loss_filter == 'loss' and our_result == '0':
                    filtered.append(game)
                elif self.loss_filter == 'draw' and our_result == '0.5':
                    filtered.append(game)
                elif self.loss_filter == 'win' and our_result == '1':
                    filtered.append(game)
            
            self.games = filtered
    
    def analyze_weak_positions(self, stockfish_path: str) -> List[WeakPosition]:
        """
        Find positions where opponent lost or eval dropped significantly.
        
        Args:
            stockfish_path: Path to Stockfish executable
            
        Returns:
            List of weak positions
        """
        self.weak_positions = []
        
        for game_idx, game in enumerate(self.games):
            try:
                print(f"[ANALYZE] Game {game_idx + 1}/{len(self.games)}...")
                board = chess.Board()
                prev_eval = 0
                
                # Get result for this game
                result = game.headers.get('Result', '*')
                if self.color.lower() == 'white':
                    game_result = 'loss' if result == '0-1' else ('draw' if result == '0.5-0.5' else 'win')
                else:
                    game_result = 'loss' if result == '1-0' else ('draw' if result == '0.5-0.5' else 'win')
                
                # Get opening name
                opening = game.headers.get('Opening', 'Unknown Opening')
                
                move_count = 0
                for move in game.mainline_moves():
                    board.push(move)
                    move_count += 1
                    
                    # Only analyze opponent's moves after opening (move 10+)
                    if move_count < 10:
                        continue
                    
                    # Check if it's opponent's turn
                    is_opponent_move = (board.turn != (self.color.lower() == 'white'))
                    if not is_opponent_move:
                        continue
                    
                    # Analyze position with Stockfish
                    try:
                        eval_score = self._evaluate_position(board, stockfish_path, depth=18)
                        
                        if eval_score is not None:
                            eval_drop = prev_eval - eval_score
                            
                            # If eval dropped by 0.5+ pawns, it's a weak position
                            if eval_drop > 0.5:
                                weak_pos = WeakPosition(
                                    fen=board.fen(),
                                    move=move.uci(),
                                    eval_drop=eval_drop,
                                    game_result=game_result,
                                    opening_name=opening
                                )
                                self.weak_positions.append(weak_pos)
                            
                            prev_eval = eval_score
                    except:
                        pass
                        
            except Exception as e:
                print(f"[WARN] Error analyzing game {game_idx}: {e}")
                continue
        
        # Sort by eval drop (biggest mistakes first)
        self.weak_positions.sort(key=lambda x: x.eval_drop, reverse=True)
        return self.weak_positions
    
    def _evaluate_position(self, board: chess.Board, stockfish_path: str, depth: int = 18) -> Optional[float]:
        """Evaluate position using Stockfish."""
        try:
            # Build command
            cmd = [stockfish_path]
            
            # Send commands to Stockfish
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Setup and analyze
            commands = [
                "setoption name Skill Level value 20",
                "position fen " + board.fen(),
                f"go depth {depth}",
                "quit"
            ]
            
            stdout, _ = process.communicate(input="\n".join(commands), timeout=10)
            
            # Parse output
            for line in stdout.split('\n'):
                if 'score cp' in line:
                    # Format: info depth 20 ... score cp 45 ...
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'cp' and i > 0:
                            try:
                                cp_score = int(parts[i + 1])
                                # Convert centipawns to pawns
                                return cp_score / 100.0
                            except:
                                pass
                elif 'score mate' in line:
                    # Mate score
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'mate' and i > 0:
                            try:
                                mate_in = int(parts[i + 1])
                                # Return high score for mate
                                return 100.0 if mate_in > 0 else -100.0
                            except:
                                pass
            
            return None
        except Exception as e:
            return None
    
    def _load_opening_names(self) -> Dict[str, str]:
        """Load ECO opening names."""
        try:
            from chess_analyzer.eco_loader import load_eco_codes
            eco_data = load_eco_codes()
            return {eco['code']: eco['name'] for eco in eco_data}
        except:
            return {}
    
    def extract_repertoire_lines(self, stockfish_path: str, depth: int = 18) -> Dict[str, List[str]]:
        """
        Extract main lines and 2-3 variations to play against opponent.
        
        Args:
            stockfish_path: Path to Stockfish
            depth: Analysis depth
            
        Returns:
            Dict of opening -> [main line, variation 1, variation 2, ...]
        """
        self.repertoire_lines = defaultdict(list)
        
        for weak_pos in self.weak_positions[:10]:  # Top 10 weak positions
            try:
                board = chess.Board(weak_pos.fen)
                opening = weak_pos.opening_name
                
                # Get recommended moves (best alternatives to opponent's move)
                legal_moves = list(board.legal_moves)
                move_evals = []
                
                for move in legal_moves[:5]:  # Top 5 legal moves
                    board.push(move)
                    try:
                        eval_score = self._evaluate_position(board, stockfish_path, depth=depth)
                        if eval_score is not None:
                            move_evals.append((move.uci(), eval_score))
                    except:
                        pass
                    board.pop()
                
                # Sort by evaluation
                move_evals.sort(key=lambda x: x[1], reverse=True)
                
                # Extract lines
                if move_evals:
                    main_move = move_evals[0][0]
                    variations = [m[0] for m in move_evals[1:3]]  # 2-3 alternatives
                    
                    line = f"{main_move}" + (f" ({', '.join(variations)})" if variations else "")
                    self.repertoire_lines[opening].append(line)
                    
            except Exception as e:
                print(f"[WARN] Error extracting repertoire: {e}")
                continue
        
        return self.repertoire_lines
    
    def generate_pgn(self, output_file: str) -> str:
        """
        Generate PGN file with anti-repertoire lines.
        
        Args:
            output_file: Path to save PGN
            
        Returns:
            Path to created file
        """
        from datetime import datetime
        
        pgn_lines = []
        
        # Header
        pgn_lines.append('[Event "Anti-Repertoire vs ' + self.opponent_name + '"]')
        pgn_lines.append('[Site "Chess Analyzer"]')
        pgn_lines.append('[Date "' + datetime.now().strftime("%Y.%m.%d") + '"]')
        pgn_lines.append('[Round "?"]')
        pgn_lines.append('[White "Preparation"]')
        pgn_lines.append('[Black "' + self.opponent_name + '"]')
        pgn_lines.append('[Result "*"]')
        pgn_lines.append('[TimeControl "-"]')
        
        pgn_lines.append('')
        
        # Add each weak position with recommended lines
        for idx, weak_pos in enumerate(self.weak_positions[:20], 1):
            pgn_lines.append(f'; Weak Position #{idx}')
            pgn_lines.append(f'; Opening: {weak_pos.opening_name}')
            pgn_lines.append(f'; Eval Drop: {weak_pos.eval_drop:.2f} pawns')
            pgn_lines.append(f'; Game Result: {weak_pos.game_result.upper()}')
            pgn_lines.append(f'; Position: {weak_pos.fen}')
            pgn_lines.append('')
            
            # Add repertoire lines for this opening
            opening = weak_pos.opening_name
            if opening in self.repertoire_lines:
                for line in self.repertoire_lines[opening]:
                    pgn_lines.append(f'; Recommended: {line}')
            
            pgn_lines.append('')
        
        # Write to file
        pgn_content = '\n'.join(pgn_lines)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pgn_content)
        
        return output_file
    
    def generate_tree_image(self, output_file: str) -> str:
        """
        Generate visual representation of weak positions as PNG/PDF.
        
        Args:
            output_file: Path to save image (with .png or .pdf extension)
            
        Returns:
            Path to created image file
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        except ImportError:
            print("[WARN] Matplotlib not installed. Skipping image generation.")
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Title
        fig.suptitle(f'Anti-Repertoire: Weak Positions vs {self.opponent_name}', 
                     fontsize=20, fontweight='bold', y=0.98)
        
        # Add weak positions as boxes
        y_pos = 10.5
        for idx, weak_pos in enumerate(self.weak_positions[:15]):  # Top 15 positions
            if y_pos < 0.5:
                break
            
            # Create box for position
            opening = weak_pos.opening_name[:40]
            eval_drop = f"{weak_pos.eval_drop:.2f}"
            result = weak_pos.game_result.upper()
            
            # Color based on result
            color_map = {'LOSS': '#2ecc71', 'DRAW': '#f39c12', 'WIN': '#e74c3c'}
            box_color = color_map.get(result, '#95a5a6')
            
            # Draw box
            box = FancyBboxPatch((0.2, y_pos - 0.6), 9.6, 0.55,
                                boxstyle="round,pad=0.05", 
                                edgecolor='black', facecolor=box_color,
                                alpha=0.3, linewidth=2)
            ax.add_patch(box)
            
            # Add text
            text = f"{idx+1}. {opening} | Eval Drop: +{eval_drop} | Result: {result}"
            ax.text(0.5, y_pos - 0.35, text, fontsize=11, fontweight='bold',
                   verticalalignment='center')
            
            y_pos -= 0.75
        
        # Add legend
        legend_y = 0.3
        ax.text(0.5, legend_y, 'Green: Losses | Orange: Draws | Red: Wins', 
               fontsize=10, style='italic', color='#555')
        
        # Save figure
        try:
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"[SUCCESS] Tree image saved: {output_file}")
            plt.close()
            return output_file
        except Exception as e:
            print(f"[WARN] Could not save image: {e}")
            plt.close()
            return None
