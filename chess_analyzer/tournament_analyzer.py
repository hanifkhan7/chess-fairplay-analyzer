"""
Tournament Forensics Analysis Module
Analyzes concluded tournaments to detect suspicious activity patterns.
"""

import requests
import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import statistics
from io import StringIO
import chess.pgn

logger = logging.getLogger(__name__)

class TournamentAnalyzer:
    """Analyzes tournament results for suspicious activity patterns."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.elo_k_factor = 32  # Standard K-factor for ELO calculation
        
    # ===== ELO PROBABILITY CALCULATIONS =====
    
    def calculate_win_probability(self, player_elo: int, opponent_elo: int) -> float:
        """
        Calculate expected win probability based on ELO difference.
        Uses standard ELO formula.
        
        Args:
            player_elo: Player's ELO rating
            opponent_elo: Opponent's ELO rating
            
        Returns:
            Probability (0-1) that player wins
        """
        elo_diff = opponent_elo - player_elo
        return 1 / (1 + 10 ** (elo_diff / 400))
    
    def calculate_tournament_win_probability(self, player_elo: int, avg_opponent_elo: int, 
                                          num_games: int) -> float:
        """
        Calculate probability of winning entire tournament.
        
        Args:
            player_elo: Player's ELO
            avg_opponent_elo: Average opponent ELO
            num_games: Number of games in tournament
            
        Returns:
            Probability of winning tournament
        """
        win_prob_per_game = self.calculate_win_probability(player_elo, avg_opponent_elo)
        tournament_win_prob = win_prob_per_game ** num_games
        return tournament_win_prob
    
    def flag_suspicious_results(self, tournament_results: Dict) -> List[Dict]:
        """
        Identify results that violate ELO expectations significantly.
        
        Args:
            tournament_results: Tournament data with player results
            
        Returns:
            List of suspicious results with probability info
        """
        suspicious = []
        
        for player_result in tournament_results.get('results', []):
            player_elo = player_result.get('rating', 0)
            wins = player_result.get('wins', 0)
            losses = player_result.get('losses', 0)
            draws = player_result.get('draws', 0)
            games_played = wins + losses + draws
            
            if games_played == 0:
                continue
            
            # Calculate average opponent ELO (approximate)
            avg_opponent_elo = tournament_results.get('avg_rating', player_elo)
            
            # Expected wins
            win_prob = self.calculate_win_probability(player_elo, avg_opponent_elo)
            expected_wins = win_prob * games_played
            actual_wins = wins + (draws * 0.5)  # Count draws as half wins
            
            # Calculate deviation from expected
            if expected_wins > 0:
                win_rate_deviation = (actual_wins - expected_wins) / expected_wins
            else:
                win_rate_deviation = 0
            
            # Flag if deviation > 20% (significant overperformance)
            if abs(win_rate_deviation) > 0.2:
                suspicious.append({
                    'player': player_result.get('username'),
                    'elo': player_elo,
                    'wins': wins,
                    'losses': losses,
                    'draws': draws,
                    'expected_wins': round(expected_wins, 1),
                    'actual_wins': actual_wins,
                    'deviation_percent': round(win_rate_deviation * 100, 1),
                    'avg_opponent_elo': avg_opponent_elo,
                    'severity': 'HIGH' if abs(win_rate_deviation) > 0.4 else 'MEDIUM',
                    'suspicion': 'OUTPERFORMING' if win_rate_deviation > 0 else 'UNDERPERFORMING'
                })
        
        return sorted(suspicious, key=lambda x: abs(x['deviation_percent']), reverse=True)
    
    # ===== TOURNAMENT FETCHING =====
    
    def fetch_chess_com_tournaments(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch concluded tournaments from Chess.com.
        
        Args:
            days_back: How many days back to search
            
        Returns:
            List of tournament data
        """
        try:
            print(f"[TOURNAMENT] Fetching Chess.com tournaments from last {days_back} days...")
            
            url = "https://api.chess.com/pub/tournaments"
            
            # Note: Chess.com doesn't have a direct tournament API
            # We'll use club tournaments or arenas if available
            tournaments = []
            
            print("[TOURNAMENT] Note: Chess.com tournament data limited. Using alternative sources.")
            return tournaments
            
        except Exception as e:
            logger.error(f"Error fetching Chess.com tournaments: {e}")
            print(f"[ERROR] {e}")
            return []
    
    def fetch_lichess_tournaments(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch concluded tournaments from Lichess.
        
        Args:
            days_back: How many days back to search
            
        Returns:
            List of tournament data
        """
        try:
            print(f"[TOURNAMENT] Fetching Lichess tournaments from last {days_back} days...")
            
            url = "https://lichess.org/api/tournament"
            headers = {'Accept': 'application/json'}
            
            # Fetch active/finished tournaments
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[ERROR] Lichess API error: {response.status_code}")
                return []
            
            data = response.json()
            tournaments = []
            
            # Filter for concluded tournaments
            for tournament in data.get('finished', []):
                created_date = datetime.fromtimestamp(tournament.get('createdAt', 0) / 1000)
                if (datetime.now() - created_date).days <= days_back:
                    tournaments.append({
                        'id': tournament.get('id'),
                        'name': tournament.get('fullName'),
                        'variant': tournament.get('variant', 'standard'),
                        'speed': tournament.get('speed'),
                        'status': 'finished',
                        'created': created_date,
                        'nb_players': tournament.get('nbPlayers', 0),
                        'duration_mins': tournament.get('durationMinutes', 0)
                    })
            
            print(f"[TOURNAMENT] Found {len(tournaments)} tournaments")
            return tournaments
            
        except Exception as e:
            logger.error(f"Error fetching Lichess tournaments: {e}")
            print(f"[ERROR] {e}")
            return []
    
    def get_tournament_standings(self, tournament_id: str, source: str = 'lichess') -> Dict:
        """
        Get tournament standings and results.
        
        Args:
            tournament_id: Tournament ID
            source: 'lichess' or 'chess.com'
            
        Returns:
            Tournament standings data
        """
        try:
            if source == 'lichess':
                url = f"https://lichess.org/api/tournament/{tournament_id}"
                headers = {'Accept': 'application/json'}
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    return {}
                
                data = response.json()
                
                # Extract standings
                standings = {
                    'tournament_name': data.get('fullName'),
                    'variant': data.get('variant'),
                    'speed': data.get('speed'),
                    'avg_rating': 0,  # Will calculate
                    'results': []
                }
                
                for standing in data.get('standing', {}).get('players', []):
                    standings['results'].append({
                        'rank': standing.get('rank'),
                        'username': standing.get('name'),
                        'rating': standing.get('rating', 0),
                        'score': standing.get('score', 0),
                        'wins': 0,  # These would need game-level data
                        'losses': 0,
                        'draws': 0
                    })
                
                # Calculate average rating
                ratings = [r.get('rating', 0) for r in standings['results']]
                if ratings:
                    standings['avg_rating'] = sum(ratings) // len(ratings)
                
                return standings
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching tournament standings: {e}")
            print(f"[ERROR] {e}")
            return {}
    
    def get_top_finishers(self, tournament_standings: Dict, top_n: int = 10) -> List[Dict]:
        """
        Get top N finishers from tournament.
        
        Args:
            tournament_standings: Tournament standings data
            top_n: Number of top finishers to return
            
        Returns:
            List of top finishers
        """
        results = tournament_standings.get('results', [])
        return sorted(results, key=lambda x: x.get('rank', float('inf')))[:top_n]
    
    # ===== DETAILED ANALYSIS =====
    
    def analyze_player_performance(self, player_name: str, tournament_games: List) -> Dict:
        """
        Deeply analyze a player's performance in tournament games.
        
        Args:
            player_name: Player username
            tournament_games: List of games player participated in
            
        Returns:
            Detailed performance analysis
        """
        analysis = {
            'player': player_name,
            'total_games': len(tournament_games),
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'average_opponent_elo': 0,
            'performance_rating': 0,
            'consistency_score': 0,
            'anomalies': []
        }
        
        if not tournament_games:
            return analysis
        
        opponent_elos = []
        results = []
        
        for game in tournament_games:
            # Determine if player won, lost, or drew
            white = game.headers.get('White', '')
            black = game.headers.get('Black', '')
            result = game.headers.get('Result', '*')
            
            is_white = white == player_name
            is_black = black == player_name
            
            if not (is_white or is_black):
                continue
            
            # Get opponent info
            opponent = black if is_white else white
            opponent_elo_str = game.headers.get('BlackElo' if is_white else 'WhiteElo', '0')
            try:
                opponent_elo = int(opponent_elo_str)
            except:
                opponent_elo = 0
            
            opponent_elos.append(opponent_elo)
            
            # Track result
            if result == '1-0':
                if is_white:
                    analysis['wins'] += 1
                    results.append(1)
                else:
                    analysis['losses'] += 1
                    results.append(0)
            elif result == '0-1':
                if is_white:
                    analysis['losses'] += 1
                    results.append(0)
                else:
                    analysis['wins'] += 1
                    results.append(1)
            elif result == '1/2-1/2':
                analysis['draws'] += 1
                results.append(0.5)
            
            # Check for anomalies
            if opponent_elo > 0:
                expected_win_prob = self.calculate_win_probability(
                    int(game.headers.get('WhiteElo' if is_white else 'BlackElo', '0')),
                    opponent_elo
                )
                
                actual_result = 1 if (is_white and result == '1-0') or (is_black and result == '0-1') else 0
                
                # Flag if unexpected result
                if actual_result == 1 and expected_win_prob < 0.3:
                    analysis['anomalies'].append({
                        'type': 'UPSET_WIN',
                        'opponent': opponent,
                        'opponent_elo': opponent_elo,
                        'win_probability': round(expected_win_prob * 100, 1),
                        'description': f"Won against {opponent} ({opponent_elo} ELO) with only {round(expected_win_prob * 100, 1)}% expected win probability"
                    })
                elif actual_result == 0 and expected_win_prob > 0.7:
                    analysis['anomalies'].append({
                        'type': 'UNEXPECTED_LOSS',
                        'opponent': opponent,
                        'opponent_elo': opponent_elo,
                        'win_probability': round(expected_win_prob * 100, 1),
                        'description': f"Lost to {opponent} ({opponent_elo} ELO) despite {round(expected_win_prob * 100, 1)}% expected win probability"
                    })
        
        # Calculate averages
        if opponent_elos:
            analysis['average_opponent_elo'] = sum(opponent_elos) // len(opponent_elos)
        
        # Calculate consistency
        if results:
            variance = statistics.variance(results) if len(results) > 1 else 0
            analysis['consistency_score'] = round(100 - (variance * 100), 1)
        
        return analysis


def analyze_tournament(tournament_id: str, source: str = 'lichess', config: Optional[Dict] = None) -> Dict:
    """
    Main function to analyze a tournament for suspicious activity.
    
    Args:
        tournament_id: Tournament ID
        source: 'lichess' or 'chess.com'
        config: Configuration
        
    Returns:
        Comprehensive tournament analysis
    """
    analyzer = TournamentAnalyzer(config)
    
    print(f"\n[TOURNAMENT ANALYSIS] Starting forensics analysis...")
    print(f"Tournament ID: {tournament_id}")
    print(f"Source: {source}")
    
    # Get tournament standings
    standings = analyzer.get_tournament_standings(tournament_id, source)
    if not standings:
        print("[ERROR] Could not fetch tournament standings")
        return {}
    
    # Get top 10 finishers
    top_finishers = analyzer.get_top_finishers(standings, top_n=10)
    print(f"[TOURNAMENT] Found {len(top_finishers)} top finishers")
    
    # Flag suspicious results
    suspicious = analyzer.flag_suspicious_results(standings)
    
    # Compile report
    report = {
        'tournament_name': standings.get('tournament_name'),
        'source': source,
        'total_players': len(standings.get('results', [])),
        'top_finishers': top_finishers,
        'suspicious_results': suspicious,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    return report
