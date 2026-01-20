"""
Enhanced Tournament Forensics Analysis
- Analyzes Chess.com arena tournaments and Lichess tournaments
- Detects suspicious activity patterns
- Calculates ELO probability violations
"""

import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TournamentForensics:
    """Analyzes tournament results for suspicious patterns."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
    def extract_tournament_id(self, tournament_input: str) -> str:
        """
        Extract tournament ID from URL or ID.
        
        Args:
            tournament_input: URL like https://www.chess.com/play/arena/4653407 or just ID
            
        Returns:
            Tournament ID
        """
        # If it's a URL, extract the ID
        if 'chess.com' in tournament_input:
            match = re.search(r'/arena/(\d+)', tournament_input)
            if match:
                return match.group(1)
        elif 'lichess.org' in tournament_input:
            match = re.search(r'/tournament/([a-zA-Z0-9]+)', tournament_input)
            if match:
                return match.group(1)
        
        # Otherwise return as-is
        return tournament_input.strip('/')
    
    def fetch_chesscom_arena(self, arena_id: str) -> Dict:
        """
        Fetch Chess.com arena/tournament data.
        
        Note: Chess.com's tournament API requires paid access.
        We provide alternative options instead.
        
        Args:
            arena_id: Arena/Tournament ID
            
        Returns:
            Tournament data with results or helpful message
        """
        print(f"[TOURNAMENT] Analyzing Chess.com arena {arena_id}...")
        print("[TOURNAMENT] ⚠️  Chess.com tournament API requires paid access")
        print("[TOURNAMENT] Alternative options:")
        print("   1. Use Lichess tournaments (free API access)")
        print("   2. Provide tournament data manually")
        print("   3. Use Chess.com games API with specific usernames")
        
        return {}
    
    def fetch_lichess_tournament(self, tournament_id: str) -> Dict:
        """
        Fetch Lichess tournament data.
        
        Args:
            tournament_id: Lichess tournament ID
            
        Returns:
            Tournament data with results
        """
        try:
            print(f"[TOURNAMENT] Fetching Lichess tournament {tournament_id}...")
            
            url = f"https://lichess.org/api/tournament/{tournament_id}"
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                print(f"[ERROR] Tournament {tournament_id} not found")
                return {}
            
            if response.status_code != 200:
                print(f"[ERROR] Lichess API error: {response.status_code}")
                return {}
            
            try:
                data = response.json()
            except:
                print(f"[ERROR] Could not parse API response")
                return {}
            
            if data:
                print(f"[TOURNAMENT] ✓ Found tournament: {data.get('fullName', 'Unknown')}")
            
            return data
            
        except Exception as e:
            print(f"[ERROR] Could not fetch tournament: {e}")
            logger.error(f"Error fetching Lichess tournament: {e}")
            return {}
    
    def extract_standings(self, tournament_data: Dict, source: str = 'lichess') -> List[Dict]:
        """
        Extract standings from tournament data.
        
        Args:
            tournament_data: Raw tournament data
            source: 'lichess' or 'chess.com'
            
        Returns:
            List of player results
        """
        standings = []
        
        if source == 'lichess' and 'standing' in tournament_data:
            standing_data = tournament_data['standing']
            
            # Get players from different possible formats
            players = standing_data.get('players', [])
            
            for idx, player in enumerate(players, 1):
                standings.append({
                    'rank': idx,
                    'username': player.get('name', player.get('username', 'Unknown')),
                    'elo': player.get('rating', 0),
                    'score': player.get('score', 0),
                    'games': player.get('gameCount', 0),
                    'win_pct': (player.get('score', 0) / max(player.get('gameCount', 1), 1)) * 100
                })
        
        return standings
    
    def calculate_elo_probability(self, player_elo: int, opponent_elo: int) -> float:
        """
        Calculate win probability based on ELO difference.
        
        Args:
            player_elo: Player's ELO
            opponent_elo: Opponent's ELO
            
        Returns:
            Win probability (0-1)
        """
        elo_diff = opponent_elo - player_elo
        return 1 / (1 + 10 ** (elo_diff / 400))
    
    def analyze_standings(self, standings: List[Dict], tournament_name: str = "") -> Dict:
        """
        Analyze tournament standings for suspicious patterns.
        
        Args:
            standings: List of player results
            tournament_name: Tournament name for reporting
            
        Returns:
            Analysis results with flags
        """
        analysis = {
            'tournament_name': tournament_name,
            'total_players': len(standings),
            'anomalies': [],
            'summary': {}
        }
        
        if not standings:
            return analysis
        
        # Calculate average ELO
        elos = [s['elo'] for s in standings if s.get('elo', 0) > 0]
        avg_elo = sum(elos) / len(elos) if elos else 0
        
        analysis['summary']['average_elo'] = round(avg_elo, 0)
        analysis['summary']['elo_range'] = (min(elos), max(elos)) if elos else (0, 0)
        
        # Check top finishers
        print(f"\n[ANALYSIS] Examining top 10 finishers...")
        
        for i, player in enumerate(standings[:10], 1):
            elo = player.get('elo', 0)
            score = player.get('score', 0)
            games = player.get('games', 1)
            
            if games == 0:
                continue
            
            # Calculate expected performance
            elo_diff_from_avg = elo - avg_elo
            
            # Flag significant ELO differences
            if elo_diff_from_avg < -200:  # Much weaker player winning
                prob = self.calculate_elo_probability(elo, avg_elo)
                anomalies_strength = f"Weaker player (Δ{elo_diff_from_avg:.0f}) won tournament. Win probability: {prob*100:.1f}%"
                
                analysis['anomalies'].append({
                    'rank': i,
                    'player': player['username'],
                    'elo': elo,
                    'type': 'elo_violation',
                    'severity': 'HIGH',
                    'description': anomalies_strength,
                    'probability_pct': round(prob * 100, 1)
                })
                
                print(f"  🚩 #{i} {player['username']} (ELO: {elo})")
                print(f"     {anomalies_strength}")
            
            # Check for unusually high scores
            if games > 0:
                expected_score = (score / games) * 100
                if expected_score > 90:  # Over 90% win rate
                    analysis['anomalies'].append({
                        'rank': i,
                        'player': player['username'],
                        'elo': elo,
                        'type': 'high_score',
                        'severity': 'MEDIUM',
                        'description': f"Unusually high win rate: {expected_score:.1f}%",
                        'win_rate': round(expected_score, 1)
                    })
                    print(f"  ⚠️  #{i} {player['username']} - High win rate: {expected_score:.1f}%")
        
        return analysis
    
    def generate_report(self, analysis: Dict) -> str:
        """
        Generate a detailed forensics report.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Formatted report
        """
        report = f"""
{'='*70}
TOURNAMENT FORENSICS ANALYSIS REPORT
{'='*70}

