"""
ECO HTML Report Generator
Creates comprehensive, professional HTML reports with:
- Opening statistics and win rates
- FEN board positions as embedded images
- PGN snapshot games
- Detailed variation analysis
- Beautiful formatted tables with CSS styling

Priority: CLARITY and ACCURACY of data representation
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json

import chess
import chess.pgn

from chess_analyzer.eco_comprehensive import ECOComprehensive, OpeningData
from chess_analyzer.fen_to_image_enhanced import FENToImageEnhanced

logger = logging.getLogger(__name__)


class ECOReportGenerator:
    """Generate comprehensive ECO analysis reports in HTML."""
    
    REPORT_DIR = Path("reports/eco_analysis")
    TEMPLATE_DIR = Path("templates")
    
    # CSS styling
    DEFAULT_CSS = """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
        }
        
        header {
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #34495e;
            font-size: 1.8em;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 5px solid #3498db;
            padding-left: 15px;
        }
        
        h3 {
            color: #34495e;
            font-size: 1.3em;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        .opening-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .opening-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        .opening-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .opening-name {
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .eco-code {
            background-color: #3498db;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .board-container {
            display: inline-block;
            margin: 10px;
            text-align: center;
        }
        
        .board-image {
            border: 2px solid #34495e;
            border-radius: 4px;
            max-width: 100%;
            height: auto;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-box {
            background-color: white;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 5px;
            text-transform: uppercase;
            font-weight: bold;
        }
        
        .stat-value {
            font-size: 1.6em;
            color: #2c3e50;
            font-weight: bold;
        }
        
        .stat-box.wins {
            border-left-color: #27ae60;
        }
        
        .stat-box.draws {
            border-left-color: #f39c12;
        }
        
        .stat-box.losses {
            border-left-color: #e74c3c;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .pgn-container {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }
        
        .percentage-bar {
            display: inline-block;
            height: 20px;
            background-color: #3498db;
            border-radius: 3px;
            position: relative;
            min-width: 40px;
        }
        
        .percentage-bar-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-weight: bold;
            font-size: 0.8em;
            white-space: nowrap;
        }
        
        .summary-section {
            background-color: #ecf0f1;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .variation-depth {
            margin-left: 20px;
            padding-left: 10px;
            border-left: 3px solid #bdc3c7;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        .label-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        
        .label-popular {
            background-color: #d4edda;
            color: #155724;
        }
        
        .label-theoretical {
            background-color: #cce5ff;
            color: #004085;
        }
        
        .label-sharp {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            h1 {
                font-size: 1.8em;
            }
            
            h2 {
                font-size: 1.4em;
            }
        }
        
        @media print {
            body {
                background-color: white;
            }
            
            .container {
                box-shadow: none;
            }
            
            .opening-card {
                page-break-inside: avoid;
            }
        }
    </style>
    """
    
    @classmethod
    def initialize(cls):
        """Initialize report generator."""
        cls.REPORT_DIR.mkdir(parents=True, exist_ok=True)
        FENToImageEnhanced.initialize_cache()
        logger.info(f"ECO Report Generator initialized at {cls.REPORT_DIR}")
    
    @classmethod
    def generate_opening_report(
        cls,
        eco_code: str,
        include_statistics: bool = True,
        include_board: bool = True,
        output_file: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Generate a detailed report for a single opening.
        
        Args:
            eco_code: ECO code
            include_statistics: Whether to include statistics
            include_board: Whether to include board images
            output_file: Path to save report (optional)
            
        Returns:
            Path to generated report
        """
        opening = ECOComprehensive.get_opening(eco_code)
        if not opening:
            logger.error(f"Opening {eco_code} not found")
            return None
        
        cls.initialize()
        
        html = cls._create_html_header(f"ECO {eco_code}: {opening.get_full_name()}")
        html += cls._create_opening_section(opening, include_statistics, include_board)
        html += cls._create_html_footer()
        
        # Save report
        if not output_file:
            output_file = cls.REPORT_DIR / f"eco_{eco_code.lower()}.html"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Generated report: {output_file}")
        return output_file
    
    @classmethod
    def generate_comprehensive_report(
        cls,
        eco_codes: Optional[List[str]] = None,
        player_name: Optional[str] = None,
        output_file: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Generate comprehensive report for multiple openings.
        
        Args:
            eco_codes: List of ECO codes to include (None = all)
            player_name: Optional player name for title
            output_file: Path to save report
            
        Returns:
            Path to generated report
        """
        cls.initialize()
        
        # Get openings to report on
        if eco_codes:
            openings = {code: ECOComprehensive.get_opening(code) for code in eco_codes}
            openings = {k: v for k, v in openings.items() if v}
        else:
            openings = ECOComprehensive.get_all_openings()
        
        if not openings:
            logger.error("No openings found for report")
            return None
        
        # Create report
        title = f"ECO Opening Analysis Report"
        if player_name:
            title += f" - {player_name}"
        
        html = cls._create_html_header(title)
        html += cls._create_summary_section(openings)
        
        # Group by opening family (A, B, C, D, E)
        families = {}
        for eco_code, opening in openings.items():
            family = eco_code[0]
            if family not in families:
                families[family] = []
            families[family].append((eco_code, opening))
        
        # Generate sections by family
        for family in sorted(families.keys()):
            html += f'<h2>{cls._get_family_name(family)} Openings</h2>\n'
            for eco_code, opening in sorted(families[family]):
                html += cls._create_opening_section(opening, include_statistics=True, include_board=True)
        
        html += cls._create_html_footer()
        
        # Save report
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = cls.REPORT_DIR / f"eco_comprehensive_{timestamp}.html"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Generated comprehensive report: {output_file}")
        return output_file
    
    @classmethod
    def _create_html_header(cls, title: str) -> str:
        """Create HTML document header."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {cls.DEFAULT_CSS}
</head>
<body>
    <div class="container">
        <header>
            <h1>♔ {title} ♔</h1>
            <p style="color: #7f8c8d; font-size: 0.95em;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </header>
"""
        return html
    
    @classmethod
    def _create_html_footer(cls) -> str:
        """Create HTML document footer."""
        return """
        <footer class="footer">
            <p>Chess FairPlay Analyzer - ECO Opening Database Report</p>
            <p>For detailed chess analysis and fair play detection</p>
        </footer>
    </div>
</body>
</html>
"""
    
    @classmethod
    def _create_opening_section(
        cls,
        opening: OpeningData,
        include_statistics: bool = True,
        include_board: bool = True,
    ) -> str:
        """Create HTML section for a single opening."""
        html = f"""
        <div class="opening-card">
            <div class="opening-header">
                <div>
                    <div class="opening-name">{opening.get_full_name()}</div>
                    <div style="color: #7f8c8d; font-size: 0.9em;">
                        Min Moves: {opening.min_moves} | Typical Depth: {opening.typical_depth}
                    </div>
                </div>
                <span class="eco-code">{opening.eco_code}</span>
            </div>
"""
        
        # Add statistics
        if include_statistics:
            stats_html = cls._create_stats_section(opening)
            html += stats_html
        
        # Add board image
        if include_board and opening.final_fen:
            html += '<div style="text-align: center;">\n'
            board_html = FENToImageEnhanced.create_html_board_with_info(
                opening.final_fen,
                title="Final Position",
                stats={
                    'Moves': opening.min_moves,
                    'Depth': opening.typical_depth,
                },
                size_key="small"
            )
            html += board_html
            html += '</div>\n'
        
        # Add PGN
        if opening.canonical_pgn:
            html += f"""
            <h3>Canonical Main Line:</h3>
            <div class="pgn-container">
                {opening.canonical_pgn}
            </div>
"""
        
        html += '</div>\n'
        return html
    
    @classmethod
    def _create_stats_section(cls, opening: OpeningData) -> str:
        """Create statistics section for an opening."""
        html = '<div class="stats-grid">\n'
        
        # Total games
        html += f"""
        <div class="stat-box">
            <div class="stat-label">Total Games</div>
            <div class="stat-value">{opening.frequency_count}</div>
        </div>
"""
        
        # Win rate
        wins_color = "wins" if opening.win_rate > 0 else ""
        html += f"""
        <div class="stat-box {wins_color}">
            <div class="stat-label">Win Rate</div>
            <div class="stat-value">{opening.win_rate:.1f}%</div>
        </div>
"""
        
        # Draw rate
        draws_color = "draws" if opening.draw_rate > 0 else ""
        html += f"""
        <div class="stat-box {draws_color}">
            <div class="stat-label">Draw Rate</div>
            <div class="stat-value">{opening.draw_rate:.1f}%</div>
        </div>
"""
        
        # Loss rate
        losses_color = "losses" if opening.loss_rate > 0 else ""
        html += f"""
        <div class="stat-box {losses_color}">
            <div class="stat-label">Loss Rate</div>
            <div class="stat-value">{opening.loss_rate:.1f}%</div>
        </div>
"""
        
        # Frequency percentage
        html += f"""
        <div class="stat-box">
            <div class="stat-label">Frequency</div>
            <div class="stat-value">{opening.frequency_percentage:.1f}%</div>
        </div>
"""
        
        html += '</div>\n'
        return html
    
    @classmethod
    def _create_summary_section(cls, openings: Dict[str, OpeningData]) -> str:
        """Create summary section for all openings."""
        total_games = sum(o.frequency_count for o in openings.values())
        total_wins = sum(int((o.win_rate / 100) * o.frequency_count) for o in openings.values())
        total_draws = sum(int((o.draw_rate / 100) * o.frequency_count) for o in openings.values())
        total_losses = sum(int((o.loss_rate / 100) * o.frequency_count) for o in openings.values())
        
        win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
        draw_rate = (total_draws / total_games * 100) if total_games > 0 else 0
        loss_rate = (total_losses / total_games * 100) if total_games > 0 else 0
        
        html = """
        <div class="summary-section">
            <h2>Overall Summary</h2>
            <div class="stats-grid">
"""
        
        html += f"""
            <div class="stat-box">
                <div class="stat-label">Total Openings</div>
                <div class="stat-value">{len(openings)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Games</div>
                <div class="stat-value">{total_games}</div>
            </div>
            <div class="stat-box wins">
                <div class="stat-label">Total Wins</div>
                <div class="stat-value">{total_wins} ({win_rate:.1f}%)</div>
            </div>
            <div class="stat-box draws">
                <div class="stat-label">Total Draws</div>
                <div class="stat-value">{total_draws} ({draw_rate:.1f}%)</div>
            </div>
            <div class="stat-box losses">
                <div class="stat-label">Total Losses</div>
                <div class="stat-value">{total_losses} ({loss_rate:.1f}%)</div>
            </div>
"""
        
        html += """
            </div>
        </div>
"""
        
        return html
    
    @classmethod
    def _get_family_name(cls, family_code: str) -> str:
        """Get full name for opening family."""
        families = {
            "A": "Flank Openings",
            "B": "1.e4 c5 and Other Sicilian-like",
            "C": "1.e4 e5 and Other Semi-Open Games",
            "D": "1.d4 d5 (Queen's Pawn Closed)",
            "E": "1.d4 Nf6 and Indian Systems",
        }
        return families.get(family_code, f"{family_code}-codes")


# Convenience functions
def generate_single_opening_report(eco_code: str) -> Optional[Path]:
    """Generate report for single opening."""
    return ECOReportGenerator.generate_opening_report(eco_code)


def generate_eco_database_report(player_name: str = None) -> Optional[Path]:
    """Generate comprehensive ECO database report."""
    return ECOReportGenerator.generate_comprehensive_report(player_name=player_name)


# Initialize on import
ECOReportGenerator.initialize()
