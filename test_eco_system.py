"""
Test Suite for Enhanced ECO System, FEN Converter, and Report Generator
Tests accuracy of opening data, FEN conversions, and HTML report generation.
"""

import unittest
import tempfile
from pathlib import Path
import json
import chess
import chess.pgn

from chess_analyzer.eco_comprehensive import (
    ECOComprehensive, OpeningData, get_opening_data, get_opening_name_with_variation,
    record_eco_game, get_eco_statistics
)
from chess_analyzer.fen_to_image_enhanced import (
    FENToImageEnhanced, FENImageInfo, create_board_html, create_board_with_stats
)
from chess_analyzer.eco_report_generator import (
    ECOReportGenerator, generate_single_opening_report, generate_eco_database_report
)


class TestECOComprehensive(unittest.TestCase):
    """Test ECO Comprehensive Database."""
    
    def setUp(self):
        ECOComprehensive.initialize()
    
    def test_eco_initialization(self):
        """Test ECO database initialization."""
        self.assertTrue(ECOComprehensive._loaded)
        self.assertGreater(len(ECOComprehensive._cache), 0)
        print(f"✓ Loaded {len(ECOComprehensive._cache)} ECO codes")
    
    def test_get_opening_by_code(self):
        """Test retrieving opening by ECO code."""
        # Test various openings
        test_codes = ["C60", "E60", "D30", "B01"]
        
        for eco_code in test_codes:
            opening = ECOComprehensive.get_opening(eco_code)
            self.assertIsNotNone(opening)
            self.assertEqual(opening.eco_code, eco_code)
            self.assertIsNotNone(opening.name)
            print(f"✓ {eco_code}: {opening.get_full_name()}")
    
    def test_opening_fen_validity(self):
        """Test FEN positions are valid."""
        test_codes = ["C60", "E60", "D30", "B01"]
        
        for eco_code in test_codes:
            opening = ECOComprehensive.get_opening(eco_code)
            if opening and opening.final_fen:
                is_valid = ECOComprehensive.validate_fen(eco_code)
                self.assertTrue(is_valid, f"Invalid FEN for {eco_code}")
                # Try to create board from FEN
                board = chess.Board(opening.final_fen)
                self.assertIsNotNone(board)
                print(f"✓ Valid FEN for {eco_code}")
    
    def test_pgn_parsing(self):
        """Test PGN move parsing."""
        opening = ECOComprehensive.get_opening("C60")
        moves = ECOComprehensive.get_pgn_moves("C60")
        
        self.assertGreater(len(moves), 0)
        print(f"✓ Parsed {len(moves)} moves from ECO C60")
        
        # Try to play moves on board
        board = chess.Board()
        for move_san in moves:
            try:
                move = board.parse_san(move_san)
                board.push(move)
            except:
                self.fail(f"Could not parse move: {move_san}")
        
        print(f"✓ All moves in C60 are valid: {' '.join(moves)}")
    
    def test_statistics_recording(self):
        """Test game result recording."""
        ECOComprehensive.clear_statistics()
        
        # Record some games
        record_eco_game("C60", "win", "Game 1")
        record_eco_game("C60", "draw", "Game 2")
        record_eco_game("C60", "loss", "Game 3")
        
        # Get statistics
        stats = get_eco_statistics("C60")
        self.assertIsNotNone(stats)
        self.assertEqual(stats['frequency'], 3)
        
        opening = ECOComprehensive.get_opening("C60")
        self.assertAlmostEqual(opening.win_rate, 33.33, places=1)
        self.assertAlmostEqual(opening.draw_rate, 33.33, places=1)
        self.assertAlmostEqual(opening.loss_rate, 33.33, places=1)
        
        print(f"✓ Statistics recorded: W:{opening.win_rate:.1f}% D:{opening.draw_rate:.1f}% L:{opening.loss_rate:.1f}%")
    
    def test_all_openings_retrieval(self):
        """Test getting all openings."""
        all_openings = ECOComprehensive.get_all_openings()
        self.assertGreater(len(all_openings), 0)
        print(f"✓ Retrieved {len(all_openings)} openings")
    
    def test_name_filtering(self):
        """Test filtering openings by name."""
        ruy_lopez = ECOComprehensive.get_all_openings("Ruy")
        self.assertGreater(len(ruy_lopez), 0)
        
        for eco_code, opening in ruy_lopez.items():
            self.assertIn("Ruy", opening.name)
        
        print(f"✓ Found {len(ruy_lopez)} 'Ruy' openings")


