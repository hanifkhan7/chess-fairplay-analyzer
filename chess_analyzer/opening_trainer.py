"""
Interactive Opening Repertoire Trainer
Play against a downloaded opening repertoire from any player.

Improvements:
- Move tree caching with FEN-based lookup
- Sorted move recommendations by win rate
- Session statistics and progress tracking
- Position history and variation exploration
"""
import chess
import chess.pgn
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)


class MoveNode:
    """Represents a move in the opening tree with statistics."""
    
    def __init__(self):
        self.count = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
    
    def add_result(self, result: str):
        """Add a game result (1-0, 0-1, or 1/2-1/2)."""
        self.count += 1
        if result == "1-0":
            self.wins += 1
        elif result == "0-1":
            self.losses += 1
        elif result == "1/2-1/2":
            self.draws += 1
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage."""
        return (self.wins / self.count * 100) if self.count > 0 else 0.0
    
    def get_draw_rate(self) -> float:
        """Calculate draw rate percentage."""
        return (self.draws / self.count * 100) if self.count > 0 else 0.0
    
    def get_loss_rate(self) -> float:
        """Calculate loss rate percentage."""
        return (self.losses / self.count * 100) if self.count > 0 else 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'count': self.count,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'win_rate': self.get_win_rate(),
            'draw_rate': self.get_draw_rate(),
            'loss_rate': self.get_loss_rate(),
        }


class OpeningTrainer:
    """Train against a player's opening repertoire."""
    
    def __init__(self, games: List[chess.pgn.Game], opponent_name: str, color: Optional[str] = None):
        """
        Initialize trainer with PGN games.
        
        Args:
            games: List of chess.pgn.Game objects
            opponent_name: Name of player whose repertoire we're learning
            color: 'white', 'black', or None for both
        """
        self.games = games
        self.opponent_name = opponent_name
        self.color = color  # Track which color to filter for opponent
        self.move_tree = self._build_move_tree()
        self.current_position = chess.Board()
        self.game_history = []
        self.stats = self._calculate_stats()
        
        logger.info(f"OpeningTrainer initialized with {len(games)} games, color filter: {color}")
    
    def _build_move_tree(self) -> Dict[str, Dict[str, MoveNode]]:
        """Build a tree of moves from all games using MoveNode objects."""
        tree: Dict[str, Dict[str, MoveNode]] = {}
        
        for game in self.games:
            board = chess.Board()
            
            # Determine opponent's color in this game
            white_name = game.headers.get("White", "").lower()
            black_name = game.headers.get("Black", "").lower()
            opponent_is_white = white_name == self.opponent_name.lower()
            opponent_is_black = black_name == self.opponent_name.lower()
            
            # If neither white nor black is opponent, skip this game
            if not opponent_is_white and not opponent_is_black:
                continue
            
            # Filter by color if specified
            if self.color == 'white' and not opponent_is_white:
                continue
            elif self.color == 'black' and not opponent_is_black:
                continue
            
            # Get game result from opponent's perspective
            result = game.headers.get("Result", "*")
            
            # Convert result if opponent is black
            if opponent_is_black:
                if result == "1-0":
                    result = "0-1"
                elif result == "0-1":
                    result = "1-0"
            
            for move in game.mainline_moves():
                is_white_turn = board.turn
                
                # Determine if it's opponent's move
                is_opponent_move = (is_white_turn and opponent_is_white) or (not is_white_turn and opponent_is_black)
                
                if is_opponent_move:
                    # Track this opponent move
                    fen = board.fen()
                    move_san = board.san(move)
                    
                    if fen not in tree:
                        tree[fen] = {}
                    
                    if move_san not in tree[fen]:
                        tree[fen][move_san] = MoveNode()
                    
                    # Add result to this move
                    tree[fen][move_san].add_result(result)
                
                board.push(move)
        
        return tree
    
    def _calculate_stats(self) -> Dict:
        """Calculate statistics from the game set."""
        stats = {
            'total_games': len(self.games),
            'total_unique_positions': len(self.move_tree),
            'opponent_name': self.opponent_name,
            'color_filter': self.color or 'Both',
            'repertoire_depth': self._calculate_depth(),
            'total_moves': self._count_total_moves(),
            'most_played_opening': self._get_most_played_opening(),
        }
        return stats
    
    def _calculate_depth(self) -> int:
        """Calculate deepest line in repertoire."""
        max_depth = 0
        for game in self.games:
            depth = len(list(game.mainline_moves()))
            max_depth = max(max_depth, depth)
        return max_depth
    
    def _count_total_moves(self) -> int:
        """Count total opponent moves in tree."""
        return sum(len(moves) for moves in self.move_tree.values())
    
    def _get_most_played_opening(self) -> str:
        """Get the most frequently played opening line."""
        # This is a simplified version - just count first move frequency
        first_move_stats = self.move_tree.get(chess.Board().fen(), {})
        if not first_move_stats:
            return "Unknown"
        
        best_move = max(first_move_stats.items(), key=lambda x: x[1].count, default=(None, None))
        return best_move[0] if best_move[0] else "Unknown"
    
    def get_top_moves(self, limit: int = 10) -> List[Tuple[str, MoveNode]]:
        """
        Get top recommended moves from current position.
        
        Sorts by: win rate (highest), then frequency (highest)
        
        Returns:
            List of (move_san, MoveNode) tuples sorted by quality
        """
        fen = self.current_position.fen()
        
        if fen not in self.move_tree:
            return []
        
        moves_data = self.move_tree[fen]
        
        # Sort by win rate (descending), then by frequency (descending)
        sorted_moves = sorted(
            moves_data.items(),
            key=lambda x: (
                -x[1].get_win_rate(),  # Highest win rate first
                -x[1].count,            # Then most frequent
            )
        )
        
        # Return up to limit moves
        return sorted_moves[:limit]
    
    def make_move(self, move_san: str) -> bool:
        """
        Make a move in the game.
        
        Args:
            move_san: Move in SAN notation (e.g., 'e4')
        
        Returns:
            True if move is legal, False otherwise
        """
        try:
            move = self.current_position.parse_san(move_san)
            self.current_position.push(move)
            self.game_history.append(move_san)
            return True
        except:
            return False
    
    def get_position_info(self) -> Dict:
        """Get information about current position."""
        return {
            'fen': self.current_position.fen(),
            'move_number': len(self.game_history) // 2 + 1,
            'is_white_turn': self.current_position.turn,
            'game_history': self.game_history,
            'is_game_over': self.current_position.is_game_over(),
            'outcome': str(self.current_position.outcome()) if self.current_position.is_game_over() else None
        }
    
    def display_board(self) -> str:
        """Get ASCII representation of board."""
        return str(self.current_position)
    
    def undo_move(self) -> bool:
        """Undo last move."""
        if self.game_history:
            self.current_position.pop()
            self.game_history.pop()
            return True
        return False
    
    def reset_game(self):
        """Reset to starting position."""
        self.current_position = chess.Board()
        self.game_history = []
    
    def get_move_statistics(self, move_san: str) -> Dict:
        """Get detailed statistics for a specific move."""
        fen = self.current_position.fen()
        
        if fen not in self.move_tree or move_san not in self.move_tree[fen]:
            return {}
        
        node = self.move_tree[fen][move_san]
        return node.to_dict()
    
    def get_legal_moves(self) -> List[str]:
        """Get all legal moves in current position."""
        return [self.current_position.san(move) for move in self.current_position.legal_moves]
    
    def is_in_repertoire(self) -> bool:
        """Check if current position is in opponent's repertoire."""
        return self.current_position.fen() in self.move_tree
    
    def get_repertoire_coverage(self) -> float:
        """Get percentage of moves in opening tree vs all legal moves at current position."""
        fen = self.current_position.fen()
        if fen not in self.move_tree:
            return 0.0
        
        known_moves = len(self.move_tree[fen])
        legal_moves = len(self.get_legal_moves())
        
        return (known_moves / legal_moves * 100) if legal_moves > 0 else 0.0
    
    def get_position_status(self) -> str:
        """Get a string description of position status in repertoire."""
        fen = self.current_position.fen()
        
        if fen not in self.move_tree:
            return "OUT OF REPERTOIRE"
        
        moves_here = len(self.move_tree[fen])
        coverage = self.get_repertoire_coverage()
        
        if coverage >= 80:
            return f"IN DEEP REPERTOIRE ({moves_here} known moves)"
        elif coverage >= 50:
            return f"IN REPERTOIRE ({moves_here} known moves)"
        else:
            return f"EDGE OF REPERTOIRE ({moves_here} known moves)"
    
    def get_summary(self) -> str:
        """Get summary of trainer."""
        return f"""
╔════════════════════════════════════════════════════════════════╗
║          OPENING TRAINER: {self.opponent_name.upper()}
╚════════════════════════════════════════════════════════════════╝

📊 REPERTOIRE STATISTICS
────────────────────────────────────────────────────────────────
  Games Analyzed:      {self.stats['total_games']}
  Unique Positions:    {self.stats['total_unique_positions']}
  Total Moves:         {self.stats['total_moves']}
  Maximum Depth:       {self.stats['repertoire_depth']} moves
  Color(s):            {self.stats['color_filter']}
  Most Played:         {self.stats['most_played_opening']}
  
🎯 INSTRUCTIONS
────────────────────────────────────────────────────────────────
  1. You play against opponent's documented openings
  2. Type moves in standard notation (e.g., 'e4', 'Nf3')
  3. Or enter a number (1-10) to select from top responses
  4. See win rates & statistics for each move
  5. Commands: 'undo', 'reset', 'quit'
  
💡 TIPS
────────────────────────────────────────────────────────────────
  • Moves are sorted by win rate (highest first)
  • Higher win rate = better performance for opponent
  • Positions marked "OUT OF REPERTOIRE" = no known responses
  • Type '?' to see all legal moves
  
────────────────────────────────────────────────────────────────
"""