Tournament: {analysis.get('tournament_name', 'Unknown')}
Total Players: {analysis.get('total_players', 0)}

SUMMARY:
  Average ELO: {analysis['summary'].get('average_elo', 'N/A')}
  ELO Range: {analysis['summary'].get('elo_range', (0, 0))}

ANOMALIES DETECTED: {len(analysis['anomalies'])}
"""
        
        if analysis['anomalies']:
            report += f"\n{'FLAGGED RESULTS:':^70}\n{'-'*70}\n"
            
            for anomaly in analysis['anomalies']:
                severity = anomaly.get('severity', 'UNKNOWN')
                emoji = '🚩' if severity == 'HIGH' else '⚠️'
                
                report += f"""
{emoji} Rank #{anomaly['rank']}: {anomaly['player']} (ELO: {anomaly['elo']})
   Type: {anomaly['type'].upper()}
   Severity: {severity}
   Details: {anomaly['description']}
"""
        
        report += f"\n{'='*70}\n"
        return report

def analyze_tournament(tournament_input: str, config: Optional[Dict] = None) -> Dict:
    """
    Main function to analyze a tournament.
    
    Args:
        tournament_input: Tournament URL or ID
        config: Configuration
        
    Returns:
        Analysis results
    """
    forensics = TournamentForensics(config)
    
    # Extract tournament ID
    tournament_id = forensics.extract_tournament_id(tournament_input)
    print(f"\n[TOURNAMENT] Tournament ID extracted: {tournament_id}")
    
    # Determine source
    if 'chess.com' in tournament_input.lower():
        print("[TOURNAMENT] Source: Chess.com")
        tournament_data = forensics.fetch_chesscom_arena(tournament_id)
        source = 'chess.com'
    else:
        print("[TOURNAMENT] Source: Lichess")
        tournament_data = forensics.fetch_lichess_tournament(tournament_id)
        source = 'lichess'
    
    if not tournament_data or tournament_data == {}:
        return {
            'error': 'Could not fetch tournament data',
            'tournament_id': tournament_id,
            'source': source
        }
    
    # Extract standings
    try:
        standings = forensics.extract_standings(tournament_data, source)
    except Exception as e:
        logger.error(f"Error extracting standings: {e}")
        print(f"[ERROR] Error parsing tournament data: {e}")
        return {
            'error': 'Could not parse tournament standings',
            'tournament_id': tournament_id,
            'source': source
        }
    
    if not standings:
        return {
            'error': 'Could not extract tournament standings',
            'tournament_id': tournament_id,
            'source': source
        }
    
    # Analyze
    tournament_name = tournament_data.get('fullName', f'Tournament {tournament_id}')
    analysis = forensics.analyze_standings(standings, tournament_name)
    
    return analysis
