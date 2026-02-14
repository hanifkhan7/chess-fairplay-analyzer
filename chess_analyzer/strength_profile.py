"""
Strength Profile & Skill Level Analysis.

Analyzes player strength by:
- Computing Intrinsic Performance Rating (IPR) vs Official Elo
- Building expected accuracy charts against peer baseline
- Creating multi-dimensional skill profiles
- Detecting aberrations from normal skill progression
"""

import statistics
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PlayerTier(Enum):
    """Chess skill tiers based on rating."""
    BEGINNER = (800, 1200)
    INTERMEDIATE = (1200, 1600)
    ADVANCED = (1600, 2000)
    EXPERT = (2000, 2400)
    MASTER = (2400, 2800)
    GRANDMASTER = (2800, 3500)

# Empirical data: Expected CPL by rating (from large databases)
EXPECTED_CPL_BY_RATING = {
    800: 200, 900: 180, 1000: 160, 1100: 145, 1200: 130, 1300: 120,
    1400: 110, 1500: 100, 1600: 90, 1700: 82, 1800: 75, 1900: 68,
    2000: 60, 2100: 53, 2200: 47, 2300: 42, 2400: 36, 2500: 32,
    2600: 28, 2700: 24, 2800: 20, 2900: 18, 3000: 16
}

# Empirical data: Expected accuracy by rating
EXPECTED_ACCURACY_BY_RATING = {
    800: 35, 900: 38, 1000: 40, 1100: 42, 1200: 44, 1300: 46,
    1400: 47, 1500: 48, 1600: 50, 1700: 52, 1800: 54, 1900: 55,
    2000: 57, 2100: 59, 2200: 61, 2300: 62, 2400: 64, 2500: 65,
    2600: 66, 2700: 67, 2800: 68, 2900: 69, 3000: 70
}

@dataclass
class SkillMetric:
    """Single skill dimension with context."""
    name: str
    value: float  # 0-100 scale
    estimated_elo: float
    percentile_among_peers: float
    expected_value: float
    deviation: float  # Actual vs expected
    strength_level: str  # 'strong', 'average', 'weak'

@dataclass
class SkillProfile:
    """Multi-dimensional skill profile."""
    username: str
    official_rating: float
    intrinsic_rating: float  # From move quality
    rating_gap: float  # IPR - Official
    
    # Skill dimensions
    opening_strength: SkillMetric
    tactical_sharpness: SkillMetric
    endgame_technique: SkillMetric
    strategy_understanding: SkillMetric
    time_management: SkillMetric
    consistency: SkillMetric
    
    # Aggregate metrics
    overall_skill_level: PlayerTier
    skill_coherence: float  # 0-1.0, how consistent are the skill dimensions
    overachievement_indicator: float  # How much above expected
    underachievement_indicator: float  # How much below expected
    
    # Empirical comparison
    percentile_among_peers: float  # Player's percentile vs peers at same rating
    skill_distribution_fit: Dict[str, float] = field(default_factory=dict)  # How well profile fits tier distribution
    
    # Anomalies
    skill_imbalance_detected: bool = False
    imbalance_details: str = ""
    superhuman_capacity: bool = False
    
    def compute_radar_data(self) -> Dict[str, float]:
        """Get skill data for radar/spider chart visualization."""
        return {
            'Opening': self.opening_strength.value,
            'Tactics': self.tactical_sharpness.value,
            'Endgame': self.endgame_technique.value,
            'Strategy': self.strategy_understanding.value,
            'Time Mgmt': self.time_management.value,
            'Consistency': self.consistency.value
        }

@dataclass
class AccuracyBenchmark:
    """Benchmark for accuracy comparison."""
    rating_band: str  # e.g., "1600-1700"
    avg_cpl: float
    avg_accuracy: float
    std_dev_cpl: float
    sample_size: int
    percentile_25: float
    percentile_50: float  # Median
    percentile_75: float

