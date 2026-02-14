"""
Advanced Multi-Metric Cheat Detection with Confidence Scoring.

This module implements modern cheat detection similar to Chess.com's Fair Play system,
combining multiple signals including:
- Intrinsic Performance Rating (IPR) vs Official Elo
- Centipawn Loss statistics with z-score analysis
- Engine Move Correlation with confidence intervals
- Move Timing Patterns (detect engine-like consistency)
- Error Pattern Analysis (detect unnaturally low error rates)
- Statistical Significance and False-Positive Risk Assessment
"""

import statistics
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Thresholds based on Regan's research and Chess.com Fair Play system
REGAN_Z_THRESHOLD = 4.5  # Highly suspicious (1 in 300k games)
MODERATE_Z_THRESHOLD = 3.5  # Moderately suspicious
LOW_Z_THRESHOLD = 2.5  # Slightly suspicious

# Centipawn loss benchmarks (average by rating)
ELO_CPL_BASELINE = {
    1000: 150, 1200: 130, 1400: 110, 1600: 90, 1800: 75,
    2000: 60, 2200: 50, 2400: 35, 2600: 25, 2800: 20
}

@dataclass
class MetricConfidence:
    """Represents a single metric with confidence assessment."""
    metric_name: str
    value: float
    percentile: float  # 0-100, where 100 is most suspicious
    z_score: float  # Standard deviations from mean
    confidence: float  # 0-1.0, likelihood this is real signal
    false_positive_risk: float  # 0-1.0, risk this is a false positive
    context: str  # Explanation of the metric
    
    @property
    def is_flagged(self) -> bool:
        """Should this metric be flagged for review?"""
        return self.z_score > LOW_Z_THRESHOLD and self.confidence > 0.5

@dataclass
class CheatSuspicionScore:
    """Comprehensive suspicion assessment with confidence intervals."""
    player_name: str
    overall_suspicion: float  # 0-100, higher = more suspicious
    confidence_level: float  # 0-1.0, confidence in the score
    likelihood_ratio: str  # Human-readable odds (e.g., "1 in 300,000")
    individual_metrics: List[MetricConfidence] = field(default_factory=list)
    flagged_metric_count: int = 0
    false_positive_risk: float = 0.0
    recommendation: str = ""
    requires_human_review: bool = True
    confidence_interval: Tuple[float, float] = (0.0, 0.0)  # Lower, Upper bounds
    
    def __str__(self) -> str:
        """Professional summary of suspicion assessment."""
        return (f"Player: {self.player_name}\n"
                f"Suspicion Score: {self.overall_suspicion:.1f}/100\n"
                f"Confidence: {self.confidence_level:.1%}\n"
                f"Likelihood: {self.likelihood_ratio}\n"
                f"False Positive Risk: {self.false_positive_risk:.1%}\n"
                f"Flagged Metrics: {self.flagged_metric_count}\n"
                f"Recommendation: {self.recommendation}")


