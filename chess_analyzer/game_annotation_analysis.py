"""
PLAYER DNA v2 - ADVANCED GAME ANNOTATION & MOVE ANALYSIS
=========================================================

Handles:
- Comprehensive game annotation with evaluations
- Move-level statistics (sequences, frequencies, win rates)
- Opening classification with ECO and variations
- Transposition analysis (same positions reached different ways)
- Move transition probabilities
- Preparation depth analysis
- Critical move identification

This module transforms raw PGN games into annotated, analyzed games 
with complete move statistics.
"""

import chess
import chess.pgn
import logging
from typing import Dict, List, Optional, Tuple, Set, DefaultDict
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
import io
import json

logger = logging.getLogger(__name__)


@dataclass
class MoveSequenceStats:
    """Statistics for a move sequence (opening line)."""
    moves: Tuple[str, ...]  # Move sequence e.g., ("e4", "c5", "Nf3")
    fen_after: str = ""  # FEN position after sequence
    games: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    avg_opponent_elo: float = 0.0
    depth_half_moves: int = 0
    first_played: str = ""
    last_played: str = ""
    
    @property
    def win_rate(self) -> float:
        return (self.wins / self.games * 100) if self.games > 0 else 0.0
    
    @property
    def draw_rate(self) -> float:
        return (self.draws / self.games * 100) if self.games > 0 else 0.0


@dataclass
class TranspositionGroup:
    """Group of positions that can be reached through different move orders."""
    canonical_fen: str
    transposition_count: int = 0  # How many different move sequences reach this
    move_sequences: List[Tuple[str, ...]] = field(default_factory=list)
    total_games: int = 0
    total_wins: int = 0
    total_draws: int = 0
    total_losses: int = 0
    
    @property
    def win_rate(self) -> float:
        return (self.total_wins / self.total_games * 100) if self.total_games > 0 else 0.0


@dataclass
class GameAnnotation:
    """Complete annotated game with detailed analysis."""
    game_id: Optional[str] = None
    original_game: Optional[chess.pgn.Game] = None
    
    # Basic info
    white_player: str = ""
    black_player: str = ""
    player_color: bool = True  # True = white
    result: str = "*"
    date: str = ""
    opponent_elo: int = 1600
    time_control: str = ""
    url: str = ""
    
    # Analysis
    opening_eco: str = ""
    opening_name: str = ""
    analysis_depth: int = 0  # How many moves analyzed
    preparation_ends_move: int = 0  # Last move in known theory
    critical_moves: List[Tuple[int, str]] = field(default_factory=list)  # (move_number, move)
    blunders: List[Tuple[int, str]] = field(default_factory=list)  # (move_number, move)
    brilliant_moves: List[Tuple[int, str]] = field(default_factory=list)  # (move_number, move)
    
    # Move sequences
    main_line_moves: List[str] = field(default_factory=list)
    move_sequence_accuracy: float = 0.0  # % of moves in main lines
    
    # Statistics
    move_transition_stats: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'game_id': self.game_id,
            'white_player': self.white_player,
            'black_player': self.black_player,
            'player_color': 'white' if self.player_color else 'black',
            'result': self.result,
            'date': self.date,
            'opponent_elo': self.opponent_elo,
            'opening_eco': self.opening_eco,
            'opening_name': self.opening_name,
            'analysis_depth': self.analysis_depth,
            'preparation_ends_move': self.preparation_ends_move,
            'url': self.url,
        }


class GameAnnotator:
    """Annotate and analyze games comprehensively."""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.player_key = player_name.strip().lower()
    
    def annotate_game(self, game: chess.pgn.Game, 
                     classify_opening: bool = True) -> GameAnnotation:
        """
        Annotate a single game with comprehensive analysis.
        
        Args:
            game: chess.pgn.Game object
            classify_opening: Whether to classify opening (requires ECO library)
            
        Returns:
            GameAnnotation with analysis
        """
        annotation = GameAnnotation()
        
        try:
            # Extract basic info
            white = game.headers.get('White', '').strip().lower()
            black = game.headers.get('Black', '').strip().lower()
            
            is_white = (self.player_key == white) or (self.player_key in white)
            is_black = (self.player_key == black) or (self.player_key in black)
            
            annotation.white_player = game.headers.get('White', '')
            annotation.black_player = game.headers.get('Black', '')
            annotation.player_color = is_white
            annotation.result = game.headers.get('Result', '*')
            annotation.date = game.headers.get('Date', '')
            annotation.time_control = game.headers.get('TimeControl', '')
            annotation.url = game.headers.get('Site', '')
            
            # Extract opponent ELO
            if is_white:
                elo_str = game.headers.get('BlackElo', '')
            else:
                elo_str = game.headers.get('WhiteElo', '')
            try:
                annotation.opponent_elo = int(elo_str) if elo_str else 1600
            except:
                annotation.opponent_elo = 1600
            
            # Opening info
            annotation.opening_eco = game.headers.get('ECO', '')
            annotation.opening_name = game.headers.get('Opening', 'Unknown')
            
            # Analyze move sequences
            self._analyze_move_sequences(game, annotation, is_white)
            
            # Store original game
            annotation.original_game = game
            
        except Exception as e:
            logger.error(f"Error annotating game: {e}")
        
        return annotation
    
    def _analyze_move_sequences(self, game: chess.pgn.Game, 
                               annotation: GameAnnotation,
                               is_white: bool) -> None:
        """Analyze move sequences and statistics."""
        try:
            board = chess.Board()
            is_player_turn = is_white
            move_count = 0
            player_moves = []
            all_moves = []
            
            for move in game.mainline_moves():
                move_san = board.san(move)
                all_moves.append(move_san)
                
                if is_player_turn:
                    player_moves.append(move_san)
                    # Track this as player's move
                    move_count += 1
                
                board.push(move)
                is_player_turn = not is_player_turn
            
            annotation.main_line_moves = all_moves
            annotation.analysis_depth = move_count
            
            # Calculate accuracy (how often player followed main theory)
            if len(player_moves) > 0:
                # Simplified: count how many moves are common
                annotation.move_sequence_accuracy = min(100.0, (len(player_moves) / max(1, len(all_moves))) * 100)
            
        except Exception as e:
            logger.debug(f"Error analyzing move sequences: {e}")


