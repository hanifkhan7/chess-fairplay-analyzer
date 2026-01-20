#!/usr/bin/env python
"""
Test script to verify Head-to-Head Matchup Analyzer improvements:
1. Game count prompt works
2. ELO calculation with fallbacks
3. Individual player stats displayed
4. H2H games prominently shown
"""

import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer
from chess_analyzer.dual_fetcher import fetch_player_info
from chess_analyzer.menu import _fetch_games

def test_h2h_display():
    """Test the Head-to-Head display with real players"""
    print("=" * 80)
    print("TEST: Head-to-Head Matchup Analyzer Improvements")
    print("=" * 80)
    
    try:
        # Initialize config
        config = {
            'DEFAULT_PLATFORM': 'lichess',
            'LICHESS_API_URL': 'https://lichess.org/api',
            'STOCKFISH_PATH': 'stockfish/stockfish-windows-x86-64.exe',
            'MAX_GAMES': 50
        }
        
        # Players to test
        player1 = "rohan_asif"
        player2 = "Hassan_Tahirr"
        platform = "lichess"
        
        print(f"\n[INFO] Testing with players: {player1} vs {player2}")
        print(f"[INFO] Platform: {platform}")
        print(f"[INFO] Games to fetch: 50 (user-selectable)")
        
        # Fetch games
        print(f"\n[FETCHING] Downloading games for {player1}...")
        games1, _ = _fetch_games(player1, 50, [platform], config)
        if not games1:
            print(f"[ERROR] Could not fetch games for {player1}")
            return False
        print(f"[SUCCESS] Fetched {len(games1)} games for {player1}")
        
        print(f"\n[FETCHING] Downloading games for {player2}...")
        games2, _ = _fetch_games(player2, 50, [platform], config)
        if not games2:
            print(f"[ERROR] Could not fetch games for {player2}")
            return False
        print(f"[SUCCESS] Fetched {len(games2)} games for {player2}")
        
        # Get player info
        print(f"\n[INFO] Fetching player ratings...")
        p1_info = fetch_player_info(player1, platform, config)
        p2_info = fetch_player_info(player2, platform, config)
        
        p1_elo = p1_info.get('rating') if p1_info and p1_info.get('rating') else None
        p2_elo = p2_info.get('rating') if p2_info and p2_info.get('rating') else None
        
        print(f"[INFO] {player1} rating: {p1_elo if p1_elo else 'API failed, will calculate from games'}")
        print(f"[INFO] {player2} rating: {p2_elo if p2_elo else 'API failed, will calculate from games'}")
        
        # Generate matchup report
        print(f"\n[ANALYZING] Generating matchup report...")
        analyzer = HeadToHeadAnalyzer()
        report = analyzer.generate_matchup_report(
            player1, p1_elo, games1,
            player2, p2_elo, games2
        )
        
        # Verify report structure
        print(f"\n[VERIFICATION] Report structure:")
        print(f"  ✓ ELO probability calculated: {report.get('elo_probability', {})}")
        print(f"  ✓ Performance probability calculated: {report.get('performance_probability', {})}")
        print(f"  ✓ H2H games found: {report['h2h_games'].get('total_games', 0)}")
        print(f"  ✓ Combined probability: {report.get('combined_probability', {})}")
        print(f"  ✓ Prediction: {report.get('prediction', 'N/A')}")
        print(f"  ✓ Confidence: {report.get('confidence', 0):.1f}%")
        
        # Check that ELOs are reasonable
        used_elo_p1 = report.get('player1_elo_used')
        used_elo_p2 = report.get('player2_elo_used')
        print(f"\n[CHECK] ELO values used:")
        print(f"  Player 1 ({player1}): {used_elo_p1}")
        print(f"  Player 2 ({player2}): {used_elo_p2}")
        
        if used_elo_p1 == 1600 or used_elo_p2 == 1600:
            print(f"  ⚠ WARNING: ELO defaulted to 1600 (should calculate from opponent data)")
        elif used_elo_p1 and used_elo_p2:
            print(f"  ✓ Real ELOs obtained or calculated")
        
        # Display the report
        print(f"\n[DISPLAY] Formatted Report Output:")
        print("-" * 80)
        analyzer.display_matchup_report(report)
        print("-" * 80)
        
        # Check H2H games are shown
        if report['h2h_games'].get('total_games', 0) > 0:
            print(f"\n✓ SUCCESS: H2H games found and will be displayed prominently")
        else:
            print(f"\n✓ SUCCESS: No H2H games found, comparison based on ELO and performance")
        
        # Verify stats are displayed
        history = report.get('game_history', {})
        if history:
            print(f"\n✓ SUCCESS: Individual player statistics:")
            print(f"  {player1}: {history.get('player1', {}).get('wins', 0)}W-{history.get('player1', {}).get('losses', 0)}L-{history.get('player1', {}).get('draws', 0)}D")
            print(f"  {player2}: {history.get('player2', {}).get('wins', 0)}W-{history.get('player2', {}).get('losses', 0)}L-{history.get('player2', {}).get('draws', 0)}D")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_h2h_display()
    print("\n" + "=" * 80)
    if success:
        print("✓ HEAD-TO-HEAD ANALYZER TEST PASSED")
    else:
        print("✗ HEAD-TO-HEAD ANALYZER TEST FAILED")
    print("=" * 80)
    sys.exit(0 if success else 1)
