"""
Opening Move Tree Generator - Builds a trie-based opening move tree from games.

Creates a deterministic tree structure that represents all opening moves played,
with statistics (frequency, win/draw rates) at each position. Can export as PGN
with variations and statistical annotations.

Algorithm:
  1. Parse all games and extract move sequences
  2. Build trie: insert each game's moves, incrementing counts at each node
  3. Track win/draw/loss results at leaf positions
  4. Export as PGN with variations and comments showing statistics
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import chess
import chess.pgn

logger = logging.getLogger(__name__)


@dataclass
class MoveNode:
    """Node in the opening tree representing a chess position."""
    
    move: Optional[str] = None  # SAN notation of the move leading to this position
    uci: Optional[str] = None   # UCI notation of the move
    
    # Statistics
    count: int = 0  # Number of games that reached this position
    wins: int = 0  # Wins from this position (for the first player)
    draws: int = 0  # Draws from this position
    losses: int = 0  # Losses from this position
    
    # Tree structure
    children: Dict[str, 'MoveNode'] = field(default_factory=dict)  # move -> MoveNode
    parent: Optional['MoveNode'] = None
    
    def get_win_rate(self) -> float:
        """Calculate win percentage from this position."""
        if self.count == 0:
            return 0.0
        return (self.wins / self.count) * 100
    
    def get_draw_rate(self) -> float:
        """Calculate draw percentage from this position."""
        if self.count == 0:
            return 0.0
        return (self.draws / self.count) * 100
    
    def to_dict(self) -> Dict:
        """Convert node to dictionary (for stats/display)."""
        return {
            'move': self.move,
            'uci': self.uci,
            'count': self.count,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'win_rate': self.get_win_rate(),
            'draw_rate': self.get_draw_rate(),
            'children_count': len(self.children)
        }


class OpeningTree:
    """Trie-based opening tree for chess positions and moves."""
    
    def __init__(self):
        """Initialize empty opening tree."""
        self.root = MoveNode()
        self.game_count = 0
        self.max_depth = 0
    
    def insert_game(self, game: chess.pgn.Game, perspective: str = 'white') -> None:
        """
        Insert a game's moves into the tree.
        
        Args:
            game: chess.pgn.Game object
            perspective: 'white', 'black', or 'both'
                - 'white': Insert White's view of moves
                - 'black': Insert Black's view of moves (from black perspective)
                - 'both': Insert from white perspective only
        """
        try:
            node = self.root
            board = game.board()
            depth = 0
            
            for move in game.mainline_moves():
                san = board.san(move)
                uci = move.uci()
                
                # Create child node if needed
                if san not in node.children:
                    child = MoveNode(move=san, uci=uci, parent=node)
                    node.children[san] = child
                
                node = node.children[san]
                node.count += 1
                depth += 1
                board.push(move)
            
            # Update result at leaf node
            result = game.headers.get("Result", "*")
            if result == "1-0":
                node.wins += 1
            elif result == "0-1":
                node.losses += 1
            elif result == "1/2-1/2":
                node.draws += 1
            
            # Track tree depth
            self.max_depth = max(self.max_depth, depth)
            self.game_count += 1
            
        except Exception as e:
            logger.warning(f"Error inserting game: {e}")
    
    def insert_games(self, games: List[chess.pgn.Game], perspective: str = 'white') -> None:
        """Insert multiple games into the tree."""
        for game in games:
            self.insert_game(game, perspective)
    
    def get_path_stats(self, path: List[str]) -> Optional[Dict]:
        """
        Get statistics for a specific move path.
        
        Args:
            path: List of moves in SAN notation
            
        Returns:
            Dictionary with stats or None if path not found
        """
        node = self.root
        for move in path:
            if move not in node.children:
                return None
            node = node.children[move]
        
        return node.to_dict()
    
    def get_most_played_line(self, max_moves: int = 20) -> List[str]:
        """
        Get the most frequently played opening line.
        
        Args:
            max_moves: Maximum moves to traverse
            
        Returns:
            List of moves in SAN notation
        """
        line = []
        node = self.root
        
        for _ in range(max_moves):
            if not node.children:
                break
            
            # Find child with most games
            best_child = max(
                node.children.values(),
                key=lambda n: n.count,
                default=None
            )
            
            if best_child is None:
                break
            
            line.append(best_child.move)
            node = best_child
        
        return line
    
    def get_line_stats(self, moves: List[str]) -> Dict:
        """Get aggregated stats for a line of moves."""
        node = self.root
        for move in moves:
            if move not in node.children:
                return {'error': 'Line not found'}
            node = node.children[move]
        
        return node.to_dict()
    
    def export_to_pgn(self, player_name: str = "Player", 
                      include_stats: bool = True) -> str:
        """
        Export the tree as a PGN string with variations.
        
        Args:
            player_name: Name of player (for headers)
            include_stats: Include move counts/win rates in comments
            
        Returns:
            PGN text as string
        """
        game = chess.pgn.Game()
        game.headers["Event"] = f"{player_name} Opening Repertoire"
        game.headers["Site"] = "Opening Tree"
        game.headers["Date"] = "2024.??.??"
        game.headers["White"] = player_name
        game.headers["Black"] = "Opponent"
        game.headers["Result"] = "*"
        
        # Build variation tree
        self._build_pgn_recursive(game, self.root, game)
        
        return str(game)
    
    def _build_pgn_recursive(self, game: chess.pgn.Game, node: MoveNode, 
                             current_node: chess.pgn.GameNode,
                             depth: int = 0, max_depth: int = 50) -> None:
        """
        Recursively build PGN variations from opening tree.
        
        Args:
            game: The base Game object
            node: Current MoveNode in opening tree
            current_node: Current GameNode in PGN
            depth: Current depth (to limit recursion)
            max_depth: Maximum depth to traverse
        """
        if depth >= max_depth or not node.children:
            return
        
        # Sort children by count (most played first)
        sorted_children = sorted(
            node.children.items(),
            key=lambda x: x[1].count,
            reverse=True
        )
        
        for idx, (move_san, child_node) in enumerate(sorted_children):
            try:
                # Try to make the move
                move = current_node.board().parse_san(move_san)
                
                if idx == 0:
                    # First (main) line
                    next_node = current_node.add_main_variation(move)
                else:
                    # Variations (alternatives)
                    next_node = current_node.add_variation(move)
                
                # Add statistics as comment
                if child_node.count > 0:
                    comment_parts = []
                    comment_parts.append(f"{child_node.count} games")
                    comment_parts.append(f"W:{child_node.wins}")
                    comment_parts.append(f"D:{child_node.draws}")
                    comment_parts.append(f"L:{child_node.losses}")
                    comment_parts.append(f"{child_node.get_win_rate():.1f}%")
                    next_node.comment = " | ".join(comment_parts)
                
                # Recurse for deeper lines
                self._build_pgn_recursive(game, child_node, next_node, 
                                         depth + 1, max_depth)
                
            except Exception as e:
                logger.warning(f"Error processing move {move_san}: {e}")
                continue
    
    def save_pgn(self, filename: str, player_name: str = "Player") -> bool:
        """
        Save the opening tree as a PGN file.
        
        Args:
            filename: Path to save PGN file
            player_name: Name to include in PGN headers
            
        Returns:
            True if successful
        """
        try:
            pgn_text = self.export_to_pgn(player_name)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(pgn_text)
            logger.info(f"Opening tree saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving PGN: {e}")
            return False
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the entire tree."""
        return {
            'total_games': self.game_count,
            'max_depth': self.max_depth,
            'unique_positions': self._count_unique_positions(self.root),
            'total_moves': self._count_total_moves(self.root)
        }
    
    def _count_unique_positions(self, node: MoveNode) -> int:
        """Count unique positions in tree."""
        count = 1  # Count current node
        for child in node.children.values():
            count += self._count_unique_positions(child)
        return count
    
    def _count_total_moves(self, node: MoveNode) -> int:
        """Sum of all move counts in tree."""
        total = node.count
        for child in node.children.values():
            total += self._count_total_moves(child)
        return total


def build_opening_tree_from_games(games: List[chess.pgn.Game], 
                                   player_name: str = "Player") -> OpeningTree:
    """
    Convenience function to build opening tree from games list.
    
    Args:
        games: List of chess.pgn.Game objects
        player_name: Name of the player (for stats)
        
    Returns:
        Populated OpeningTree object
    """
    tree = OpeningTree()
    tree.insert_games(games)
    return tree