class StrengthProfileAnalyzer:
    """Analyze player strength across multiple dimensions."""
    
    @staticmethod
    def build_skill_profile(games: List[Dict[str, Any]], 
                           username: str,
                           official_rating: int,
                           peer_data: Optional[Dict[str, Any]] = None) -> SkillProfile:
        """
        Build comprehensive skill profile from games.
        
        Args:
            games: List of game analysis dicts
            username: Player username
            official_rating: Official player rating
            peer_data: Optional peer statistics for benchmarking
            
        Returns:
            SkillProfile with multi-dimensional skill assessment
        """
        
        # Calculate IPR from move quality
        all_cpls = [g.get('cpl', 50) for g in games if g.get('cpl')]
        ipr = StrengthProfileAnalyzer._calculate_ipr(all_cpls, official_rating)
        rating_gap = ipr - official_rating
        
        # Extract phase-specific data
        opening_accs = []
        tactical_accs = []
        endgame_accs = []
        opening_cpls = []
        endgame_cpls = []
        move_times = []
        accuracies = []
        
        for game in games:
            accs = game.get('accuracy', 50)
            accuracies.append(accs)
            
            if 'phase_scores' in game:
                phases = game['phase_scores']
                opening_accs.append(phases.get('opening', 50))
                tactical_accs.append(phases.get('tactical', 50))
                endgame_accs.append(phases.get('endgame', 50))
                opening_cpls.append(phases.get('opening_cpl', 50))
                endgame_cpls.append(phases.get('endgame_cpl', 50))
            
            if 'move_times' in game and game['move_times']:
                move_times.extend(game['move_times'])
        
        # Calculate expected values for rating
        expected_accuracy = StrengthProfileAnalyzer._get_expected_value(
            official_rating, EXPECTED_ACCURACY_BY_RATING
        )
        expected_cpl = StrengthProfileAnalyzer._get_expected_value(
            official_rating, EXPECTED_CPL_BY_RATING
        )
        
        # Build individual skill metrics
        opening_strength = SkillMetric(
            name='Opening Knowledge',
            value=statistics.mean(opening_accs) if opening_accs else expected_accuracy,
            estimated_elo=StrengthProfileAnalyzer._accuracy_to_elo(
                statistics.mean(opening_accs) if opening_accs else expected_accuracy
            ),
            percentile_among_peers=StrengthProfileAnalyzer._calculate_percentile(
                statistics.mean(opening_accs) if opening_accs else expected_accuracy,
                expected_accuracy, 10  # ±10% std dev
            ),
            expected_value=expected_accuracy,
            deviation=(statistics.mean(opening_accs) - expected_accuracy) if opening_accs else 0,
            strength_level=StrengthProfileAnalyzer._assess_strength(
                statistics.mean(opening_accs) if opening_accs else expected_accuracy,
                expected_accuracy
            )
        )
        
        tactical_sharpness = SkillMetric(
            name='Tactical Sharpness',
            value=statistics.mean(tactical_accs) if tactical_accs else expected_accuracy,
            estimated_elo=StrengthProfileAnalyzer._accuracy_to_elo(
                statistics.mean(tactical_accs) if tactical_accs else expected_accuracy
            ),
            percentile_among_peers=StrengthProfileAnalyzer._calculate_percentile(
                statistics.mean(tactical_accs) if tactical_accs else expected_accuracy,
                expected_accuracy, 12
            ),
            expected_value=expected_accuracy,
            deviation=(statistics.mean(tactical_accs) - expected_accuracy) if tactical_accs else 0,
            strength_level=StrengthProfileAnalyzer._assess_strength(
                statistics.mean(tactical_accs) if tactical_accs else expected_accuracy,
                expected_accuracy
            )
        )
        
        endgame_technique = SkillMetric(
            name='Endgame Technique',
            value=statistics.mean(endgame_accs) if endgame_accs else expected_accuracy,
            estimated_elo=StrengthProfileAnalyzer._accuracy_to_elo(
                statistics.mean(endgame_accs) if endgame_accs else expected_accuracy
            ),
            percentile_among_peers=StrengthProfileAnalyzer._calculate_percentile(
                statistics.mean(endgame_accs) if endgame_accs else expected_accuracy,
                expected_accuracy, 10
            ),
            expected_value=expected_accuracy,
            deviation=(statistics.mean(endgame_accs) - expected_accuracy) if endgame_accs else 0,
            strength_level=StrengthProfileAnalyzer._assess_strength(
                statistics.mean(endgame_accs) if endgame_accs else expected_accuracy,
                expected_accuracy
            )
        )
        
        # Strategy = How well overall vs opponent strength
        strategy_value = statistics.mean(accuracies) if accuracies else expected_accuracy
        strategy_understanding = SkillMetric(
            name='Strategic Understanding',
            value=strategy_value,
            estimated_elo=StrengthProfileAnalyzer._accuracy_to_elo(strategy_value),
            percentile_among_peers=StrengthProfileAnalyzer._calculate_percentile(
                strategy_value, expected_accuracy, 15
            ),
            expected_value=expected_accuracy,
            deviation=strategy_value - expected_accuracy,
            strength_level=StrengthProfileAnalyzer._assess_strength(strategy_value, expected_accuracy)
        )
        
        # Time management = consistency of move times
        time_consistency = 0.0
        if move_times and len(move_times) > 5:
            try:
                mean_time = statistics.mean(move_times)
                stdev = statistics.stdev(move_times)
                cv = stdev / mean_time if mean_time > 0 else 0
                # Convert CV to score (higher CV = better time management)
                time_consistency = min(100, (cv / 1.5) * 100)  # Normalize
            except (statistics.StatisticsError, ValueError):
                time_consistency = 50
        else:
            time_consistency = 50
        
        time_management = SkillMetric(
            name='Time Management',
            value=time_consistency,
            estimated_elo=official_rating,  # Harder to estimate from time alone
            percentile_among_peers=50,
            expected_value=50,
            deviation=time_consistency - 50,
            strength_level=StrengthProfileAnalyzer._assess_strength(time_consistency, 50)
        )
        
        # Consistency = how stable is accuracy across games
        consistency_score = 0.0
        if len(accuracies) > 2:
            try:
                std_dev = statistics.stdev(accuracies)
                # Lower std dev = better consistency
                consistency_score = max(0, 100 - std_dev * 2)
            except statistics.StatisticsError:
                consistency_score = 50
        else:
            consistency_score = 50
        
        consistency = SkillMetric(
            name='Consistency',
            value=consistency_score,
            estimated_elo=official_rating,
            percentile_among_peers=StrengthProfileAnalyzer._calculate_percentile(
                consistency_score, 50, 20
            ),
            expected_value=50,
            deviation=consistency_score - 50,
            strength_level=StrengthProfileAnalyzer._assess_strength(consistency_score, 50)
        )
        
        # Determine overall tier
        overall_tier = StrengthProfileAnalyzer._get_tier_from_rating(official_rating)
        
        # Detect skill imbalance
        skill_values = [
            opening_strength.value,
            tactical_sharpness.value,
            endgame_technique.value,
            strategy_understanding.value
        ]
        skill_imbalance = False
        imbalance_details = ""
        
        if skill_values:
            skill_range = max(skill_values) - min(skill_values)
            if skill_range > 20:  # >20 point spread = imbalance
                skill_imbalance = True
                if tactical_sharpness.value < opening_strength.value - 15:
                    imbalance_details = "Weak in tactics despite openings strength"
                elif endgame_technique.value < (opening_strength.value + tactical_sharpness.value) / 2 - 15:
                    imbalance_details = "Endgame weakness not aligned with opening/tactical strength"
        
        # Superhuman capacity detection
        superhuman = rating_gap > 200 and consistency_score > 70
        
        return SkillProfile(
            username=username,
            official_rating=official_rating,
            intrinsic_rating=ipr,
            rating_gap=rating_gap,
            opening_strength=opening_strength,
            tactical_sharpness=tactical_sharpness,
            endgame_technique=endgame_technique,
            strategy_understanding=strategy_understanding,
            time_management=time_management,
            consistency=consistency,
            overall_skill_level=overall_tier,
            skill_coherence=StrengthProfileAnalyzer._calculate_coherence(
                [opening_strength, tactical_sharpness, endgame_technique, strategy_understanding]
            ),
            overachievement_indicator=max(0, rating_gap),
            underachievement_indicator=max(0, -rating_gap),
            percentile_among_peers=StrengthProfileAnalyzer._calculate_percentile(ipr, official_rating, official_rating * 0.1),
            skill_imbalance_detected=skill_imbalance,
            imbalance_details=imbalance_details,
            superhuman_capacity=superhuman
        )
    
    @staticmethod
    def _calculate_ipr(cpls: List[float], official_rating: int) -> float:
        """Calculate Intrinsic Performance Rating from centipawn losses."""
        if not cpls:
            return official_rating
        
        avg_cpl = statistics.mean(cpls)
        
        # Linear interpolation between known points
        for rating in sorted(EXPECTED_CPL_BY_RATING.keys(), reverse=True):
            if EXPECTED_CPL_BY_RATING[rating] >= avg_cpl:
                estimated_rating = rating
            else:
                break
        
        return estimated_rating
    
    @staticmethod
    def _get_expected_value(rating: int, baseline_dict: Dict[int, float]) -> float:
        """Get expected value for a rating by interpolation."""
        if rating in baseline_dict:
            return baseline_dict[rating]
        
        # Find nearest neighbors
        sorted_ratings = sorted(baseline_dict.keys())
        if rating < sorted_ratings[0]:
            return baseline_dict[sorted_ratings[0]]
        if rating > sorted_ratings[-1]:
            return baseline_dict[sorted_ratings[-1]]
        
        # Linear interpolation
        for i, r in enumerate(sorted_ratings[:-1]):
            if r <= rating < sorted_ratings[i + 1]:
                r1, r2 = r, sorted_ratings[i + 1]
                v1, v2 = baseline_dict[r1], baseline_dict[r2]
                return v1 + (v2 - v1) * (rating - r1) / (r2 - r1)
        
        return baseline_dict[sorted_ratings[-1]]
    
    @staticmethod
    def _accuracy_to_elo(accuracy: float) -> float:
        """Estimate Elo from accuracy percentage."""
        # Empirical: Each 1% accuracy ≈ ~40 Elo points (rough)
        base_rating = 1000
        return base_rating + (accuracy - 40) * 40
    
    @staticmethod
    def _assess_strength(actual: float, expected: float) -> str:
        """Assess relative strength vs expectation."""
        diff = actual - expected
        if diff > 15:
            return "strong"
        elif diff > 5:
            return "above average"
        elif diff > -5:
            return "average"
        elif diff > -15:
            return "below average"
        else:
            return "weak"
    
    @staticmethod
    def _calculate_percentile(value: float, mean: float, std_dev: float) -> float:
        """Estimate percentile from value, mean, and std dev."""
        if std_dev == 0:
            return 50
        z = (value - mean) / std_dev
        # Approximate percentile from z-score
        percentile = 50 + z * 15  # Rough conversion
        return max(1, min(99, percentile))
    
    @staticmethod
    def _get_tier_from_rating(rating: int) -> PlayerTier:
        """Get player tier from rating."""
        for tier in PlayerTier:
            if tier.value[0] <= rating < tier.value[1]:
                return tier
        return PlayerTier.GRANDMASTER if rating >= 2800 else PlayerTier.BEGINNER
    
    @staticmethod
    def _calculate_coherence(skill_metrics: List[SkillMetric]) -> float:
        """
        Calculate how coherent the skill profile is.
        
        Coherent = all skills at similar level
        Incoherent = wildly varying skills
        """
        if len(skill_metrics) < 2:
            return 1.0
        
        values = [m.value for m in skill_metrics]
        try:
            std_dev = statistics.stdev(values)
        except statistics.StatisticsError:
            return 1.0
        
        mean_val = statistics.mean(values)
        cv = std_dev / mean_val if mean_val > 0 else 0
        
        # Lower CV = higher coherence
        coherence = max(0, 1 - cv)
        return coherence
    
    @staticmethod
    def build_accuracy_benchmark(peer_games: List[Dict[str, Any]],
                                rating_center: int,
                                rating_width: int = 100) -> AccuracyBenchmark:
        """
        Build accuracy benchmark for a rating band.
        
        Args:
            peer_games: Games from peers in this rating band
            rating_center: Center rating for the band
            rating_width: Width of the band (±rating_width from center)
            
        Returns:
            AccuracyBenchmark with statistics
        """
        cpls = [g.get('cpl', 50) for g in peer_games if 'cpl' in g]
        accuracies = [g.get('accuracy', 50) for g in peer_games if 'accuracy' in g]
        
        if not cpls or not accuracies:
            # Return default
            expected_cpl = StrengthProfileAnalyzer._get_expected_value(
                rating_center, EXPECTED_CPL_BY_RATING
            )
            expected_acc = StrengthProfileAnalyzer._get_expected_value(
                rating_center, EXPECTED_ACCURACY_BY_RATING
            )
            return AccuracyBenchmark(
                rating_band=f"{rating_center - rating_width//2}-{rating_center + rating_width//2}",
                avg_cpl=expected_cpl,
                avg_accuracy=expected_acc,
                std_dev_cpl=expected_cpl * 0.25,
                sample_size=0,
                percentile_25=expected_cpl * 1.1,
                percentile_50=expected_cpl,
                percentile_75=expected_cpl * 0.9
            )
        
        try:
            cpl_stdev = statistics.stdev(cpls)
            acc_stdev = statistics.stdev(accuracies)
        except statistics.StatisticsError:
            cpl_stdev = statistics.mean(cpls) * 0.25
            acc_stdev = 5
        
        cpls_sorted = sorted(cpls)
        acc_idx_25 = int(len(cpls_sorted) * 0.25)
        acc_idx_50 = int(len(cpls_sorted) * 0.50)
        acc_idx_75 = int(len(cpls_sorted) * 0.75)
        
        return AccuracyBenchmark(
            rating_band=f"{rating_center - rating_width//2}-{rating_center + rating_width//2}",
            avg_cpl=statistics.mean(cpls),
            avg_accuracy=statistics.mean(accuracies),
            std_dev_cpl=cpl_stdev,
            sample_size=len(cpls),
            percentile_25=cpls_sorted[acc_idx_25],
            percentile_50=cpls_sorted[acc_idx_50],
            percentile_75=cpls_sorted[acc_idx_75]
        )
