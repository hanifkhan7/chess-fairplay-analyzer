"""
Player DNA Analysis: Comprehensive Statistical Opening Repertoire

Creates a detailed statistical profile of how a player actually plays openings
by analyzing game collection to show:
- Opening preferences and move frequencies
- Win rates by opening and variation
- Weak lines and strongest performances
- Favorite vs risky lines
- Complete opening identity profile

Player DNA becomes increasingly accurate with more games:
- 20-50 games: Basic repertoire outline
- 50-200 games: Strong opening profile
- 200+ games: Complete DNA profile
"""

import chess
import chess.pgn
import json
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
from pathlib import Path
import io


class PlayerDNAAnalyzer:
    """Analyze and build player opening DNA profile."""
    
    def __init__(self, min_games: int = 1):
        """
        Initialize analyzer.
        
        Args:
            min_games: Minimum games required to include variation (default 1)
        """
        self.min_games = min_games
        self.opening_tree = {}
        self.opening_stats = defaultdict(lambda: {
            'games': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
        })
        self.move_sequences = []
    
    def analyze_games(self, games: List, player_name: str,
                     color: Optional[str] = None) -> Dict:
        """
        Analyze games to build player DNA.
        
        Args:
            games: List of games - either chess.pgn.Game objects or dicts with 'pgn' key
            player_name: Player username to analyze
            color: 'white', 'black', or None (both)
            
        Returns:
            DNA profile dict with openings and statistics
        """
        player_games_data = []
        
        # Parse all games and filter for player
        for game_item in games:
            try:
                # Handle both chess.pgn.Game objects and dict format
                if isinstance(game_item, dict):
                    pgn_str = game_item.get('pgn', '')
                    if not pgn_str:
                        continue
                    game = chess.pgn.read_game(io.StringIO(pgn_str))
                    if not game:
                        continue
                elif isinstance(game_item, chess.pgn.Game):
                    game = game_item
                else:
                    # Try to handle as string PGN
                    game = chess.pgn.read_game(io.StringIO(str(game_item)))
                    if not game:
                        continue
                
                white = game.headers.get('White', '').strip().lower()
                black = game.headers.get('Black', '').strip().lower()
                player_key = player_name.strip().lower()
                
                # Check if player is in game
                # Use both exact match and 'in' match for flexibility
                player_is_white = (player_key == white) or (player_key in white)
                player_is_black = (player_key == black) or (player_key in black)
                
                if not (player_is_white or player_is_black):
                    continue
                
                # Filter by color if specified
                if color == 'white' and not player_is_white:
                    continue
                elif color == 'black' and not player_is_black:
                    continue
                
                # Get result
                result = game.headers.get('Result', '*')
                white_won = result == '1-0'
                black_won = result == '0-1'
                draw = result == '1/2-1/2'
                
                # Determine if player won
                if player_is_white:
                    player_won = white_won
                    player_draw = draw
                    player_lost = black_won
                else:  # black
                    player_won = black_won
                    player_draw = draw
                    player_lost = white_won
                
                player_games_data.append({
                    'game': game,
                    'is_white': player_is_white,
                    'won': player_won,
                    'draw': player_draw,
                    'lost': player_lost,
                })
            
            except Exception as e:
                continue
        
        if not player_games_data:
            return {
                'players': player_name,
                'color': color or 'all',
                'total_games': 0,
                'openings': {},
                'statistics': {},
                'error': 'No games found for analysis'
            }
        
        # Analyze openings
        self._analyze_openings(player_games_data)
        
        # Generate reports
        dna_profile = {
            'player': player_name,
            'color': color or 'both',
            'total_games': len(player_games_data),
            'openings': self.opening_stats,
            'statistics': self._calculate_statistics(player_games_data),
            'favorite_openings': self._get_favorite_openings(5),
            'weak_lines': self._get_weak_lines(3),
            'surprising_weapons': self._get_risky_openings(3),
        }
        
        return dna_profile
    
    def _analyze_openings(self, player_games: List[Dict]):
        """Extract opening statistics from games."""
        for game_data in player_games:
            game = game_data['game']
            
            # Get opening name
            opening_name = game.headers.get('Opening', 'Unknown Opening')
            opening_eco = game.headers.get('ECO', '')
            
            # Full opening key
            opening_key = opening_name
            
            # Update stats
            self.opening_stats[opening_key]['games'] += 1
            
            if game_data['won']:
                self.opening_stats[opening_key]['wins'] += 1
            elif game_data['draw']:
                self.opening_stats[opening_key]['draws'] += 1
            elif game_data['lost']:
                self.opening_stats[opening_key]['losses'] += 1
    
    def _calculate_statistics(self, player_games: List[Dict]) -> Dict:
        """Calculate overall statistics."""
        wins = sum(1 for g in player_games if g['won'])
        draws = sum(1 for g in player_games if g['draw'])
        losses = sum(1 for g in player_games if g['lost'])
        total = len(player_games)
        
        return {
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'total': total,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'draw_rate': (draws / total * 100) if total > 0 else 0,
            'loss_rate': (losses / total * 100) if total > 0 else 0,
        }
    
    def _get_favorite_openings(self, limit: int = 5) -> List[Dict]:
        """Get most played openings with win rates."""
        openings = []
        
        for opening, stats in self.opening_stats.items():
            if stats['games'] >= self.min_games:
                win_rate = stats['wins'] / stats['games'] * 100 if stats['games'] > 0 else 0
                openings.append({
                    'name': opening,
                    'games': stats['games'],
                    'wins': stats['wins'],
                    'draws': stats['draws'],
                    'losses': stats['losses'],
                    'win_rate': round(win_rate, 1),
                })
        
        # Sort by games played (most played first)
        openings.sort(key=lambda x: x['games'], reverse=True)
        return openings[:limit]
    
    def _get_weak_lines(self, limit: int = 3) -> List[Dict]:
        """Get openings with lowest win rates (played multiple times)."""
        openings = []
        
        for opening, stats in self.opening_stats.items():
            if stats['games'] >= max(2, self.min_games):  # At least 2 games
                win_rate = stats['wins'] / stats['games'] * 100 if stats['games'] > 0 else 0
                openings.append({
                    'name': opening,
                    'games': stats['games'],
                    'win_rate': round(win_rate, 1),
                })
        
        # Sort by win rate (lowest first)
        openings.sort(key=lambda x: x['win_rate'])
        return openings[:limit]
    
    def _get_risky_openings(self, limit: int = 3) -> List[Dict]:
        """Get openings played less frequently but with high win rate (bold choices)."""
        openings = []
        
        for opening, stats in self.opening_stats.items():
            if stats['games'] >= 1:  # At least 1 game
                win_rate = stats['wins'] / stats['games'] * 100 if stats['games'] > 0 else 0
                # Risky = fewer games but high win rate
                if 1 <= stats['games'] <= 5 and win_rate >= 60:
                    openings.append({
                        'name': opening,
                        'games': stats['games'],
                        'wins': stats['wins'],
                        'win_rate': round(win_rate, 1),
                    })
        
        # Sort by win rate (highest first)
        openings.sort(key=lambda x: x['win_rate'], reverse=True)
        return openings[:limit]
    
    def generate_report(self) -> str:
        """Generate text report of DNA analysis."""
        report = []
        report.append("\n" + "="*70)
        report.append("[DNA REPORT] Opening Repertoire Profile")
        report.append("="*70)
        
        if not self.opening_stats:
            report.append("\n✗ No opening data found")
            return "\n".join(report)
        
        report.append(f"\nTotal Openings: {len(self.opening_stats)}")
        
        return "\n".join(report)


