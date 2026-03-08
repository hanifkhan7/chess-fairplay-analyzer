"""
Test Suite for Enhanced Player DNA System
Tests accuracy of player opening repertoire analysis and PGN export.
"""

import unittest
import tempfile
from pathlib import Path
import json
import io
import chess
import chess.pgn

from chess_analyzer.player_dna_enhanced import (
    PlayerDNAEnhanced, PlayerDNAProfile, OpeningStats,
    analyze_player_games, export_player_repertoire, export_player_dna_json
)
from chess_analyzer.eco_comprehensive import ECOComprehensive


class TestPlayerDNAEnhanced(unittest.TestCase):
    """Test enhanced player DNA functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        PlayerDNAEnhanced.initialize()
        ECOComprehensive.initialize()
        
        # Create test games
        cls.test_games = cls._create_test_games()
    
    @staticmethod
    def _create_test_games():
        """Create sample chess games for testing."""
        games = []
        
        # Game 1: Ruy Lopez (C60) - Win
        pgn1 = """[Event "Test Tournament"]
[White "TestPlayer"]
[Black "Opponent1"]
[Result "1-0"]
[ECO "C60"]
[Date "2024.01.01"]

1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Be7 1-0
"""
        games.append(pgn1)
        
        # Game 2: Ruy Lopez (C60) - Loss
        pgn2 = """[Event "Test Tournament"]
[White "Opponent2"]
[Black "TestPlayer"]
[Result "1-0"]
[ECO "C60"]
[Date "2024.01.02"]

1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.0-0 Be7 0-1
"""
        games.append(pgn2)
        
        # Game 3: King's Indian Defense (E60) - Draw
        pgn3 = """[Event "Test Tournament"]
[White "TestPlayer"]
[Black "Opponent3"]
[Result "1/2-1/2"]
[ECO "E60"]
[Date "2024.01.03"]

1.d4 Nf6 2.c4 g6 3.Nc3 Bg7 4.e4 d6 1/2-1/2
"""
        games.append(pgn3)
        
        # Game 4: Sicilian Defense (B20) - Win
        pgn4 = """[Event "Test Tournament"]
[White "Opponent4"]
[Black "TestPlayer"]
[Result "0-1"]
[ECO "B20"]
[Date "2024.01.04"]

1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 1-0
"""
        games.append(pgn4)
        
        return games
    
    def test_player_name_extraction(self):
        """Test player identification from games."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        self.assertEqual(dna.player_name, "TestPlayer")
        self.assertGreater(dna.total_games_analyzed, 0)
        print(f"✓ Extracted {dna.total_games_analyzed} games for TestPlayer")
    
    def test_game_counting(self):
        """Test correct counting of games."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        self.assertEqual(dna.total_games_analyzed, 4)
        self.assertEqual(dna.white_games + dna.black_games, 4)
        
        print(f"✓ Found {dna.white_games} white games and {dna.black_games} black games")
    
    def test_opening_statistics(self):
        """Test opening statistics are calculated correctly."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        self.assertGreater(len(dna.opening_stats), 0)
        
        # Check Ruy Lopez
        if "C60" in dna.opening_stats:
            c60_stats = dna.opening_stats["C60"]
            self.assertEqual(c60_stats.total_games, 2)
            # One win, one loss
            print(f"✓ C60 stats: {c60_stats.total_games} games, {c60_stats.win_rate:.1f}% wins")
    
    def test_win_rate_calculation(self):
        """Test win rate calculation."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        for eco, stats in dna.opening_stats.items():
            # Win + Draw + Loss should equal total games
            total = stats.wins + stats.draws + stats.losses
            self.assertEqual(total, stats.total_games)
            
            # Percentages should sum to ~100%
            total_rate = stats.win_rate + stats.draw_rate + stats.loss_rate
            self.assertAlmostEqual(total_rate, 100.0, places=1)
        
        print("✓ Win/Draw/Loss rates calculated correctly")
    
    def test_favorite_openings_ranking(self):
        """Test favorite openings are ranked correctly."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        self.assertGreater(len(dna.favorite_openings), 0)
        
        # Verify they're sorted by frequency
        for i in range(len(dna.favorite_openings) - 1):
            games_i = dna.opening_stats[dna.favorite_openings[i]].total_games
            games_j = dna.opening_stats[dna.favorite_openings[i+1]].total_games
            self.assertGreaterEqual(games_i, games_j)
        
        print(f"✓ Found {len(dna.favorite_openings)} favorite openings")
    
    def test_weak_lines_identification(self):
        """Test identification of weak lines."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        # May or may not have weak lines depending on results
        # Just verify the list is accessible
        self.assertIsInstance(dna.weak_lines, list)
        print(f"✓ Weak lines identified: {len(dna.weak_lines)}")
    
    def test_risky_openings_identification(self):
        """Test identification of risky/sharp openings."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        # May or may not have risky openings
        self.assertIsInstance(dna.risky_openings, list)
        print(f"✓ Risky openings identified: {len(dna.risky_openings)}")
    
    def test_color_filtering(self):
        """Test filtering games by color."""
        # White games only
        dna_white = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer", color="white")
        self.assertGreater(dna_white.white_games, 0)
        self.assertEqual(dna_white.black_games, 0)
        
        # Black games only
        dna_black = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer", color="black")
        self.assertGreater(dna_black.black_games, 0)
        self.assertEqual(dna_black.white_games, 0)
        
        print("✓ Color filtering works correctly")
    
    def test_opening_stats_dataclass(self):
        """Test OpeningStats dataclass."""
        stats = OpeningStats(
            eco_code="C60",
            opening_name="Ruy Lopez",
            total_games=10,
            wins=7,
            draws=2,
            losses=1
        )
        
        stats.calculate_rates()
        
        self.assertAlmostEqual(stats.win_rate, 70.0, places=1)
        self.assertAlmostEqual(stats.draw_rate, 20.0, places=1)
        self.assertAlmostEqual(stats.loss_rate, 10.0, places=1)
        
        # Test to_dict conversion
        data_dict = stats.to_dict()
        self.assertEqual(data_dict['eco_code'], "C60")
        self.assertEqual(data_dict['wins'], 7)
        
        print("✓ OpeningStats dataclass works correctly")


