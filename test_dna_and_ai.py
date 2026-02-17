#!/usr/bin/env python3
"""
Comprehensive test suite for Player DNA fix + AI integration.
Tests:
1. Player DNA building with different game formats
2. AI module initialization
3. AI explanation generation (mocked)
4. Menu integration
"""

import sys
import os
import json
from pathlib import Path

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chess_analyzer'))

import chess.pgn
from io import StringIO
from typing import List, Dict


# Sample PGN games for testing
SAMPLE_PGNS = [
    """[Event "Chess.com"]
[White "hikaru"]
[Black "elo1600"]
[Result "1-0"]
[Opening "Ruy Lopez"]
[ECO "C60"]
[TimeControl "600+3"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Na5 10. Bc2 c5 1-0""",
    
    """[Event "Chess.com"]
[White "hikaru"]
[Black "elo1700"]
[Result "1/2-1/2"]
[Opening "Sicilian Defense"]
[ECO "B20"]
[TimeControl "600+3"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 1/2-1/2""",
    
    """[Event "Chess.com"]
[White "opponent1"]
[Black "hikaru"]
[Result "0-1"]
[Opening "Queen's Gambit"]
[ECO "D40"]
[TimeControl "600+3"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Ne4 5. Bh4 Nxc3 0-1""",

    """[Event "Chess.com"]
[White "hikaru"]
[Black "elo1500"]
[Result "1-0"]
[Opening "Italian Game"]
[ECO "C50"]
[TimeControl "600+3"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5 6. d4 exd4 7. O-O d3 1-0""",

    """[Event "Lichess"]
[White "hikaru"]
[Black "elo1650"]
[Result "1-0"]
[Opening "French Defense"]
[ECO "C00"]
[TimeControl "600+3"]

1. e4 e6 2. d4 d5 3. Nc3 Nf6 4. e5 Nfd7 5. f4 c5 6. Nf3 Nc6 1-0""",
]


