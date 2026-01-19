"""
Network analysis for Chess Detective v2.2
Analyze player connection networks and relationships.
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict


class NetworkAnalyzer:
    """Analyze player networks and connections."""
    
    def __init__(self, games: List, username: str):
        """
        Initialize network analyzer.
        
        Args:
            games: List of chess game objects
            username: Central player username
        """
        self.games = games
        self.username = username.lower()
        self.opponents = defaultdict(int)
        self.opponent_results = defaultdict(lambda: {'wins': 0, 'draws': 0, 'losses': 0})
        self.common_opponents = defaultdict(set)
        self._build_network()
    
    def _build_network(self):
        """Build the opponent network."""
        for game in self.games:
            headers = game.headers
            white = headers.get("White", "").lower()
            black = headers.get("Black", "").lower()
            is_player_white = white == self.username
            
            opponent = black if is_player_white else white
            if opponent == self.username:
                continue  # Skip games against self
            
            # Count games against opponent
            self.opponents[opponent] += 1
            
            # Track results
            result = headers.get('Result', '*')
            if result == '1-0':
                if is_player_white:
                    self.opponent_results[opponent]['wins'] += 1
                else:
                    self.opponent_results[opponent]['losses'] += 1
            elif result == '0-1':
                if is_player_white:
                    self.opponent_results[opponent]['losses'] += 1
                else:
                    self.opponent_results[opponent]['wins'] += 1
            else:
                self.opponent_results[opponent]['draws'] += 1
    
    def get_top_opponents(self, n: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently played opponents.
        
        Args:
            n: Number of opponents to return
        
        Returns:
            List of (opponent, game_count) tuples
        """
        sorted_opponents = sorted(self.opponents.items(), key=lambda x: x[1], reverse=True)
        return sorted_opponents[:n]
    
    def get_opponent_statistics(self) -> Dict[str, Dict]:
        """
        Get detailed statistics against each opponent.
        
        Returns:
            Dictionary with statistics for each opponent
        """
        stats = {}
        
        for opponent, game_count in self.opponents.items():
            results = self.opponent_results[opponent]
            total = results['wins'] + results['draws'] + results['losses']
            
            if total > 0:
                win_rate = (results['wins'] / total * 100)
                draw_rate = (results['draws'] / total * 100)
                loss_rate = (results['losses'] / total * 100)
                score = results['wins'] + (results['draws'] * 0.5)
            else:
                win_rate = draw_rate = loss_rate = score = 0
            
            stats[opponent] = {
                'games': game_count,
                'wins': results['wins'],
                'draws': results['draws'],
                'losses': results['losses'],
                'win_rate': win_rate,
                'draw_rate': draw_rate,
                'loss_rate': loss_rate,
                'score': score
            }
        
        return stats
    
    def detect_playing_circle(self) -> Dict[str, List[str]]:
        """
        Detect if player plays within specific circles/groups.
        
        Returns:
            Dictionary with potential playing circles
        """
        circles = {}
        
        # Find groups of opponents who play each other frequently
        # This is a simplified analysis looking at common time controls
        
        for game in self.games:
            headers = game.headers
            white = headers.get("White", "").lower()
            black = headers.get("Black", "").lower()
            time_control = headers.get('TimeControl', 'Unknown')
            
            is_player_white = white == self.username
            opponent = black if is_player_white else white
            
            # Group by time control
            if time_control not in circles:
                circles[time_control] = set()
            
            circles[time_control].add(opponent)
        
        # Convert to list and calculate concentration
        result = {}
        for tc, opponents_set in circles.items():
            result[tc] = {
                'opponents_in_group': list(opponents_set),
                'num_opponents': len(opponents_set),
                'concentration_level': self._calculate_concentration(list(opponents_set))
            }
        
        return result
    
    def _calculate_concentration(self, opponents: List[str]) -> str:
        """
        Calculate opponent concentration level.
        
        Args:
            opponents: List of opponent names
        
        Returns:
            Concentration level string
        """
        if not opponents:
            return 'none'
        
        total_games = len(self.games)
        unique_opponents = len(opponents)
        
        concentration = (unique_opponents / total_games * 100) if total_games > 0 else 0
        
        if concentration > 50:
            return 'very_low'  # Many opponents relative to games
        elif concentration > 30:
            return 'low'
        elif concentration > 15:
            return 'moderate'
        elif concentration > 5:
            return 'high'
        else:
            return 'very_high'  # Few opponents, many games
    
    def detect_suspicious_patterns(self) -> Dict[str, List[Dict]]:
        """
        Detect suspicious patterns in playing network.
        
        Returns:
            Dictionary with potential suspicious patterns
        """
        patterns = defaultdict(list)
        
        # Pattern 1: Too many games against same opponent
        opponent_stats = self.get_opponent_statistics()
        for opponent, stats in opponent_stats.items():
            if stats['games'] > 20:
                concentration = (stats['games'] / len(self.games) * 100)
                patterns['high_concentration'].append({
                    'opponent': opponent,
                    'games': stats['games'],
                    'percentage': concentration,
                    'severity': 'high' if concentration > 15 else 'medium'
                })
        
        # Pattern 2: Unusual win rate against specific opponent
        for opponent, stats in opponent_stats.items():
            if stats['games'] > 5:  # Minimum games for statistical significance
                if stats['win_rate'] > 80 or stats['win_rate'] < 20:
                    patterns['unusual_win_rate'].append({
                        'opponent': opponent,
                        'win_rate': stats['win_rate'],
                        'games': stats['games'],
                        'severity': 'high' if stats['win_rate'] > 90 or stats['win_rate'] < 10 else 'medium'
                    })
        
        # Pattern 3: Limited opponent pool (plays same people repeatedly)
        unique_opponents = len(self.opponents)
        if unique_opponents < 5 and len(self.games) > 20:
            patterns['limited_circle'].append({
                'unique_opponents': unique_opponents,
                'total_games': len(self.games),
                'ratio': len(self.games) / unique_opponents if unique_opponents > 0 else 0,
                'severity': 'high'
            })
        
        return dict(patterns)
    
    def get_network_summary(self) -> Dict:
        """
        Get comprehensive network summary.
        
        Returns:
            Dictionary with complete network analysis
        """
        return {
            'player': self.username,
            'total_games': len(self.games),
            'unique_opponents': len(self.opponents),
            'top_opponents': self.get_top_opponents(10),
            'opponent_stats': self.get_opponent_statistics(),
            'playing_circles': self.detect_playing_circle(),
            'suspicious_patterns': self.detect_suspicious_patterns()
        }


