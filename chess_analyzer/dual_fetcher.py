"""
Dual-platform game fetcher supporting both Chess.com and Lichess.
Seamlessly integrates games from both sources for unified analysis.
"""
import requests
import chess.pgn
import json
import logging
from io import StringIO
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

def fetch_dual_platform_games(
    username: str,
    max_games: int = 50,
    platforms: Optional[List[str]] = None,
    config: Optional[Dict] = None
) -> Tuple[List[chess.pgn.Game], Dict[str, int]]:
    """
    Fetch games from both Chess.com and Lichess for a player.
    
    Args:
        username: Player username (same on both platforms)
        max_games: Maximum total games to fetch
        platforms: Which platforms to fetch from ['chess.com', 'lichess']. Default: both
        config: Configuration dictionary
    
    Returns:
        Tuple of (list of games, dict with platform counts)
    
    Example:
        games, counts = fetch_dual_platform_games('hikaru', max_games=50)
        # counts = {'chess.com': 30, 'lichess': 20}
    """
    if config is None:
        config = {}
    
    if platforms is None:
        platforms = ['chess.com', 'lichess']
    
    all_games = []
    platform_counts = {'chess.com': 0, 'lichess': 0}
    
    # Calculate how many games to fetch from each platform
    games_per_platform = max_games // len(platforms) if platforms else max_games
    remainder = max_games % len(platforms) if platforms else 0
    
    print(f"\n[DUAL-FETCH] Fetching from {', '.join(platforms).title()}")
    print(f"[DUAL-FETCH] Target: {max_games} games total")
    
    # Fetch from Chess.com if requested
    if 'chess.com' in platforms:
        try:
            fetch_amount = games_per_platform + (remainder if 'chess.com' == platforms[0] else 0)
            print(f"\n[CHESS.COM] Fetching up to {fetch_amount} games...")
            
            from .fetcher import fetch_player_games as fetch_chess_com
            chess_com_games = fetch_chess_com(username, fetch_amount, config)
            
            print(f"[CHESS.COM] Retrieved {len(chess_com_games)} games")
            all_games.extend(chess_com_games)
            platform_counts['chess.com'] = len(chess_com_games)
            
        except Exception as e:
            print(f"[CHESS.COM] Error: {str(e)}")
            logger.error(f"Chess.com fetch failed: {e}")
    
    # Fetch from Lichess if requested
    if 'lichess' in platforms:
        try:
            fetch_amount = games_per_platform + (remainder if 'lichess' == platforms[-1] else 0)
            print(f"\n[LICHESS] Fetching up to {fetch_amount} games...")
            
            games, count = fetch_lichess_games(username, fetch_amount, config)
            print(f"[LICHESS] Retrieved {len(games)} games")
            all_games.extend(games)
            platform_counts['lichess'] = count
            
        except Exception as e:
            print(f"[LICHESS] Error: {str(e)}")
            logger.error(f"Lichess fetch failed: {e}")
    
    # Summary
    print(f"\n[SUMMARY] Total games fetched: {len(all_games)}")
    for platform, count in platform_counts.items():
        if count > 0:
            print(f"  {platform.title()}: {count} games")
    
    return all_games, platform_counts


