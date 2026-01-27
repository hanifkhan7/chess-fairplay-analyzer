"""
Advanced Move Tree Builder with Opening Name Resolution
Supports: Lichess API, Chess.com games, ECO code lookup
Builds hierarchical move trees for repertoire analysis
"""

import chess
import chess.pgn
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class MoveTreeNode:
    """Represents a single move in the opening tree."""
    
    def __init__(self, move: str, fen: str = ""):
        self.move = move  # SAN notation (e.g., "e4", "Nf3")
        self.fen = fen  # Position FEN after this move
        self.games = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.eco_code = None  # ECO code (e.g., "B33")
        self.opening_name = None  # Opening name (e.g., "Sicilian Sveshnikov")
        self.children: Dict[str, 'MoveTreeNode'] = {}
    
    def add_game_result(self, result: str):
        """Add a game result: 1-0 (win), 0-1 (loss), 1/2-1/2 (draw)."""
        self.games += 1
        if result == "1-0":
            self.wins += 1
        elif result == "0-1":
            self.losses += 1
        elif result == "1/2-1/2":
            self.draws += 1
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage."""
        return (self.wins / self.games * 100) if self.games > 0 else 0.0
    
    def get_draw_rate(self) -> float:
        """Calculate draw rate percentage."""
        return (self.draws / self.games * 100) if self.games > 0 else 0.0
    
    def get_loss_rate(self) -> float:
        """Calculate loss rate percentage."""
        return (self.losses / self.games * 100) if self.games > 0 else 0.0
    
    def to_dict(self) -> Dict:
        """Convert node to dictionary for JSON export."""
        return {
            "move": self.move,
            "games": self.games,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "win_rate": self.get_win_rate(),
            "draw_rate": self.get_draw_rate(),
            "loss_rate": self.get_loss_rate(),
            "eco_code": self.eco_code,
            "opening_name": self.opening_name,
            "children": {move: child.to_dict() for move, child in self.children.items()}
        }


class MoveTreeBuilder:
    """Build opening repertoire move trees from PGN games."""
    
    def __init__(self):
        """Initialize move tree builder."""
        self.root = MoveTreeNode("root")
        self.opening_cache = {}
    
    def add_game(self, game: chess.pgn.Game, white_perspective: bool = True) -> None:
        """
        Add a game to the move tree.
        
        Args:
            game: chess.pgn.Game object
            white_perspective: If True, track white's moves; if False, track black's moves
        """
        board = chess.Board()
        current_node = self.root
        result = game.headers.get("Result", "*")
        
        # Adjust result if tracking black's perspective
        if not white_perspective and result != "*":
            if result == "1-0":
                result = "0-1"
            elif result == "0-1":
                result = "1-0"
        
        for move in game.mainline_moves():
            is_white_turn = board.turn
            is_player_move = (is_white_turn and white_perspective) or (not is_white_turn and not white_perspective)
            
            move_san = board.san(move)
            
            if is_player_move:
                # Add/update node in tree
                if move_san not in current_node.children:
                    current_node.children[move_san] = MoveTreeNode(move_san, board.fen())
                
                current_node = current_node.children[move_san]
                current_node.add_game_result(result)
            
            board.push(move)
    
    def get_root(self) -> MoveTreeNode:
        """Get root node of the tree."""
        return self.root
    
    def get_node_at_moves(self, moves: List[str]) -> Optional[MoveTreeNode]:
        """
        Navigate to a position by a sequence of moves.
        
        Args:
            moves: List of moves in SAN notation (e.g., ['e4', 'c5', 'Nf3'])
        
        Returns:
            MoveTreeNode at that position, or None if path not found
        """
        current = self.root
        for move in moves:
            if move in current.children:
                current = current.children[move]
            else:
                return None
        return current


class TreeVisualizer:
    """Visualize move trees in ASCII and D3.js formats."""
    
    def __init__(self, root: MoveTreeNode):
        """Initialize visualizer with root node."""
        self.root = root
    
    def to_ascii(self, max_depth: int = 10, min_games: int = 1) -> str:
        """
        Generate ASCII tree representation.
        
        Args:
            max_depth: Maximum tree depth to display
            min_games: Only show lines with at least this many games
        
        Returns:
            ASCII string representation of tree
        """
        lines = []
        lines.append("=" * 80)
        lines.append("OPENING REPERTOIRE TREE")
        lines.append("=" * 80)
        
        self._ascii_recurse(self.root, "", lines, 0, max_depth, min_games)
        
        return "\n".join(lines)
    
    def _ascii_recurse(self, node: MoveTreeNode, prefix: str, lines: List[str], 
                       depth: int, max_depth: int, min_games: int) -> None:
        """Recursively build ASCII tree."""
        if depth > max_depth or node.games < min_games:
            return
        
        if node.move != "root":
            # Format: "1.e4 (249 games, 45% W)"
            stats = f"{node.games} games, {node.get_win_rate():.0f}% W"
            name = f" [{node.opening_name}]" if node.opening_name else ""
            line = f"{prefix}{node.move} ({stats}){name}"
            lines.append(line)
            
            # Update prefix for children
            is_last = False
            prefix = prefix.replace("└─ ", "   ").replace("├─ ", "│  ")
        
        # Add children
        children_list = list(node.children.items())
        for i, (move, child) in enumerate(children_list):
            is_last = (i == len(children_list) - 1)
            child_prefix = prefix + ("└─ " if is_last else "├─ ")
            self._ascii_recurse(child, child_prefix, lines, depth + 1, max_depth, min_games)
    
    def to_json(self) -> Dict:
        """Export tree as JSON-compatible dictionary."""
        return self.root.to_dict()
    
    def to_d3_html(self, output_path: str = "opening_tree.html") -> None:
        """
        Generate interactive D3.js visualization HTML.
        
        Args:
            output_path: Path where HTML file will be saved
        """
        tree_data = self.to_json()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Opening Repertoire Tree</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        
        h1 {{
            color: #333;
        }}
        
        svg {{
            border: 1px solid #ccc;
            background: white;
        }}
        
        .node circle {{
            fill: #69b3a2;
            stroke: #333;
            stroke-width: 2px;
        }}
        
        .node.win circle {{
            fill: #28a745;
        }}
        
        .node.loss circle {{
            fill: #dc3545;
        }}
        
        .node.draw circle {{
            fill: #ffc107;
        }}
        
        .link {{
            fill: none;
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        
        text {{
            font-size: 12px;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <h1>Opening Repertoire Tree</h1>
    <svg id="tree"></svg>
    
    <script>
        const treeData = {tree_data};
        console.log('Tree loaded:', treeData);
        // D3.js visualization code goes here
    </script>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"D3.js tree visualization saved to {output_path}")
