"""
Fetch games from Chess.com API for analysis.
"""
import requests
import time
import chess.pgn
import json
import logging
from io import StringIO
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Local imports
from .utils.helpers import rate_limiter, validate_username

logger = logging.getLogger(__name__)

class ChessComAPIError(Exception):
    """Custom exception for Chess.com API errors."""
    pass

def fetch_player_games(username: str, max_games: int = 50, config: Optional[Dict] = None) -> List[chess.pgn.Game]:
    """
    Fetch games for a given Chess.com username - FIXED TO FETCH MORE GAMES.
    
    Args:
        username: Chess.com username
        max_games: Maximum number of games to fetch (0 = all available)
        config: Configuration dictionary
    
    Returns:
        List of chess.pgn.Game objects
    
    Raises:
        ChessComAPIError: If API request fails
        ValueError: If username is invalid
    """
    if config is None:
        config = {}
    
    # Get configuration with defaults
    api_base = config.get('chess_com', {}).get('api_base', 'https://api.chess.com/pub/player')
    request_delay = config.get('chess_com', {}).get('request_delay', 1.0)
    cache_enabled = config.get('chess_com', {}).get('cache_enabled', True)
    cache_dir = config.get('chess_com', {}).get('cache_dir', 'cache')
    
    # Validate username
    if not validate_username(username):
        raise ValueError(f"Invalid username format: {username}")
    
    logger.info(f"Starting game fetch for user: {username}")
    logger.info(f"Max games to fetch: {max_games if max_games > 0 else 'All available'}")
    
    # Create cache directory if enabled
    if cache_enabled:
        Path(cache_dir).mkdir(exist_ok=True)
        cache_file = Path(cache_dir) / f"{username}_games.json"
        
        # Check cache first (24 hour validity for game data)
        if cache_file.exists():
            logger.info(f"Checking cache: {cache_file}")
            cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age < 86400:  # 24 hour cache validity for games
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    # Check if cache has enough games for the request
                    cached_game_count = cached_data.get('game_count', 0)
                    if max_games <= 0 or cached_game_count >= max_games:
                        # Parse games from cache
                        games = _parse_games_from_cache(cached_data, max_games)
                        if games:
                            logger.info(f"Loaded {len(games)} games from cache")
                            return games
                    else:
                        logger.info(f"Cache has only {cached_game_count} games but {max_games} requested. Fetching fresh data...")
                except Exception as e:
                    logger.warning(f"Cache read failed: {e}")
    
    try:
        # Use improved headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        # Step 1: Get player info first
        logger.info(f"Fetching player info for {username}")
        player_info = _fetch_player_info(username, api_base, request_delay, headers)
        
        if not player_info:
            logger.error(f"Player {username} not found on Chess.com")
            logger.info(f"Try visiting: https://www.chess.com/member/{username}")
            raise ChessComAPIError(f"Player {username} not found on Chess.com")
        
        logger.info(f"Player found: {player_info.get('username')}")
        
        # Step 2: Get ALL monthly archives (FIXED: Get ALL archives)
        logger.info("Fetching ALL game archives...")
        archives = _fetch_game_archives(username, api_base, request_delay, headers)
        
        if not archives:
            logger.warning(f"No game archives found for {username}")
            return []
        
        logger.info(f"Found {len(archives)} monthly archives")
        
        # Step 3: Fetch games from ALL archives (FIXED: Process all archives)
        all_games_data = []
        total_archives = len(archives)
        
        # Process archives from NEWEST to OLDEST
        for i, archive_url in enumerate(reversed(archives), 1):
            archive_num = total_archives - i + 1
            
            # Check if we have enough games
            if max_games > 0 and len(all_games_data) >= max_games:
                logger.info(f"Reached max games limit ({max_games}), stopping fetch")
                break
            
            logger.debug(f"Fetching from archive {archive_num}/{total_archives}: {archive_url}")
            
            # Calculate how many more games we need
            games_needed = max_games - len(all_games_data) if max_games > 0 else 0
            
            month_games = _fetch_monthly_games(
                archive_url, 
                headers,
                games_needed
            )
            
            if month_games:
                all_games_data.extend(month_games)
                logger.info(f"Archive {archive_num}/{total_archives}: Added {len(month_games)} games "
                           f"(Total: {len(all_games_data)})")
            
            # Respectful delay between archives
            if i < total_archives:  # No delay after last archive
                time.sleep(request_delay)
        
        # Step 4: Parse games
        games = _parse_games_from_data(all_games_data, max_games)
        
        if not games:
            logger.warning(f"No valid games could be parsed for {username}")
            return []
        
        logger.info(f"Successfully parsed {len(games)} games")
        
        # Step 5: Cache results
        if cache_enabled and games:
            try:
                cache_data = {
                    'username': username,
                    'fetched_at': datetime.now().isoformat(),
                    'game_count': len(games),
                    'archives_count': total_archives,
                    'games': all_games_data[:200]  # Cache up to 200 games
                }
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2)
                logger.info(f"Cached {len(games)} games to {cache_file}")
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
        
        return games
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching games: {e}")
        raise ChessComAPIError(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching games: {e}")
        raise ChessComAPIError(f"Fetch failed: {str(e)}")

def _parse_games_from_cache(cache_data: Dict, max_games: int = 0) -> List[chess.pgn.Game]:
    """Parse games from cache data."""
    games_data = cache_data.get('games', [])
    return _parse_games_from_data(games_data, max_games)

@rate_limiter(1.0)
def _fetch_player_info(username: str, api_base: str, delay: float, headers: Dict) -> Optional[Dict]:
    """Fetch basic player information."""
    try:
        url = f"{api_base}/{username}"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.error(f"Player {username} not found on Chess.com (404)")
            return None
        else:
            logger.error(f"HTTP {response.status_code} fetching player info for {username}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching player info for {username}: {e}")
        return None

@rate_limiter(1.0)
def _fetch_game_archives(username: str, api_base: str, delay: float, headers: Dict) -> List[str]:
    """Fetch list of ALL monthly game archives."""
    try:
        url = f"{api_base}/{username}/games/archives"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            archives = data.get('archives', [])
            logger.info(f"Found {len(archives)} monthly archives")
            return archives
        else:
            logger.warning(f"HTTP {response.status_code} fetching archives")
            return []
    except Exception as e:
        logger.error(f"Error fetching game archives: {e}")
        return []

def _fetch_monthly_games(archive_url: str, headers: Dict, max_games: int = 0) -> List[Dict]:
    """Fetch games from a monthly archive."""
    try:
        response = requests.get(archive_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            games = data.get('games', [])
            
            # Filter standard chess games
            filtered_games = []
            for game in games:
                if game.get('rules') == 'chess':  # Only standard chess
                    filtered_games.append(game)
                
                if max_games > 0 and len(filtered_games) >= max_games:
                    break
            
            return filtered_games
        else:
            logger.warning(f"HTTP {response.status_code} for archive {archive_url[-7:]}")
            return []
        
    except Exception as e:
        logger.error(f"Error fetching monthly games: {e}")
        return []

def _parse_games_from_data(games_data: List[Dict], max_games: int = 0) -> List[chess.pgn.Game]:
    """Parse PGN strings from API data into chess.pgn.Game objects."""
    parsed_games = []
    parse_errors = 0
    
    for i, game_data in enumerate(games_data):
        if max_games > 0 and len(parsed_games) >= max_games:
            break
        
        try:
            pgn_text = game_data.get('pgn', '')
            if not pgn_text:
                continue
            
            # Parse PGN
            pgn_io = StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)
            
            if game is None:
                parse_errors += 1
                continue
            
            # Add metadata from Chess.com
            _add_metadata_to_game(game, game_data)
            
            parsed_games.append(game)
            
        except Exception as e:
            parse_errors += 1
            logger.debug(f"Error parsing game {i+1}: {e}")
            continue
    
    if parse_errors > 0:
        logger.warning(f"Failed to parse {parse_errors} games")
    
    return parsed_games

def _add_metadata_to_game(game: chess.pgn.Game, game_data: Dict) -> None:
    """Add Chess.com metadata to game object."""
    # Extract useful metadata
    metadata = {
        'chess_com_url': game_data.get('url', ''),
        'time_control': game_data.get('time_control', ''),
        'time_class': game_data.get('time_class', ''),
        'rated': game_data.get('rated', False),
        'end_time': game_data.get('end_time'),
    }
    
    # Add to game headers
    for key, value in metadata.items():
        if value is not None:
            game.headers[key] = str(value)
    
    # Add player ratings if available
    if 'white' in game_data and isinstance(game_data['white'], dict):
        white_player = game_data['white']
        game.headers['WhiteRating'] = str(white_player.get('rating', ''))
    
    if 'black' in game_data and isinstance(game_data['black'], dict):
        black_player = game_data['black']
        game.headers['BlackRating'] = str(black_player.get('rating', ''))