def fetch_lichess_games(
    username: str,
    max_games: int = 50,
    config: Optional[Dict] = None
) -> Tuple[List[chess.pgn.Game], int]:
    """
    Fetch games from Lichess API.
    
    Args:
        username: Lichess username
        max_games: Maximum number of games to fetch
        config: Configuration dictionary
    
    Returns:
        Tuple of (list of games, count fetched)
    """
    if config is None:
        config = {}
    
    try:
        base_url = "https://lichess.org/api"
        headers = {
            'Accept': 'application/x-ndjson'
            # Minimal headers - User-Agent and Auth headers can cause connection issues
        }
        
        # Note: Lichess API token support commented out for now due to connection issues
        # lichess_config = config.get('lichess', {})
        # api_token = lichess_config.get('api_token', '')
        # if api_token:
        #     headers['Authorization'] = f'Bearer {api_token}'
        
        # Fetch games
        url = f"{base_url}/games/user/{username}"
        params = {
            'max': min(max_games, 300),  # Lichess API limit is 300
            'sort': 'dateDesc',  # Most recent first
            'pgnInJson': 'true'  # Include PGN in response (required for parsing)
        }
        
        logger.info(f"Fetching Lichess games from {url}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 404:
            logger.warning(f"Lichess user '{username}' not found")
            return [], 0
        
        if response.status_code != 200:
            logger.error(f"Lichess API error: {response.status_code}")
            return [], 0
        
        games = []
        game_count = 0
        
        # Parse NDJSON response
        lines = response.text.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            
            try:
                game_data = json.loads(line)
                pgn = game_data.get('pgn', '')
                
                if pgn:
                    game = chess.pgn.read_game(StringIO(pgn))
                    if game:
                        games.append(game)
                        game_count += 1
                        
                        if game_count >= max_games:
                            break
                            
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to parse Lichess game: {e}")
                continue
        
        logger.info(f"Parsed {game_count} games from Lichess")
        return games, game_count
        
    except Exception as e:
        logger.error(f"Lichess fetch error: {e}")
        return [], 0


def get_platform_source(game: chess.pgn.Game) -> str:
    """
    Determine if a game is from Chess.com or Lichess based on headers.
    
    Args:
        game: chess.pgn.Game object
    
    Returns:
        'chess.com', 'lichess', or 'unknown'
    """
    link = game.headers.get('Link', '').lower()
    site = game.headers.get('Site', '').lower()
    
    if 'lichess.org' in link or 'lichess.org' in site:
        return 'lichess'
    elif 'chess.com' in link or 'chess.com' in site:
        return 'chess.com'
    else:
        return 'unknown'


def merge_platform_results(
    analyses: List[Dict],
    platform_counts: Dict[str, int]
) -> Dict[str, Any]:
    """
    Merge analysis results from multiple platforms with breakdown.
    
    Args:
        analyses: List of game analysis results
        platform_counts: Dictionary with platform game counts
    
    Returns:
        Merged results with platform breakdown
    """
    result = {
        'total_games': len(analyses),
        'platform_breakdown': platform_counts,
        'games': analyses,
    }
    
    # Calculate stats per platform
    for platform in ['chess.com', 'lichess']:
        platform_games = [
            a for a in analyses
            if a.get('source', 'unknown') == platform
        ]
        
        if platform_games:
            result[f'{platform}_stats'] = {
                'count': len(platform_games),
                'avg_score': sum(g.get('suspicion_score', 0) for g in platform_games) / len(platform_games),
            }
    
    return result


def detect_player_platforms(username: str, config: Optional[Dict] = None) -> Dict[str, bool]:
    """
    Auto-detect which platforms a player has accounts on.
    
    Args:
        username: Player username
        config: Configuration dictionary
    
    Returns:
        Dictionary with platform availability:
        {'chess.com': True/False, 'lichess': True/False}
    
    Example:
        platforms = detect_player_platforms('hikaru')
        # {'chess.com': True, 'lichess': True}
    """
    if config is None:
        config = {}
    
    results = {'chess.com': False, 'lichess': False}
    
    # Check Chess.com
    try:
        print("[DETECT] Checking Chess.com...", end=' ')
        url = f"https://api.chess.com/pub/player/{username.lower()}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results['chess.com'] = True
            print("Found")
        elif response.status_code == 403:
            # 403 means user exists but profile is private
            results['chess.com'] = True
            print("Found (private)")
        else:
            print("Not found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check Lichess
    try:
        print("[DETECT] Checking Lichess...", end=' ')
        url = f"https://lichess.org/api/user/{username.lower()}"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            results['lichess'] = True
            print("Found")
        else:
            print("Not found")
    except Exception as e:
        print(f"Error: {e}")
    
    return results


def prompt_platform_selection(username: str, config: Optional[Dict] = None) -> List[str]:
    """
    Interactive menu to select which platform(s) to fetch from.
    Shows auto-detected availability.
    
    Args:
        username: Player username
        config: Configuration dictionary
    
    Returns:
        List of selected platforms: ['chess.com'], ['lichess'], or ['chess.com', 'lichess']
    
    Example:
        platforms = prompt_platform_selection('hikaru')
        # User selects: ['chess.com', 'lichess']
    """
    print(f"\n[PLATFORMS] Detecting accounts for '{username}'...")
    
    # Auto-detect availability
    availability = detect_player_platforms(username, config)
    
    available_count = sum(1 for v in availability.values() if v)
    
    if available_count == 0:
        print("\n[ERROR] Player not found on any platform!")
        print("  - Check spelling of username")
        print("  - Try different username")
        return []
    
    print(f"\n[AVAILABLE] {username} is on:")
    if availability['chess.com']:
        print("  ✓ Chess.com")
    if availability['lichess']:
        print("  ✓ Lichess")
    
    # If only one platform available, use it
    if available_count == 1:
        if availability['chess.com']:
            print("\n[AUTO] Using Chess.com (only available platform)")
            return ['chess.com']
        else:
            print("\n[AUTO] Using Lichess (only available platform)")
            return ['lichess']
    
    # If both available, ask user
    print("\n[SELECT] Which platform(s) to fetch from?")
    print("1. Chess.com only")
    print("2. Lichess only")
    print("3. Both platforms (recommended)")
    choice = input("Choose (1-3, default 3): ").strip() or "3"
    
    if choice == "1":
        return ['chess.com']
    elif choice == "2":
        return ['lichess']
    else:  # default to both
        return ['chess.com', 'lichess']


def fetch_player_info(username: str, platform: str, config: Optional[Dict] = None) -> Optional[Dict]:
    """
    Fetch player information (rating, title, etc) from platform.
    Tries to get rating from blitz, bullet, and rapid in that order.
    
    Args:
        username: Player username
        platform: 'chess.com' or 'lichess'
        config: Configuration dict
        
    Returns:
        Player info dict with rating, title, etc. or None
    """
    try:
        if platform.lower() == 'chess.com':
            url = f"https://api.chess.com/pub/player/{username}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                stats = data.get('stats', {})
                # Try to get blitz, then bullet, then rapid
                rating = (stats.get('chess_blitz', {}).get('rating') or 
                         stats.get('chess_bullet', {}).get('rating') or
                         stats.get('chess_rapid', {}).get('rating') or 
                         1600)
                return {
                    'username': data.get('username'),
                    'rating': int(rating),
                    'title': data.get('title', ''),
                    'country': data.get('country', '')
                }
        
        elif platform.lower() == 'lichess':
            url = f"https://lichess.org/api/user/{username}"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                perfs = data.get('perfs', {})
                # Try blitz, bullet, rapid in order of preference
                rating = (perfs.get('blitz', {}).get('rating') or
                         perfs.get('bullet', {}).get('rating') or
                         perfs.get('rapid', {}).get('rating') or
                         1600)
                return {
                    'username': data.get('username'),
                    'rating': int(rating),
                    'title': data.get('title', ''),
                    'country': data.get('location', '')
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching player info: {e}")
        return None
