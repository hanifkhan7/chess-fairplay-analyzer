"""
Multi-Player Comparison System.

Enables side-by-side analysis and comparison of multiple players with:
- Head-to-head metrics
- Statistical significance tests
- Relative performance charts
- Clustering and grouping analysis
"""

import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ComparisonMetric(Enum):
    """Metrics that can be compared across players."""
    RATING = "rating"
    ACCURACY = "accuracy"
    CPL = "centipawn_loss"
    WIN_RATE = "win_rate"
    CONSISTENCY = "consistency"
    IPR = "intrinsic_rating"
    SUSPICION = "suspicion_score"

@dataclass
class PlayerComparison:
    """Side-by-side comparison of two players."""
    player1_name: str
    player2_name: str
    metrics: Dict[ComparisonMetric, Dict[str, float]] = field(default_factory=dict)
    statistical_significance: Dict[str, float] = field(default_factory=dict)
    advantage_indicators: List[str] = field(default_factory=list)
    confidence_levels: Dict[str, float] = field(default_factory=dict)

@dataclass
class MultiPlayerComparison:
    """Comparison of multiple players."""
    players: List[str]
    metrics_matrix: Dict[str, List[float]] = field(default_factory=dict)  # metric -> [p1, p2, p3, ...]
    ranking: Dict[ComparisonMetric, List[Tuple[str, float]]] = field(default_factory=dict)
    clusters: List[List[str]] = field(default_factory=list)  # Groups of similar players
    outliers: List[str] = field(default_factory=list)  # Players significantly different
    pairwise_comparisons: List[PlayerComparison] = field(default_factory=list)

