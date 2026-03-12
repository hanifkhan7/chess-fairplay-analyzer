"""
Test suite for HTML Interface Integration

Tests the connections between frontend HTML interfaces and backend modules.
"""

import json
import sys
from pathlib import Path

# Add chess_analyzer to path
sys.path.insert(0, str(Path(__file__).parent))

from chess_analyzer.html_interface_api import HTMLInterfaceAPI


def test_fen_analysis():
    """Test FEN position analysis."""
    print("\n" + "="*60)
    print("TEST 1: FEN Analysis")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    # Test starting position
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    result = api.analyze_fen(fen)
    
    print(f"✓ Status: {result.get('status')}")
    print(f"✓ FEN Valid: {result.get('fen')[:30]}...")
    
    if 'statistics' in result:
        stats = result['statistics']
        print(f"✓ Material - White: {stats.get('material_value', {}).get('white')}, Black: {stats.get('material_value', {}).get('black')}")
        print(f"✓ Side to Move: {stats.get('side_to_move')}")
        print(f"✓ Fullmove: {stats.get('fullmove_number')}")
    
    if 'opening_info' in result:
        opening = result['opening_info']
        print(f"✓ Opening: {opening.get('name')}")
    
    if 'analysis' in result:
        analysis = result['analysis']
        print(f"✓ Position Phase: {analysis.get('phase')}")
        print(f"✓ Legal Moves: {analysis.get('legal_moves')}")
    
    print(f"✓ Board Image Generated: {'board_image' in result and len(result['board_image']) > 50}")
    
    return result.get('status') == 'success'


def test_invalid_fen():
    """Test FEN validation."""
    print("\n" + "="*60)
    print("TEST 2: Invalid FEN Detection")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    # Test invalid FEN
    invalid_fen = 'invalid fen string'
    result = api.analyze_fen(invalid_fen)
    
    print(f"✓ Error Status: {result.get('status')}")
    print(f"✓ Error Message: {result.get('message', 'N/A')[:50]}...")
    
    return result.get('status') == 'error'


def test_opponent_analysis():
    """Test opponent profile generation."""
    print("\n" + "="*60)
    print("TEST 3: Opponent Analysis")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    result = api.analyze_opponent('Kasparov')
    
    print(f"✓ Status: {result.get('status')}")
    print(f"✓ Opponent: {result.get('opponent')}")
    
    if 'statistics' in result:
        stats = result['statistics']
        print(f"✓ Total Games: {stats.get('wins')} + {stats.get('draws')} + {stats.get('losses')} = {stats.get('wins', 0) + stats.get('draws', 0) + stats.get('losses', 0)}")
        print(f"✓ Win Rate: {stats.get('win_rate')}%")
    
    if 'opening_repertoire' in result:
        rep = result['opening_repertoire']
        white_count = len(rep.get('white', {}))
        black_count = len(rep.get('black', {}))
        print(f"✓ White Openings: {white_count}")
        print(f"✓ Black Openings: {black_count}")
    
    if 'weak_lines' in result:
        print(f"✓ Weak Lines Identified: {len(result['weak_lines'])}")
        for weak in result['weak_lines'][:2]:
            print(f"  - {weak.get('opening')} ({weak.get('win_rate')}% vs expected)")
    
    if 'exploitation_strategies' in result:
        print(f"✓ Exploitation Strategies: {len(result['exploitation_strategies'])}")
    
    return result.get('status') == 'success'


def test_player_repertoire():
    """Test player DNA analysis."""
    print("\n" + "="*60)
    print("TEST 4: Player Repertoire & DNA")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    result = api.analyze_player_repertoire()
    
    print(f"✓ Status: {result.get('status')}")
    print(f"✓ Player: {result.get('player')}")
    
    if 'statistics' in result:
        stats = result['statistics']
        print(f"✓ Total Games: {stats.get('total_games')}")
        print(f"✓ Total Openings: {stats.get('total_openings')}")
        print(f"✓ Playing Style: {stats.get('favorite_style')}")
    
    if 'white_repertoire' in result:
        print(f"✓ White Repertoire Items: {len(result['white_repertoire'])}")
        for rep in result['white_repertoire'][:2]:
            print(f"  - {rep.get('opening')} ({rep.get('games')} games, {rep.get('win_rate')}%)")
    
    if 'black_repertoire' in result:
        print(f"✓ Black Repertoire Items: {len(result['black_repertoire'])}")
        for rep in result['black_repertoire'][:2]:
            print(f"  - {rep.get('opening')} ({rep.get('games')} games, {rep.get('win_rate')}%)")
    
    if 'favorite_openings' in result:
        print(f"✓ Favorite Openings: {len(result['favorite_openings'])}")
        for fav in result['favorite_openings'][:2]:
            print(f"  - {fav.get('name')} ({fav.get('games')} games)")
    
    if 'weak_lines' in result:
        print(f"✓ Weak Lines: {len(result['weak_lines'])}")
        for weak in result['weak_lines'][:2]:
            print(f"  - {weak.get('opening')} (Elo loss: {weak.get('elo_loss', 'N/A')})")
    
    return result.get('status') == 'success'


