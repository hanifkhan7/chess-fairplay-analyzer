"""
PLAYER DNA v2 - COMPLETE INTEGRATION MODULE
============================================

Unified system that combines:
- PlayerDNAv2: Lifetime repertoire framework
- GameAnnotator: Game-level analysis
- RepertoireAnalyzer: Move sequence and transposition analysis
- LiveStatsIntegration: Chess.com and Lichess stats
- PlayingStyleAnalyzer: Style detection and profiling

This is the MASTER module that orchestrates everything for a complete 
opponent analysis system.
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import io

try:
    import chess
    import chess.pgn
except:
    pass

from chess_analyzer.player_dna_v2 import (
    PlayerDNAv2, LiveStatsIntegration, PlayerStyleAnalyzer, 
    OpeningRepetoire
)

from chess_analyzer.game_annotation_analysis import (
    GameAnnotator, RepertoireAnalyzer, MoveTransitionAnalyzer,
    OpeningClassifier
)

logger = logging.getLogger(__name__)


class ComprehensivePlayerProfile:
    """
    Complete opponent profile combining all analysis systems.
    This is what you show to the player for maximum exploitation.
    """
    
    def __init__(self, username: str, fetch_live_stats: bool = True):
        """Initialize complete player profile."""
        self.username = username
        
        # Core systems
        self.dna_v2: Optional[PlayerDNAv2] = None
        self.repertoire_analyzer: Optional[RepertoireAnalyzer] = None
        self.game_annotator: Optional[GameAnnotator] = None
        self.move_analyzer: Optional[MoveTransitionAnalyzer] = None
        
        # Fetched data
        self.live_stats = None
        
        # Derived insights
        self.key_weaknesses: List[Dict] = []
        self.favorite_weapons: List[Dict] = []
        self.unexpected_variations: List[Dict] = []
        self.playing_tendencies: Dict = {}
        self.counter_strategies: List[Dict] = []
        
        # Metadata
        self.analysis_date = datetime.now().isoformat()
        self.total_games_analyzed = 0
        self.total_unique_openings = 0
        
        # Initialize systems
        if fetch_live_stats:
            self.live_stats = LiveStatsIntegration.fetch_chesscom_stats(username)
            if not self.live_stats:
                self.live_stats = LiveStatsIntegration.fetch_lichess_stats(username)
    
    def analyze_complete(self, games: List, color: Optional[str] = None) -> None:
        """
        Complete end-to-end analysis of all games.
        
        Args:
            games: List of chess.pgn.Game objects or PGN strings
            color: 'white', 'black', or None (both)
        """
        logger.info(f"[COMPLETE ANALYSIS] Starting comprehensive analysis for {self.username}")
        
        try:
            # Initialize systems
            self.dna_v2 = PlayerDNAv2(self.username, fetch_live_stats=False)
            if self.live_stats:
                self.dna_v2.player_stats = self.live_stats
            
            self.game_annotator = GameAnnotator(self.username)
            self.repertoire_analyzer = RepertoireAnalyzer(self.username)
            self.move_analyzer = MoveTransitionAnalyzer()
            
            # Run analyses
            logger.info("  [1/3] Analyzing lifetime repertoire...")
            self.dna_v2.analyze_games(games, color)
            
            logger.info("  [2/3] Annotating and analyzing games...")
            self._run_detailed_analysis(games, color)
            
            logger.info("  [3/3] Deriving exploitation strategies...")
            self._derive_strategies()
            
            # Store summary
            self.total_games_analyzed = self.dna_v2.total_games
            self.total_unique_openings = len(self.dna_v2.repertoire)
            
            logger.info(f"✓ Complete analysis done: {self.total_games_analyzed} games, {self.total_unique_openings} openings")
            
        except Exception as e:
            logger.error(f"Error during complete analysis: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_detailed_analysis(self, games: List, color: Optional[str] = None) -> None:
        """Run detailed game-by-game analysis."""
        # Parse games
        parsed_games = self._parse_games(games)
        
        # Determine player's color if not specified
        if not color:
            is_white = self._guess_player_color(parsed_games)
            color_param = 'white' if is_white else 'black'
        else:
            color_param = color
        
        # Run repertoire analyzer
        self.repertoire_analyzer.analyze_games(parsed_games, color_param == 'white')
    
    def _parse_games(self, games: List) -> List:
        """Parse games from various formats."""
        parsed = []
        for game_item in games:
            try:
                if isinstance(game_item, chess.pgn.Game):
                    parsed.append(game_item)
                elif isinstance(game_item, dict):
                    pgn_str = game_item.get('pgn', '')
                    if pgn_str:
                        game = chess.pgn.read_game(io.StringIO(pgn_str))
                        if game:
                            parsed.append(game)
                elif isinstance(game_item, str):
                    game = chess.pgn.read_game(io.StringIO(game_item))
                    if game:
                        parsed.append(game)
            except:
                continue
        return parsed
    
    def _guess_player_color(self, games: List) -> bool:
        """Guess if player usually plays white."""
        if not games:
            return True
        
        player_key = self.username.strip().lower()
        white_count = 0
        
        for game in games[:min(50, len(games))]:
            try:
                white = game.headers.get('White', '').strip().lower()
                black = game.headers.get('Black', '').strip().lower()
                
                is_white = (player_key == white) or (player_key in white)
                if is_white:
                    white_count += 1
            except:
                continue
        
        return white_count > len(games) // 2
    
    def _derive_strategies(self) -> None:
        """Derive exploitation strategies from analysis."""
        # Key weaknesses (lowest win rate openings)
        weak = self.dna_v2.get_weak_lines(5)
        for eco, rep in weak:
            self.key_weaknesses.append({
                'opening': rep.name,
                'eco': eco,
                'win_rate': rep.win_rate,
                'games': rep.total_games,
                'recommendation': f"Opponent struggles in {rep.name} ({rep.win_rate:.1f}% WR)"
            })
        
        # Favorite weapons (highest win rate)
        fav = self.dna_v2.get_best_performances(5)
        for eco, rep in fav:
            self.favorite_weapons.append({
                'opening': rep.name,
                'eco': eco,
                'win_rate': rep.win_rate,
                'games': rep.total_games,
                'note': f"Opponent dominates in {rep.name} ({rep.win_rate:.1f}% WR) - AVOID"
            })
        
        # Unexpected variations (rare but successful)
        top_seq = self.repertoire_analyzer.get_top_sequences(20) if self.repertoire_analyzer else []
        for moves, stats in top_seq:
            if 0 < stats.games <= 3 and stats.win_rate >= 70:  # Rare but successful
                moves_str = " ".join(moves)
                self.unexpected_variations.append({
                    'variation': moves_str,
                    'games': stats.games,
                    'win_rate': stats.win_rate,
                    'note': f"Prepared trap: {moves_str} ({stats.games}G)"
                })
        
        # Playing tendencies
        if self.dna_v2.playing_style:
            self.playing_tendencies = {
                'style': self.dna_v2.playing_style.value,
                'white_preference': self.dna_v2.white_games > self.dna_v2.black_games,
                'opening_variety': len(self.dna_v2.repertoire),
                'avg_games_per_opening': (
                    self.dna_v2.total_games / len(self.dna_v2.repertoire)
                    if self.dna_v2.repertoire else 0
                )
            }
        
        # Counter strategies
        self._generate_counter_strategies()
    
    def _generate_counter_strategies(self) -> None:
        """Generate specific counter-strategies."""
        if not self.key_weaknesses:
            return
        
        for weakness in self.key_weaknesses:
            strategy = {
                'opening': weakness['opening'],
                'eco': weakness['eco'],
                'strategy': f"Play {weakness['opening']} to exploit weakness",
                'preparation_notes': f"Focus on lines where opponent underperforms",
                'expected_win_rate': 100 - weakness['win_rate'],
            }
            self.counter_strategies.append(strategy)
    
    def generate_executive_summary(self) -> str:
        """
        Generate executive summary for quick exploitation.
        Designed to be shown to the player before a game.
        """
        lines = []
        lines.append("\n" + "="*80)
        lines.append("⚔️  OPPONENT PROFILE & EXPLOITATION GUIDE")
        lines.append(f"Target: {self.username.upper()}")
        lines.append("="*80)
        
        # Live stats
        if self.live_stats:
            lines.append(f"\n📊 LIVE STATS:")
            lines.append(f"  Rating: {self.live_stats.get_current_rating()}")
            if self.live_stats.titled:
                lines.append(f"  Title: {self.live_stats.titled}")
            lines.append(f"  Games Played: {self.live_stats.games_played}")
        
        # Analysis summary
        lines.append(f"\n📈 ANALYSIS SUMMARY:")
        lines.append(f"  Games Analyzed: {self.total_games_analyzed}")
        lines.append(f"  Distinct Openings: {self.total_unique_openings}")
        lines.append(f"  Playing Style: {self.playing_tendencies.get('style', 'Unknown')}")
        
        # Key weaknesses to exploit
        lines.append(f"\n🎯 EXPLOITATION TARGETS:")
        if self.key_weaknesses:
            for i, weakness in enumerate(self.key_weaknesses[:3], 1):
                lines.append(f"  {i}. {weakness['opening']}")
                lines.append(f"     └─ Win Rate: {weakness['win_rate']:.1f}% ({weakness['games']} games)")
                lines.append(f"     └─ ACTION: {weakness['recommendation']}")
        else:
            lines.append("  • No clear weaknesses identified")
        
        # Avoid these openings
        lines.append(f"\n⚠️  OPPONENT STRENGTHS (AVOID):")
        if self.favorite_weapons:
            for i, weapon in enumerate(self.favorite_weapons[:3], 1):
                lines.append(f"  {i}. {weapon['opening']}")
                lines.append(f"     └─ Player Win Rate: {weapon['win_rate']:.1f}% ({weapon['games']} games)")
                lines.append(f"     └─ {weapon['note']}")
        else:
            lines.append("  • No standout strengths")
        
        # Prepared traps
        lines.append(f"\n🎲 PREPARED TRAPS & VARIATIONS:")
        if self.unexpected_variations:
            for i, trap in enumerate(self.unexpected_variations[:3], 1):
                lines.append(f"  {i}. {trap['variation'][:50]}")
                lines.append(f"     └─ {trap['note']}")
        else:
            lines.append("  • No notable trap variations")
        
        # Counter strategies
        lines.append(f"\n💡 COUNTER-STRATEGIES:")
        if self.counter_strategies:
            for i, strategy in enumerate(self.counter_strategies[:3], 1):
                lines.append(f"  {i}. PLAY: {strategy['opening']}")
                lines.append(f"     └─ {strategy['strategy']}")
                lines.append(f"     └─ Expected Advantage: +{strategy['expected_win_rate']:.1f}%")
        else:
            lines.append("  • General preparation recommended")
        
        # Final recommendation
        lines.append(f"\n🏆 PRE-GAME CHECKLIST:")
        lines.append(f"  □ Study opponent's {self.key_weaknesses[0]['opening'] if self.key_weaknesses else 'main openings'}")
        lines.append(f"  □ Prepare counter-strategies")
        lines.append(f"  □ Avoid {self.favorite_weapons[0]['opening'] if self.favorite_weapons else 'sharp positions'}")
        lines.append(f"  □ Be ready for {self.playing_tendencies.get('style', 'their style')}")
        
        lines.append("\n" + "="*80)
        lines.append("Good luck! 🎯")
        lines.append("="*80)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export."""
        return {
            'username': self.username,
            'analysis_date': self.analysis_date,
            'total_games_analyzed': self.total_games_analyzed,
            'total_unique_openings': self.total_unique_openings,
            'live_stats': self.live_stats.__dict__ if self.live_stats else None,
            'playing_style': self.playing_tendencies.get('style'),
            'key_weaknesses': self.key_weaknesses,
            'favorite_weapons': self.favorite_weapons,
            'unexpected_variations': self.unexpected_variations,
            'counter_strategies': self.counter_strategies,
            'lifetime_repertoire': (
                self.dna_v2.to_dict() if self.dna_v2 else None
            ),
        }
    
    def export_json(self, output_file: str) -> None:
        """Export complete profile to JSON."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Exported profile to {output_file}")
    
    def save_report(self, output_file: str) -> None:
        """Save executive summary to text file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_executive_summary())
        logger.info(f"✓ Saved report to {output_file}")


# Convenience function
def analyze_player_complete(username: str, games: List, 
                           color: Optional[str] = None,
                           fetch_live_stats: bool = True) -> ComprehensivePlayerProfile:
    """
    Complete end-to-end player analysis.
    
    Args:
        username: Player username
        games: List of games (chess.pgn.Game or PGN strings)
        color: 'white', 'black', or None
        fetch_live_stats: Whether to fetch Chess.com/Lichess stats
        
    Returns:
        ComprehensivePlayerProfile with complete analysis
        
    Example:
        >>> profile = analyze_player_complete('hikaru', games)
        >>> print(profile.generate_executive_summary())
        >>> profile.export_json('hikaru_profile.json')
    """
    profile = ComprehensivePlayerProfile(username, fetch_live_stats=fetch_live_stats)
    profile.analyze_complete(games, color)
    return profile