class MultiPlayerAnalyzer:
    """Analyze and compare multiple players."""
    
    @staticmethod
    def compare_two_players(player1_data: Dict[str, Any],
                           player2_data: Dict[str, Any],
                           player1_name: str,
                           player2_name: str) -> PlayerComparison:
        """
        Compare two players side-by-side.
        
        Args:
            player1_data: Dict with keys like 'rating', 'accuracy', 'cpl', 'win_rate'
            player2_data: Same structure as player1
            
        Returns:
            PlayerComparison with metrics and insights
        """
        comparison = PlayerComparison(
            player1_name=player1_name,
            player2_name=player2_name
        )
        
        # Compare each metric
        for metric in ComparisonMetric:
            key = metric.value
            if key in player1_data and key in player2_data:
                p1_val = player1_data[key]
                p2_val = player2_data[key]
                
                comparison.metrics[metric] = {
                    'player1': p1_val,
                    'player2': p2_val,
                    'difference': p1_val - p2_val,
                    'ratio': p1_val / p2_val if p2_val != 0 else 1.0
                }
                
                # Determine who is better
                # (lower is better for CPL and suspicion, higher for others)
                if metric in [ComparisonMetric.CPL, ComparisonMetric.SUSPICION]:
                    if p1_val < p2_val:
                        comparison.advantage_indicators.append(f"{player1_name} better on {metric.value}")
                    elif p2_val < p1_val:
                        comparison.advantage_indicators.append(f"{player2_name} better on {metric.value}")
                else:
                    if p1_val > p2_val:
                        comparison.advantage_indicators.append(f"{player1_name} better on {metric.value}")
                    elif p2_val > p1_val:
                        comparison.advantage_indicators.append(f"{player2_name} better on {metric.value}")
        
        return comparison
    
    @staticmethod
    def compare_multiple_players(players_data: Dict[str, Dict[str, Any]]) -> MultiPlayerComparison:
        """
        Compare multiple players in aggregate.
        
        Args:
            players_data: Dict mapping player names to their metrics
            
        Returns:
            MultiPlayerComparison with matrices, rankings, clusters
        """
        player_names = list(players_data.keys())
        comparison = MultiPlayerComparison(players=player_names)
        
        # Build metrics matrix
        for metric in ComparisonMetric:
            key = metric.value
            values = []
            for name in player_names:
                if key in players_data[name]:
                    values.append(players_data[name][key])
                else:
                    values.append(None)
            
            if all(v is not None for v in values):
                comparison.metrics_matrix[key] = values
                
                # Rank players on this metric
                ranked = sorted(
                    zip(player_names, values),
                    key=lambda x: x[1],
                    reverse=(metric not in [ComparisonMetric.CPL, ComparisonMetric.SUSPICION])
                )
                comparison.ranking[metric] = ranked
        
        # Clustering based on overall similarity
        comparison.clusters = MultiPlayerAnalyzer._cluster_players(players_data, player_names)
        
        # Find outliers
        comparison.outliers = MultiPlayerAnalyzer._find_outliers(players_data, player_names, comparison.clusters)
        
        # Pairwise comparisons
        for i, p1_name in enumerate(player_names):
            for p2_name in player_names[i+1:]:
                p_comparison = MultiPlayerAnalyzer.compare_two_players(
                    players_data[p1_name],
                    players_data[p2_name],
                    p1_name,
                    p2_name
                )
                comparison.pairwise_comparisons.append(p_comparison)
        
        return comparison
    
    @staticmethod
    def _cluster_players(players_data: Dict[str, Dict[str, Any]],
                        player_names: List[str]) -> List[List[str]]:
        """
        Cluster players by similarity (K-means-like approach).
        """
        if len(player_names) <= 2:
            return [player_names]
        
        # Simple clustering: group by rating bands
        rating_clusters = {}
        for name in player_names:
            if 'rating' in players_data[name]:
                rating = players_data[name]['rating']
                band = (rating // 200) * 200  # Band of 200
                if band not in rating_clusters:
                    rating_clusters[band] = []
                rating_clusters[band].append(name)
        
        if not rating_clusters:
            return [player_names]
        
        return list(rating_clusters.values())
    
    @staticmethod
    def _find_outliers(players_data: Dict[str, Dict[str, Any]],
                      player_names: List[str],
                      clusters: List[List[str]]) -> List[str]:
        """Find players significantly different from their cluster."""
        outliers = []
        
        for cluster in clusters:
            if len(cluster) < 2:
                continue
            
            # Calculate cluster centroids for key metrics
            accuracy_vals = [players_data[p].get('accuracy', 50) for p in cluster if 'accuracy' in players_data[p]]
            cpl_vals = [players_data[p].get('cpl', 50) for p in cluster if 'cpl' in players_data[p]]
            
            if accuracy_vals and len(accuracy_vals) > 1:
                try:
                    acc_mean = statistics.mean(accuracy_vals)
                    acc_stdev = statistics.stdev(accuracy_vals)
                    
                    for player in cluster:
                        if 'accuracy' in players_data[player]:
                            z_score = abs((players_data[player]['accuracy'] - acc_mean) / (acc_stdev + 0.1))
                            if z_score > 2.0:  # >2 std dev
                                outliers.append(player)
                except:
                    pass
        
        return list(set(outliers))
    
    @staticmethod
    def create_comparison_summary(comparison: MultiPlayerComparison) -> str:
        """Generate text summary of multi-player comparison."""
        lines = [
            f"\\nComparison of {len(comparison.players)} players: {', '.join(comparison.players)}",
            "=" * 80,
            ""
        ]
        
        # Overall rankings
        lines.append("Rankings by Key Metrics:")
        lines.append("-" * 80)
        for metric, ranking in comparison.ranking.items():
            lines.append(f"\\n{metric.value.replace('_', ' ').title()}:")
            for i, (name, value) in enumerate(ranking, 1):
                lines.append(f"  {i}. {name}: {value:.2f}")
        
        # Clusters
        if comparison.clusters:
            lines.append(f"\\n\\nClusters:")
            lines.append("-" * 80)
            for i, cluster in enumerate(comparison.clusters, 1):
                lines.append(f"Cluster {i}: {', '.join(cluster)}")
        
        # Outliers
        if comparison.outliers:
            lines.append(f"\\n\\nOutliers (significantly different from their group):")
            lines.append("-" * 80)
            for outlier in comparison.outliers:
                lines.append(f"  • {outlier}")
        
        # Advantages
        lines.append(f"\\n\\nKey Differences:")
        lines.append("-" * 80)
        for p_comp in comparison.pairwise_comparisons:
            if p_comp.advantage_indicators:
                lines.append(f"\\n{p_comp.player1_name} vs {p_comp.player2_name}:")
                for advantage in p_comp.advantage_indicators[:3]:  # Top 3
                    lines.append(f"  • {advantage}")
        
        return "\\n".join(lines)
    
    @staticmethod
    def calculate_effect_size(group1_values: List[float],
                            group2_values: List[float]) -> float:
        """
        Calculate Cohen's d effect size between two groups.
        
        0-0.2: negligible
        0.2-0.5: small
        0.5-0.8: medium
        0.8+: large
        """
        if not group1_values or not group2_values:
            return 0.0
        
        mean1 = statistics.mean(group1_values)
        mean2 = statistics.mean(group2_values)
        
        try:
            std1 = statistics.stdev(group1_values) if len(group1_values) > 1 else 0
            std2 = statistics.stdev(group2_values) if len(group2_values) > 1 else 0
        except statistics.StatisticsError:
            return 0.0
        
        # Pooled standard deviation
        n1, n2 = len(group1_values), len(group2_values)
        pooled_std = ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
        pooled_std = pooled_std ** 0.5
        
        if pooled_std == 0:
            return 0.0
        
        return (mean1 - mean2) / pooled_std
    
    @staticmethod
    def assess_tournament_performance(tournament_games: List[Dict[str, Any]],
                                      players: List[str]) -> Dict[str, Any]:
        """
        Analyze tournament performance for selected players.
        
        Args:
            tournament_games: List of games with 'white_player', 'black_player', 'result'
            players: List of player names to analyze
            
        Returns:
            Dict with tournament stats for each player
        """
        stats = {}
        
        for player in players:
            player_games = [g for g in tournament_games 
                          if g.get('white_player') == player or g.get('black_player') == player]
            
            if not player_games:
                continue
            
            # Calculate stats
            as_white = [g for g in player_games if g.get('white_player') == player]
            as_black = [g for g in player_games if g.get('black_player') == player]
            
            wins = sum(1 for g in player_games if 
                      (g.get('white_player') == player and g.get('result') in ['1-0', '1']) or
                      (g.get('black_player') == player and g.get('result') in ['0-1', '-1']))
            draws = sum(1 for g in player_games if g.get('result') in ['0.5-0.5', '0.5'])
            losses = len(player_games) - wins - draws
            
            stats[player] = {
                'games': len(player_games),
                'as_white': len(as_white),
                'as_black': len(as_black),
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'win_rate': wins / len(player_games) if player_games else 0,
                'draw_rate': draws / len(player_games) if player_games else 0,
                'score': wins + 0.5 * draws,
                'expected_score': sum(g.get('expected_score', 0.5) for g in player_games),
                'performance_rating': MultiPlayerAnalyzer._calculate_tournament_rating(
                    player_games, wins, draws
                )
            }
        
        return stats
    
    @staticmethod
    def _calculate_tournament_rating(games: List[Dict[str, Any]], 
                                     wins: int, draws: int) -> float:
        """Estimate performance rating from tournament result."""
        losses = len(games) - wins - draws
        total = len(games)
        
        if total == 0:
            return 0
        
        # Simple estimation: compare to average opponent rating
        opponent_ratings = []
        for game in games:
            if 'opponent_rating' in game:
                opponent_ratings.append(game['opponent_rating'])
        
        if not opponent_ratings:
            return 0
        
        avg_opponent_rating = statistics.mean(opponent_ratings)
        
        # Score percentage
        score_pct = (wins + 0.5 * draws) / total
        
        # Elo gain formula: Performance = Opponent Rating + 400 * (Score - Expected) / N
        # Assuming 50% expected
        perf_rating = avg_opponent_rating + 400 * (score_pct - 0.5) / 1.0
        
        return perf_rating