class TestFENToImageEnhanced(unittest.TestCase):
    """Test FEN to Image conversion."""
    
    def setUp(self):
        FENToImageEnhanced.initialize_cache()
        self.test_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # Starting position
        self.test_ruy_fen = "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4"  # Ruy Lopez
    
    def test_fen_validation(self):
        """Test FEN validation."""
        self.assertTrue(FENToImageEnhanced.validate_fen(self.test_fen))
        self.assertTrue(FENToImageEnhanced.validate_fen(self.test_ruy_fen))
        self.assertFalse(FENToImageEnhanced.validate_fen("invalid"))
        print("✓ FEN validation works")
    
    def test_svg_generation(self):
        """Test SVG generation from FEN."""
        svg = FENToImageEnhanced.fen_to_svg(self.test_fen, square_size=40)
        self.assertIsNotNone(svg)
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        print("✓ SVG generation successful")
    
    def test_base64_conversion(self):
        """Test base64 image conversion."""
        base64_data = FENToImageEnhanced.fen_to_base64(self.test_fen, "small")
        
        # Should be a data URL or SVG base64
        if base64_data:
            self.assertTrue(
                base64_data.startswith("data:image/") or base64_data.startswith("data:application/")
            )
            print("✓ Base64 conversion successful")
        else:
            print("⚠ Base64 conversion returned empty (cairosvg may not be installed)")
    
    def test_image_hash_consistency(self):
        """Test hash generation is consistent."""
        hash1 = FENToImageEnhanced.get_image_hash(self.test_fen, "normal")
        hash2 = FENToImageEnhanced.get_image_hash(self.test_fen, "normal")
        
        self.assertEqual(hash1, hash2)
        print("✓ Image hash is consistent")
    
    def test_different_sizes(self):
        """Test different image sizes."""
        for size_key in FENToImageEnhanced.SQUARE_SIZES.keys():
            svg = FENToImageEnhanced.fen_to_svg(
                self.test_fen,
                square_size=FENToImageEnhanced.SQUARE_SIZES[size_key]
            )
            self.assertIsNotNone(svg)
        
        print(f"✓ All {len(FENToImageEnhanced.SQUARE_SIZES)} image sizes generated")
    
    def test_html_element_generation(self):
        """Test HTML element generation."""
        html = FENToImageEnhanced.create_html_image_element(
            self.test_fen,
            alt_text="Test position",
            size_key="small"
        )
        
        self.assertIn("<img", html)
        self.assertIn("Test position", html)
        print("✓ HTML image element generated")
    
    def test_board_with_stats(self):
        """Test board with statistics."""
        stats = {"Accuracy": "95%", "Depth": "20"}
        html = FENToImageEnhanced.create_html_board_with_info(
            self.test_fen,
            title="Test Board",
            stats=stats,
            size_key="small"
        )
        
        self.assertIn("Test Board", html)
        self.assertIn("Accuracy", html)
        self.assertIn("95%", html)
        print("✓ Board with statistics generated")


class TestECOReportGenerator(unittest.TestCase):
    """Test ECO Report Generator."""
    
    def setUp(self):
        ECOReportGenerator.initialize()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_report_initialization(self):
        """Test report generator initialization."""
        self.assertTrue(ECOReportGenerator.REPORT_DIR.exists())
        print("✓ Report directory initialized")
    
    def test_single_opening_report(self):
        """Test single opening report generation."""
        ECOComprehensive.initialize()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            result = ECOReportGenerator.generate_opening_report(
                "C60",
                output_file=output_path
            )
            
            self.assertIsNotNone(result)
            self.assertTrue(output_path.exists())
            
            # Verify HTML content
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("C60", content)
                self.assertIn("Ruy Lopez", content)
                self.assertIn("<!DOCTYPE html>", content)
            
            print(f"✓ Single opening report generated: {output_path}")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_comprehensive_report(self):
        """Test comprehensive report generation."""
        ECOComprehensive.initialize()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            # Generate report for sample openings
            test_codes = ["C60", "E60", "D30", "B01"]
            result = ECOReportGenerator.generate_comprehensive_report(
                eco_codes=test_codes,
                player_name="Test Player",
                output_file=output_path
            )
            
            self.assertIsNotNone(result)
            self.assertTrue(output_path.exists())
            
            # Verify HTML content
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("Test Player", content)
                self.assertIn("C60", content)
                self.assertIn("<!DOCTYPE html>", content)
            
            print(f"✓ Comprehensive report generated: {output_path}")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_html_structure(self):
        """Test HTML structure is valid."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            ECOReportGenerator.generate_opening_report("C60", output_file=output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                
                # Check basic HTML structure
                self.assertIn("<!DOCTYPE html>", content)
                self.assertIn("<html", content)
                self.assertIn("</html>", content)
                self.assertIn("<head>", content)
                self.assertIn("<body>", content)
                self.assertIn("</body>", content)
                
                # Check CSS
                self.assertIn("<style>", content)
                self.assertIn("</style>", content)
            
            print("✓ HTML structure is valid")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_css_styling(self):
        """Test CSS styling is included."""
        html_header = ECOReportGenerator._create_html_header("Test")
        
        self.assertIn("<style>", html_header)
        self.assertIn(".container", html_header)
        self.assertIn(".opening-card", html_header)
        self.assertIn(".stat-box", html_header)
        
        print("✓ CSS styling included in reports")


class TestIntegration(unittest.TestCase):
    """Integration tests for all components."""
    
    def setUp(self):
        ECOComprehensive.initialize()
        FENToImageEnhanced.initialize_cache()
        ECOReportGenerator.initialize()
    
    def test_eco_to_report_workflow(self):
        """Test complete workflow from ECO to report."""
        # Get opening
        opening = ECOComprehensive.get_opening("C60")
        self.assertIsNotNone(opening)
        
        # Create board image
        base64_data = FENToImageEnhanced.fen_to_base64(opening.final_fen, "small")
        # May be empty if cairosvg not installed, but shouldn't error
        
        # Generate report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            result = ECOReportGenerator.generate_opening_report("C60", output_file=output_path)
            self.assertIsNotNone(result)
            
            print("✓ Complete ECO to report workflow successful")
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_statistics_in_report(self):
        """Test statistics are recorded and included in reports."""
        ECOComprehensive.clear_statistics()
        
        # Record games
        record_eco_game("C60", "win")
        record_eco_game("C60", "win")
        record_eco_game("C60", "draw")
        
        # Generate report
        opening = ECOComprehensive.get_opening("C60")
        self.assertEqual(opening.frequency_count, 3)
        self.assertAlmostEqual(opening.win_rate, 66.67, places=1)
        
        print("✓ Statistics correctly tracked and available for reports")


def run_tests():
    """Run all tests with detailed output."""
    print("\n" + "="*70)
    print("ECO COMPREHENSIVE SYSTEM - TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestECOComprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestFENToImageEnhanced))
    suite.addTests(loader.loadTestsFromTestCase(TestECOReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
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