class PlayerDNAProfile:
    """
    Wrapper class for player DNA profile data.
    Provides convenient methods for accessing and formatting DNA analysis.
    """
    
    def __init__(self, data: Dict):
        """
        Initialize with DNA data dict.
        
        Args:
            data: DNA analysis dictionary
        """
        self.data = data
    
    def get_tree_report(self, limit: int = 15) -> str:
        """
        Get formatted tree report of opening lines.
        
        Args:
            limit: Maximum openings to show
            
        Returns:
            Formatted report string
        """
        report = []
        report.append(f"\n{'='*70}")
        report.append(f"[OPENING TREE] {self.data.get('player', 'Unknown').upper()}")
        report.append(f"{'='*70}\n")
        
        total = self.data.get('total_games', 0)
        report.append(f"Total Games: {total}")
        report.append(f"Color: {self.data.get('color', 'both').upper()}")
        report.append("")
        
        # Statistics
        stats = self.data.get('statistics', {})
        report.append(f"Record: {stats.get('wins', 0)}W {stats.get('draws', 0)}D {stats.get('losses', 0)}L")
        report.append(f"Win Rate: {stats.get('win_rate', 0):.1f}%")
        report.append("")
        
        # Favorite openings
        report.append("⭐ FAVORITE OPENINGS (Best Performance):")
        favorites = self.data.get('favorite_openings', [])[:limit]
        for i, opening in enumerate(favorites, 1):
            report.append(f"  {i:2d}. {opening['name']:<40} ({opening['games']:3d}G) {opening['win_rate']:5.1f}%")
        
        report.append("")
        
        # Weak lines
        report.append("⚠️  WEAK LINES (Needs Improvement):")
        weak = self.data.get('weak_openings', [])[:limit]
        for i, opening in enumerate(weak, 1):
            report.append(f"  {i:2d}. {opening['name']:<40} ({opening['games']:3d}G) {opening['win_rate']:5.1f}%")
        
        report.append("")
        
        # Risky lines
        report.append("🎲 RISKY LINES (High Variance):")
        risky = self.data.get('risky_openings', [])[:limit]
        for i, opening in enumerate(risky, 1):
            report.append(f"  {i:2d}. {opening['name']:<40} ({opening['games']:3d}G) Draw%: {opening.get('draw_rate', 0):.1f}%")
        
        report.append("")
        report.append("="*70)
        
        return "\n".join(report)
    
    def get_statistics(self) -> Dict:
        """Get player statistics."""
        return self.data.get('statistics', {})
    
    def get_favorite_openings(self, limit: int = 10) -> List[Dict]:
        """Get favorite openings."""
        return self.data.get('favorite_openings', [])[:limit]
    
    def get_weak_openings(self, limit: int = 10) -> List[Dict]:
        """Get weak openings."""
        return self.data.get('weak_openings', [])[:limit]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.data
    
    def save_json(self, output_file: str):
        """Save profile to JSON file."""
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f"<PlayerDNAProfile: {self.data.get('player', 'Unknown')} ({self.data.get('total_games', 0)} games)>"


