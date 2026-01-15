"""
Chess Fairplay Analyzer
A forensic tool for statistical detection of potential cheating in chess.
"""

__version__ = "1.0.0"
__author__ = "Chess Fairplay Analyzer"
__description__ = "Analyze chess games for fair play violations"

# Import key components
from .cli import main
from .fetcher import fetch_player_games
from .analyzer import ChessAnalyzer
from .reporter import ReportGenerator, generate_report
from .engine import StockfishManager, EngineResult

__all__ = [
    'main',
    'fetch_player_games',
    'ChessAnalyzer',
    'ReportGenerator',
    'generate_report',
    'StockfishManager',
    'EngineResult',
    '__version__',
    '__author__',
    '__description__'
]