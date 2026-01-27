"""
Move Tree Builder
Builds hierarchical opening trees from PGN games with statistics.

Structure:
1.e4 (249 games, 45% W)
├─ 1...c5 (80 games, 48%)
│  ├─ 2.Nf3 (70 games)
│  │  ├─ 2...Nc6 (Sicilian Sveshnikov, 62%)
│  │  └─ 2...d6 (Sicilian Scheveningen, 38%)
└─ 1...e5 (70 games, 52%)
   ├─ 2.Nf3 (50 games)
   └─ 2.Nc3 (20 games)
"""

import chess
import chess.pgn
from typing import Dict, List, Optional, Any
from collections import defaultdict
import json
import logging

from .eco_loader import get_opening_name

logger = logging.getLogger(__name__)


class MoveNode:
    """Single node in the move tree"""
    
    def __init__(self, move: str, fen: str):
        self.move = move
        self.fen = fen
        self.games = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.eco_code: Optional[str] = None
        self.opening_name: Optional[str] = None
        self.children: Dict[str, 'MoveNode'] = {}
    
    def add_result(self, result: str):
        """Add a game result"""
        self.games += 1
        if result == "1-0":
            self.wins += 1
        elif result == "0-1":
            self.losses += 1
        elif result == "1/2-1/2":
            self.draws += 1
    
    def get_win_rate(self) -> float:
        """Get win rate percentage"""
        return (self.wins / self.games * 100) if self.games > 0 else 0.0
    
    def get_draw_rate(self) -> float:
        """Get draw rate percentage"""
        return (self.draws / self.games * 100) if self.games > 0 else 0.0
    
    def get_loss_rate(self) -> float:
        """Get loss rate percentage"""
        return (self.losses / self.games * 100) if self.games > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            'move': self.move,
            'games': self.games,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'win_rate': self.get_win_rate(),
            'draw_rate': self.get_draw_rate(),
            'loss_rate': self.get_loss_rate(),
            'eco': self.eco_code,
            'opening': self.opening_name,
            'children': {move: child.to_dict() for move, child in self.children.items()}
        }


