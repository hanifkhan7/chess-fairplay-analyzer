"""Build anti-repertoires against specific opponents based on their weaknesses."""

import chess
import chess.pgn
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import re


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
        from chess_analyzer.stockfish_analyzer import StockfishAnalyzer
        
        self.weak_positions = []
        opening_map = self._load_opening_names()
        
        for game_idx, game in enumerate(self.games):
            try:
                print(f"Analyzing game {game_idx + 1}/{len(self.games)}...")
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
                    
                    # Analyze position
                    try:
                        info = StockfishAnalyzer.evaluate_position(board, stockfish_path, depth=20)
                        
                        if info and 'score' in info:
                            eval_score = info['score']
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
                print(f"Error analyzing game {game_idx}: {e}")
                continue
        
        # Sort by eval drop (biggest mistakes first)
        self.weak_positions.sort(key=lambda x: x.eval_drop, reverse=True)
        return self.weak_positions
    
    def _load_opening_names(self) -> Dict[str, str]:
        """Load ECO opening names."""
        try:
            from chess_analyzer.eco_loader import load_eco_codes
            eco_data = load_eco_codes()
            return {eco['code']: eco['name'] for eco in eco_data}
        except:
            return {}
    
    def extract_repertoire_lines(self, stockfish_path: str, depth: int = 20) -> Dict[str, List[str]]:
        """
        Extract main lines and 2-3 variations to play against opponent.
        
        Args:
            stockfish_path: Path to Stockfish
            depth: Analysis depth
            
        Returns:
            Dict of opening -> [main line, variation 1, variation 2, ...]
        """
        from chess_analyzer.stockfish_analyzer import StockfishAnalyzer
        
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
                        info = StockfishAnalyzer.evaluate_position(board, stockfish_path, depth=depth)
                        if info and 'score' in info:
                            move_evals.append((move.uci(), info['score']))
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
                print(f"Error extracting repertoire: {e}")
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
        pgn_lines = []
        
        # Header
        pgn_lines.append('[Event "Anti-Repertoire vs ' + self.opponent_name + '"]')
        pgn_lines.append('[Site "Chess Analyzer"]')
        pgn_lines.append('[Date "' + chess.pgn.headers.PGN_DEFAULT_HEADERS.get('Date', '') + '"]')
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
