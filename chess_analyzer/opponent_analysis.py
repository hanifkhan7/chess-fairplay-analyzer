"""
Enhanced Opponent Analysis with Multi-Level Insights.

Provides comprehensive opponent profiling including:
- Aggregated metrics across games
- Performance trends over time
- Opening-specific analysis
- Vulnerability detection
- Statistical significance testing
"""

import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class OpeningPerformance:
    """Performance data for a specific opening."""
    opening_name: str
    eco_code: str
    times_played: int
    wins: int
    draws: int
    losses: int
    avg_cpl: float
    avg_accuracy: float
    avg_depth: int
    rating_change: float
    
    @property
    def win_rate(self) -> float:
        """Win rate as percentage."""
        if self.times_played == 0:
            return 0.0
        return (self.wins / self.times_played) * 100
    
    @property
    def draw_rate(self) -> float:
        """Draw rate as percentage."""
        if self.times_played == 0:
            return 0.0
        return (self.draws / self.times_played) * 100
    
    @property
    def loss_rate(self) -> float:
        """Loss rate as percentage."""
        if self.times_played == 0:
            return 0.0
        return (self.losses / self.times_played) * 100
    
    @property
    def is_weak_opening(self) -> bool:
        """Flag if opponent performs poorly in this opening."""
        return self.win_rate < 40 and self.times_played >= 3

@dataclass
class OpponentPhaseAnalysis:
    """Performance breakdown by game phase."""
    opening_accuracy: float
    middlegame_accuracy: float
    endgame_accuracy: float
    opening_avg_cpl: float
    middlegame_avg_cpl: float
    endgame_avg_cpl: float
    opening_error_count: int
    middlegame_error_count: int
    endgame_error_count: int

@dataclass
class OpponentProfile:
    """Comprehensive opponent profile with aggregated metrics."""
    username: str
    games_analyzed: int
    avg_rating: float
    peak_rating: float
    min_rating: float
    current_rating: float
    
    # Overall performance
    total_wins: int
    total_draws: int
    total_losses: int
    avg_cpl: float
    avg_accuracy: float
    accuracy_consistency: float  # Std dev of accuracy
    
    # Opening analysis
    opening_performances: List[OpeningPerformance] = field(default_factory=list)
    weak_openings: List[str] = field(default_factory=list)
    strong_openings: List[str] = field(default_factory=list)
    openings_repertoire_diversity: float = 0.0  # Shannon entropy
    
    # Phase analysis
    phase_analysis: Optional[OpponentPhaseAnalysis] = None
    
    # Trend data
    rating_trend: float = 0.0  # Rating change over time
    performance_trend: float = 0.0  # Accuracy trend
    win_streak_data: Dict[str, Any] = field(default_factory=dict)
    
    # Tendencies
    preferred_color: Optional[str] = None  # 'white', 'black', or None
    time_control_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    vs_rating_bands: Dict[str, Dict[str, float]] = field(default_factory=dict)  # Performance vs opponent ratings
    
    # Anomalies
    sudden_improvement: bool = False
    rating_spike_detected: bool = False
    anomalous_games: List[int] = field(default_factory=list)  # Game indices with unusual performance
    
    @property
    def win_rate(self) -> float:
        """Overall win rate."""
        total = self.total_wins + self.total_draws + self.total_losses
        if total == 0:
            return 0.0
        return (self.total_wins / total) * 100
    
    @property
    def draw_rate(self) -> float:
        """Draw rate."""
        total = self.total_wins + self.total_draws + self.total_losses
        if total == 0:
            return 0.0
        return (self.total_draws / total) * 100
    
    @property
    def loss_rate(self) -> float:
        """Loss rate."""
        total = self.total_wins + self.total_draws + self.total_losses
        if total == 0:
            return 0.0
        return (self.total_losses / total) * 100


