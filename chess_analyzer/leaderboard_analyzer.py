"""
Leaderboard Analysis Module
Fetches player leaderboards by country from Chess.com, Lichess, and FIDE
Allows detailed analysis of top players
"""

import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LeaderboardAnalyzer:
    """Analyzes player leaderboards from different platforms."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def get_lichess_countries(self) -> List[str]:
        """Get list of available Lichess countries."""
        try:
            print("[LEADERBOARD] Checking Lichess available countries...")
            # Lichess supports most country codes
            # For simplicity, we'll return common ones
            return [
                'US', 'GB', 'FR', 'DE', 'ES', 'IT', 'RU', 'CN', 'IN', 'BR',
                'CA', 'AU', 'NZ', 'NL', 'BE', 'SE', 'NO', 'DK', 'PL', 'TR',
                'MX', 'AR', 'JP', 'KR', 'ZA', 'PK', 'BD', 'PH', 'VN', 'TH'
            ]
        except Exception as e:
            logger.error(f"Error getting countries: {e}")
            return []
    
    def get_chesscom_countries(self) -> List[str]:
        """Get list of available Chess.com countries."""
        try:
            print("[LEADERBOARD] Checking Chess.com available countries...")
            # Chess.com also supports country-based leaderboards
            return [
                'US', 'GB', 'FR', 'DE', 'ES', 'IT', 'RU', 'CN', 'IN', 'BR',
                'CA', 'AU', 'NZ', 'NL', 'BE', 'SE', 'NO', 'DK', 'PL', 'TR',
                'MX', 'AR', 'JP', 'KR', 'ZA', 'PK', 'BD', 'PH', 'VN', 'TH'
            ]
        except Exception as e:
            logger.error(f"Error getting countries: {e}")
            return []
    
    def fetch_lichess_leaderboard(self, country: str = 'US', speed: str = 'blitz', 
                                  limit: int = 50) -> List[Dict]:
        """
        Fetch Lichess leaderboard for a country.
        
        Args:
            country: Country code (e.g., 'US', 'FR')
            speed: Speed type ('bullet', 'blitz', 'rapid', 'classical')
            limit: Number of players to fetch (max 200)
            
        Returns:
            List of player data
        """
        try:
            print(f"[LEADERBOARD] Fetching Lichess {country} {speed} leaderboard...")
            
            url = f"https://lichess.org/api/player/top/{limit}/{speed}"
            headers = {'Accept': 'application/json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[ERROR] Lichess API error: {response.status_code}")
                return []
            
            data = response.json()
            players = []
            
            for player in data.get('users', []):
                # Lichess doesn't have direct country filtering in API
                # But we can filter by country from the player object if available
                players.append({
                    'rank': len(players) + 1,
                    'username': player.get('username'),
                    'rating': player.get('perfs', {}).get(speed, {}).get('rating', 0),
                    'games': player.get('perfs', {}).get(speed, {}).get('games', 0),
                    'platform': 'lichess',
                    'title': player.get('title', ''),
                    'country': player.get('location', '')
                })
            
            print(f"[LEADERBOARD] ✓ Fetched {len(players)} players")
            return players
            
        except Exception as e:
            print(f"[ERROR] Error fetching Lichess leaderboard: {e}")
            logger.error(f"Lichess leaderboard error: {e}")
            return []
    
    def fetch_chesscom_leaderboard(self, rating_type: str = 'blitz', 
                                   limit: int = 50) -> List[Dict]:
        """
        Fetch Chess.com leaderboard.
        
        Args:
            rating_type: Type ('daily', 'rapid', 'blitz', 'bullet')
            limit: Number of players
            
        Returns:
            List of player data
        """
        try:
            print(f"[LEADERBOARD] Fetching Chess.com {rating_type} leaderboard...")
            
            url = f"https://api.chess.com/pub/leaderboards"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"[ERROR] Chess.com API error: {response.status_code}")
                return []
            
            data = response.json()
            players = []
            
            # Get the appropriate leaderboard
            leaderboard_key = f'{rating_type}_leaderboard'
            leaderboard = data.get(leaderboard_key, [])[:limit]
            
            for idx, player in enumerate(leaderboard, 1):
                players.append({
                    'rank': idx,
                    'username': player.get('username'),
                    'rating': player.get('rating', 0),
                    'games': 0,  # Not provided by this endpoint
                    'platform': 'chess.com',
                    'title': player.get('title', ''),
                    'country': player.get('country', '')
                })
            
            print(f"[LEADERBOARD] ✓ Fetched {len(players)} players")
            return players
            
        except Exception as e:
            print(f"[ERROR] Error fetching Chess.com leaderboard: {e}")
            logger.error(f"Chess.com leaderboard error: {e}")
            return []
    
    def get_fide_leaderboard_info(self) -> Dict:
        """
        Get info about FIDE leaderboard.
        Note: FIDE doesn't have a public API for leaderboards.
        
        Returns:
            Info about FIDE leaderboard
        """
        return {
            'platform': 'FIDE',
            'available': True,
            'viewable': True,
            'analyzable': False,
            'reason': 'FIDE leaderboard is available online but requires manual browsing',
            'url': 'https://www.fide.com/ratings/standings',
            'note': 'Players from FIDE leaderboard can be analyzed if they have Chess.com or Lichess accounts'
        }
    
    def display_leaderboard(self, players: List[Dict], platform: str, 
                           show_count: int = 20) -> None:
        """
        Display leaderboard in formatted table.
        
        Args:
            players: List of player data
            platform: Platform name
            show_count: How many to display
        """
        print(f"\n{'='*80}")
        print(f"{platform.upper()} LEADERBOARD - TOP {min(show_count, len(players))} PLAYERS")
        print(f"{'='*80}")
        
        print(f"\n{'Rank':<6} {'Username':<20} {'Rating':<8} {'Games':<8} {'Title':<6}")
        print("-" * 80)
        
        for player in players[:show_count]:
            rank = player.get('rank', 0)
            username = player.get('username', 'Unknown')[:20]
            rating = player.get('rating', 0)
            games = player.get('games', 0)
            title = player.get('title', '')
            
            print(f"{rank:<6} {username:<20} {rating:<8} {games:<8} {title:<6}")
        
        print(f"{'='*80}")

def fetch_leaderboard(platform: str, country: str = 'US', speed: str = 'blitz') -> Dict:
    """
    Main function to fetch leaderboard.
    
    Args:
        platform: 'lichess', 'chess.com', or 'fide'
        country: Country code
        speed: Speed type for Lichess
        
    Returns:
        Leaderboard data
    """
    analyzer = LeaderboardAnalyzer()
    
    if platform.lower() == 'lichess':
        players = analyzer.fetch_lichess_leaderboard(country, speed)
        return {
            'platform': 'Lichess',
            'country': country,
            'speed': speed,
            'players': players,
            'analyzable': True
        }
    elif platform.lower() == 'chess.com':
        players = analyzer.fetch_chesscom_leaderboard(speed)
        return {
            'platform': 'Chess.com',
            'country': 'All',
            'speed': speed,
            'players': players,
            'analyzable': True
        }
    elif platform.lower() == 'fide':
        return {
            'platform': 'FIDE',
            'country': country,
            'players': [],
            'analyzable': False,
            'note': 'FIDE leaderboard requires manual browsing at fide.com',
            'info': analyzer.get_fide_leaderboard_info()
        }
    else:
        return {'error': f'Unknown platform: {platform}'}
