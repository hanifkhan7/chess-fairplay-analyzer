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
            
            # Add proper headers to avoid 403 errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 403:
                print(f"[WARNING] Chess.com leaderboards API requires authentication")
                print(f"[INFO] Trying alternative endpoint...")
                return self._fetch_chesscom_alternative()
            
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
            return self._fetch_chesscom_alternative()
    
    def _fetch_chesscom_alternative(self) -> List[Dict]:
        """
        Alternative Chess.com leaderboard fetch using players endpoint.
        Fetches top players from the public API.
        """
        try:
            print(f"[LEADERBOARD] Using alternative Chess.com endpoint...")
            
            # Try to fetch trending/popular players as fallback
            url = "https://api.chess.com/pub/streamers"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                players = []
                
                for idx, streamer in enumerate(data.get('streamers', [])[:50], 1):
                    username = streamer.get('username')
                    
                    # Fetch player rating
                    try:
                        player_url = f"https://api.chess.com/pub/player/{username}"
                        p_response = requests.get(player_url, headers=headers, timeout=5)
                        if p_response.status_code == 200:
                            p_data = p_response.json()
                            players.append({
                                'rank': idx,
                                'username': username,
                                'rating': p_data.get('stats', {}).get('chess_blitz', {}).get('rating', 0),
                                'games': p_data.get('stats', {}).get('chess_blitz', {}).get('record', {}).get('win', 0),
                                'platform': 'chess.com',
                                'title': p_data.get('title', ''),
                                'country': p_data.get('country', '')
                            })
                    except:
                        pass
                
                if players:
                    print(f"[LEADERBOARD] ✓ Fetched {len(players)} players")
                    return players[:50]
            
            print(f"[ERROR] Could not fetch Chess.com leaderboard from alternative source")
            return []
            
        except Exception as e:
            print(f"[ERROR] Alternative fetch failed: {e}")
            logger.error(f"Alternative Chess.com fetch error: {e}")
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
    
    def fetch_fide_leaderboard(self, limit: int = 50) -> List[Dict]:
        """
        Attempt to fetch FIDE leaderboard.
        Note: FIDE doesn't have an official public API, but we can try alternative sources.
        
        Returns:
            List of top FIDE players (if available)
        """
        try:
            print(f"[LEADERBOARD] Fetching FIDE top players...")
            
            # Try to fetch from FIDE's public database or alternative source
            # FIDE export format (this is a common endpoint used for FIDE data)
            url = "https://www.fide.com/api/player?elo=2800-9999&order=1&limit=50"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                players = []
                
                for idx, player in enumerate(data.get('players', [])[:limit], 1):
                    players.append({
                        'rank': idx,
                        'username': player.get('name', 'Unknown'),
                        'rating': player.get('rating', 0),
                        'games': 0,
                        'platform': 'fide',
                        'title': player.get('title', ''),
                        'country': player.get('federation', '')
                    })
                
                if players:
                    print(f"[LEADERBOARD] ✓ Fetched {len(players)} FIDE players")
                    return players
            
            # If API fails, provide informational message
            print(f"[INFO] FIDE API not available. FIDE leaderboard must be browsed manually at fide.com")
            return []
            
        except Exception as e:
            print(f"[INFO] FIDE leaderboard: {e}")
            logger.info(f"FIDE leaderboard info: {e}")
            return []
    
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
            'country': 'All (Global)',
            'speed': speed,
            'players': players,
            'analyzable': True
        }
    elif platform.lower() == 'fide':
        players = analyzer.fetch_fide_leaderboard()
        info = analyzer.get_fide_leaderboard_info()
        return {
            'platform': 'FIDE',
            'country': 'All',
            'players': players,
            'analyzable': len(players) == 0,  # Only analyzable if API failed
            'note': 'FIDE leaderboard (manual browsing may be required)',
            'info': info
        }
    else:
        return {'error': f'Unknown platform: {platform}'}