def display_network_analysis(games, username: str):
    """
    Display network analysis results.
    
    Args:
        games: List of chess games
        username: Player username
    """
    print("\n" + "="*80)
    print(f"  NETWORK ANALYSIS - {username.upper()}")
    print("="*80 + "\n")
    
    analyzer = NetworkAnalyzer(games, username)
    summary = analyzer.get_network_summary()
    
    print(f"Total Games: {summary['total_games']}")
    print(f"Unique Opponents: {summary['unique_opponents']}\n")
    
    # Top Opponents
    print("-"*80)
    print("  TOP OPPONENTS")
    print("-"*80)
    top_opponents = summary['top_opponents']
    opponent_stats = summary['opponent_stats']
    
    if top_opponents:
        print(f"  {'Rank':<6} {'Opponent':<20} {'Games':<10} {'W-D-L':<20} {'Win %':<10}")
        print("  " + "-"*75)
        
        for rank, (opponent, game_count) in enumerate(top_opponents, 1):
            stats = opponent_stats.get(opponent, {})
            w = stats.get('wins', 0)
            d = stats.get('draws', 0)
            l = stats.get('losses', 0)
            wr = stats.get('win_rate', 0)
            
            print(f"  {rank:<6} {opponent:<20} {game_count:<10} {w}-{d}-{l:<18} {wr:<10.1f}%")
    
    # Playing Circles
    print("\n" + "-"*80)
    print("  PLAYING CIRCLES (by Time Control)")
    print("-"*80)
    circles = summary['playing_circles']
    
    for time_control, circle_data in circles.items():
        print(f"\n  {time_control}:")
        print(f"    Opponents: {circle_data['num_opponents']}")
        print(f"    Concentration: {circle_data['concentration_level'].upper()}")
    
    # Suspicious Patterns
    patterns = summary['suspicious_patterns']
    if patterns:
        print("\n" + "-"*80)
        print("  SUSPICIOUS PATTERNS DETECTED")
        print("-"*80)
        
        # High concentration
        if 'high_concentration' in patterns:
            print("\n  ⚠️  High Concentration (too many games vs same opponent):")
            for item in patterns['high_concentration'][:5]:
                print(f"    • {item['opponent']}: {item['games']} games ({item['percentage']:.1f}%) [{item['severity'].upper()}]")
        
        # Unusual win rates
        if 'unusual_win_rate' in patterns:
            print("\n  ⚠️  Unusual Win Rates:")
            for item in patterns['unusual_win_rate'][:5]:
                print(f"    • {item['opponent']}: {item['win_rate']:.1f}% ({item['games']} games) [{item['severity'].upper()}]")
        
        # Limited circle
        if 'limited_circle' in patterns:
            print("\n  ⚠️  Limited Playing Circle:")
            for item in patterns['limited_circle']:
                print(f"    • Only {item['unique_opponents']} opponents in {item['total_games']} games")
                print(f"    • Average {item['ratio']:.1f} games per opponent [HIGH]")
    else:
        print("\n  ✓ No suspicious patterns detected")
    
    print("\n" + "="*80 + "\n")
