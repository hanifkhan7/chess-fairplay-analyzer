"""
Tournament Inspector - Analyze head-to-head records and suspicious patterns
Detects suspicious wins, anomalies in ELO-based expectations, and match rigging
"""

import json
import math
from typing import List, Dict, Tuple
from datetime import datetime
import requests
import chess.pgn
import io
from pathlib import Path


class TournamentInspector:
    """Analyzes tournament/player group for suspicious activity"""
    
    def __init__(self):
        self.cache_dir = Path("cache/tournament")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
    
    def fetch_recent_games(self, username: str, max_games: int = 50) -> List[Dict]:
        """Fetch most recent games for a player from Chess.com"""
        try:
            print(f"[FETCH] Getting most recent {max_games} games for {username}...")
            
            # Chess.com API for games - add proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = f"https://api.chess.com/pub/player/{username}/games/archives"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"  [NOT FOUND] Player not found or API error: {response.status_code}")
                return []
            
            archives = response.json().get('archives', [])
            if not archives:
                print(f"  [EMPTY] No game archives for {username}")
                return []
            
            # Fetch from most recent archive first
            games = []
            for archive_url in reversed(archives):  # Start with most recent
                if len(games) >= max_games:
                    break
                
                print(f"  Fetching from {archive_url.split('/')[-2]}/{archive_url.split('/')[-1]}...")
                archive_response = requests.get(f"{archive_url}/pgn", headers=headers, timeout=10)
                
                if archive_response.status_code == 200:
                    # Parse PGN
                    pgn_text = archive_response.text
                    game_strings = pgn_text.split("\n\n[Event")
                    
                    for game_str in game_strings:
                        if len(games) >= max_games:
                            break
                        
                        if not game_str.strip():
                            continue
                        
                        try:
                            pgn_io = io.StringIO("[Event" + game_str if not game_str.startswith("[Event") else game_str)
                            game = chess.pgn.read_game(pgn_io)
                            
                            if game:
                                game_dict = {
                                    'white': game.headers.get('White', '?'),
                                    'black': game.headers.get('Black', '?'),
                                    'result': game.headers.get('Result', '*'),
                                    'white_elo': int(game.headers.get('WhiteElo', 0)) if game.headers.get('WhiteElo', '0').isdigit() else 0,
                                    'black_elo': int(game.headers.get('BlackElo', 0)) if game.headers.get('BlackElo', '0').isdigit() else 0,
                                    'time_control': game.headers.get('TimeControl', '?'),
                                    'date': game.headers.get('Date', '?'),
                                    'link': game.headers.get('Link', ''),
                                }
                                games.append(game_dict)
                        except:
                            continue
            
            print(f"  [OK] Got {len(games)} most recent games")
            return games[:max_games]
        
        except Exception as e:
            print(f"  [ERROR] Error fetching games: {e}")
            return []
    
    def calculate_win_probability(self, elo1: int, elo2: int) -> float:
        """Calculate expected win probability based on ELO difference"""
        if elo1 == 0 or elo2 == 0:
            return 0.5
        
        elo_diff = elo2 - elo1
        # Standard ELO formula
        probability = 1 / (1 + pow(10, elo_diff / 400))
        return probability
    
    def analyze_head_to_head(self, usernames: List[str], games_data: Dict[str, List]) -> Dict:
        """Analyze head-to-head records between players"""
        
        results = {
            'players': usernames,
            'matchups': {},
            'anomalies': [],
            'suspicious_patterns': []
        }
        
        # Create matchup table
        for u1 in usernames:
            for u2 in usernames:
                if u1 >= u2:  # Avoid duplicates
                    continue
                
                matchup_key = f"{u1} vs {u2}"
                u1_games = games_data.get(u1, [])
                u2_games = games_data.get(u2, [])
                
                # Find games between these two players
                head_to_head = []
                for game in u1_games:
                    white = game['white'].lower()
                    black = game['black'].lower()
                    
                    if (white == u1.lower() and black == u2.lower()) or \
                       (white == u2.lower() and black == u1.lower()):
                        head_to_head.append(game)
                
                if head_to_head:
                    # Analyze the matchup
                    u1_wins = 0
                    u2_wins = 0
                    draws = 0
                    
                    for game in head_to_head:
                        white = game['white'].lower()
                        result = game['result']
                        
                        if result == '1-0':
                            if white == u1.lower():
                                u1_wins += 1
                            else:
                                u2_wins += 1
                        elif result == '0-1':
                            if white == u1.lower():
                                u2_wins += 1
                            else:
                                u1_wins += 1
                        else:
                            draws += 1
                    
                    total = len(head_to_head)
                    u1_pct = (u1_wins / total * 100) if total > 0 else 0
                    
                    # Get average ELO
                    u1_avg_elo = sum([g['white_elo'] if g['white'].lower() == u1.lower() else g['black_elo'] 
                                     for g in head_to_head]) / len(head_to_head) if head_to_head else 0
                    u2_avg_elo = sum([g['black_elo'] if g['white'].lower() == u1.lower() else g['white_elo'] 
                                     for g in head_to_head]) / len(head_to_head) if head_to_head else 0
                    
                    # Calculate expected vs actual
                    expected_u1_prob = self.calculate_win_probability(u1_avg_elo, u2_avg_elo)
                    expected_u1_wins = expected_u1_prob * total
                    
                    # Check for anomalies
                    anomaly_score = 0
                    reason = []
                    
                    if abs(u1_wins - expected_u1_wins) > 2:
                        anomaly_score += 30
                        reason.append(f"Win count anomaly: expected {expected_u1_wins:.1f}, got {u1_wins}")
                    
                    if total >= 5 and u1_pct < 20:
                        anomaly_score += 20
                        reason.append(f"Extremely low win rate: {u1_pct:.1f}%")
                    
                    if total >= 5 and u1_pct > 80:
                        anomaly_score += 20
                        reason.append(f"Extremely high win rate: {u1_pct:.1f}%")
                    
                    results['matchups'][matchup_key] = {
                        'games': total,
                        f'{u1}_wins': u1_wins,
                        f'{u2}_wins': u2_wins,
                        'draws': draws,
                        f'{u1}_win_pct': u1_pct,
                        f'{u1}_avg_elo': u1_avg_elo,
                        f'{u2}_avg_elo': u2_avg_elo,
                        'expected_win_prob': expected_u1_prob * 100,
                        'anomaly_score': anomaly_score,
                        'anomaly_reason': reason if anomaly_score > 0 else []
                    }
                    
                    if anomaly_score > 0:
                        results['suspicious_patterns'].append({
                            'matchup': matchup_key,
                            'score': anomaly_score,
                            'reasons': reason
                        })
        
        return results
    
    def display_results(self, results: Dict):
        """Display tournament analysis results"""
        
        print("\n" + "=" * 80)
        print("TOURNAMENT INSPECTOR - HEAD-TO-HEAD ANALYSIS")
        print("=" * 80)
        
        print(f"\nPlayers Analyzed: {', '.join(results['players'])}")
        
        if results['matchups']:
            print("\n" + "-" * 80)
            print("HEAD-TO-HEAD RECORDS")
            print("-" * 80)
            
            for matchup_key, data in sorted(results['matchups'].items()):
                players = matchup_key.split(' vs ')
                p1, p2 = players[0], players[1]
                
                print(f"\n{matchup_key}")
                print(f"  Games: {data['games']}")
                print(f"  {p1} Record: {data[f'{p1}_wins']}-{data[f'{p2}_wins']}-{data['draws']} ({data[f'{p1}_win_pct']:.1f}%)")
                print(f"  ELO: {p1}={data[f'{p1}_avg_elo']:.0f}, {p2}={data[f'{p2}_avg_elo']:.0f}")
                print(f"  Expected {p1} Win Rate: {data['expected_win_prob']:.1f}%")
                
                if data['anomaly_score'] > 0:
                    print(f"  [ALERT] ANOMALY SCORE: {data['anomaly_score']}/100")
                    for reason in data['anomaly_reason']:
                        print(f"     - {reason}")
        
        if results['suspicious_patterns']:
            print("\n" + "-" * 80)
            print("SUSPICIOUS PATTERNS DETECTED")
            print("-" * 80)
            
            for pattern in sorted(results['suspicious_patterns'], key=lambda x: x['score'], reverse=True):
                print(f"\n[WARNING] {pattern['matchup']} - Score: {pattern['score']}/100")
                for reason in pattern['reasons']:
                    print(f"    {reason}")
        else:
            print("\n[OK] No suspicious patterns detected")
        
        print("\n" + "=" * 80)
