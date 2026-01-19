"""
Account-level behavioral metrics for Chess Detective v2.1
Non-accusatory, statistical analysis of player behavior.
"""

from .stats import (
    calculate_rating_progression,
    calculate_move_time_patterns,
    calculate_consistency_score,
    detect_game_clustering,
    calculate_opponent_strength_anomaly,
    calculate_rating_volatility,
    analyze_opening_variety,
    analyze_time_management
)

def analyze_account_behavior(games, username):
    ratings = []
    opponent_ratings = []
    move_times = []
    game_dates = []
    accuracies = []

    for game in games:
        headers = game.headers
        white = headers.get("White", "").lower()
        black = headers.get("Black", "").lower()

        is_player_white = white == username.lower()

        # Ratings
        player_elo = headers.get("WhiteElo" if is_player_white else "BlackElo")
        opponent_elo = headers.get("BlackElo" if is_player_white else "WhiteElo")

        try:
            if player_elo and opponent_elo:
                ratings.append(int(player_elo))
                opponent_ratings.append(int(opponent_elo))
        except:
            pass

        # Dates
        date = headers.get("Date")
        if date:
            game_dates.append(date)

        # Move count proxy for time patterns (safe approximation)
        move_count = len(list(game.mainline_moves()))
        if move_count > 0:
            move_times.append(move_count)

    results = {}

    # Rating volatility
    if ratings:
        results["rating_progression"] = calculate_rating_progression(ratings)
        results["rating_volatility"] = calculate_rating_volatility(ratings)

    # Move time patterns
    if move_times:
        results["time_patterns"] = calculate_move_time_patterns(move_times)

    # Opponent anomaly
    if ratings and opponent_ratings:
        results["opponent_strength_anomaly"] = calculate_opponent_strength_anomaly(
            ratings, opponent_ratings
        )

    # Game clustering
    if game_dates:
        results["game_clustering"] = detect_game_clustering(game_dates)

    # Time management analysis
    if games:
        results["time_management"] = analyze_time_management(games)

    # Opening variety analysis
    if games:
        results["opening_variety"] = analyze_opening_variety(games)

    return results