def test_pgn_export():
    """Test PGN export functionality."""
    print("\n" + "="*60)
    print("TEST 5: PGN Export")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    pgn = api.export_player_repertoire_pgn('Test Player', [])
    
    print(f"✓ PGN Generated: {len(pgn) > 0}")
    print(f"✓ Contains Event Header: {'Event' in pgn}")
    print(f"✓ Contains Player Name: {'Test Player' in pgn}")
    print(f"✓ Sample (first 100 chars):\n{pgn[:100]}...")
    
    return len(pgn) > 0 and 'Event' in pgn


def test_json_export():
    """Test JSON export functionality."""
    print("\n" + "="*60)
    print("TEST 6: JSON Export")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    profile = {
        'total_games': 1200,
        'favorite_openings': ['Sicilian', 'Ruy Lopez'],
        'win_rate': 60.5
    }
    
    json_str = api.export_player_dna_json('Test Player', profile)
    
    print(f"✓ JSON Generated: {len(json_str) > 0}")
    
    try:
        data = json.loads(json_str)
        print(f"✓ Valid JSON: True")
        print(f"✓ Player Name: {data.get('player_name')}")
        print(f"✓ Has Profile Data: {'profile_data' in data}")
        success = True
    except:
        print(f"✓ Valid JSON: False")
        success = False
    
    return success


def test_html_report_generation():
    """Test HTML report generation."""
    print("\n" + "="*60)
    print("TEST 7: HTML Report Generation")
    print("="*60)
    
    api = HTMLInterfaceAPI()
    
    # Test FEN report
    fen_data = {'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'material_value': {'difference': 0},
                'opening_name': 'Starting Position'}
    fen_html = api.generate_html_report('fen_analysis', fen_data)
    
    print(f"✓ FEN Report Generated: {len(fen_html) > 0}")
    print(f"✓ Contains HTML Tags: {'<html>' in fen_html}")
    print(f"✓ Contains Title: {'<h1>' in fen_html}")
    
    # Test opponent report
    opp_data = {'opponent': 'Kasparov',
                'win_rate': 60.0,
                'weak_lines': [{'opening': 'Line1'}, {'opening': 'Line2'}]}
    opp_html = api.generate_html_report('opponent_analysis', opp_data)
    
    print(f"✓ Opponent Report Generated: {len(opp_html) > 0}")
    print(f"✓ Contains Opponent Name: {'Kasparov' in opp_html}")
    
    # Test repertoire report
    rep_data = {'total_games': 1200,
                'total_openings': 32,
                'favorite_openings': [{'name': 'Sicilian', 'games': 145}]}
    rep_html = api.generate_html_report('repertoire_analysis', rep_data)
    
    print(f"✓ Repertoire Report Generated: {len(rep_html) > 0}")
    print(f"✓ Contains Statistics: {'1200' in rep_html}")
    
    return len(fen_html) > 0 and len(opp_html) > 0 and len(rep_html) > 0


def test_api_initialization():
    """Test API module initialization."""
    print("\n" + "="*60)
    print("TEST 0: API Module Initialization")
    print("="*60)
    
    try:
        api = HTMLInterfaceAPI()
        print(f"✓ HTMLInterfaceAPI Created")
        print(f"✓ ECO Module: {api.eco is not None}")
        print(f"✓ FEN Converter: {api.fen_converter is not None}")
        print(f"✓ Player DNA Module: {api.player_dna is not None}")
        return True
    except Exception as e:
        print(f"✗ Initialization Failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "█"*60)
    print("█  HTML INTERFACE API TEST SUITE")
    print("█"*60)
    
    tests = [
        ('API Initialization', test_api_initialization),
        ('FEN Position Analysis', test_fen_analysis),
        ('Invalid FEN Detection', test_invalid_fen),
        ('Opponent Analysis', test_opponent_analysis),
        ('Player Repertoire & DNA', test_player_repertoire),
        ('PGN Export', test_pgn_export),
        ('JSON Export', test_json_export),
        ('HTML Report Generation', test_html_report_generation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = '✓ PASS' if result else '✗ FAIL'
        except Exception as e:
            print(f"\n✗ Test Exception: {e}")
            results[test_name] = '✗ ERROR'
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if 'PASS' in v)
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{result} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Integration Ready!")
    else:
        print(f"\n⚠ {total - passed} test(s) need attention")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