class InteractiveTrainer:
    """Interactive chess training interface with advanced statistics."""
    
    def __init__(self, trainer: OpeningTrainer):
        """Initialize interactive trainer."""
        self.trainer = trainer
        self.session_stats = {
            'moves_played': 0,
            'in_repertoire': 0,
            'out_of_repertoire': 0,
            'total_position_value': 0.0,  # Sum of opponent win rates
            'positions_visited': set(),
        }
    
    def display_position(self):
        """Display current board and position info with enhanced stats."""
        print("\n" + "="*70)
        
        # Display board
        board_display = self.trainer.display_board()
        print(board_display)
        
        # Display position info
        info = self.trainer.get_position_info()
        move_num = info['move_number']
        turn = "White" if info['is_white_turn'] else "Black"
        
        print(f"\nMove {move_num} | {turn} to move")
        print(f"Moves: {' '.join(info['game_history']) if info['game_history'] else 'None'}")
        
        # Show position status in repertoire
        status = self.trainer.get_position_status()
        coverage = self.trainer.get_repertoire_coverage()
        print(f"Status: {status} | Coverage: {coverage:.0f}%")
        
        print("="*70)
    
    def display_top_moves(self, limit: int = 10):
        """Display top opponent responses with enhanced statistics."""
        top_moves = self.trainer.get_top_moves(limit)
        
        if not top_moves:
            print("\n⚠️  This position is NOT in opponent's repertoire!")
            print("   Opponent has not played this position before.")
            return False
        
        num_moves = len(top_moves)
        print(f"\n📊 TOP {num_moves} RESPONSES BY {self.trainer.opponent_name.upper()}")
        print("─" * 85)
        print(f"{'#':<3} {'Move':<6} {'Count':<8} {'Win%':<10} {'Draw%':<10} {'Loss%':<10} {'Rating':<8}")
        print("─" * 85)
        
        for i, (move_san, node) in enumerate(top_moves, 1):
            stats = node.to_dict()
            count = stats['count']
            win_rate = stats['win_rate']
            draw_rate = stats['draw_rate']
            loss_rate = stats['loss_rate']
            
            # Simple rating indicator based on win rate
            if win_rate >= 60:
                rating = "⭐⭐⭐"
            elif win_rate >= 50:
                rating = "⭐⭐"
            elif win_rate >= 40:
                rating = "⭐"
            else:
                rating = "•"
            
            print(f"{i:<3} {move_san:<6} {count:<8} {win_rate:>8.1f}% {draw_rate:>9.1f}% {loss_rate:>9.1f}%  {rating:<8}")
            
            # Track position value
            self.session_stats['total_position_value'] += win_rate
        
        print("─" * 85)
        return True
    
    def run_interactive_game(self, max_moves: int = 50):
        """Run interactive training session with improved interface."""
        print(self.trainer.get_summary())
        
        input("Start training session? (y/n): ")
        
        move_count = 0
        while move_count < max_moves and not self.trainer.current_position.is_game_over():
            self.display_position()
            
            # Show top 10 moves from opponent's repertoire
            has_responses = self.display_top_moves(10)
            
            # Get legal moves for fallback
            legal_moves = self.trainer.get_legal_moves()
            
            # Get player input
            print("\n" + "─" * 70)
            move_input = input("Your move (1-10 to select, or move notation, or 'undo'/'reset'/'quit'/'?'): ").strip()
            
            if move_input.lower() == 'quit':
                print("\n✓ Game ended.")
                self._display_session_summary()
                break
            
            if move_input.lower() == '?':
                print(f"Legal moves: {', '.join(legal_moves)}")
                continue
            
            if move_input.lower() == 'undo':
                if self.trainer.undo_move():
                    print("✓ Move undone.")
                    continue
                else:
                    print("❌ No moves to undo.")
                    continue
            
            if move_input.lower() == 'reset':
                self.trainer.reset_game()
                self.session_stats = {
                    'moves_played': 0,
                    'in_repertoire': 0,
                    'out_of_repertoire': 0,
                    'total_position_value': 0.0,
                    'positions_visited': set(),
                }
                print("✓ Game reset.")
                continue
            
            # Determine the move to play
            selected_move = None
            
            # Check if user entered a number to select from top 10
            if move_input.isdigit():
                move_num = int(move_input)
                top_moves = self.trainer.get_top_moves(10)
                if 1 <= move_num <= len(top_moves):
                    selected_move = top_moves[move_num - 1][0]
                else:
                    print(f"❌ Please enter a number between 1 and {len(top_moves)}")
                    continue
            else:
                # User entered a move in notation
                selected_move = move_input
            
            # Validate the move
            move_valid = False
            actual_move = selected_move
            
            # Try direct match first
            if selected_move in legal_moves:
                move_valid = True
                actual_move = selected_move
            else:
                # Try to find a matching move (handle disambiguation)
                for legal in legal_moves:
                    if legal.endswith(selected_move) or legal.rstrip('+#') == selected_move:
                        move_valid = True
                        actual_move = legal
                        break
            
            if not move_valid:
                print(f"❌ Illegal move! Legal moves: {', '.join(legal_moves[:5])}{'...' if len(legal_moves) > 5 else ''}")
                continue
            
            # Make the player's move
            if self.trainer.make_move(actual_move):
                self.session_stats['moves_played'] += 1
                fen = self.trainer.current_position.fen()
                self.session_stats['positions_visited'].add(fen)
                
                # Check if in repertoire
                if self.trainer.is_in_repertoire():
                    self.session_stats['in_repertoire'] += 1
                    print(f"\n✓ Move '{actual_move}' played. IN REPERTOIRE!")
                else:
                    self.session_stats['out_of_repertoire'] += 1
                    print(f"\n✓ Move '{actual_move}' played. OUT OF KNOWN REPERTOIRE.")
            else:
                print(f"❌ Failed to make move.")
                continue
            
            # Let opponent respond with best move from repertoire
            top_moves = self.trainer.get_top_moves(1)
            if top_moves:
                best_move, node = top_moves[0]
                best_win_rate = node.get_win_rate()
                if self.trainer.make_move(best_move):
                    print(f"   {self.trainer.opponent_name} plays: {best_move} (win rate: {best_win_rate:.1f}%)")
                    self.session_stats['moves_played'] += 1
                else:
                    print(f"   Error: Could not make opponent's move.")
                    break
            else:
                # Out of repertoire - offer to continue
                print(f"\n⚠️  Out of repertoire!")
                print(f"   {self.trainer.opponent_name} has not played this position before.")
                print(f"   Continue exploring? (y/n): ", end='')
                if input().strip().lower() != 'y':
                    self._display_session_summary()
                    break
            
            move_count += 1
        
        # Display session summary if game ended normally
        if move_count >= max_moves or self.trainer.current_position.is_game_over():
            self._display_session_summary()
    
    def _display_session_summary(self):
        """Display detailed session statistics."""
        print("\n📊 SESSION SUMMARY")
        print("="*70)
        print(f"Moves Played:              {self.session_stats['moves_played']}")
        print(f"Positions In Repertoire:   {self.session_stats['in_repertoire']}")
        print(f"Positions Out of Rep.:     {self.session_stats['out_of_repertoire']}")
        print(f"Unique Positions Visited:  {len(self.session_stats['positions_visited'])}")
        
        if self.session_stats['moves_played'] > 0:
            coverage = (self.session_stats['in_repertoire'] / self.session_stats['moves_played'] * 100)
            avg_opponent_strength = self.session_stats['total_position_value'] / self.session_stats['in_repertoire'] if self.session_stats['in_repertoire'] > 0 else 0
            
            print(f"Repertoire Coverage:       {coverage:.1f}%")
            print(f"Avg Opponent Strength:     {avg_opponent_strength:.1f}% (win rate)")
            
            # Performance assessment
            print("\n💡 ASSESSMENT:")
            if coverage >= 80:
                print("   ✅ Excellent repertoire understanding!")
            elif coverage >= 60:
                print("   👍 Good repertoire knowledge!")
            elif coverage >= 40:
                print("   📚 Fair knowledge - keep studying!")
            else:
                print("   📖 Need more study of this repertoire.")
        
        print("="*70)
