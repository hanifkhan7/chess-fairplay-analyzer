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
        Detect statistical anomalies and outliers with enhanced sensitivity.
        
        Returns:
            Dictionary with anomalies detected for each player
        """
        anomalies = {}
        
        # Get all comparisons
        ratings = self.get_rating_comparison()
        winrates = self.get_winrate_comparison()
        volatility = self.get_rating_volatility_comparison()
        openings = self.get_opening_comparison()
        time_mgmt = self.get_time_management_comparison()
        
        # Calculate averages for baseline
        avg_rating = sum([d['avg_rating'] for d in ratings.values()]) / len(ratings) if ratings else 0
        avg_winrate = sum([d['win_rate'] for d in winrates.values()]) / len(winrates) if winrates else 50
        avg_volatility = sum([d['volatility_score'] for d in volatility.values()]) / len(volatility) if volatility else 0
        avg_diversity = sum([d['diversity'] for d in openings.values()]) / len(openings) if openings else 50
        
        # Calculate standard deviations for better outlier detection
        if ratings and len(ratings) > 1:
            import statistics
            rating_values = [d['avg_rating'] for d in ratings.values()]
            rating_std = statistics.stdev(rating_values) if len(rating_values) > 1 else 0
        else:
            rating_std = 100
        
        for username in self.usernames:
            anomalies[username] = []
            
            # Enhanced Rating anomaly (2+ standard deviations)
            if username in ratings:
                rating_diff = ratings[username]['avg_rating'] - avg_rating
                if rating_std > 0 and abs(rating_diff) > 2 * rating_std:
                    anomalies[username].append(('Extreme Rating Difference', abs(rating_diff)))
                elif abs(rating_diff) > 150:
                    anomalies[username].append(('Unusual Rating', abs(rating_diff)))
            
            # Enhanced Win rate anomaly
            if username in winrates:
                winrate_diff = abs(winrates[username]['win_rate'] - avg_winrate)
                if winrate_diff > 15:
                    severity = "CRITICAL" if winrate_diff > 25 else "HIGH"
                    anomalies[username].append((f'Extreme Win Rate [{severity}]', winrate_diff))
                elif winrate_diff > 10:
                    anomalies[username].append(('Unusual Win Rate', winrate_diff))
            
            # Enhanced Volatility anomaly
            if username in volatility:
                vol_diff = abs(volatility[username]['volatility_score'] - avg_volatility)
                if vol_diff > 30:
                    anomalies[username].append(('CRITICAL Volatility', volatility[username]['volatility_score']))
                elif vol_diff > 20:
                    anomalies[username].append(('High Volatility', volatility[username]['volatility_score']))
            
            # Opening diversity anomaly
            if username in openings:
                div_diff = abs(openings[username]['diversity'] - avg_diversity)
                if div_diff > 30:
                    anomalies[username].append(('Unusual Opening Diversity', openings[username]['diversity']))
            
            # Single time control focus anomaly
            if username in time_mgmt:
                primary_pct = time_mgmt[username]['primary_tc_pct']
                if primary_pct > 70:
                    anomalies[username].append(('Extreme Time Control Focus', primary_pct))
            
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
    
    def estimate_iq(self) -> Dict[str, Dict]:
        """
        Estimate 'Chess IQ' based on multiple factors.
        Factors include: rating, accuracy, consistency, time management, opening knowledge
        
        Returns:
            Dictionary with IQ estimates for each player
        """
        iq_scores = {}
        
        for player in self.player_data:
            data = self.player_data[player]
            games = self.player_games.get(player, [])
            
            # Base score from rating (normalized to 100-200 scale)
            rating = data.get('avg_rating', 1200)
            rating_score = min(200, 50 + (rating - 800) / 10)  # 800 rating = 50 IQ, 2200 = 200 IQ
            
            # Accuracy/move quality bonus
            accuracy = data.get('avg_accuracy', 50)
            accuracy_bonus = accuracy * 0.5  # Up to +50 IQ points
            
            # Consistency (low volatility = smart play)
            volatility_data = data.get('rating_volatility', {})
            volatility = volatility_data.get('volatility_score', 50) if isinstance(volatility_data, dict) else 50
            consistency_bonus = max(0, 30 - (volatility * 0.3))  # Up to +30 IQ points
            
            # Win rate against stronger opponents
            win_rate = data.get('win_rate', 50)
            win_bonus = (win_rate - 50) * 0.3  # Bonus for beating stronger opponents
            
            # Time management (faster decisions = confidence/pattern recognition)
            avg_move_time = data.get('avg_move_time', 5)
            time_bonus = min(20, 40 / avg_move_time if avg_move_time > 0 else 0)  # Faster = smarter
            
            # Calculate final IQ (capped at ~200)
            estimated_iq = min(200, max(50, 
                rating_score + accuracy_bonus + consistency_bonus + win_bonus + time_bonus
            ))
            
            iq_scores[player] = {
                'estimated_iq': estimated_iq,
                'rating_component': rating_score,
                'accuracy_component': accuracy_bonus,
                'consistency_component': consistency_bonus,
                'competitive_component': win_bonus,
                'time_component': time_bonus
            }
        
        return iq_scores


def compare_players_display(usernames: List[str], max_games: int = 100):
    """
    Display multi-player comparison results with enhanced anomaly detection.
    
    Args:
        usernames: List of usernames to compare
        max_games: Maximum games to fetch per player
    """
    print("\n" + "="*90)
    print(f"  MULTI-PLAYER COMPARISON - {len(usernames)} Players")
    print("="*90 + "\n")
    
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
    
    # Calculate and display IQ estimates
    print("-"*90)
    print("  ESTIMATED CHESS IQ (Fun Factor! :)")
    print("-"*90)
    iq_scores = comparison.estimate_iq()
    if iq_scores:
        sorted_iq = sorted(iq_scores.items(), key=lambda x: x[1]['estimated_iq'], reverse=True)
        print(f"  {'Player':<20} {'Chess IQ':<12} {'Components':<55}")
        print("  " + "-"*85)
        for player, iq_data in sorted_iq:
            iq = iq_data['estimated_iq']
            
            # IQ classification
            if iq >= 180:
                category = "GENIUS"
            elif iq >= 160:
                category = "Very Superior"
            elif iq >= 140:
                category = "Superior"
            elif iq >= 120:
                category = "High Average"
            elif iq >= 100:
                category = "Average"
            elif iq >= 80:
                category = "Low Average"
            else:
                category = "Below Average"
            
            components = f"Rating:{iq_data['rating_component']:+.0f} Accuracy:{iq_data['accuracy_component']:+.0f} Consistency:{iq_data['consistency_component']:+.0f}"
            print(f"  {player:<20} {iq:<12.0f} {components:<55} ({category})")
    
    # Display Rating Comparison
    print("\n" + "-"*90)
    print("  RATING COMPARISON")
    print("-"*90)
    ratings = summary['rating_comparison']
    if ratings:
        avg_ratings = sorted(ratings.items(), key=lambda x: x[1]['avg_rating'], reverse=True)
        print(f"  {'Player':<20} {'Avg Rating':<15} {'Range':<20} {'Games':<10}")
        print("  " + "-"*85)
        for player, data in avg_ratings:
            rating_range = f"{data['min_rating']}-{data['max_rating']}"
            print(f"  {player:<20} {data['avg_rating']:<15.0f} {rating_range:<20} {data['games_with_rating']:<10}")
    
    # Display Win Rate Comparison
    print("\n" + "-"*90)
    print("  WIN RATE COMPARISON")
    print("-"*90)
    winrates = summary['winrate_comparison']
    if winrates:
        sorted_wr = sorted(winrates.items(), key=lambda x: x[1]['win_rate'], reverse=True)
        print(f"  {'Player':<20} {'Win %':<12} {'Record (W-D-L)':<20} {'Score':<10}")
        print("  " + "-"*85)
        for player, data in sorted_wr:
            record = f"{data['wins']}-{data['draws']}-{data['losses']}"
            print(f"  {player:<20} {data['win_rate']:<12.1f}% {record:<20} {data['score']:<10.1f}")
    
    # Display Rating Volatility
    print("\n" + "-"*90)
    print("  RATING VOLATILITY & TREND ANALYSIS")
    print("-"*90)
    volatility = summary['volatility_comparison']
    if volatility:
        sorted_vol = sorted(volatility.items(), key=lambda x: x[1]['volatility_score'], reverse=True)
        print(f"  {'Player':<20} {'Volatility':<15} {'Std Dev':<12} {'Trend':<12} {'Direction':<12}")
        print("  " + "-"*85)
        for player, data in sorted_vol:
            trend_indicator = "📈" if data['trend_direction'] == 'Upward' else "📉" if data['trend_direction'] == 'Downward' else "➡️"
            print(f"  {player:<20} {data['volatility_score']:<15.1f} {data['std_deviation']:<12.1f} {data['rating_trend']:<12} {trend_indicator}")
    
    # Display Opening Analysis
    print("\n" + "-"*90)
    print("  OPENING REPERTOIRE COMPARISON")
    print("-"*90)
    openings = summary['opening_comparison']
    if openings:
        sorted_open = sorted(openings.items(), key=lambda x: x[1]['diversity'], reverse=True)
        print(f"  {'Player':<20} {'# Openings':<15} {'Diversity':<15} {'Type':<20}")
        print("  " + "-"*85)
        for player, data in sorted_open:
            print(f"  {player:<20} {data['num_openings']:<15} {data['diversity']:<15.1f}% {data['repertoire_type']:<20}")
    
    # Display Anomalies with Enhanced Detection
    print("\n" + "-"*90)
    print("  DETECTED ANOMALIES & OUTLIERS (ENHANCED)")
    print("-"*90)
    anomalies = summary['anomalies']
    has_anomalies = False
    
    for player in sorted(anomalies.keys()):
        anom_list = anomalies[player]
        if anom_list:
            has_anomalies = True
            severity_icon = "🚨" if any("CRITICAL" in a[0] for a in anom_list) else "⚠️"
            print(f"\n  {severity_icon} {player}:")
            for anomaly_type, severity in anom_list[:5]:  # Show top 5 anomalies
                severity_color = "CRITICAL" if severity > 30 else "HIGH" if severity > 20 else "MODERATE"
                print(f"     • {anomaly_type}: {severity:.1f}")
    
    if not has_anomalies:
        print("\n  ✓ No significant anomalies detected - players appear consistent")
    
    print("\n" + "="*90 + "\n")