class AdvancedCheatDetector:
    """
    Multi-metric cheat detection with confidence scoring.
    
    Based on research by Ken Regan and Chess.com's Fair Play team.
    """
    
    def __init__(self, rating_distribution: Optional[Dict[str, List[float]]] = None):
        """
        Initialize detector with optional peer distribution data.
        
        Args:
            rating_distribution: Dict mapping rating ranges to CPL distributions
        """
        self.rating_distribution = rating_distribution or {}
        self.peer_baselines = self._build_peer_baselines()
    
    def _build_peer_baselines(self) -> Dict[int, Dict[str, float]]:
        """Build baseline statistics for each rating band."""
        baselines = {}
        for elo, baseline_cpl in ELO_CPL_BASELINE.items():
            baselines[elo] = {
                'avg_cpl': baseline_cpl,
                'std_dev': baseline_cpl * 0.25,  # ~25% variation
                'max_expected_cpl': baseline_cpl * 1.5,
                'min_expected_cpl': baseline_cpl * 0.4
            }
        return baselines
    
    def calculate_ipr(self, game_evaluations: List[float], player_rating: float) -> float:
        """
        Calculate Intrinsic Performance Rating from move quality.
        
        Maps centipawn loss to an Elo-equivalent rating based on empirical data.
        High IPR vs official rating suggests cheating.
        
        Args:
            game_evaluations: List of centipawn losses per move
            player_rating: Player's official rating
            
        Returns:
            Estimated rating based on move quality (IPR)
        """
        if not game_evaluations:
            return player_rating
        
        avg_cpl = statistics.mean(game_evaluations)
        
        # Inverse mapping: lower CPL = higher rating
        # Using empirical formula: Rating ≈ 3200 - (100 * CPL / base_cpl)
        # Conservative estimate
        if avg_cpl < 10:
            ipr = 3200
        elif avg_cpl < 20:
            ipr = 2800
        elif avg_cpl < 30:
            ipr = 2500
        elif avg_cpl < 40:
            ipr = 2300
        elif avg_cpl < 50:
            ipr = 2100
        elif avg_cpl < 60:
            ipr = 1900
        elif avg_cpl < 75:
            ipr = 1750
        elif avg_cpl < 90:
            ipr = 1600
        elif avg_cpl < 110:
            ipr = 1450
        else:
            # Linear interpolation for lower ratings
            ipr = 1400 - (avg_cpl - 110) * 5
        
        return max(800, min(3200, ipr))  # Clamp to realistic range
    
    def calculate_cpl_z_score(self, avg_cpl: float, player_rating: float,
                             peer_cpls: Optional[List[float]] = None) -> Tuple[float, float]:
        """
        Calculate z-score for centipawn loss against peers.
        
        High z-score (>4.5) indicates statistical impossibility.
        
        Args:
            avg_cpl: Player's average centipawn loss
            player_rating: Player's official rating
            peer_cpls: Optional list of peer CPLs for distribution
            
        Returns:
            (z_score, percentile) tuple
        """
        if peer_cpls:
            mean = statistics.mean(peer_cpls)
            try:
                stdev = statistics.stdev(peer_cpls)
            except statistics.StatisticsError:
                stdev = 1
        else:
            # Use rating-based baseline
            closest_rating = min(ELO_CPL_BASELINE.keys(), 
                                key=lambda x: abs(x - player_rating))
            baseline = self.peer_baselines[closest_rating]
            mean = baseline['avg_cpl']
            stdev = baseline['std_dev']
        
        if stdev == 0:
            z_score = 0
        else:
            z_score = (avg_cpl - mean) / stdev
        
        # Convert z-score to percentile
        percentile = self._z_score_to_percentile(z_score)
        
        return z_score, percentile
    
    def calculate_engine_correlation_ci(self, correlation: float, 
                                        num_moves: int,
                                        peer_correlation: Optional[float] = None) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate confidence interval for engine correlation percentage.
        
        Higher correlation with narrower uncertainty = more suspicious.
        
        Args:
            correlation: Engine correlation percentage (0-100)
            num_moves: Number of moves analyzed
            peer_correlation: Optional peer average correlation
            
        Returns:
            (z_score, confidence_interval) tuple
        """
        # Standard error for proportion
        p = correlation / 100
        se = math.sqrt(p * (1 - p) / num_moves) * 100
        
        # 95% CI
        ci_lower = max(0, correlation - 1.96 * se)
        ci_upper = min(100, correlation + 1.96 * se)
        
        # Z-score calculation (vs expected)
        if peer_correlation is None:
            # Expected correlation varies by rating
            peer_correlation = 70  # Default assumption
        
        z_score = (correlation - peer_correlation) / (se / 100) if se > 0 else 0
        
        return z_score, (ci_lower, ci_upper)
    
    def detect_timing_anomaly(self, move_times: List[float]) -> Tuple[float, str]:
        """
        Detect unnaturally uniform move timing (engine-like).
        
        Human players show variable thinking times; engines are consistent.
        
        Args:
            move_times: List of move times in seconds
            
        Returns:
            (suspicion_score, explanation) tuple
        """
        if len(move_times) < 5:
            return 0.0, "Insufficient move data"
        
        # Calculate coefficient of variation (stdev / mean)
        mean_time = statistics.mean(move_times)
        if mean_time == 0:
            return 0.0, "Unknown"
        
        try:
            stdev = statistics.stdev(move_times)
        except statistics.StatisticsError:
            return 0.0, "Insufficient variance"
        
        cv = stdev / mean_time
        
        # Humans typically CV > 0.8, Engines CV < 0.3
        if cv < 0.3:
            suspicion = 85
            explanation = "Engine-like timing consistency"
        elif cv < 0.5:
            suspicion = 60
            explanation = "Unusually consistent timing (moderately suspicious)"
        elif cv < 0.7:
            suspicion = 30
            explanation = "Somewhat consistent (borderline normal)"
        else:
            suspicion = 10
            explanation = "Natural human-like timing variation"
        
        return suspicion, explanation
    
    def detect_error_pattern_anomaly(self, move_classifications: Dict[str, int]) -> Tuple[float, str]:
        """
        Detect unnaturally low error rates (missing human mistakes).
        
        Humans make mistakes; no mistakes = suspicious.
        
        Args:
            move_classifications: Dict with counts like {'best': 10, 'inaccuracy': 1, 'mistake': 0}
            
        Returns:
            (suspicion_score, explanation) tuple
        """
        total_moves = sum(move_classifications.values())
        if total_moves < 10:
            return 0.0, "Insufficient moves"
        
        error_count = move_classifications.get('mistake', 0) + move_classifications.get('blunder', 0)
        error_rate = error_count / total_moves if total_moves > 0 else 0
        
        # Expected error rates by move type
        # Masters: ~3-5% mistakes
        # Expert: ~5-8%
        # Amateur: ~10-15%
        
        if error_rate < 0.01:  # <1% mistakes
            suspicion = 90
            explanation = "Impossibly low error rate (<1%)"
        elif error_rate < 0.03:  # <3%
            suspicion = 70
            explanation = "Suspiciously low error rate (<3%)"
        elif error_rate < 0.05:  # 3-5%
            suspicion = 30
            explanation = "Low error rate (borderline normal for strong players)"
        else:
            suspicion = 0
            explanation = "Normal error rate for skill level"
        
        return suspicion, explanation
    
    def assess_false_positive_risk(self, metrics: List[MetricConfidence],
                                  games_analyzed: int) -> Tuple[float, str]:
        """
        Assess risk of false positive given the metrics and sample size.
        
        Args:
            metrics: List of evaluated metrics
            games_analyzed: Number of games analyzed
            
        Returns:
            (risk_percentage, explanation) tuple
        """
        # Risk factors
        risk = 0.0
        factors = []
        
        # Small sample size increases false positive risk
        if games_analyzed < 10:
            risk += 40
            factors.append("Small sample size (<10 games)")
        elif games_analyzed < 20:
            risk += 20
            factors.append("Moderate sample size (10-20 games)")
        
        # Single metric > multiple metrics
        flagged = sum(1 for m in metrics if m.is_flagged)
        if flagged == 1 and len(metrics) > 0:
            risk += 30
            factors.append("Single flagged metric (high FP risk)")
        elif flagged == 0:
            risk += 50
            factors.append("No strong individual signals (high FP risk)")
        
        # Low individual confidence scores
        avg_confidence = statistics.mean([m.confidence for m in metrics]) if metrics else 0
        if avg_confidence < 0.6:
            risk += 25
            factors.append("Low individual metric confidence")
        
        risk = min(100, max(0, risk))
        explanation = "; ".join(factors) if factors else "Risk factors identified"
        
        return risk, explanation
    
    def compute_suspicion_score(self, game_metrics: Dict[str, Any],
                               player_rating: int,
                               peer_data: Optional[Dict[str, Any]] = None) -> CheatSuspicionScore:
        """
        Compute comprehensive suspicion score combining all metrics.
        
        Args:
            game_metrics: Dict with keys like 'avg_cpl', 'engine_correlation', 
                         'move_times', 'move_classifications'
            player_rating: Official player rating
            peer_data: Optional peer statistics for context
            
        Returns:
            CheatSuspicionScore with detailed analysis
        """
        metrics = []
        suspicion_components = []
        
        # Metric 1: Intrinsic Performance Rating vs Official Rating
        if 'game_evaluations' in game_metrics and game_metrics['game_evaluations']:
            ipr = self.calculate_ipr(game_metrics['game_evaluations'], player_rating)
            ipr_gap = ipr - player_rating
            
            if ipr_gap > 300:
                confidence = 1.0
                percentile = 95
                z_score = 3.5
                context = f"IPR {ipr:.0f} vs Rating {player_rating} (+{ipr_gap:.0f})"
            elif ipr_gap > 150:
                confidence = 0.7
                percentile = 80
                z_score = 2.0
                context = f"IPR {ipr:.0f} vs Rating {player_rating} (+{ipr_gap:.0f})"
            else:
                confidence = 0.3
                percentile = 40
                z_score = 0.5
                context = f"IPR {ipr:.0f} vs Rating {player_rating} (normal)"
            
            metric = MetricConfidence(
                metric_name="Intrinsic Performance Rating",
                value=ipr_gap,
                percentile=percentile,
                z_score=z_score,
                confidence=confidence,
                false_positive_risk=0.15,
                context=context
            )
            metrics.append(metric)
            if metric.is_flagged:
                suspicion_components.append(metric.percentile * 0.25)
        
        # Metric 2: Centipawn Loss Z-Score
        if 'avg_cpl' in game_metrics:
            z_score, percentile = self.calculate_cpl_z_score(
                game_metrics['avg_cpl'], 
                player_rating,
                peer_data.get('cpl_distribution') if peer_data else None
            )
            
            if z_score > REGAN_Z_THRESHOLD:
                confidence = 0.99
                context = f"CPL {game_metrics['avg_cpl']:.1f}, z={z_score:.2f} (1 in 300k)"
                fp_risk = 0.001
            elif z_score > MODERATE_Z_THRESHOLD:
                confidence = 0.85
                context = f"CPL {game_metrics['avg_cpl']:.1f}, z={z_score:.2f}"
                fp_risk = 0.05
            else:
                confidence = 0.4
                context = f"CPL {game_metrics['avg_cpl']:.1f}, z={z_score:.2f} (normal)"
                fp_risk = 0.25
            
            metric = MetricConfidence(
                metric_name="Centipawn Loss Z-Score",
                value=z_score,
                percentile=percentile,
                z_score=z_score,
                confidence=confidence,
                false_positive_risk=fp_risk,
                context=context
            )
            metrics.append(metric)
            if metric.is_flagged:
                suspicion_components.append(metric.percentile * 0.30)
        
        # Metric 3: Engine Correlation with CI
        if 'engine_correlation' in game_metrics:
            num_moves = game_metrics.get('games_analyzed', 50) * 30  # Rough estimate
            ec_z_score, (ci_lower, ci_upper) = self.calculate_engine_correlation_ci(
                game_metrics['engine_correlation'],
                num_moves,
                peer_data.get('avg_correlation') if peer_data else None
            )
            
            if ec_z_score > 3.0:
                confidence = 0.90
                percentile = 90
                context = f"Correlation {game_metrics['engine_correlation']:.1f}% (95% CI: {ci_lower:.1f}-{ci_upper:.1f}%)"
                fp_risk = 0.08
            elif ec_z_score > 1.5:
                confidence = 0.65
                percentile = 70
                context = f"Correlation {game_metrics['engine_correlation']:.1f}% (moderate)"
                fp_risk = 0.20
            else:
                confidence = 0.3
                percentile = 40
                context = f"Correlation {game_metrics['engine_correlation']:.1f}% (normal)"
                fp_risk = 0.35
            
            metric = MetricConfidence(
                metric_name="Engine Move Correlation",
                value=game_metrics['engine_correlation'],
                percentile=percentile,
                z_score=ec_z_score,
                confidence=confidence,
                false_positive_risk=fp_risk,
                context=context
            )
            metrics.append(metric)
            if metric.is_flagged:
                suspicion_components.append(metric.percentile * 0.25)
        
        # Metric 4: Timing Anomaly
        if 'move_times' in game_metrics and game_metrics['move_times']:
            timing_suspicion, timing_explanation = self.detect_timing_anomaly(
                game_metrics['move_times']
            )
            
            metric = MetricConfidence(
                metric_name="Move Timing Consistency",
                value=timing_suspicion,
                percentile=timing_suspicion,
                z_score=timing_suspicion / 20,
                confidence=0.7 if timing_suspicion > 60 else 0.4,
                false_positive_risk=0.20 if timing_suspicion < 60 else 0.05,
                context=timing_explanation
            )
            metrics.append(metric)
            if metric.is_flagged:
                suspicion_components.append(metric.percentile * 0.12)
        
        # Metric 5: Error Pattern Anomaly
        if 'move_classifications' in game_metrics:
            error_suspicion, error_explanation = self.detect_error_pattern_anomaly(
                game_metrics['move_classifications']
            )
            
            metric = MetricConfidence(
                metric_name="Error Pattern Analysis",
                value=error_suspicion,
                percentile=error_suspicion,
                z_score=error_suspicion / 25,
                confidence=0.85 if error_suspicion > 60 else 0.5,
                false_positive_risk=0.25 if error_suspicion < 50 else 0.08,
                context=error_explanation
            )
            metrics.append(metric)
            if metric.is_flagged:
                suspicion_components.append(metric.percentile * 0.08)
        
        # Calculate overall suspicion score
        if suspicion_components:
            # Weighted average with decreasing returns
            base_suspicion = statistics.mean(suspicion_components)
            overall_suspicion = min(100, base_suspicion)
        else:
            overall_suspicion = 0.0
        
        # Calculate confidence level
        avg_metric_confidence = statistics.mean([m.confidence for m in metrics]) if metrics else 0.3
        confidence_level = avg_metric_confidence * (1 - max(m.false_positive_risk for m in metrics) if metrics else 0.5)
        
        # False positive risk
        fp_risk, fp_explanation = self.assess_false_positive_risk(
            metrics,
            game_metrics.get('games_analyzed', 10)
        )
        
        # Generate recommendation and likelihood
        if overall_suspicion > 70 and confidence_level > 0.7:
            recommendation = "Recommend human review. Multiple strong signals detected."
            likelihood = self._suspicion_to_likelihood(overall_suspicion, confidence_level)
        elif overall_suspicion > 50 and confidence_level > 0.6:
            recommendation = "Warrant further investigation. Moderately unusual patterns."
            likelihood = self._suspicion_to_likelihood(overall_suspicion, confidence_level)
        else:
            recommendation = "No strong evidence of rule violations. Results within normal variation."
            likelihood = "Consistent with expected play"
        
        # Confidence interval
        ci_width = 20 * (1 - confidence_level)
        ci_lower = max(0, overall_suspicion - ci_width)
        ci_upper = min(100, overall_suspicion + ci_width)
        
        flagged_count = sum(1 for m in metrics if m.is_flagged)
        
        return CheatSuspicionScore(
            player_name=game_metrics.get('player_name', 'Unknown'),
            overall_suspicion=overall_suspicion,
            confidence_level=confidence_level,
            likelihood_ratio=likelihood,
            individual_metrics=metrics,
            flagged_metric_count=flagged_count,
            false_positive_risk=fp_risk / 100,
            recommendation=recommendation,
            requires_human_review=overall_suspicion > 50,
            confidence_interval=(ci_lower, ci_upper)
        )
    
    @staticmethod
    def _z_score_to_percentile(z_score: float) -> float:
        """Convert z-score to percentile (0-100)."""
        # Approximate conversion using error function
        # For z=4.5, percentile ≈ 99.9997
        if z_score < -3:
            return 0.1
        elif z_score > 3:
            return min(99.99, 50 + (z_score - 3) * 20)
        else:
            # Simple approximation for normal distribution
            return 50 + z_score * 15
    
    @staticmethod
    def _suspicion_to_likelihood(suspicion: float, confidence: float) -> str:
        """Convert suspicion score and confidence to human-readable odds."""
        # Map suspicion to likelihood ratio
        if suspicion > 90 and confidence > 0.85:
            return "1 in 100,000+ (extremely rare)"
        elif suspicion > 80 and confidence > 0.75:
            return "1 in 10,000+ (extremely rare)"
        elif suspicion > 70 and confidence > 0.65:
            return "1 in 1,000-10,000"
        elif suspicion > 60 and confidence > 0.60:
            return "1 in 100-1,000"
        elif suspicion > 50:
            return "1 in 30-100 (moderately unusual)"
        else:
            return "Consistent with expected play"


def create_suspicion_report(score: CheatSuspicionScore) -> str:
    """Generate a professional text report from a suspicion score."""
    report_lines = [
        "=" * 70,
        "CHESS FAIRPLAY ANALYSIS - SUSPICION ASSESSMENT REPORT",
        "=" * 70,
        "",
        f"Player: {score.player_name}",
        f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "EXECUTIVE SUMMARY",
        "-" * 70,
        f"Overall Suspicion Score: {score.overall_suspicion:.1f}/100",
        f"Assessment Confidence: {score.confidence_level:.1%}",
        f"Likelihood Ratio: {score.likelihood_ratio}",
        f"Flagged Metrics: {score.flagged_metric_count}",
        f"False Positive Risk: {score.false_positive_risk:.1%}",
        f"95% Confidence Interval: {score.confidence_interval[0]:.1f} - {score.confidence_interval[1]:.1f}",
        "",
        "DETAILED METRIC ANALYSIS",
        "-" * 70,
    ]
    
    for metric in score.individual_metrics:
        status = "⚠️ FLAGGED" if metric.is_flagged else "✓ OK"
        report_lines.extend([
            f"\n{metric.metric_name}: {status}",
            f"  Value: {metric.value:.2f} ({metric.percentile:.0f}th percentile)",
            f"  Z-Score: {metric.z_score:.2f}",
            f"  Confidence: {metric.confidence:.1%}",
            f"  False Positive Risk: {metric.false_positive_risk:.1%}",
            f"  {metric.context}",
        ])
    
    report_lines.extend([
        "",
        "RECOMMENDATION",
        "-" * 70,
        score.recommendation,
        "",
        "IMPORTANT DISCLAIMER",
        "-" * 70,
        "• This analysis is statistical in nature and cannot prove rule violations.",
        "• High suspicion scores may reflect extraordinary legitimate skill.",
        "• All conclusions require human expert review.",
        "• False positives are possible, especially with small sample sizes.",
        "• Final judgment rests with Chess.com/Lichess Fair Play teams.",
        "",
        "Sources: Ken Regan's research, Chess.com Fair Play detection methods",
        "=" * 70,
    ])
    
    return "\n".join(report_lines)
