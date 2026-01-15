import sys
sys.path.insert(0, '.')

print("🧪 TESTING MULTI-GAME ANALYSIS")
print("=" * 60)

from chess_analyzer.fetcher import fetch_player_games
from chess_analyzer.analyzer import ChessAnalyzer
from chess_analyzer.utils.helpers import load_config

# Load config
config = load_config()

# Test username
test_user = "hikaru"  # Change to any user
games_to_fetch = 10

print(f"\n📥 Fetching {games_to_fetch} games for {test_user}...")
try:
    games = fetch_player_games(test_user, max_games=games_to_fetch, config=config)
    print(f"✅ Fetched {len(games)} games")
    
    if games:
        print(f"\n🎮 Sample game: {games[0].headers.get('White')} vs {games[0].headers.get('Black')}")
        print(f"   Result: {games[0].headers.get('Result')}")
        print(f"   Date: {games[0].headers.get('Date')}")
        
        print(f"\n🧠 Analyzing {len(games)} games...")
        analyzer = ChessAnalyzer(config)
        player_analysis = analyzer.analyze_games(games)
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   Games analyzed: {player_analysis.games_analyzed}/{len(games)}")
        print(f"   Suspicion score: {player_analysis.suspicion_score:.1f}/100")
        print(f"   Risk level: {player_analysis.risk_level}")
        print(f"   Avg engine correlation: {player_analysis.avg_engine_correlation:.1f}%")
        print(f"   Avg centipawn loss: {player_analysis.avg_centipawn_loss:.1f}")
        print(f"   Suspicious games: {player_analysis.suspicious_game_count}")
        
        analyzer.cleanup()
        print("\n✅ Multi-game analysis successful!")
    else:
        print("❌ No games fetched")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()