def build_player_dna(player_name: str, games: List[Dict],
                    color: Optional[str] = None,
                    min_games: int = 1) -> 'PlayerDNAProfile':
    """
    Build comprehensive player DNA from game collection.
    
    Args:
        player_name: Player username
        games: List of game dicts with 'pgn' key
        color: 'white', 'black', or None for both
        min_games: Minimum games to include variation (default 1)
        
    Returns:
        PlayerDNAProfile with opening analysis
        
    Example:
        >>> dna = build_player_dna('hikaru', games, color='white', min_games=2)
        >>> print(dna.data['total_games'])
        >>> print(dna.get_favorite_openings())
    """
    
    if not games:
        empty_data = {
            'player': player_name,
            'color': color or 'both',
            'total_games': 0,
            'error': 'No games provided',
            'statistics': {'wins': 0, 'draws': 0, 'losses': 0, 'win_rate': 0},
            'favorite_openings': [],
            'weak_openings': [],
            'risky_openings': [],
        }
        return PlayerDNAProfile(empty_data)
    
    # Analyze
    analyzer = PlayerDNAAnalyzer(min_games=min_games)
    dna_data = analyzer.analyze_games(games, player_name, color)
    
    # Wrap in profile object
    return PlayerDNAProfile(dna_data)


def generate_player_dna_report(dna: Dict) -> str:
    """
    Generate detailed text report from DNA analysis.
    
    Args:
        dna: DNA dict from build_player_dna()
        
    Returns:
        Formatted text report
    """
    report = []
    report.append("\n" + "="*70)
    report.append(f"[DNA] {dna.get('player', 'Unknown').upper()} - OPENING REPERTOIRE PROFILE")
    report.append("="*70)
    
    if 'error' in dna:
        report.append(f"\n✗ {dna['error']}")
        return "\n".join(report)
    
    # Summary
    stats = dna.get('statistics', {})
    report.append(f"\nColor: {dna.get('color', 'unknown').upper()}")
    report.append(f"Total Games: {dna.get('total_games', 0)}")
    report.append(f"Record: {stats.get('wins', 0)}W {stats.get('draws', 0)}D {stats.get('losses', 0)}L")
    report.append(f"Win Rate: {stats.get('win_rate', 0):.1f}%")
    
    # Favorite openings
    favorites = dna.get('favorite_openings', [])
    if favorites:
        report.append("\n📊 FAVORITE OPENINGS (Most Played)")
        report.append("-" * 70)
        for i, opening in enumerate(favorites, 1):
            report.append(
                f"{i}. {opening['name']:<40} "
                f"{opening['games']}G {opening['win_rate']:.0f}%"
            )
    
    # Weak lines
    weak = dna.get('weak_lines', [])
    if weak:
        report.append("\n⚠️  WEAK LINES (Struggling Against)")
        report.append("-" * 70)
        for i, opening in enumerate(weak, 1):
            report.append(
                f"{i}. {opening['name']:<40} "
                f"{opening['games']}G {opening['win_rate']:.0f}%"
            )
    
    # Risky weapons
    risky = dna.get('surprising_weapons', [])
    if risky:
        report.append("\n⚡ SURPRISING WEAPONS (Bold Choices)")
        report.append("-" * 70)
        for i, opening in enumerate(risky, 1):
            report.append(
                f"{i}. {opening['name']:<40} "
                f"{opening['games']}G {opening['win_rate']:.0f}%"
            )
    
    report.append("\n" + "="*70)
    
    return "\n".join(report)