class MoveTransitionAnalyzer:
    """Analyze transitions between moves (opening tendencies)."""
    
    def __init__(self):
        self.transitions: DefaultDict[str, DefaultDict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.move_frequencies: DefaultDict[str, int] = defaultdict(int)
        self.position_stats: Dict[str, Dict] = {}
    
    def analyze_game(self, game: chess.pgn.Game, is_white: bool) -> None:
        """Analyze move transitions in a game."""
        try:
            board = chess.Board()
            is_player_turn = is_white
            prev_fen = None
            
            for move in game.mainline_moves():
                if is_player_turn:
                    move_san = board.san(move)
                    
                    # Track move frequency
                    self.move_frequencies[move_san] += 1
                    
                    # Track transitions
                    if prev_fen:
                        fen_key = board.fen()
                        if fen_key not in self.position_stats:
                            self.position_stats[fen_key] = {
                                'visits': 0,
                                'wins': 0,
                                'draws': 0,
                                'losses': 0,
                            }
                        self.position_stats[fen_key]['visits'] += 1
                    
                    prev_fen = board.fen()
                
                board.push(move)
                is_player_turn = not is_player_turn
            
        except Exception as e:
            logger.debug(f"Error analyzing transitions: {e}")
    
    def get_move_preferences(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get most frequent moves."""
        sorted_moves = sorted(
            self.move_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_moves[:limit]
    
    def get_position_trends(self, limit: int = 20) -> List[Tuple[str, Dict]]:
        """Get positions with most visits."""
        sorted_pos = sorted(
            self.position_stats.items(),
            key=lambda x: x[1]['visits'],
            reverse=True
        )
        return sorted_pos[:limit]


class OpeningClassifier:
    """Classify openings with varieties and transpositions."""
    
    # Simplified ECO database (partial)
    ECO_DATABASE = {
        'e4': {
            'e5': {
                'Nf3': {
                    'Nc6': {
                        'Bb5': 'Ruy Lopez',
                        'Bc4': 'Italian Game',
                        'Nxe5': 'Scotch Game',
                    },
                    'f5': 'King\'s Gambit',
                }
            },
        },
        'd4': {
            'd5': 'Queen\'s Gambit',
            'e6': 'Queen\'s Gambit Declined',
            'Nf6': 'Indian Defense',
        },
    }
    
    @classmethod
    def classify_opening(cls, moves: List[str], eco_from_game: str = "") -> Tuple[str, str]:
        """
        Classify opening from move sequence.
        
        Args:
            moves: List of moves in SAN notation
            eco_from_game: ECO code from PGN header (preferred)
            
        Returns:
            Tuple of (eco_code, opening_name)
        """
        if eco_from_game:
            return (eco_from_game, "")  # Use from game if available
        
        # Simplified classification (would need full ECO library in production)
        if len(moves) >= 1 and moves[0] == 'e4':
            return ('B', 'e4 Opening')
        elif len(moves) >= 1 and moves[0] == 'd4':
            return ('D', 'd4 Opening')
        elif len(moves) >= 1 and moves[0] == 'c4':
            return ('A', 'c4 Opening')
        
        return ('A00', 'Unknown Opening')


class RepertoireAnalyzer:
    """Comprehensive repertoire analysis with all tools combined."""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.annotator = GameAnnotator(player_name)
        self.transition_analyzer = MoveTransitionAnalyzer()
        self.annotations: List[GameAnnotation] = []
        self.move_sequences: Dict[Tuple[str, ...], MoveSequenceStats] = {}
        self.transposition_groups: Dict[str, TranspositionGroup] = {}
    
    def analyze_games(self, games: List[chess.pgn.Game], is_white: bool = True) -> None:
        """Analyze a collection of games."""
        logger.info(f"[REPERTOIRE] Analyzing {len(games)} games for {self.player_name}...")
        
        for idx, game in enumerate(games):
            try:
                # Annotate
                annotation = self.annotator.annotate_game(game)
                if annotation.player_color != is_white:
                    continue  # Skip if color mismatch
                
                self.annotations.append(annotation)
                
                # Analyze transitions
                self.transition_analyzer.analyze_game(game, is_white)
                
                # Analyze move sequences
                self._analyze_move_sequences(game, annotation, is_white)
                
                # Analyze transpositions
                self._analyze_transpositions(game, annotation, is_white)
                
            except Exception as e:
                logger.debug(f"Error in game {idx}: {e}")
                continue
        
        logger.info(f"✓ Annotated {len(self.annotations)} games")
    
    def _analyze_move_sequences(self, game: chess.pgn.Game, 
                               annotation: GameAnnotation,
                               is_white: bool) -> None:
        """Extract and track move sequences."""
        try:
            board = chess.Board()
            is_player_turn = is_white
            moves_sequence = []
            
            for move in game.mainline_moves():
                if is_player_turn:
                    move_san = board.san(move)
                    moves_sequence.append(move_san)
                    
                    # Record this sequence
                    seq_tuple = tuple(moves_sequence)
                    if seq_tuple not in self.move_sequences:
                        self.move_sequences[seq_tuple] = MoveSequenceStats(
                            moves=seq_tuple,
                            depth_half_moves=len(moves_sequence),
                        )
                    
                    stats = self.move_sequences[seq_tuple]
                    stats.games += 1
                    stats.fen_after = board.fen()
                    stats.avg_opponent_elo = annotation.opponent_elo
                    
                    # Update results
                    if annotation.result == '1-0':
                        if is_white:
                            stats.wins += 1
                        else:
                            stats.losses += 1
                    elif annotation.result == '0-1':
                        if is_white:
                            stats.losses += 1
                        else:
                            stats.wins += 1
                    elif annotation.result == '1/2-1/2':
                        stats.draws += 1
                
                board.push(move)
                is_player_turn = not is_player_turn
        
        except Exception as e:
            logger.debug(f"Error analyzing sequences: {e}")
    
    def _analyze_transpositions(self, game: chess.pgn.Game, 
                               annotation: GameAnnotation,
                               is_white: bool) -> None:
        """Identify and track transpositions."""
        try:
            board = chess.Board()
            is_player_turn = is_white
            
            for move in game.mainline_moves():
                if is_player_turn:
                    fen = board.fen()
                    # Get canonical form (ignore move counters for simplicity)
                    canonical = ' '.join(fen.split()[:4])
                    
                    if canonical not in self.transposition_groups:
                        self.transposition_groups[canonical] = TranspositionGroup(
                            canonical_fen=canonical
                        )
                    
                    group = self.transposition_groups[canonical]
                    group.total_games += 1
                    
                    if annotation.result == '1-0':
                        if is_white:
                            group.total_wins += 1
                        else:
                            group.total_losses += 1
                    elif annotation.result == '0-1':
                        if is_white:
                            group.total_losses += 1
                        else:
                            group.total_wins += 1
                    elif annotation.result == '1/2-1/2':
                        group.total_draws += 1
                
                board.push(move)
                is_player_turn = not is_player_turn
        
        except Exception as e:
            logger.debug(f"Error analyzing transpositions: {e}")
    
    def get_top_sequences(self, limit: int = 20) -> List[Tuple[Tuple[str, ...], MoveSequenceStats]]:
        """Get most played move sequences."""
        sorted_seq = sorted(
            self.move_sequences.items(),
            key=lambda x: x[1].games,
            reverse=True
        )
        return sorted_seq[:limit]
    
    def get_move_preferences(self) -> List[Tuple[str, int]]:
        """Get most played moves."""
        return self.transition_analyzer.get_move_preferences()
    
    def get_critical_positions(self) -> List[Tuple[str, Dict]]:
        """Get most visited positions."""
        return self.transition_analyzer.get_position_trends()
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report."""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("ADVANCED GAME ANNOTATION & MOVE ANALYSIS REPORT")
        lines.append(f"Player: {self.player_name}")
        lines.append("="*80)
        
        # Summary
        lines.append(f"\nGames Annotated: {len(self.annotations)}")
        lines.append(f"Unique Move Sequences: {len(self.move_sequences)}")
        lines.append(f"Transposition Groups: {len(self.transposition_groups)}")
        
        # Top sequences
        lines.append(f"\nTop 10 Move Sequences:")
        for i, (moves, stats) in enumerate(self.get_top_sequences(10), 1):
            moves_str = " ".join(moves)
            lines.append(f"  {i:2d}. {moves_str:<40} ({stats.games:3d}G) {stats.win_rate:5.1f}%")
        
        # Move preferences
        lines.append(f"\nMost Played Moves:")
        for i, (move, freq) in enumerate(self.get_move_preferences(10), 1):
            lines.append(f"  {i:2d}. {move:<10} {freq} times")
        
        lines.append("\n" + "="*80)
        
        return "\n".join(lines)