class OpponentAnalyzer:
    """Analyze opponent performance patterns across multiple games."""
    
    @staticmethod
    def build_profile(opponent_games: List[Dict[str, Any]], 
                      opponent_name: str) -> OpponentProfile:
        """
        Build comprehensive profile from opponent's games.
        
        Args:
            opponent_games: List of game dicts with keys like 'rating', 'result', 'cpl', etc.
            opponent_name: Opponent's username
            
        Returns:
            OpponentProfile with aggregated metrics
        """
        if not opponent_games:
            return OpponentProfile(username=opponent_name, games_analyzed=0,
                                  avg_rating=0, peak_rating=0, min_rating=0,
                                  current_rating=0, total_wins=0, total_draws=0,
                                  total_losses=0, avg_cpl=0, avg_accuracy=0,
                                  accuracy_consistency=0)
        
        # Extract ratings
        ratings = [g.get('rating', 1500) for g in opponent_games]
        cpls = [g.get('cpl', 50) for g in opponent_games if g.get('cpl') is not None]
        accuracies = [g.get('accuracy', 50) for g in opponent_games if g.get('accuracy') is not None]
        
        # Count results
        wins = sum(1 for g in opponent_games if g.get('result') == 'win')
        draws = sum(1 for g in opponent_games if g.get('result') == 'draw')
        losses = sum(1 for g in opponent_games if g.get('result') == 'loss')
        
        # Calculate statistics
        avg_rating = statistics.mean(ratings) if ratings else 1500
        peak_rating = max(ratings) if ratings else 1500
        min_rating = min(ratings) if ratings else 1500
        current_rating = ratings[-1] if ratings else 1500
        
        avg_cpl = statistics.mean(cpls) if cpls else 50
        avg_accuracy = statistics.mean(accuracies) if accuracies else 50
        
        try:
            accuracy_consistency = statistics.stdev(accuracies) if len(accuracies) > 1 else 0
        except statistics.StatisticsError:
            accuracy_consistency = 0
        
        # Build opening performances
        opening_scores = defaultdict(lambda: {'wins': 0, 'draws': 0, 'losses': 0,
                                             'cpls': [], 'accuracies': [], 'depths': [],
                                             'rating_changes': []})
        
        for game in opponent_games:
            opening_key = game.get('opening', 'Unknown')
            eco = game.get('eco', 'N/A')
            result = game.get('result', 'loss')
            
            key = (opening_key, eco)
            if result == 'win':
                opening_scores[key]['wins'] += 1
            elif result == 'draw':
                opening_scores[key]['draws'] += 1
            else:
                opening_scores[key]['losses'] += 1
            
            if 'cpl' in game:
                opening_scores[key]['cpls'].append(game['cpl'])
            if 'accuracy' in game:
                opening_scores[key]['accuracies'].append(game['accuracy'])
            if 'depth' in game:
                opening_scores[key]['depths'].append(game['depth'])
            if 'rating_change' in game:
                opening_scores[key]['rating_changes'].append(game['rating_change'])
        
        # Create opening performance objects
        opening_perfs = []
        weak_openings = []
        strong_openings = []
        
        for (opening_name, eco), stats in opening_scores.items():
            perf = OpeningPerformance(
                opening_name=opening_name,
                eco_code=eco,
                times_played=stats['wins'] + stats['draws'] + stats['losses'],
                wins=stats['wins'],
                draws=stats['draws'],
                losses=stats['losses'],
                avg_cpl=statistics.mean(stats['cpls']) if stats['cpls'] else 50,
                avg_accuracy=statistics.mean(stats['accuracies']) if stats['accuracies'] else 50,
                avg_depth=int(statistics.mean(stats['depths'])) if stats['depths'] else 20,
                rating_change=statistics.mean(stats['rating_changes']) if stats['rating_changes'] else 0
            )
            opening_perfs.append(perf)
            
            if perf.is_weak_opening:
                weak_openings.append(opening_name)
            elif perf.win_rate > 60 and perf.times_played >= 3:
                strong_openings.append(opening_name)
        
        # Sort by frequency
        opening_perfs.sort(key=lambda x: x.times_played, reverse=True)
        
        # Calculate repertoire diversity (Shannon entropy)
        diversity = OpponentAnalyzer._calculate_repertoire_entropy(opening_perfs)
        
        # Phase analysis
        phase_analysis = OpponentAnalyzer._analyze_by_phase(opponent_games)
        
        # Detect anomalies
        sudden_improvement = OpponentAnalyzer._detect_improvement(accuracies)
        anomalous_games = OpponentAnalyzer._find_anomalous_games(opponent_games, avg_cpl, avg_accuracy)
        
        profile = OpponentProfile(
            username=opponent_name,
            games_analyzed=len(opponent_games),
            avg_rating=avg_rating,
            peak_rating=peak_rating,
            min_rating=min_rating,
            current_rating=current_rating,
            total_wins=wins,
            total_draws=draws,
            total_losses=losses,
            avg_cpl=avg_cpl,
            avg_accuracy=avg_accuracy,
            accuracy_consistency=accuracy_consistency,
            opening_performances=opening_perfs,
            weak_openings=weak_openings[:5],  # Top 5
            strong_openings=strong_openings[:5],  # Top 5
            openings_repertoire_diversity=diversity,
            phase_analysis=phase_analysis,
            sudden_improvement=sudden_improvement,
            anomalous_games=anomalous_games
        )
        
        return profile
    
    @staticmethod
    def _calculate_repertoire_entropy(opening_perfs: List[OpeningPerformance]) -> float:
        """
        Calculate Shannon entropy of opening repertoire.
        Higher = more diverse, Lower = specialist
        
        Range: 0-2.3 (for ~10 opening families)
        """
        if not opening_perfs:
            return 0.0
        
        total_games = sum(op.times_played for op in opening_perfs)
        if total_games == 0:
            return 0.0
        
        entropy = 0.0
        for op in opening_perfs:
            if op.times_played > 0:
                p = op.times_played / total_games
                if p > 0:
                    entropy -= p * (p ** 0.5)  # Weighted by frequency
        
        return min(2.3, entropy)  # Normalize to typical range
    
    @staticmethod
    def _analyze_by_phase(games: List[Dict[str, Any]]) -> OpponentPhaseAnalysis:
        """Analyze performance by game phase."""
        opening_accs = []
        middlegame_accs = []
        endgame_accs = []
        opening_cpls = []
        middlegame_cpls = []
        endgame_cpls = []
        
        for game in games:
            if 'phase_analysis' in game:
                phases = game['phase_analysis']
                if 'opening' in phases:
                    opening_accs.append(phases['opening'].get('accuracy', 50))
                    opening_cpls.append(phases['opening'].get('cpl', 50))
                if 'middlegame' in phases:
                    middlegame_accs.append(phases['middlegame'].get('accuracy', 50))
                    middlegame_cpls.append(phases['middlegame'].get('cpl', 50))
                if 'endgame' in phases:
                    endgame_accs.append(phases['endgame'].get('accuracy', 50))
                    endgame_cpls.append(phases['endgame'].get('cpl', 50))
        
        return OpponentPhaseAnalysis(
            opening_accuracy=statistics.mean(opening_accs) if opening_accs else 50,
            middlegame_accuracy=statistics.mean(middlegame_accs) if middlegame_accs else 50,
            endgame_accuracy=statistics.mean(endgame_accs) if endgame_accs else 50,
            opening_avg_cpl=statistics.mean(opening_cpls) if opening_cpls else 50,
            middlegame_avg_cpl=statistics.mean(middlegame_cpls) if middlegame_cpls else 50,
            endgame_avg_cpl=statistics.mean(endgame_cpls) if endgame_cpls else 50,
            opening_error_count=sum(1 for g in games if g.get('opening_errors', 0) > 0),
            middlegame_error_count=sum(1 for g in games if g.get('middlegame_errors', 0) > 0),
            endgame_error_count=sum(1 for g in games if g.get('endgame_errors', 0) > 0)
        )
    
    @staticmethod
    def _detect_improvement(accuracies: List[float], window_size: int = 10) -> bool:
        """Detect sudden improvement in accuracy."""
        if len(accuracies) < window_size * 2:
            return False
        
        early = statistics.mean(accuracies[:window_size])
        recent = statistics.mean(accuracies[-window_size:])
        
        return recent - early > 15  # 15% improvement threshold
    
    @staticmethod
    def _find_anomalous_games(games: List[Dict[str, Any]], 
                             avg_cpl: float, avg_accuracy: float,
                             threshold: float = 2.0) -> List[int]:
        """Find games with anomalous performance (>2 std dev from mean)."""
        cpls = [g.get('cpl', avg_cpl) for g in games]
        accuracies = [g.get('accuracy', avg_accuracy) for g in games]
        
        if len(cpls) < 3 or len(accuracies) < 3:
            return []
        
        try:
            cpl_std = statistics.stdev(cpls)
            acc_std = statistics.stdev(accuracies)
        except statistics.StatisticsError:
            return []
        
        anomalous = []
        for i, game in enumerate(games):
            cpl = game.get('cpl', avg_cpl)
            acc = game.get('accuracy', avg_accuracy)
            
            cpl_z = abs((cpl - avg_cpl) / cpl_std) if cpl_std > 0 else 0
            acc_z = abs((acc - avg_accuracy) / acc_std) if acc_std > 0 else 0
            
            if cpl_z > threshold or acc_z > threshold:
                anomalous.append(i)
        
        return anomalous[:20]  # Top 20 most anomalous
    
    @staticmethod
    def get_vulnerability_summary(profile: OpponentProfile) -> Dict[str, Any]:
        """
        Summarize opponent vulnerabilities for tactical exploitation.
        
        Returns dict with:
        - weak_openings: Openings where opponent scores poorly
        - weak_phases: Which game phases opponent struggles
        - performance_gaps: Variation in performance levels
        - rating_depletion: Performance drop against stronger opponents
        """
        weaknesses = {
            'weak_openings': [
                {
                    'name': op.opening_name,
                    'win_rate': op.win_rate,
                    'times_played': op.times_played,
                    'avg_cpl': op.avg_cpl
                }
                for op in profile.opening_performances
                if op.is_weak_opening
            ][:5],
            'weak_phases': {},
            'performance_gaps': 0.0,
            'rating_depletion': False
        }
        
        # Phase weaknesses
        if profile.phase_analysis:
            phase_accs = [
                profile.phase_analysis.opening_accuracy,
                profile.phase_analysis.middlegame_accuracy,
                profile.phase_analysis.endgame_accuracy
            ]
            if phase_accs:
                avg_phase_acc = statistics.mean(phase_accs)
                weaknesses['weak_phases'] = {
                    'opening': profile.phase_analysis.opening_accuracy if profile.phase_analysis.opening_accuracy < avg_phase_acc else None,
                    'middlegame': profile.phase_analysis.middlegame_accuracy if profile.phase_analysis.middlegame_accuracy < avg_phase_acc else None,
                    'endgame': profile.phase_analysis.endgame_accuracy if profile.phase_analysis.endgame_accuracy < avg_phase_acc else None
                }
                weaknesses['weak_phases'] = {k: v for k, v in weaknesses['weak_phases'].items() if v is not None}
                
                # Calculate performance gap
                weaknesses['performance_gaps'] = max(phase_accs) - min(phase_accs)
        
        # Rating sensitivity
        if profile.vs_rating_bands:
            for rating_band, stats in profile.vs_rating_bands.items():
                if stats.get('win_rate', 0) < 45:
                    weaknesses['rating_depletion'] = True
        
        return weaknesses