class MoveTreeBuilder:
    """Build opening trees from PGN games"""
    
    def __init__(self, games: List[chess.pgn.Game], opponent_name: str, color: Optional[str] = None):
        """
        Initialize tree builder.
        
        Args:
            games: List of PGN games
            opponent_name: Name of opponent to track
            color: 'white', 'black', or None for both
        """
        self.games = games
        self.opponent_name = opponent_name.lower()
        self.color = color
        self.root = MoveNode("START", chess.Board().fen())
        self._build_tree()
    
    def _build_tree(self):
        """Build the tree from all games"""
        for game in self.games:
            self._add_game_to_tree(game)
    
    def _add_game_to_tree(self, game: chess.pgn.Game):
        """Add a single game to the tree"""
        board = chess.Board()
        
        # Get game info
        white_name = str(game.headers.get("White", "")).lower()
        black_name = str(game.headers.get("Black", "")).lower()
        result = game.headers.get("Result", "*")
        
        # Determine which player is opponent
        opponent_is_white = white_name == self.opponent_name
        opponent_is_black = black_name == self.opponent_name
        
        if not opponent_is_white and not opponent_is_black:
            return
        
        # Filter by color if specified
        if self.color == 'white' and not opponent_is_white:
            return
        elif self.color == 'black' and not opponent_is_black:
            return
        
        # Adjust result for black perspective
        game_result = result
        if opponent_is_black:
            if result == "1-0":
                game_result = "0-1"
            elif result == "0-1":
                game_result = "1-0"
        
        # Walk through the game
        current_node = self.root
        move_count = 0
        
        for move in game.mainline_moves():
            move_san = board.san(move)
            
            # Determine if it's opponent's move (before pushing)
            is_opponent_move = (board.turn and opponent_is_white) or (not board.turn and opponent_is_black)
            
            # Push the move
            board.push(move)
            
            if is_opponent_move:
                # Get position FEN AFTER the move
                next_fen = board.fen()
                
                # Create or get child node
                if move_san not in current_node.children:
                    current_node.children[move_san] = MoveNode(move_san, next_fen)
                
                child = current_node.children[move_san]
                child.add_result(game_result)
                
                # Set ECO on first move from root
                if move_count == 0:
                    eco = str(game.headers.get("ECO", "")).strip()
                    if eco:
                        child.eco_code = eco
                        child.opening_name = get_opening_name(eco)
                
                current_node = child
                move_count += 1
    
    def get_root(self) -> MoveNode:
        """Get root node"""
        return self.root
    
    def get_tree_depth(self) -> int:
        """Get maximum depth of tree"""
        def max_depth(node: MoveNode) -> int:
            if not node.children:
                return 0
            return 1 + max(max_depth(child) for child in node.children.values())
        
        return max_depth(self.root)
    
    def get_total_positions(self) -> int:
        """Get total unique positions"""
        def count_nodes(node: MoveNode) -> int:
            return 1 + sum(count_nodes(child) for child in node.children.values())
        
        return count_nodes(self.root) - 1  # Don't count root
    
    def get_top_moves(self, node: Optional[MoveNode] = None, limit: int = 10) -> List[tuple]:
        """
        Get top moves from a node sorted by win rate.
        
        Args:
            node: Node to get moves from (default: root)
            limit: Max moves to return
            
        Returns:
            List of (move, node) tuples sorted by win rate
        """
        if node is None:
            node = self.root
        
        if not node.children:
            return []
        
        sorted_moves = sorted(
            node.children.items(),
            key=lambda x: (-x[1].get_win_rate(), -x[1].games)
        )
        
        return sorted_moves[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tree to dictionary"""
        return {
            'opponent': self.opponent_name,
            'color_filter': self.color or 'both',
            'depth': self.get_tree_depth(),
            'positions': self.get_total_positions(),
            'games': len(self.games),
            'tree': self.root.to_dict()
        }
    
    def save_json(self, filepath: str):
        """Save tree to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Tree saved to {filepath}")
    
    def get_summary(self) -> str:
        """Get summary of the tree"""
        return f"""
╔═══════════════════════════════════════════╗
║  MOVE TREE SUMMARY: {self.opponent_name.upper():<20} ║
╚═══════════════════════════════════════════╝

Tree Depth:        {self.get_tree_depth()} moves
Unique Positions:  {self.get_total_positions()}
Games Analyzed:    {len(self.games)}
Color Filter:      {self.color.upper() if self.color else 'Both'}

Top Opening Moves:
"""
    
    def display_tree(self, node: Optional[MoveNode] = None, depth: int = 0, prefix: str = "") -> str:
        """
        Get ASCII representation of tree.
        
        Args:
            node: Node to display (default: root)
            depth: Current depth
            prefix: Indentation prefix
            
        Returns:
            ASCII tree string
        """
        if node is None:
            node = self.root
            output = self.get_summary()
        else:
            output = ""
        
        if depth > 0:  # Skip root
            move_str = f"{node.move}"
            if node.eco_code:
                move_str += f" ({node.opening_name or node.eco_code})"
            stats_str = f"{node.games} games, {node.get_win_rate():.0f}% W"
            
            connector = "├─" if node != list(node.children.values())[-1:] else "└─"
            output += f"\n{prefix}{connector} {move_str:<30} {stats_str}"
        
        # Display children
        children = list(node.children.values())
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            extension = "   " if is_last else "│  "
            new_prefix = prefix + extension if depth > 0 else prefix
            
            child_output = self.display_tree(child, depth + 1, new_prefix)
            if output and depth == 0:
                output += child_output
            else:
                output += child_output
        
        return output


# Test function
if __name__ == "__main__":
    print("[TEST] MoveTreeBuilder")
    print("=" * 50)
    
    # Create simple test
    import io
    
    # Create a test PGN
    pgn_text = """[Event "Test"]
[Site "Test"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]
[ECO "C45"]

1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.b4 Bxb4 1-0
"""
    
    pgn_file = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_file)
    
    if game:
        builder = MoveTreeBuilder([game], "Player2")
        print(f"Tree created successfully!")
        print(f"Positions: {builder.get_total_positions()}")
        print(f"Depth: {builder.get_tree_depth()}")
        print("✓ Test passed!")
    else:
        print("✗ Failed to parse PGN")
