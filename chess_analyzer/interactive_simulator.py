"""
Interactive Opponent Simulator: Play against opponent's actual game patterns

This module allows users to play against a real opponent's typical moves
by analyzing their game database and suggesting their most likely responses.

Features:
- Load opponent games
- Build move statistics from games
- Interactive play with live suggestions
- Performance analysis
"""

import chess
import chess.pgn
import io
from typing import List, Dict, Tuple, Optional, Set
from collections import Counter, defaultdict
from pathlib import Path

from .move_tree_builder import MoveTreeBuilder


class OpponentMoveDatabase:
    """Database of opponent's move patterns."""
    
    def __init__(self, games: List[Dict], player_name: str = "Opponent"):
        """
        Initialize opponent database.
        
        Args:
            games: List of game dicts with 'pgn' or 'moves' keys
            player_name: Name of opponent
        """
        self.player_name = player_name
        self.games = games
        self.move_stats = defaultdict(lambda: Counter())  # FEN -> {move: count}
        self.opening_stats = {}  # Opening names and frequencies
        self.game_count = 0
        self.white_games = 0
        self.black_games = 0
        self.white_score = 0  # Wins as white
        self.black_score = 0  # Wins as black
        
        self._build_database()
    
    def _build_database(self):
        """Build move statistics from games."""
        for game in self.games:
            try:
                self._process_game(game)
            except Exception as e:
                print(f"  ⚠ Error processing game: {e}")
                continue
    
    def _process_game(self, game):
        """Extract moves and statistics from a game."""
        # Handle both chess.pgn.Game objects and dicts
        if isinstance(game, dict):
            if 'pgn' in game:
                try:
                    pgn = chess.pgn.read_game(io.StringIO(game['pgn']))
                    if pgn is None:
                        return
                except:
                    return
            else:
                return
        elif isinstance(game, chess.pgn.GameNode):
            pgn = game
        else:
            return
        
        # Determine player color
        white_player = pgn.headers.get('White', '').strip()
        black_player = pgn.headers.get('Black', '').strip()
        
        # Skip if we can't determine player
        if not white_player or not black_player:
            return
        
        is_white = self.player_name.lower() in white_player.lower()
        is_black = self.player_name.lower() in black_player.lower()
        
        if not (is_white or is_black):
            return
        
        # Track color
        if is_white:
            self.white_games += 1
        else:
            self.black_games += 1
        
        self.game_count += 1
        
        # Get result
        result = pgn.headers.get('Result', '*')
        if is_white and result == '1-0':
            self.white_score += 1
        elif is_black and result == '0-1':
            self.black_score += 1
        elif result == '1/2-1/2':
            if is_white:
                self.white_score += 0.5
            else:
                self.black_score += 0.5
        
        # Process moves
        board = pgn.board()
        move_count = 0
        
        for move in pgn.mainline_moves():
            fen = board.fen()
            move_san = board.san(move)
            move_uci = move.uci()
            
            # Record move by opponent
            if (is_white and board.turn == chess.WHITE) or (is_black and board.turn == chess.BLACK):
                self.move_stats[fen][move_uci] += 1
            
            board.push(move)
            move_count += 1
    
    def get_moves_from_position(self, fen: str) -> List[Tuple[str, int, float]]:
        """
        Get opponent's likely moves from a position.
        
        Args:
            fen: FEN string of position
            
        Returns:
            List of (move_uci, count, percentage) sorted by frequency
        """
        if fen not in self.move_stats:
            return []
        
        moves = self.move_stats[fen]
        total = sum(moves.values())
        
        result = [
            (move, count, count / total * 100)
            for move, count in moves.most_common()
        ]
        
        return result
    
    def get_best_move(self, fen: str) -> Optional[str]:
        """Get opponent's most likely move."""
        moves = self.get_moves_from_position(fen)
        return moves[0][0] if moves else None
    
    def get_openings(self) -> Dict[str, int]:
        """Get opening frequencies."""
        openings = Counter()
        
        for game in self.games:
            pgn = None
            
            if isinstance(game, dict) and 'pgn' in game:
                try:
                    pgn = chess.pgn.read_game(io.StringIO(game['pgn']))
                except:
                    pass
            elif isinstance(game, chess.pgn.GameNode):
                pgn = game
            
            if pgn:
                opening = pgn.headers.get('Opening', 'Unknown')
                openings[opening] += 1
        
        return dict(openings.most_common(10))
    
    def summary(self) -> str:
        """Get database summary."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"Opponent: {self.player_name}")
        lines.append(f"{'='*60}")
        lines.append(f"Total games analyzed: {self.game_count}")
        lines.append(f"  White: {self.white_games} ({self.white_score:.1f} points)")
        lines.append(f"  Black: {self.black_games} ({self.black_score:.1f} points)")
        
        if self.game_count > 0:
            total_score = self.white_score + self.black_score
            win_pct = (total_score / self.game_count) * 100
            lines.append(f"Overall: {total_score:.1f}/{self.game_count} ({win_pct:.1f}%)")
        
        lines.append(f"\nFavorite openings:")
        openings = self.get_openings()
        for opening, count in list(openings.items())[:5]:
            lines.append(f"  {opening}: {count} games")
        
        lines.append(f"{'='*60}")
        
        return "\n".join(lines)


class InteractiveSimulator:
    """Interactive play simulator against opponent patterns."""
    
    def __init__(self, games: List[Dict], player_name: str = "Opponent"):
        """
        Initialize simulator.
        
        Args:
            games: List of opponent's games
            player_name: Opponent's username
        """
        self.player_name = player_name
        self.database = OpponentMoveDatabase(games, player_name)
        self.board = chess.Board()
        self.moves_played = []
        self.user_is_white = None
    
    def run_interactive_session(self):
        """Main interactive play loop."""
        print(self.database.summary())
        
        # Ask user color
        while True:
            color = input("\n[INPUT] Play as (white/black): ").strip().lower()
            if color in ['white', 'w']:
                self.user_is_white = True
                break
            elif color in ['black', 'b']:
                self.user_is_white = False
                break
            print("Please enter 'white' or 'black'")
        
        print(f"\n✓ You are playing as {('White' if self.user_is_white else 'Black')}")
        print("Type 'quit' to exit, 'board' to show board, 'stats' for move stats\n")
        
        # Main game loop
        while not self.board.is_game_over():
            self._display_position()
            self._process_move()
        
        self._game_end()
    
    def _display_position(self):
        """Display current board position and opponent suggestions."""
        print(f"\n{self.board}")
        
        # Opponent's turn?
        opponent_turn = (self.board.turn == chess.WHITE) != self.user_is_white
        
        if opponent_turn:
            print(f"\n[DETECT] {self.player_name} is thinking...\n")
            self._show_opponent_options()
        else:
            print(f"\n[INPUT] Your move (e.g., e2e4, Nf3):")
    
    def _show_opponent_options(self):
        """Show opponent's most likely moves."""
        fen = self.board.fen()
        moves = self.database.get_moves_from_position(fen)
        
        if not moves:
            print(f"  [?] No data for this position. Showing all legal moves:\n")
            legal_moves = list(self.board.legal_moves)
            for i, move in enumerate(legal_moves[:5], 1):
                print(f"    {i}. {self.board.san(move)}")
            return
        
        print(f"  Based on {self.database.game_count} games:\n")
        
        for i, (move_uci, count, pct) in enumerate(moves[:5], 1):
            move = chess.Move.from_uci(move_uci)
            san = self.board.san(move)
            bar_length = int(pct / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"    {i}. {san:6} {bar} {pct:5.1f}% ({count} games)")
        
        print()
    
    def _process_move(self):
        """Process a user move or opponent move."""
        opponent_turn = (self.board.turn == chess.WHITE) != self.user_is_white
        
        if opponent_turn:
            # Opponent's turn - make move based on data
            best_move = self.database.get_best_move(self.board.fen())
            
            if best_move:
                move = chess.Move.from_uci(best_move)
                san = self.board.san(move)
                print(f"  → {self.player_name} plays: {san}")
                self.board.push(move)
                self.moves_played.append(move)
            else:
                # No data available, play a random legal move
                import random
                move = random.choice(list(self.board.legal_moves))
                san = self.board.san(move)
                print(f"  → {self.player_name} plays: {san} (no data)")
                self.board.push(move)
                self.moves_played.append(move)
        else:
            # User's turn
            while True:
                try:
                    user_input = input("  Your move: ").strip()
                    
                    # Handle special commands (case-insensitive)
                    cmd = user_input.lower()
                    if cmd == 'quit':
                        print("\nGame ended.")
                        return
                    elif cmd == 'board':
                        print(f"\n{self.board}")
                        continue
                    elif cmd == 'stats':
                        self._show_opponent_stats()
                        continue
                    elif cmd == 'fen':
                        print(f"FEN: {self.board.fen()}")
                        continue
                    
                    # Parse move (try SAN first with original case, then UCI)
                    move = None
                    try:
                        move = self.board.parse_san(user_input)
                    except:
                        try:
                            move = self.board.parse_uci(user_input.lower())
                        except:
                            try:
                                move = self.board.parse_san(user_input.upper())
                            except:
                                move = None
                    
                    if move and move in self.board.legal_moves:
                        san = self.board.san(move)
                        self.board.push(move)
                        self.moves_played.append(move)
                        print(f"  ✓ {san}")
                        break
                    else:
                        legal = ', '.join(self.board.san(m) for m in list(self.board.legal_moves)[:5])
                        print(f"  ✗ Invalid move. Try: {legal}...")
                
                except Exception as e:
                    print(f"  ✗ Error: {e}")
    
    def _show_opponent_stats(self):
        """Show opponent's statistics for current position."""
        fen = self.board.fen()
        moves = self.database.get_moves_from_position(fen)
        
        print(f"\n{'='*50}")
        print(f"Position Statistics for {self.player_name}")
        print(f"{'='*50}")
        
        if not moves:
            print("No data available for this position")
        else:
            print(f"Opponent has reached this position {sum(m[1] for m in moves)} times\n")
            print("Top responses:")
            for i, (move_uci, count, pct) in enumerate(moves[:10], 1):
                move = chess.Move.from_uci(move_uci)
                san = self.board.san(move)
                print(f"  {i:2}. {san:6} {pct:5.1f}% ({count:3} games)")
        
        print(f"{'='*50}\n")
    
    def _game_end(self):
        """Handle game end."""
        print(f"\n{'='*60}")
        print("GAME ENDED")
        print(f"{'='*60}")
        
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            print(f"Checkmate! {winner} wins!")
        elif self.board.is_stalemate():
            print("Stalemate! Draw.")
        elif self.board.is_insufficient_material():
            print("Insufficient material. Draw.")
        elif self.board.is_fivefold_repetition():
            print("Fivefold repetition. Draw.")
        elif self.board.is_seventyfive_move_rule():
            print("75-move rule. Draw.")
        else:
            print(f"Game Over")
        
        print(f"\nMoves played: {len(self.moves_played)}")
        print(f"Final FEN: {self.board.fen()}")
        
        # Ask to save PGN
        save = input("\n[INPUT] Save game as PGN? (y/n): ").strip().lower()
        if save == 'y':
            self._save_pgn()
        
        print(f"{'='*60}\n")
    
    def _save_pgn(self):
        """Save game as PGN."""
        from datetime import datetime
        
        filename = input("Filename (without .pgn): ").strip()
        if not filename:
            filename = f"vs_{self.player_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = Path(filename).with_suffix('.pgn')
        
        # Create game object
        game = chess.pgn.Game()
        game.headers["Event"] = f"Interactive Simulation"
        game.headers["White"] = "You" if self.user_is_white else self.player_name
        game.headers["Black"] = self.player_name if self.user_is_white else "You"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        
        # Add moves
        node = game
        board = chess.Board()
        for move in self.moves_played:
            node = node.add_variation(move)
            board.push(move)
        
        # Save
        try:
            with open(filepath, 'w') as f:
                f.write(str(game))
            print(f"✓ Game saved to {filepath}")
        except Exception as e:
            print(f"✗ Error saving game: {e}")


# Convenience function for menu integration
def start_interactive_session(games: List[Dict], player_name: str = "Opponent"):
    """Start interactive opponent simulator session."""
    if not games:
        print("✗ No games found for opponent")
        return
    
    print(f"\n✓ Loaded {len(games)} games for {player_name}")
    simulator = InteractiveSimulator(games, player_name)
    simulator.run_interactive_session()