def generate_player_dna_json(dna: Dict, output_file: str):
    """
    Save DNA analysis to JSON file.
    
    Args:
        dna: DNA dict from build_player_dna()
        output_file: Path to save JSON
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dna, f, indent=2, ensure_ascii=False)


def generate_player_dna_pgn(dna: Dict, player_name: str) -> str:
    """
    Generate annotated PGN comment summarizing player DNA.
    
    Args:
        dna: DNA dict from build_player_dna()
        player_name: Player name
        
    Returns:
        PGN comment string
    """
    lines = []
    lines.append(f"[Event \"Player DNA Analysis: {player_name}\"]")
    lines.append(f"[ECO \"Opening Analysis\"]")
    lines.append(f"[Annotator \"Chess Fairplay Analyzer\"]")
    lines.append("")
    
    stats = dna.get('statistics', {})
    lines.append(f"Record: {stats.get('wins', 0)}W {stats.get('draws', 0)}D {stats.get('losses', 0)}L")
    lines.append(f"Win Rate: {stats.get('win_rate', 0):.1f}%")
    lines.append("")
    
    favorites = dna.get('favorite_openings', [])[:3]
    if favorites:
        lines.append("Favorite Openings:")
        for opening in favorites:
            lines.append(f"  {opening['name']}: {opening['win_rate']:.0f}% ({opening['games']}G)")
    
    return "\n".join(lines)
