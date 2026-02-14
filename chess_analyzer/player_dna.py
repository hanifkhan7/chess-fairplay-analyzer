"""
Player DNA - Opening Tree Intelligence System

Builds a comprehensive statistical opening tree from thousands of games,
showing exactly how a player actually plays openings with move statistics.

Features:
- Downloads large game samples (1000+)
- Merges identical positions
- Calculates win rates per move
- Generates professional PGN files
- Creates opening tree reports
"""

import json
import chess
import chess.pgn
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
from io import StringIO
import os


class PlayerDNABuilder:
    """Build comprehensive opening DNA from player games."""
    
    def __init__(self, username: str):
        """Initialize Player DNA builder."""
        self.username = username
        self.root = TreeNode()
        self.move_stats = defaultdict(lambda: {
            'count': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'avg_opponent_rating': 0,
            'avg_accuracy': 0,
        })
        self.total_games = 0
        self.games_by_opening = defaultdict(int)
        self.opening_stats = {}
    
    def ingest_games(self, games: List[Dict], player_color: str = 'white') -> int:
        """
        Ingest and merge games into the opening tree.
        
        Args:
            games: List of game dicts with 'moves' key
            player_color: 'white', 'black', or 'both'
            
        Returns:
            Number of games processed
        """
        games_processed = 0
        
        for game_idx, game in enumerate(games):
            if 'moves' not in game:
                continue
            
            # Parse game
            board = chess.Board()
            moves = []
            
            for move_san in game.get('moves', []):
                try:
                    move = board.parse_san(move_san)
                    moves.append(move)
                    board.push(move)
                except:
                    break
            
            if not moves:
                continue
            
            # Determine result
            result = game.get('result', '*')
            if result == '1-0':
                white_result = 1
            elif result == '0-1':
                white_result = -1
            else:
                white_result = 0
            
            # Process based on player color
            should_process = False
            if player_color == 'white' or player_color == 'both':
                should_process = True
                player_result = white_result
            elif player_color == 'black' or player_color == 'both':
                should_process = True
                player_result = -white_result
            
            if not should_process:
                continue
            
            # Build game tree
            board = chess.Board()
            position_count = 0
            
            for move in moves:
                position_count += 1
                
                # Stop at depth 25 (captures most opening theory)
                if position_count > 50:
                    break
                
                fen = board.fen()
                move_uci = move.uci()
                
                # Record move statistics
                key = f"{fen}|{move_uci}"
                self.move_stats[key]['count'] += 1
                
                if player_result == 1:
                    self.move_stats[key]['wins'] += 1
                elif player_result == -1:
                    self.move_stats[key]['losses'] += 1
                else:
                    self.move_stats[key]['draws'] += 1
                
                # Add to tree
                self.root.add_move(board, move, player_result)
                
                board.push(move)
                
                # Get opening name
                try:
                    from .eco_loader import eco_tree
                    opening = eco_tree.get_opening(board.fen())
                except:
                    opening = "Unknown"
                
                self.games_by_opening[opening] += 1
            
            games_processed += 1
        
        self.total_games = games_processed
        return games_processed
    
    def get_top_openings(self, limit: int = 20) -> List[Tuple[str, int, float]]:
        """
        Get most-played openings by player.
        
        Returns: List of (opening_name, count, win_rate)
        """
        results = []
        
        for opening, count in sorted(self.games_by_opening.items(), key=lambda x: x[1], reverse=True)[:limit]:
            # Calculate win rate for this opening
            wins = 0
            total = 0
            
            for key, stats in self.move_stats.items():
                if key.startswith("opening:"):
                    continue
                
                total += stats['count']
                wins += stats['wins']
            
            wr = (wins / total * 100) if total > 0 else 0
            results.append((opening, count, wr))
        
        return results
    
    def get_main_line(self, depth: int = 15) -> str:
        """
        Get the main line (most frequently played continuation).
        
        Args:
            depth: How deep to go (moves)
            
        Returns:
            PGN string of main line
        """
        moves = []
        node = self.root
        
        for _ in range(depth):
            if not node.children:
                break
            
            # Find most-played child
            best_child = max(node.children.values(), key=lambda x: x.count)
            if best_child.count < 2:  # Minimum threshold
                break
            
            moves.append(best_child.move)
            node = best_child
        
        # Convert to PGN
        board = chess.Board()
        pgn_moves = []
        move_num = 1
        
        for i, move in enumerate(moves):
            board.push(move)
            
            if i % 2 == 0:
                pgn_moves.append(f"{move_num}. {board.san(move)}")
            else:
                pgn_moves.append(f"{board.san(move)}")
                move_num += 1
        
        return " ".join(pgn_moves)
    
    def generate_pgn_with_stats(self) -> str:
        """
        Generate a professional PGN file with embedded statistics.
        
        Returns:
            PGN string with stats as comments
        """
        pgn_lines = []
        
        # Headers
        pgn_lines.append(f'[Event "Player DNA: {self.username}"]')
        pgn_lines.append(f'[Site "Chess Fairplay Analyzer"]')
        pgn_lines.append(f'[Date "2026.02.14"]')
        pgn_lines.append(f'[White "{self.username}"]')
        pgn_lines.append(f'[Black "Opponents"]')
        pgn_lines.append(f'[Result "*"]')
        pgn_lines.append('')
        
        # Generate main line with stats
        board = chess.Board()
        node = self.root
        move_num = 1
        
        max_depth = 0
        while node.children and max_depth < 40:
            # Find best continuation
            if not node.children:
                break
            
            best_child = max(node.children.values(), key=lambda x: x.count)
            if best_child.count == 0:
                break
            
            move = best_child.move
            board.push(move)
            
            # Calculate stats for this move
            wr = (best_child.wins / best_child.count * 100) if best_child.count > 0 else 0
            dr = (best_child.draws / best_child.count * 100) if best_child.count > 0 else 0
            lr = (best_child.losses / best_child.count * 100) if best_child.count > 0 else 0
            
            # Format: "1. e4 {Played 512 times | 57% W, 15% D, 28% L}"
            if (max_depth + 1) % 2 == 1:
                pgn_lines.append(f"{move_num}. {board.san(move)} {{Played {best_child.count} times | {wr:.0f}% W, {dr:.0f}% D, {lr:.0f}% L}}")
            else:
                pgn_lines.append(f"{board.san(move)} {{Played {best_child.count} times | {wr:.0f}% W, {dr:.0f}% D, {lr:.0f}% L}}")
                move_num += 1
            
            node = best_child
            max_depth += 1
        
        pgn_lines.append('*')
        return '\n'.join(pgn_lines)
    
    def get_tree_report(self, limit: int = 10) -> str:
        """
        Generate a professional tree report.
        
        Returns:
            Formatted text report
        """
        report = []
        report.append("="*70)
        report.append(f"PLAYER DNA REPORT: {self.username.upper()}")
        report.append("="*70)
        report.append(f"\nGames Analyzed: {self.total_games}")
        report.append(f"Total Positions in Tree: {len(self.move_stats)}")
        report.append(f"Unique Openings: {len(self.games_by_opening)}")
        
        # Top openings
        report.append(f"\n{'MOST PLAYED OPENINGS':-^70}")
        top_openings = self.get_top_openings(limit)
        
        for i, (opening, count, wr) in enumerate(top_openings, 1):
            report.append(f"{i:2d}. {opening:40s} {count:3d} games ({wr:.0f}% WR)")
        
        # Main line
        main_line = self.get_main_line(15)
        report.append(f"\n{'MAIN REPERTOIRE LINE':-^70}")
        report.append(main_line)
        
        report.append("\n" + "="*70)
        
        return '\n'.join(report)