class TestRepertoireExport(unittest.TestCase):
    """Test lifetime repertoire export functionality."""
    
    def setUp(self):
        PlayerDNAEnhanced.initialize()
        ECOComprehensive.initialize()
        self.test_games = TestPlayerDNAEnhanced._create_test_games()
    
    def test_pgn_export(self):
        """Test exporting repertoire as PGN."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            result = PlayerDNAEnhanced.export_lifetime_repertoire_pgn(dna, output_path)
            
            self.assertIsNotNone(result)
            self.assertTrue(output_path.exists())
            
            # Verify PGN content
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("Lifetime Repertoire", content)
                self.assertIn("TestPlayer", content)
                self.assertIn("Opening", content)
            
            print(f"✓ Lifetime repertoire PGN exported: {output_path}")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_pgn_has_annotations(self):
        """Test PGN export includes annotations."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            PlayerDNAEnhanced.export_lifetime_repertoire_pgn(dna, output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                # Should have statistics annotations
                self.assertIn("Games:", content)
                self.assertIn("Win Rate:", content)
                self.assertIn("Results:", content)
            
            print("✓ PGN includes statistical annotations")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_json_export(self):
        """Test exporting DNA profile as JSON."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            result = PlayerDNAEnhanced.export_dna_json(dna, output_path)
            
            self.assertIsNotNone(result)
            self.assertTrue(output_path.exists())
            
            # Verify JSON content
            with open(output_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['player_name'], "TestPlayer")
                self.assertIn('opening_statistics', data)
                self.assertIn('total_games_analyzed', data)
            
            print(f"✓ DNA profile JSON exported: {output_path}")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_json_structure(self):
        """Test exported JSON structure."""
        dna = PlayerDNAEnhanced.analyze_games(self.test_games, "TestPlayer")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            PlayerDNAEnhanced.export_dna_json(dna, output_path)
            
            with open(output_path, 'r') as f:
                data = json.load(f)
                
                # Check required fields
                self.assertIn('player_name', data)
                self.assertIn('total_games_analyzed', data)
                self.assertIn('total_openings', data)
                self.assertIn('white_games', data)
                self.assertIn('black_games', data)
                self.assertIn('generated_at', data)
                self.assertIn('favorite_openings', data)
                self.assertIn('opening_statistics', data)
                
                # Check opening stats structure
                for eco, stats in data['opening_statistics'].items():
                    self.assertIn('eco_code', stats)
                    self.assertIn('opening_name', stats)
                    self.assertIn('total_games', stats)
                    self.assertIn('wins', stats)
                    self.assertIn('win_rate', stats)
            
            print("✓ JSON structure is complete and valid")
        finally:
            if output_path.exists():
                output_path.unlink()


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def setUp(self):
        PlayerDNAEnhanced.initialize()
        self.test_games = TestPlayerDNAEnhanced._create_test_games()
    
    def test_analyze_player_games_function(self):
        """Test analyze_player_games convenience function."""
        dna = analyze_player_games(self.test_games, "TestPlayer")
        
        self.assertIsInstance(dna, PlayerDNAProfile)
        self.assertEqual(dna.player_name, "TestPlayer")
        self.assertGreater(dna.total_games_analyzed, 0)
        
        print("✓ analyze_player_games convenience function works")
    
    def test_export_functions(self):
        """Test export convenience functions."""
        dna = analyze_player_games(self.test_games, "TestPlayer")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pgn', delete=False) as f:
            pgn_path = Path(f.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        
        try:
            # Update paths in profile
            dna_copy = dna
            
            # Export using convenience functions
            pgn_result = export_player_repertoire(dna_copy)
            json_result = export_player_dna_json(dna_copy)
            
            self.assertIsNotNone(pgn_result)
            self.assertIsNotNone(json_result)
            
            print("✓ Export convenience functions work")
        finally:
            for p in [pgn_path, json_path]:
                if p.exists():
                    p.unlink()


def run_tests():
    """Run all tests with detailed output."""
    print("\n" + "="*70)
    print("PLAYER DNA ENHANCED - TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPlayerDNAEnhanced))
    suite.addTests(loader.loadTestsFromTestCase(TestRepertoireExport))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
