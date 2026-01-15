"""
Additional statistical functions for chess analysis - ENHANCED DETECTIVE MODE.
"""
import statistics
import math
from typing import List, Dict, Tuple, Optional
import numpy as np

def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Calculate confidence interval for data.
    
    Args:
        data: List of numerical values
        confidence: Confidence level (0.95 for 95%)
    
    Returns:
        Tuple of (mean, lower_bound, upper_bound)
    """
    if not data:
        return 0, 0, 0
    
    n = len(data)
    if n < 2:
        return data[0], data[0], data[0]
    
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    
    # Z-score for confidence level
    z_scores = {
        0.90: 1.645,
        0.95: 1.960,
        0.99: 2.576
    }
    z = z_scores.get(confidence, 1.960)
    
    margin = z * (stdev / math.sqrt(n))
    
    return mean, mean - margin, mean + margin

def calculate_performance_rating(wins: int, draws: int, losses: int, avg_opponent_rating: float) -> float:
    """
    Calculate performance rating.
    
    Args:
        wins: Number of wins
        draws: Number of draws
        losses: Number of losses
        avg_opponent_rating: Average opponent rating
    
    Returns:
        Performance rating
    """
    total_games = wins + draws + losses
    if total_games == 0:
        return 0
    
    score = wins + (draws * 0.5)
    score_percentage = score / total_games
    
    # Convert percentage to rating difference
    # Based on Elo formula: expected_score = 1 / (1 + 10^(-rating_diff/400))
    if score_percentage >= 0.99:
        rating_diff = 800
    elif score_percentage <= 0.01:
        rating_diff = -800
    else:
        rating_diff = -400 * math.log10(1/score_percentage - 1)
    
    return avg_opponent_rating + rating_diff

def detect_outliers_iqr(data: List[float]) -> List[Tuple[int, float]]:
    """
    Detect outliers using Interquartile Range method.
    
    Args:
        data: List of numerical values
    
    Returns:
        List of (index, value) for outliers
    """
    if len(data) < 4:
        return []
    
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    
    outliers = []
    for i, value in enumerate(data):
        if value < lower_bound or value > upper_bound:
            outliers.append((i, value))
    
    return outliers

def calculate_consistency_score(accuracies: List[float]) -> float:
    """
    Calculate consistency score (0-100).
    
    Args:
        accuracies: List of accuracy percentages
    
    Returns:
        Consistency score (higher = more consistent)
    """
    if len(accuracies) < 2:
        return 100.0
    
    stdev = statistics.stdev(accuracies)
    
    # Convert to 0-100 scale
    # Lower stdev = higher consistency
    max_stdev = 50  # Assuming 50% stdev is maximum expected
    consistency = max(0, 100 - (stdev / max_stdev * 100))
    
    return consistency

def calculate_move_time_patterns(move_times: List[float]) -> Dict[str, float]:
    """
    Analyze move time patterns for suspicious consistency.
    
    Args:
        move_times: List of move times in seconds
    
    Returns:
        Dictionary of pattern statistics
    """
    if not move_times:
        return {}
    
    # Calculate various statistics
    mean_time = statistics.mean(move_times)
    stdev_time = statistics.stdev(move_times) if len(move_times) > 1 else 0
    
    # Check for suspicious patterns
    cv = (stdev_time / mean_time * 100) if mean_time > 0 else 0  # Coefficient of variation
    
    # Count moves with very similar times
    time_groups = {}
    for time in move_times:
        rounded = round(time, 1)  # Group by 0.1s precision
        time_groups[rounded] = time_groups.get(rounded, 0) + 1
    
    most_common_time = max(time_groups.items(), key=lambda x: x[1]) if time_groups else (0, 0)
    common_time_percentage = (most_common_time[1] / len(move_times) * 100) if move_times else 0
    
    return {
        'mean_time': mean_time,
        'stdev_time': stdev_time,
        'coefficient_variation': cv,
        'most_common_time': most_common_time[0],
        'common_time_percentage': common_time_percentage,
        'is_suspicious': common_time_percentage > 30 and cv < 20  # Too consistent
    }

def calculate_rating_progression(ratings: List[int]) -> Dict[str, float]:
    """
    Analyze rating progression for suspicious jumps.
    
    Args:
        ratings: List of ratings over time
    
    Returns:
        Dictionary of progression statistics
    """
    if len(ratings) < 2:
        return {'avg_change': 0, 'max_change': 0, 'suspicious': False}
    
    changes = []
    for i in range(1, len(ratings)):
        changes.append(ratings[i] - ratings[i - 1])
    
    avg_change = statistics.mean(changes)
    max_change = max(abs(c) for c in changes) if changes else 0
    
    # Check for suspicious rating jumps
    suspicious = max_change > 200  # More than 200 point jump is suspicious
    
    return {
        'avg_change': avg_change,
        'max_change': max_change,
        'suspicious': suspicious,
        'changes': changes
    }

def calculate_accuracy_anomaly(recent_accuracy: float, historical_average: float) -> float:
    """
    Calculate accuracy anomaly score.
    ENHANCED: Detect when accuracy jumps unusually.
    
    Args:
        recent_accuracy: Recent average accuracy
        historical_average: Historical average accuracy
    
    Returns:
        Anomaly score (0-100, higher = more anomalous)
    """
    if historical_average == 0:
        return 0.0
    
    diff = recent_accuracy - historical_average
    # Normalize to 0-100 scale
    anomaly = min(100, abs(diff) * 2)  # Max 50% difference
    return anomaly

def detect_game_clustering(game_dates: List[str]) -> Dict[str, float]:
    """
    ENHANCED: Detect suspicious clustering of games (all played in short time period).
    
    Args:
        game_dates: List of game date strings
    
    Returns:
        Dictionary with clustering metrics
    """
    if len(game_dates) < 2:
        return {'is_clustered': False, 'clustering_score': 0.0}
    
    # Count games per day (approximate)
    day_counts = {}
    for date in game_dates:
        day = date[:10] if len(date) >= 10 else date  # Get YYYY-MM-DD
        day_counts[day] = day_counts.get(day, 0) + 1
    
    # Check if too many games in one day (suspicious for blitz)
    max_games_per_day = max(day_counts.values()) if day_counts else 0
    clustering_score = min(100, (max_games_per_day - 5) * 10) if max_games_per_day > 5 else 0
    
    return {
        'is_clustered': max_games_per_day > 10,
        'clustering_score': clustering_score,
        'max_games_per_day': max_games_per_day,
        'days_played': len(day_counts)
    }

def calculate_opponent_strength_anomaly(player_ratings: List[int], opponent_ratings: List[int]) -> float:
    """
    ENHANCED: Detect if player is consistently beating much stronger opponents (or weaker).
    
    Args:
        player_ratings: List of player ratings per game
        opponent_ratings: List of opponent ratings per game
    
    Returns:
        Anomaly score (higher = more suspicious)
    """
    if len(player_ratings) != len(opponent_ratings) or not player_ratings:
        return 0.0
    
    rating_differences = [opp - player for player, opp in zip(player_ratings, opponent_ratings)]
    avg_diff = statistics.mean(rating_differences)
    
    # Positive means player is beating stronger opponents
    # More than +100 average is suspicious
    anomaly = min(100, max(0, (abs(avg_diff) - 50) / 50 * 100)) if avg_diff != 0 else 0
    
    return anomaly