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

def calculate_rating_volatility(ratings: List[int]) -> Dict[str, float]:
    """
    Analyze rating volatility and stability.
    
    Args:
        ratings: List of ratings over time (in order)
    
    Returns:
        Dictionary with volatility metrics
    """
    if len(ratings) < 2:
        return {
            'volatility_score': 0.0,
            'standard_deviation': 0.0,
            'coefficient_of_variation': 0.0,
            'rating_trend': 'stable',
            'trend_direction': 'neutral'
        }
    
    stdev = statistics.stdev(ratings)
    mean_rating = statistics.mean(ratings)
    cv = (stdev / mean_rating * 100) if mean_rating > 0 else 0  # Coefficient of variation
    
    # Check trend: compare first half to second half
    mid = len(ratings) // 2
    first_half_mean = statistics.mean(ratings[:mid])
    second_half_mean = statistics.mean(ratings[mid:])
    trend_diff = second_half_mean - first_half_mean
    
    if abs(trend_diff) < 20:
        trend_direction = 'stable'
    elif trend_diff > 0:
        trend_direction = 'improving'
    else:
        trend_direction = 'declining'
    
    # Volatility classification
    if cv < 2:
        rating_trend = 'very_stable'
    elif cv < 5:
        rating_trend = 'stable'
    elif cv < 10:
        rating_trend = 'moderate'
    else:
        rating_trend = 'volatile'
    
    return {
        'volatility_score': min(100, cv * 10),  # 0-100 scale
        'standard_deviation': stdev,
        'coefficient_of_variation': cv,
        'rating_trend': rating_trend,
        'trend_direction': trend_direction,
        'trend_value': trend_diff
    }

def analyze_time_management(games) -> Dict[str, any]:
    """
    Analyze time management and time control distribution.
    
    Args:
        games: List of chess game objects
    
    Returns:
        Dictionary with time management metrics
    """
    time_controls = {}
    time_control_results = {}
    avg_time_per_move = {}
    
    for game in games:
        headers = game.headers
        time_control = headers.get('TimeControl', 'Unknown')
        result = headers.get('Result', '*')
        
        if time_control not in time_controls:
            time_controls[time_control] = 0
            time_control_results[time_control] = {'wins': 0, 'draws': 0, 'losses': 0}
            avg_time_per_move[time_control] = []
        
        time_controls[time_control] += 1
        
        # Track results by time control
        if result == '1-0':
            time_control_results[time_control]['wins'] += 1
        elif result == '0-1':
            time_control_results[time_control]['losses'] += 1
        else:
            time_control_results[time_control]['draws'] += 1
        
        # Estimate time per move from time control
        try:
            # Parse time control format: "minutes+increment" or "minutes"
            tc_parts = time_control.split('+')
            if len(tc_parts) >= 1:
                base_time = int(tc_parts[0])
                increment = int(tc_parts[1]) if len(tc_parts) > 1 else 0
                
                # Estimate avg time per move
                moves_estimate = 40  # Average game length
                estimated_time_per_move = (base_time / moves_estimate) + increment
                avg_time_per_move[time_control].append(estimated_time_per_move)
        except:
            pass
    
    # Calculate time management metrics
    total_games = len(games) if games else 1
    num_time_controls = len(time_controls)
    
    # Find primary time control
    primary_tc = max(time_controls.items(), key=lambda x: x[1]) if time_controls else ('Unknown', 0)
    primary_tc_percentage = (primary_tc[1] / total_games * 100) if total_games > 0 else 0
    
    # Time control diversity
    if num_time_controls > 3:
        time_control_type = 'very_diverse'
    elif num_time_controls > 2:
        time_control_type = 'diverse'
    elif num_time_controls > 1:
        time_control_type = 'mixed'
    else:
        time_control_type = 'focused'
    
    # Calculate win rates by time control
    time_control_performance = {}
    for tc, results in time_control_results.items():
        total = results['wins'] + results['draws'] + results['losses']
        if total > 0:
            win_rate = (results['wins'] / total * 100)
            draw_rate = (results['draws'] / total * 100)
            loss_rate = (results['losses'] / total * 100)
            
            time_control_performance[tc] = {
                'win_rate': win_rate,
                'draw_rate': draw_rate,
                'loss_rate': loss_rate,
                'games': total
            }
    
    return {
        'time_control_distribution': time_controls,
        'primary_time_control': primary_tc[0],
        'primary_tc_percentage': primary_tc_percentage,
        'time_control_variety': time_control_type,
        'num_time_controls': num_time_controls,
        'time_control_performance': time_control_performance
    }

def analyze_opening_variety(games) -> Dict[str, any]:
    """
    Analyze opening variety and repertoire.
    
    Args:
        games: List of chess game objects
    
    Returns:
        Dictionary with opening diversity metrics
    """
    openings = {}  # Format: "ECO - Opening Name"
    eco_codes = {}
    time_controls = {}
    results_by_opening = {}
    
    for game in games:
        headers = game.headers
        eco = headers.get('ECO', 'Unknown')
        opening = headers.get('Opening', 'Unknown')
        time_control = headers.get('TimeControl', 'Unknown')
        
        # Create opening key combining ECO and name
        if eco != 'Unknown' and opening != 'Unknown':
            opening_key = f"{eco} - {opening}"
        elif eco != 'Unknown':
            opening_key = eco
        else:
            opening_key = opening
        
        # Track opening frequency
        if opening_key not in openings:
            openings[opening_key] = 0
            eco_codes[opening_key] = eco
            results_by_opening[opening_key] = {'wins': 0, 'draws': 0, 'losses': 0}
        openings[opening_key] += 1
        
        # Track time control
        time_controls[time_control] = time_controls.get(time_control, 0) + 1
        
        # Track results
        result = headers.get('Result', '*')
        white = headers.get('White', '').lower()
        black = headers.get('Black', '').lower()
        
        # Determine if player is white or black (use first game to infer)
        # This is a simplification - ideally we'd have username
        is_white = True  # Default assumption
        
        if result == '1-0':
            winner = 'white'
        elif result == '0-1':
            winner = 'black'
        else:
            winner = 'draw'
        
        if winner == 'draw':
            results_by_opening[opening_key]['draws'] += 1
        elif (winner == 'white' and is_white) or (winner == 'black' and not is_white):
            results_by_opening[opening_key]['wins'] += 1
        else:
            results_by_opening[opening_key]['losses'] += 1
    
    # Calculate diversity metrics
    num_openings = len(openings)
    total_games = len(games) if games else 1
    opening_diversity = (num_openings / total_games * 100) if total_games > 0 else 0
    
    # Find most played opening
    most_played = max(openings.items(), key=lambda x: x[1]) if openings else ('None', 0)
    most_played_percentage = (most_played[1] / total_games * 100) if total_games > 0 else 0
    
    # Opening concentration (are they playing a limited repertoire?)
    if opening_diversity > 50:
        repertoire_type = 'very_diverse'
    elif opening_diversity > 30:
        repertoire_type = 'diverse'
    elif opening_diversity > 15:
        repertoire_type = 'moderate'
    else:
        repertoire_type = 'limited'
    
    return {
        'num_openings': num_openings,
        'opening_diversity_percent': opening_diversity,
        'most_played_opening': most_played[0],
        'most_played_count': most_played[1],
        'most_played_percentage': most_played_percentage,
        'repertoire_type': repertoire_type,
        'time_control_distribution': time_controls,
        'opening_stats': results_by_opening
    }