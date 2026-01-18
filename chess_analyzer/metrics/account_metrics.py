"""
Account Metrics Analyzer - Provides comprehensive account statistics
Includes account age, recent activity, rating progression, and account health
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class AccountMetricsAnalyzer:
    """Analyzes account-level metrics like age, activity, and rating trends."""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def analyze_account_metrics(self, games: List, player_stats: Dict) -> Dict:
        """
        Analyze comprehensive account metrics.
        
        Args:
            games: List of game objects with headers
            player_stats: Player statistics from Chess.com API
        
        Returns:
            Dictionary with account metrics
        """
        metrics = {
            'account_age': self._calculate_account_age(player_stats),
            'activity_dashboard': self._analyze_activity(games, player_stats),
            'rating_volatility': self._calculate_rating_volatility(player_stats),
            'win_rate_by_bracket': self._analyze_win_rate_by_bracket(games),
            'game_volume': self._analyze_game_volume(games),
            'account_health_score': 0.0
        }
        
        # Calculate overall account health score
        metrics['account_health_score'] = self._calculate_health_score(metrics)
        
        return metrics
    
    def _calculate_account_age(self, player_stats: Dict) -> Dict:
        """Calculate account age and creation date."""
        joined = player_stats.get('joined', 0)
        
        if joined == 0:
            return {
                'joined_timestamp': None,
                'joined_date': 'Unknown',
                'account_age_days': None,
                'account_age_text': 'Unknown'
            }
        
        joined_datetime = datetime.fromtimestamp(joined)
        today = datetime.now()
        account_age = (today - joined_datetime).days
        
        # Friendly text format
        if account_age < 30:
            age_text = f"New account ({account_age} days)"
        elif account_age < 365:
            months = account_age // 30
            age_text = f"{months} months old"
        else:
            years = account_age // 365
            months = (account_age % 365) // 30
            if months > 0:
                age_text = f"{years} year{'s' if years != 1 else ''} {months} months"
            else:
                age_text = f"{years} year{'s' if years != 1 else ''}"
        
        return {
            'joined_timestamp': joined,
            'joined_date': joined_datetime.strftime('%Y-%m-%d'),
            'account_age_days': account_age,
            'account_age_text': age_text,
            'new_account_flag': account_age < 90  # Red flag if very new
        }
    
    def _analyze_activity(self, games: List, player_stats: Dict) -> Dict:
        """Analyze recent activity dashboard."""
        if not games:
            return {
                'total_games': 0,
                'rapid_games': 0,
                'blitz_games': 0,
                'bullet_games': 0,
                'games_last_30_days': 0,
                'games_last_7_days': 0,
                'games_today': 0,
                'last_game_date': None,
                'activity_level': 'Inactive'
            }
        
        # Count games by time control
        time_controls = {
            'rapid': 0,
            'blitz': 0,
            'bullet': 0,
            'classical': 0
        }
        
        # Dates for activity analysis
        today = datetime.now()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        
        games_in_7d = 0
        games_in_30d = 0
        games_today = 0
        last_game_date = None
        
        for game in games:
            tc = game.headers.get('TimeControl', '')
            date_str = game.headers.get('Date', '')
            
            # Parse time control
            if tc:
                if tc.startswith('60') or tc == '360' or (tc.count('+') and int(tc.split('+')[0]) >= 300):
                    time_controls['rapid'] += 1
                elif tc.startswith('300') or tc.startswith('180'):
                    time_controls['blitz'] += 1
                elif int(tc.split('+')[0]) if '+' in tc else int(tc) < 180:
                    time_controls['bullet'] += 1
                else:
                    time_controls['classical'] += 1
            
            # Parse date
            if date_str and date_str != '?':
                try:
                    game_date = datetime.strptime(date_str, '%Y.%m.%d')
                    if not last_game_date or game_date > last_game_date:
                        last_game_date = game_date
                    
                    if game_date >= last_7_days:
                        games_in_7d += 1
                    if game_date >= last_30_days:
                        games_in_30d += 1
                    if game_date.date() == today.date():
                        games_today += 1
                except:
                    pass
        
        # Determine activity level
        if games_today > 0:
            activity_level = "Very Active (Playing today)"
        elif games_in_7d > 3:
            activity_level = "Active (Multiple games this week)"
        elif games_in_7d > 0:
            activity_level = "Moderate (Played this week)"
        elif games_in_30d > 0:
            activity_level = "Light (Played this month)"
        else:
            activity_level = "Inactive"
        
        return {
            'total_games': len(games),
            'rapid_games': time_controls['rapid'],
            'blitz_games': time_controls['blitz'],
            'bullet_games': time_controls['bullet'],
            'classical_games': time_controls['classical'],
            'games_last_30_days': games_in_30d,
            'games_last_7_days': games_in_7d,
            'games_today': games_today,
            'last_game_date': last_game_date.strftime('%Y-%m-%d') if last_game_date else 'Never',
            'activity_level': activity_level
        }
    
    def _calculate_rating_volatility(self, player_stats: Dict) -> Dict:
        """Calculate rating volatility - sudden rating changes indicate suspicion."""
        stats = {
            'current_rapid': 0,
            'current_blitz': 0,
            'current_bullet': 0,
            'peak_rapid': 0,
            'peak_blitz': 0,
            'peak_bullet': 0,
            'volatility_score': 0.0,
            'recent_jumps': []
        }
        
        # Extract current and peak ratings
        if 'rapid' in player_stats:
            stats['current_rapid'] = player_stats['rapid'].get('rating', 0)
            stats['peak_rapid'] = player_stats['rapid'].get('best', {}).get('rating', 0)
        
        if 'blitz' in player_stats:
            stats['current_blitz'] = player_stats['blitz'].get('rating', 0)
            stats['peak_blitz'] = player_stats['blitz'].get('best', {}).get('rating', 0)
        
        if 'bullet' in player_stats:
            stats['current_bullet'] = player_stats['bullet'].get('rating', 0)
            stats['peak_bullet'] = player_stats['bullet'].get('best', {}).get('rating', 0)
        
        # Calculate volatility
        # (This would require historical rating data from API)
        # For now, we calculate based on current vs peak
        all_ratings = [
            stats['current_rapid'], stats['current_blitz'], stats['current_bullet']
        ]
        valid_ratings = [r for r in all_ratings if r > 0]
        
        if valid_ratings:
            avg_current = sum(valid_ratings) / len(valid_ratings)
            peaks = [
                stats['peak_rapid'], stats['peak_blitz'], stats['peak_bullet']
            ]
            valid_peaks = [p for p in peaks if p > 0]
            avg_peak = sum(valid_peaks) / len(valid_peaks) if valid_peaks else avg_current
            
            # Volatility is how much current differs from peak
            volatility = ((avg_peak - avg_current) / avg_peak * 100) if avg_peak > 0 else 0
            stats['volatility_score'] = max(0, min(100, volatility))
        
        return stats
    
    def _analyze_win_rate_by_bracket(self, games: List) -> Dict:
        """Analyze win rates against different rating brackets."""
        brackets = {}
        
        for game in games:
            white = game.headers.get('White', '').lower()
            black = game.headers.get('Black', '').lower()
            result = game.headers.get('Result', '*')
            
            # Get opponent rating
            white_elo = game.headers.get('WhiteElo', '?')
            black_elo = game.headers.get('BlackElo', '?')
            
            if white_elo != '?' and black_elo != '?':
                try:
                    opponent_elo = int(black_elo) if white.lower() != 'computer' else int(white_elo)
                    bracket = f"{(opponent_elo // 100) * 100}-{(opponent_elo // 100) * 100 + 99}"
                    
                    if bracket not in brackets:
                        brackets[bracket] = {'wins': 0, 'losses': 0, 'draws': 0, 'count': 0}
                    
                    brackets[bracket]['count'] += 1
                    
                    if result == '1-0':
                        brackets[bracket]['wins'] += 1
                    elif result == '0-1':
                        brackets[bracket]['losses'] += 1
                    else:
                        brackets[bracket]['draws'] += 1
                except:
                    pass
        
        # Calculate win rates
        bracket_stats = {}
        for bracket, data in sorted(brackets.items()):
            if data['count'] > 0:
                wr = (data['wins'] / data['count'] * 100)
                bracket_stats[bracket] = {
                    'win_rate': wr,
                    'record': f"{data['wins']}-{data['losses']}-{data['draws']}",
                    'games': data['count']
                }
        
        return bracket_stats
    
    def _analyze_game_volume(self, games: List) -> Dict:
        """Analyze game volume and playing patterns."""
        if not games:
            return {'avg_games_per_day': 0, 'peak_game_day': None, 'volume_level': 'Low'}
        
        # Group games by date
        games_by_date = {}
        for game in games:
            date_str = game.headers.get('Date', '')
            if date_str and date_str != '?':
                try:
                    game_date = datetime.strptime(date_str, '%Y.%m.%d').date()
                    if game_date not in games_by_date:
                        games_by_date[game_date] = 0
                    games_by_date[game_date] += 1
                except:
                    pass
        
        if not games_by_date:
            return {'avg_games_per_day': 0, 'peak_game_day': None, 'volume_level': 'Unknown'}
        
        # Calculate statistics
        avg_per_day = len(games) / len(games_by_date) if games_by_date else 0
        peak_day = max(games_by_date.items(), key=lambda x: x[1])
        
        if avg_per_day > 20:
            volume_level = "Very High - Suspicious activity"
        elif avg_per_day > 10:
            volume_level = "High"
        elif avg_per_day > 5:
            volume_level = "Moderate"
        elif avg_per_day > 2:
            volume_level = "Low"
        else:
            volume_level = "Very Low"
        
        return {
            'avg_games_per_day': round(avg_per_day, 2),
            'peak_game_day': peak_day[0].strftime('%Y-%m-%d'),
            'peak_game_count': peak_day[1],
            'days_with_games': len(games_by_date),
            'volume_level': volume_level
        }
    
    def _calculate_health_score(self, metrics: Dict) -> float:
        """
        Calculate overall account health score (0-100).
        Lower scores indicate more suspicious activity.
        """
        score = 100.0
        
        # New account penalty
        account_age = metrics['account_age']
        if account_age['new_account_flag']:
            score -= 20
        
        # Activity score
        activity = metrics['activity_dashboard']
        if activity['games_last_30_days'] == 0 and account_age['account_age_days'] > 7:
            score -= 10  # Inactive accounts are less suspicious
        
        # Rating volatility penalty
        volatility = metrics['rating_volatility']['volatility_score']
        if volatility > 30:
            score -= 15
        
        # Game volume penalty (very high volume is suspicious)
        volume = metrics['game_volume']
        if 'Very High' in volume.get('volume_level', ''):
            score -= 25
        
        return max(0, min(100, score))
