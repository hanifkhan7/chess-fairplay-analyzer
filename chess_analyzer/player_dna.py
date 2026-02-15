"""
Player DNA Analysis: Comprehensive Statistical Opening Tree

Creates a detailed statistical profile of how a player actually plays openings
by merging thousands of games into a single tree showing:
- Move frequencies and win rates
- Opening preferences and surprise weapons
- Weak lines and areas for improvement
"""

import chess
import chess.pgn
import json
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path
import io

from .move_tree_builder import MoveTreeBuilder, MoveNode


class PlayerDNABuilder:
    """Build comprehensive player opening profile."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize builder."""
        self.config = config or {}
        self.tree_builder = MoveTreeBuilder(config)
        self.opening_tree = None
        self.move_stats = defaultdict(lambda: {
            'count': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
        })
    
    def build_from_games(self, games: List[Dict], player_name: str, 
                        color: Optional[str] = None, max_depth: int = 15) -> Dict:
        """
        Build player DNA from game collection.
        
        Args:
            games: List of game dicts with 'pgn', 'result', 'headers' keys
            player_name: Player being analyzed
            color: 'white', 'black', or None for both
            max_depth: Maximum move depth to analyze
            
        Returns:
            DNA profile dict with opening tree and statistics
        """
        print(f"Building Player DNA for {player_name}...")
        print(f"Processing {len(games)} games...")
        
        valid_games = []
        
        for i, game_data in enumerate(games):
            try:
                # Parse PGN
                pgn_str = game_data.get('pgn', '')
                if not pgn_str:
                    continue
                
                game = chess.pgn.read_game(io.StringIO(pgn_str))
                if not game is None:
                    valid_games.append(game)
                    
                if (i + 1) % 500 == 0:
                    print(f"  Processed {i + 1} games...")
            except Exception as e:
                continue
        
        print(f"✓ Successfully parsed {len(valid_games)} games")
        
        # Build opening tree
        self._build_opening_tree(valid_games, player_name, color, max_depth)
        
        # Generate statistics
        stats = self._generate_statistics(valid_games, player_name, color)
        
        return {
            'opening_tree': self.opening_tree.to_dict() if self.opening_tree else {},
            'statistics': stats,
            'games_analyzed': len(valid_games),
            'player': player_name,
        }
    
    def _build_opening_tree(self, games: List[chess.pgn.GameNode], 
                           player_name: str, color: Optional[str],
                           max_depth: int):
        """Build opening repertoire tree."""
        board = chess.Board()
        root = MoveNode()
        
        for game in games:
            board.reset()
            current_node = root
            move_count = 0
            
            # Check if player is in this game
            white_name = game.headers.get('White', '').lower()
            black_name = game.headers.get('Black', '').lower()
            player_key = player_name.lower()
            
            player_color = None
            if player_key in white_name:
                player_color = 'white'
            elif player_key in black_name:
                player_color = 'black'
            else:
                continue
            
            # Filter by color if specified
            if color and color.lower() != player_color:
                continue
            
            # Process moves
            is_player_turn_now = (player_color == 'white')
            
            for move in game.mainline_moves():
                if move_count >= max_depth * 2:  # Moves are made by both colors
                    break
                
                move_san = board.san(move)
                
                # Only track player's moves
                if is_player_turn_now:
                    # Get or create child node
                    if move_san not in current_node.children:
                        current_node.children[move_san] = MoveNode(move_san)
                    
                    child = current_node.children[move_san]
                    child.count += 1
                    
                    # Track result outcome for this move
                    result = game.headers.get('Result', '*')
                    if player_color == 'white':
                        if result == '1-0':
                            child.wins += 1
                        elif result == '0-1':
                            child.losses += 1
                        elif result == '1/2-1/2':
                            child.draws += 1
                    else:  # black
                        if result == '0-1':
                            child.wins += 1
                        elif result == '1-0':
                            child.losses += 1
                        elif result == '1/2-1/2':
                            child.draws += 1
                
                board.push(move)
                is_player_turn_now = not is_player_turn_now
                move_count += 1
        
        self.opening_tree = root
    
    def _generate_statistics(self, games: List[chess.pgn.GameNode],
                            player_name: str, color: Optional[str]) -> Dict:
        """Generate opening statistics."""
        stats = {
            'total_games': len(games),
            'by_opening': {},
            'by_result': {'wins': 0, 'draws': 0, 'losses': 0},
            'favorite_openings': [],
            'weak_lines': [],
            'surprising_weapons': [],
        }
        
        opening_stats = defaultdict(lambda: {
            'games': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
        })
        
        for game in games:
            white_name = game.headers.get('White', '').lower()
            black_name = game.headers.get('Black', '').lower()
            player_key = player_name.lower()
            
            if player_key not in white_name and player_key not in black_name:
                continue
            
            player_is_white = player_key in white_name
            
            # Get opening name
            opening = game.headers.get('Opening', 'Unknown')
            
            result = game.headers.get('Result', '*')
            
            opening_stats[opening]['games'] += 1
            
            if player_is_white:
                if result == '1-0':
                    opening_stats[opening]['wins'] += 1
                    stats['by_result']['wins'] += 1
                elif result == '0-1':
                    opening_stats[opening]['losses'] += 1
                    stats['by_result']['losses'] += 1
                elif result == '1/2-1/2':
                    opening_stats[opening]['draws'] += 1
                    stats['by_result']['draws'] += 1
            else:  # black
                if result == '0-1':
                    opening_stats[opening]['wins'] += 1
                    stats['by_result']['wins'] += 1
                elif result == '1-0':
                    opening_stats[opening]['losses'] += 1
                    stats['by_result']['losses'] += 1
                elif result == '1/2-1/2':
                    opening_stats[opening]['draws'] += 1
                    stats['by_result']['draws'] += 1
        
        # Calculate win rates
        for opening, data in opening_stats.items():
            if data['games'] > 0:
                win_rate = data['wins'] / data['games']
                stats['by_opening'][opening] = {
                    'games': data['games'],
                    'win_rate': win_rate,
                    'wins': data['wins'],
                    'draws': data['draws'],
                    'losses': data['losses'],
                }
        
        # Find favorite openings (most games with good win rate)
        sorted_openings = sorted(
            stats['by_opening'].items(),
            key=lambda x: (x[1]['games'], x[1]['win_rate']),
            reverse=True
        )
        
        stats['favorite_openings'] = [
            {
                'name': name,
                'games': data['games'],
                'win_rate': data['win_rate'],
            }
            for name, data in sorted_openings[:5]
        ]
        
        # Find weak lines (high game count but low win rate)
        weak = sorted(
            stats['by_opening'].items(),
            key=lambda x: x[1]['win_rate']
        )
        
        stats['weak_lines'] = [
            {
                'name': name,
                'games': data['games'],
                'win_rate': data['win_rate'],
            }
            for name, data in weak[:3]
            if data['games'] >= 3
        ]
        
        return stats
    
    def generate_pacing_report(self) -> str:
        """Generate player DNA report."""
        if not self.opening_tree:
            return "No opening data available"
        
        report = []
        report.append("=" * 70)
        report.append("PLAYER DNA ANALYSIS - OPENING REPERTOIRE")
        report.append("=" * 70)
        
        report.append("\n📊 OPENING TREE STATISTICS\n")
        
        def print_tree(node: MoveNode, depth: int = 0, prefix: str = ""):
            if depth > 8:  # Limit depth for readability
                return
            
            if depth == 0:
                children = sorted(node.children.items(), 
                                 key=lambda x: x[1].count, 
                                 reverse=True)
            else:
                children = sorted(node.children.items(),
                                 key=lambda x: x[1].count,
                                 reverse=True)[:5]  # Top 5 at each level
            
            for i, (move_san, child) in enumerate(children):
                if child.count > 0:
                    win_rate = (child.wins / child.count * 100) if child.count > 0 else 0
                    line = f"{prefix}{move_san}: {child.count} games ({win_rate:.1f}% WR)"
                    report.append(line)
                    
                    if depth < 3:
                        new_prefix = prefix + "  "
                        print_tree(child, depth + 1, new_prefix)
        
        print_tree(self.opening_tree)
        
        return "\n".join(report)


def build_player_dna(player_name: str, config: Optional[Dict] = None) -> Dict:
    """
    Build comprehensive player opening DNA.
    
    Args:
        player_name: Player username
        config: Configuration dict with API credentials
        
    Returns:
        Player DNA profile dict
    """
    from .dual_fetcher import UnifiedFetcher
    
    config = config or {}
    fetcher = UnifiedFetcher(config)
    
    print(f"\n{'='*70}")
    print(f"[DNA] PLAYER DNA ANALYSIS")
    print(f"Builds comprehensive statistical opening tree from games")
    print(f"{'='*70}\n")
    
    # Get games
    print(f"Fetching games for {player_name}...")
    games = fetcher.get_player_games(player_name, max_games=1000)
    
    if not games:
        print(f"✗ No games found for {player_name}")
        return {}
    
    print(f"✓ Found {len(games)} games")
    
    # Build DNA
    builder = PlayerDNABuilder(config)
    dna = builder.build_from_games(games, player_name)
    
    # Generate report
    print("\n" + builder.generate_pacing_report())
    
    return dna
