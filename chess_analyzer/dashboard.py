"""
Dashboard for displaying account metrics and analytics for Chess Detective v2.1
"""

from datetime import datetime
from .account_metrics import analyze_account_behavior
from .fetcher import fetch_player_games


def format_percentage(value: float) -> str:
    """Format a value as percentage."""
    return f"{value:.1f}%" if value else "N/A"


def format_rating(value: int) -> str:
    """Format a rating value."""
    return f"{value}" if value else "N/A"


def print_dashboard_header(username: str):
    """Print dashboard header."""
    print("\n" + "="*70)
    print(f"  CHESS DETECTIVE ACCOUNT METRICS DASHBOARD - {username.upper()}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


def print_section_header(title: str):
    """Print a section header."""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)


def display_account_summary(games, username):
    """Display account summary metrics."""
    if not games:
        print("No games found for this player.")
        return
    
    # Basic stats
    total_games = len(games)
    wins = 0
    draws = 0
    losses = 0
    
    for game in games:
        result = game.headers.get('Result', '*')
        if result == '1-0':
            wins += 1
        elif result == '0-1':
            losses += 1
        else:
            draws += 1
    
    print_section_header("ACCOUNT SUMMARY")
    print(f"  Total Games:        {total_games}")
    print(f"  Wins:               {wins} ({wins/total_games*100:.1f}%)")
    print(f"  Draws:              {draws} ({draws/total_games*100:.1f}%)")
    print(f"  Losses:             {losses} ({losses/total_games*100:.1f}%)")
    
    # Calculate win rate
    score = wins + (draws * 0.5)
    win_rate = (score / total_games * 100) if total_games > 0 else 0
    print(f"  Score:              {score}/{total_games} ({win_rate:.1f}%)")


def display_rating_metrics(account_data):
    """Display rating-related metrics."""
    if 'rating_volatility' not in account_data:
        return
    
    volatility = account_data['rating_volatility']
    progression = account_data.get('rating_progression', {})
    
    print_section_header("RATING ANALYSIS")
    
    if volatility:
        print(f"  Volatility Score:   {volatility.get('volatility_score', 0):.1f}/100")
        print(f"  Rating Trend:       {volatility.get('rating_trend', 'N/A').upper()}")
        print(f"  Trend Direction:    {volatility.get('trend_direction', 'N/A').upper()}")
        print(f"  Std Deviation:      {volatility.get('standard_deviation', 0):.2f}")
    
    if progression:
        print(f"  Avg Rating Change:  {progression.get('avg_change', 0):.1f}")
        print(f"  Max Rating Jump:    {progression.get('max_change', 0)}")
        suspicious = progression.get('suspicious', False)
        print(f"  Suspicious Jumps:   {'YES' if suspicious else 'NO'}")


def display_time_management(account_data):
    """Display time management metrics."""
    if 'time_management' not in account_data:
        return
    
    time_mgmt = account_data['time_management']
    
    print_section_header("TIME MANAGEMENT")
    
    primary_tc = time_mgmt.get('primary_time_control', 'Unknown')
    primary_pct = time_mgmt.get('primary_tc_percentage', 0)
    variety = time_mgmt.get('time_control_variety', 'Unknown').upper()
    
    print(f"  Primary Time Control:  {primary_tc} ({primary_pct:.1f}%)")
    print(f"  Variety:               {variety}")
    print(f"  Time Controls Used:    {time_mgmt.get('num_time_controls', 0)}")
    
    # Performance by time control
    performance = time_mgmt.get('time_control_performance', {})
    if performance:
        print(f"\n  Performance by Time Control:")
        for tc, stats in list(performance.items())[:5]:  # Show top 5
            win_rate = stats.get('win_rate', 0)
            games = stats.get('games', 0)
            print(f"    {tc:20s}: {win_rate:5.1f}% ({games} games)")


def display_opening_analysis(account_data):
    """Display opening analysis metrics."""
    if 'opening_variety' not in account_data:
        return
    
    openings = account_data['opening_variety']
    
    print_section_header("OPENING ANALYSIS")
    
    diversity = openings.get('opening_diversity_percent', 0)
    repertoire = openings.get('repertoire_type', 'Unknown').upper()
    num_openings = openings.get('num_openings', 0)
    most_played = openings.get('most_played_opening', 'Unknown')
    most_played_pct = openings.get('most_played_percentage', 0)
    
    print(f"  Opening Diversity:    {diversity:.1f}%")
    print(f"  Repertoire Type:      {repertoire}")
    print(f"  Total Openings:       {num_openings}")
    print(f"  Most Played Opening:  {most_played}")
    print(f"  Most Played %:        {most_played_pct:.1f}%")
    
    # Time control distribution
    tc_dist = openings.get('time_control_distribution', {})
    if tc_dist:
        print(f"\n  Time Control Distribution:")
        for tc, count in list(tc_dist.items())[:5]:
            pct = (count / sum(tc_dist.values()) * 100) if tc_dist else 0
            print(f"    {tc:20s}: {count} games ({pct:.1f}%)")


def display_opponent_analysis(account_data):
    """Display opponent strength analysis."""
    if 'opponent_strength_anomaly' not in account_data:
        return
    
    anomaly = account_data['opponent_strength_anomaly']
    clustering = account_data.get('game_clustering', {})
    
    print_section_header("OPPONENT & BEHAVIOR ANALYSIS")
    
    print(f"  Opponent Strength Anomaly: {anomaly:.1f}/100")
    
    if clustering:
        clustering_score = clustering.get('clustering_score', 0)
        is_clustered = clustering.get('is_clustered', False)
        max_games = clustering.get('max_games_per_day', 0)
        days_played = clustering.get('days_played', 0)
        
        print(f"  Game Clustering Score:     {clustering_score:.1f}/100")
        print(f"  Games Clustered:           {'YES' if is_clustered else 'NO'}")
        print(f"  Max Games Per Day:         {max_games}")
        print(f"  Days Played:               {days_played}")


def display_quick_dashboard(username: str):
    """Display quick dashboard view."""
    print_dashboard_header(username)
    
    # Fetch games
    print("Fetching games...")
    games = fetch_player_games(username, max_games=100)
    
    if not games:
        print("No games found!")
        return
    
    print(f"Analyzing {len(games)} games...")
    
    # Analyze account behavior
    account_data = analyze_account_behavior(games, username)
    
    # Display sections
    display_account_summary(games, username)
    display_rating_metrics(account_data)
    display_time_management(account_data)
    display_opening_analysis(account_data)
    display_opponent_analysis(account_data)
    
    # Footer
    print("\n" + "="*70)
    print("  Dashboard complete.")
    print("="*70 + "\n")


def display_dashboard_from_games(games, username: str):
    """Display dashboard from already-loaded games."""
    if not games:
        print("No games provided!")
        return
    
    print_dashboard_header(username)
    print(f"Analyzing {len(games)} games...\n")
    
    # Analyze account behavior
    account_data = analyze_account_behavior(games, username)
    
    # Display sections
    display_account_summary(games, username)
    display_rating_metrics(account_data)
    display_time_management(account_data)
    display_opening_analysis(account_data)
    display_opponent_analysis(account_data)
    
    # Footer
    print("\n" + "="*70)
    print("  Dashboard complete.")
    print("="*70 + "\n")