def test_player_dna_building():
    """Test 1: Player DNA building with chess.pgn.Game objects."""
    print("\n" + "="*70)
    print("TEST 1: Player DNA Building")
    print("="*70)
    
    try:
        from player_dna import build_player_dna
        
        # Parse games
        games = []
        for pgn in SAMPLE_PGNS:
            game = chess.pgn.read_game(StringIO(pgn))
            if game:
                games.append(game)
        
        print(f"✓ Parsed {len(games)} games")
        
        # Build DNA
        dna = build_player_dna('hikaru', games, color='white', min_games=1)
        
        print(f"✓ DNA built: {dna.data['total_games']} games analyzed")
        print(f"  - Record: {dna.data['statistics']['wins']}W {dna.data['statistics']['draws']}D {dna.data['statistics']['losses']}L")
        print(f"  - Win rate: {dna.data['statistics']['win_rate']:.1f}%")
        print(f"  - Openings: {len(dna.data['favorite_openings'])}")
        
        if dna.data['total_games'] > 0:
            print("\n✓ TEST 1 PASSED")
            return True, dna
        else:
            print("\n✗ TEST 1 FAILED: No games analyzed")
            return False, None
    
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_ai_module():
    """Test 2: AI module import and provider detection."""
    print("\n" + "="*70)
    print("TEST 2: AI Module Import")
    print("="*70)
    
    try:
        from ai_integration import (
            AIIntegration,
            get_provider_info,
            OpenAIProvider,
            ClaudeProvider,
            OllamaProvider,
            DeepseekProvider
        )
        
        print("✓ All AI modules imported successfully")
        
        # Check provider info
        providers = get_provider_info()
        print(f"✓ {len(providers)} providers available:")
        
        for provider_name, info in providers.items():
            print(f"  - {info['name']}")
        
        print("\n✓ TEST 2 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_menu_integration():
    """Test 3: AI Menu Integration module."""
    print("\n" + "="*70)
    print("TEST 3: AI Menu Integration")
    print("="*70)
    
    try:
        from ai_menu_integration import AIReportGenerator, create_ai_enhanced_report
        
        print("✓ AI Menu Integration module imported")
        
        # Create generator
        gen = AIReportGenerator()
        print(f"✓ AIReportGenerator created")
        
        # Test that it can load config (even if empty)
        print(f"✓ Config loaded (current_provider: {gen.current_provider or 'None'})")
        
        print("\n✓ TEST 3 PASSED")
        return True
    
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dna_json_export(dna):
    """Test 4: DNA JSON export."""
    print("\n" + "="*70)
    print("TEST 4: DNA JSON Export")
    print("="*70)
    
    try:
        test_file = "test_dna_export.json"
        dna.save_json(test_file)
        
        # Verify file exists
        if Path(test_file).exists():
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            print(f"✓ Saved to {test_file}")
            print(f"✓ Verified JSON format")
            print(f"✓ Player: {data.get('player')}")
            print(f"✓ Total games: {data.get('total_games')}")
            
            # Cleanup
            os.remove(test_file)
            
            print("\n✓ TEST 4 PASSED")
            return True
        else:
            print(f"\n✗ TEST 4 FAILED: File not created")
            return False
    
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_detection():
    """Test 5: Provider detection and validation."""
    print("\n" + "="*70)
    print("TEST 5: Provider Detection")
    print("="*70)
    
    try:
        from ai_integration import AIIntegration
        
        ai = AIIntegration()
        available = ai.get_available_providers()
        
        print(f"✓ Available providers: {available}")
        
        if len(available) >= 4:
            print(f"✓ All 4 core providers detected:")
            for provider in ['openai', 'claude', 'ollama', 'deepseek']:
                if provider in available:
                    print(f"  ✓ {provider}")
            
            print("\n✓ TEST 5 PASSED")
            return True
        else:
            print(f"\n✗ TEST 5 FAILED: Expected 4+ providers, got {len(available)}")
            return False
    
    except Exception as e:
        print(f"\n✗ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dna_report_generation(dna):
    """Test 6: DNA report generation."""
    print("\n" + "="*70)
    print("TEST 6: DNA Report Generation")
    print("="*70)
    
    try:
        from player_dna import generate_player_dna_report
        
        report = generate_player_dna_report(dna.to_dict())
        
        # Check report content
        if "PLAYER DNA" in report and dna.data['player'].upper() in report:
            lines = report.split('\n')
            print(f"✓ Report generated: {len(lines)} lines")
            print(f"✓ Contains player name: {dna.data['player']}")
            
            # Show sample
            print(f"\nSample report preview:")
            print("\n".join(lines[:10]))
            
            print("\n✓ TEST 6 PASSED")
            return True
        else:
            print(f"\n✗ TEST 6 FAILED: Report missing expected content")
            return False
    
    except Exception as e:
        print(f"\n✗ TEST 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUITE")
    print("Player DNA Fix + AI Integration")
    print("="*70)
    
    results = {}
    dna = None
    
    # Test 1: DNA Building
    results['dna_building'], dna = test_player_dna_building()
    if not dna:
        print("\n✗ CRITICAL: DNA building failed, aborting remaining tests")
        return 1
    
    # Test 2: AI Module
    results['ai_module'] = test_ai_module()
    
    # Test 3: Menu Integration
    results['menu_integration'] = test_ai_menu_integration()
    
    # Test 4: JSON Export
    results['json_export'] = test_dna_json_export(dna)
    
    # Test 5: Provider Detection
    results['provider_detection'] = test_provider_detection()
    
    # Test 6: Report Generation
    results['report_generation'] = test_dna_report_generation(dna)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nReady to test:")
        print("1. Run Menu Option 10 (Opening Repertoire & DNA)")
        print("2. Test AI report generation with real player data")
        print("3. Verify all menu integrations")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TEST(S) FAILED ✗✗✗")
        return 1


if __name__ == '__main__':
    sys.exit(main())
