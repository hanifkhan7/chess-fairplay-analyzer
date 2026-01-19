"""
Multi-player comparison analyzer for Chess Detective v2.2
Compare statistics across multiple players to identify patterns and anomalies.
"""

from typing import List, Dict, Tuple
from .account_metrics import analyze_account_behavior
from .fetcher import fetch_player_games


class PlayerComparison:
    """Compare multiple players' statistics and patterns."""
    
    def __init__(self, usernames: List[str], max_games: int = 100):
        """
        Initialize player comparison.
        
        Args:
            usernames: List of Chess.com usernames to compare
            max_games: Maximum games to fetch per player
        """
        self.usernames = usernames
        self.max_games = max_games
        self.player_data = {}
        self.player_games = {}
    
    def fetch_all_players(self) -> bool:
        """
        Fetch games for all players.
        
        Returns:
            True if successful, False otherwise
        """
        for username in self.usernames:
            try:
                print(f"  Fetching {self.max_games} games for {username}...")
                games = fetch_player_games(username, max_games=self.max_games)
                if games:
                    self.player_games[username] = games
                    self.player_data[username] = analyze_account_behavior(games, username)
                else:
                    print(f"    ⚠️  No games found for {username}")
            except Exception as e:
                print(f"    ❌ Error fetching games for {username}: {e}")
                return False
        
        return len(self.player_data) > 0
    
    def get_rating_comparison(self) -> Dict[str, Dict]:
        """
        Compare ratings across players.
        
        Returns:
            Dictionary with rating statistics for each player
        """
        comparison = {}
        
        for username, games in self.player_games.items():
            if not games:
                continue
            
            ratings = []
            for game in games:
                headers = game.headers
                white = headers.get("White", "").lower()
                black = headers.get("Black", "").lower()
                is_player_white = white == username.lower()
                
                player_elo = headers.get("WhiteElo" if is_player_white else "BlackElo")
                try:
                    if player_elo:
                        ratings.append(int(player_elo))
                except:
                    pass
            
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                min_rating = min(ratings)
                max_rating = max(ratings)
                
                comparison[username] = {
                    'avg_rating': avg_rating,
                    'min_rating': min_rating,
                    'max_rating': max_rating,
                    'games_with_rating': len(ratings)
                }
        
        return comparison
    
    def get_winrate_comparison(self) -> Dict[str, Dict]:
        """
        Compare win rates across players.
        
        Returns:
            Dictionary with win rate statistics for each player
        """
        comparison = {}
        
        for username, games in self.player_games.items():
            if not games:
                continue
            
            wins = draws = losses = 0
            
            for game in games:
                result = game.headers.get('Result', '*')
                headers = game.headers
                white = headers.get("White", "").lower()
                black = headers.get("Black", "").lower()
                is_player_white = white == username.lower()
                
                if result == '1-0':
                    if is_player_white:
                        wins += 1
                    else:
                        losses += 1
                elif result == '0-1':
                    if is_player_white:
                        losses += 1
                    else:
                        wins += 1
                else:
                    draws += 1
            
            total = wins + draws + losses
            if total > 0:
                comparison[username] = {
                    'wins': wins,
                    'draws': draws,
                    'losses': losses,
                    'total_games': total,
                    'win_rate': (wins / total * 100),
                    'draw_rate': (draws / total * 100),
                    'loss_rate': (losses / total * 100),
                    'score': wins + (draws * 0.5)
                }
        
        return comparison
    
    def get_rating_volatility_comparison(self) -> Dict[str, Dict]:
        """
        Compare rating volatility across players.
        
        Returns:
            Dictionary with volatility metrics for each player
        """
        comparison = {}
        
        for username, data in self.player_data.items():
            volatility = data.get('rating_volatility', {})
            if volatility:
                comparison[username] = {
                    'volatility_score': volatility.get('volatility_score', 0),
                    'rating_trend': volatility.get('rating_trend', 'Unknown'),
                    'trend_direction': volatility.get('trend_direction', 'Unknown'),
                    'std_deviation': volatility.get('standard_deviation', 0)
                }
        
        return comparison
    
    def get_opening_comparison(self) -> Dict[str, Dict]:
        """
        Compare opening variety across players.
        
        Returns:
            Dictionary with opening statistics for each player
        """
        comparison = {}
        
        for username, data in self.player_data.items():
            openings = data.get('opening_variety', {})
            if openings:
                comparison[username] = {
                    'num_openings': openings.get('num_openings', 0),
                    'diversity': openings.get('opening_diversity_percent', 0),
                    'repertoire_type': openings.get('repertoire_type', 'Unknown'),
                    'most_played': openings.get('most_played_opening', 'Unknown'),
                    'most_played_pct': openings.get('most_played_percentage', 0)
                }
        
        return comparison
    
    def get_time_management_comparison(self) -> Dict[str, Dict]:
        """
        Compare time management across players.
        
        Returns:
            Dictionary with time management metrics for each player
        """
        comparison = {}
        
        for username, data in self.player_data.items():
            time_mgmt = data.get('time_management', {})
            if time_mgmt:
                comparison[username] = {
                    'primary_tc': time_mgmt.get('primary_time_control', 'Unknown'),
                    'primary_tc_pct': time_mgmt.get('primary_tc_percentage', 0),
                    'variety': time_mgmt.get('time_control_variety', 'Unknown'),
                    'num_tc': time_mgmt.get('num_time_controls', 0)
                }
        
        return comparison
    
    def detect_anomalies(self) -> Dict[str, List[Tuple[str, float]]]:
        """
        Detect statistical anomalies and outliers.
        
        Returns:
            Dictionary with anomalies detected for each player
        """
        anomalies = {}
        
        # Get all comparisons
        ratings = self.get_rating_comparison()
        winrates = self.get_winrate_comparison()
        volatility = self.get_rating_volatility_comparison()
        
        # Calculate averages for baseline
        avg_rating = sum([d['avg_rating'] for d in ratings.values()]) / len(ratings) if ratings else 0
        avg_winrate = sum([d['win_rate'] for d in winrates.values()]) / len(winrates) if winrates else 50
        avg_volatility = sum([d['volatility_score'] for d in volatility.values()]) / len(volatility) if volatility else 0
        
        for username in self.usernames:
            anomalies[username] = []
            
            # Rating anomaly
            if username in ratings:
                rating_diff = ratings[username]['avg_rating'] - avg_rating
                if abs(rating_diff) > 100:
                    anomalies[username].append(('Unusual Rating', abs(rating_diff)))
            
            # Win rate anomaly
            if username in winrates:
                winrate_diff = abs(winrates[username]['win_rate'] - avg_winrate)
                if winrate_diff > 10:
                    anomalies[username].append(('Unusual Win Rate', winrate_diff))
            
            # Volatility anomaly
            if username in volatility:
                vol_diff = abs(volatility[username]['volatility_score'] - avg_volatility)
                if vol_diff > 20:
                    anomalies[username].append(('High Volatility', volatility[username]['volatility_score']))
            
            # Sort by severity
            anomalies[username].sort(key=lambda x: x[1], reverse=True)
        
        return anomalies
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive comparison summary.
        
        Returns:
            Dictionary with all comparison data
        """
        return {
            'players': self.usernames,
            'rating_comparison': self.get_rating_comparison(),
            'winrate_comparison': self.get_winrate_comparison(),
            'volatility_comparison': self.get_rating_volatility_comparison(),
            'opening_comparison': self.get_opening_comparison(),
            'time_management_comparison': self.get_time_management_comparison(),
            'anomalies': self.detect_anomalies()
        }


def compare_players_display(usernames: List[str], max_games: int = 100):
    """
    Display multi-player comparison results.
    
    Args:
        usernames: List of usernames to compare
        max_games: Maximum games to fetch per player
    """
    print("\n" + "="*80)
    print(f"  MULTI-PLAYER COMPARISON - {len(usernames)} Players")
    print("="*80 + "\n")
    
    # Initialize comparison
    comparison = PlayerComparison(usernames, max_games)
    
    # Fetch all players
    print("Fetching game data...")
    if not comparison.fetch_all_players():
        print("❌ Failed to fetch data for any players")
        return
    
    print(f"\n✓ Successfully loaded data for {len(comparison.player_data)} players\n")
    
    # Get summary
    summary = comparison.get_summary()
    
    # Display Rating Comparison
    print("-"*80)
    print("  RATING COMPARISON")
    print("-"*80)
    ratings = summary['rating_comparison']
    if ratings:
        avg_ratings = sorted(ratings.items(), key=lambda x: x[1]['avg_rating'], reverse=True)
        print(f"  {'Player':<20} {'Avg Rating':<15} {'Min':<10} {'Max':<10} {'Games':<10}")
        print("  " + "-"*75)
        for player, data in avg_ratings:
            print(f"  {player:<20} {data['avg_rating']:<15.0f} {data['min_rating']:<10} {data['max_rating']:<10} {data['games_with_rating']:<10}")
    
    # Display Win Rate Comparison
    print("\n" + "-"*80)
    print("  WIN RATE COMPARISON")
    print("-"*80)
    winrates = summary['winrate_comparison']
    if winrates:
        sorted_wr = sorted(winrates.items(), key=lambda x: x[1]['win_rate'], reverse=True)
        print(f"  {'Player':<20} {'Win %':<12} {'Wins':<8} {'Draws':<8} {'Losses':<8} {'Games':<8}")
        print("  " + "-"*75)
        for player, data in sorted_wr:
            print(f"  {player:<20} {data['win_rate']:<12.1f}% {data['wins']:<8} {data['draws']:<8} {data['losses']:<8} {data['total_games']:<8}")
    
    # Display Rating Volatility
    print("\n" + "-"*80)
    print("  RATING VOLATILITY COMPARISON")
    print("-"*80)
    volatility = summary['volatility_comparison']
    if volatility:
        sorted_vol = sorted(volatility.items(), key=lambda x: x[1]['volatility_score'], reverse=True)
        print(f"  {'Player':<20} {'Volatility':<15} {'Trend':<15} {'Direction':<15}")
        print("  " + "-"*75)
        for player, data in sorted_vol:
            print(f"  {player:<20} {data['volatility_score']:<15.1f} {data['rating_trend']:<15} {data['trend_direction']:<15}")
    
    # Display Opening Analysis
    print("\n" + "-"*80)
    print("  OPENING REPERTOIRE COMPARISON")
    print("-"*80)
    openings = summary['opening_comparison']
    if openings:
        sorted_open = sorted(openings.items(), key=lambda x: x[1]['diversity'], reverse=True)
        print(f"  {'Player':<20} {'# Openings':<15} {'Diversity':<15} {'Type':<15}")
        print("  " + "-"*75)
        for player, data in sorted_open:
            print(f"  {player:<20} {data['num_openings']:<15} {data['diversity']:<15.1f}% {data['repertoire_type']:<15}")
    
    # Display Anomalies
    print("\n" + "-"*80)
    print("  DETECTED ANOMALIES & OUTLIERS")
    print("-"*80)
    anomalies = summary['anomalies']
    has_anomalies = False
    for player, anom_list in anomalies.items():
        if anom_list:
            has_anomalies = True
            print(f"\n  {player}:")
            for anomaly_type, severity in anom_list:
                print(f"    • {anomaly_type}: {severity:.1f}")
    
    if not has_anomalies:
        print("\n  ✓ No significant anomalies detected")
    
    print("\n" + "="*80 + "\n")
