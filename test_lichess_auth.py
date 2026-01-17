#!/usr/bin/env python3
"""Test Lichess API authentication with the provided token."""

import sys
import yaml
from chess_analyzer.fetcher import ChessComFetcher
from chess_analyzer.lichess_analyzer import LichessAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lichess_auth():
    """Test Lichess authentication and analyze a game."""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check Lichess config
    lichess_config = config.get('lichess', {})
    token = lichess_config.get('api_token', '')
    username = lichess_config.get('username', '')
    
    print(f"✓ Lichess username: {username}")
    print(f"✓ API token configured: {'Yes' if token else 'No'}")
    print(f"✓ Lichess enabled: {lichess_config.get('enabled', False)}")
    print()
    
    if not token:
        print("✗ No API token configured!")
        return False
    
    # Fetch a game
    print("Fetching games from Chess.com...")
    fetcher = ChessComFetcher(config)
    games = fetcher.fetch_games(username, max_games=1)
    
    if not games:
        print("✗ No games found!")
        return False
    
    print(f"✓ Fetched {len(games)} game(s)")
    game = games[0]
    print(f"  Game: {game.headers.get('White')} vs {game.headers.get('Black')}")
    print()
    
    # Test Lichess analyzer
    print("Testing Lichess analyzer with authentication...")
    analyzer = LichessAnalyzer(config)
    
    try:
        print("Submitting game for Lichess analysis...")
        result = analyzer.analyze_game(game)
        
        if 'error' in result:
            print(f"✗ Error: {result['error']}")
            return False
        
        if result.get('status') == 'processing':
            print("⏳ Analysis request accepted (still processing)")
            return True
        
        positions = result.get('positions', [])
        summary = result.get('summary', {})
        
        if not positions:
            print("⚠ No positions analyzed yet")
            return True
        
        print(f"✓ Analysis complete!")
        print(f"  Total moves: {summary.get('total_moves', 0)}")
        print(f"  Positions analyzed: {summary.get('positions_analyzed', 0)}")
        print(f"  Engine correlation: {summary.get('engine_correlation', 0):.1f}%")
        print(f"  Source: {summary.get('source', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        analyzer.cleanup()

if __name__ == '__main__':
    success = test_lichess_auth()
    sys.exit(0 if success else 1)
