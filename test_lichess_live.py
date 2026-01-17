#!/usr/bin/env python3
"""Quick test of Lichess API integration."""

import yaml
from chess_analyzer.fetcher import ChessComFetcher
from chess_analyzer.analyzer import ChessAnalyzer
import time

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

print("=" * 60)
print("LICHESS API INTEGRATION TEST")
print("=" * 60)

# Check config
lichess_config = config.get('lichess', {})
analysis_config = config.get('analysis', {})

print(f"\n✓ Lichess Username: {lichess_config.get('username', 'N/A')}")
print(f"✓ API Token Configured: {'Yes' if lichess_config.get('api_token') else 'No'}")
print(f"✓ Use Lichess: {analysis_config.get('use_lichess', False)}")
print(f"✓ Fallback Stockfish Depth: {analysis_config.get('engine_depth', 14)}")

# Fetch a few games
print("\nFetching 1 game from Chess.com (HNF467)...")
fetcher = ChessComFetcher(config)
games = fetcher.fetch_games('HNF467', max_games=1)

if not games:
    print("✗ Could not fetch games")
    exit(1)

print(f"✓ Fetched {len(games)} game")
game = games[0]
print(f"  {game.headers.get('White')} vs {game.headers.get('Black')}")

# Analyze with Lichess
print("\nStarting analysis with Lichess API...")
analyzer = ChessAnalyzer(config)

start = time.time()
results = analyzer.analyze_games(games)
elapsed = time.time() - start

print(f"\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"Analysis Time: {elapsed:.1f} seconds")
print(f"Games Analyzed: {results.games_analyzed}")
print(f"Engine Correlation: {results.avg_engine_correlation:.1f}%")
print(f"Avg Centipawn Loss: {results.avg_centipawn_loss:.1f}")
print(f"Suspicion Score: {results.suspicion_score:.1f}/100")

print("\n✓ Lichess API integration working!")