class TreeNode:
    """Node in opening tree."""
    
    def __init__(self, move: Optional[chess.Move] = None, fen: Optional[str] = None):
        """Initialize tree node."""
        self.move = move
        self.fen = fen
        self.children = {}  # Map: move.uci() -> TreeNode
        
        # Statistics
        self.count = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
    
    def add_move(self, board: chess.Board, move: chess.Move, result: int) -> 'TreeNode':
        """
        Add a move to the tree and update statistics.
        
        Args:
            board: Current board position (before move)
            move: Move to add
            result: Game result (1=win, 0=draw, -1=loss)
            
        Returns:
            Child node
        """
        move_uci = move.uci()
        
        if move_uci not in self.children:
            board_copy = board.copy()
            board_copy.push(move)
            self.children[move_uci] = TreeNode(move, board_copy.fen())
        
        child = self.children[move_uci]
        child.count += 1
        
        if result == 1:
            child.wins += 1
        elif result == 0:
            child.draws += 1
        else:
            child.losses += 1
        
        return child
    
    def get_stats_text(self) -> str:
        """Get statistics as formatted text."""
        if self.count == 0:
            return ""
        
        wr = self.wins / self.count * 100
        dr = self.draws / self.count * 100
        lr = self.losses / self.count * 100
        
        return f"{self.count}x | {wr:.0f}% W {dr:.0f}% D {lr:.0f}% L"


def build_player_dna(username: str, games: List[Dict], 
                    player_color: str = 'white', 
                    min_games: int = 20) -> Optional[PlayerDNABuilder]:
    """
    Build Player DNA from games.
    
    Args:
        username: Player username
        games: List of game dicts
        player_color: 'white', 'black', or 'both'
        min_games: Minimum games required
        
    Returns:
        PlayerDNABuilder instance or None if insufficient data
    """
    if len(games) < min_games:
        print(f"[ERROR] Need at least {min_games} games (got {len(games)})")
        return None
    
    print(f"[BUILD] Building Player DNA for {username}...")
    builder = PlayerDNABuilder(username)
    processed = builder.ingest_games(games, player_color)
    
    if processed == 0:
        return None
    
    print(f"[OK] Processed {processed} games")
    return builder
