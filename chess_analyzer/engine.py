"""
Stockfish chess engine integration for game analysis.
"""
import chess
import chess.engine
import logging
import os
import subprocess
import platform
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Local imports
from .utils.helpers import find_stockfish_windows, test_stockfish_installation

logger = logging.getLogger(__name__)

@dataclass
class EngineResult:
    """Container for engine analysis results."""
    best_move: Optional[chess.Move] = None
    score: Optional[chess.engine.PovScore] = None
    depth: int = 0
    pv: List[chess.Move] = None
    time_used: float = 0.0
    
    def __post_init__(self):
        if self.pv is None:
            self.pv = []
    
    @property
    def centipawns(self) -> Optional[float]:
        """Get score in centipawns."""
        if self.score is None:
            return None
        return self.score.white().score(mate_score=10000)

class StockfishManager:
    """Manages Stockfish engine instances for analysis - FIXED FOR SF16."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Stockfish manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.engine_path = self._get_engine_path()
        self.engine_depth = self.config.get('analysis', {}).get('engine_depth', 18)
        self.threads = self.config.get('analysis', {}).get('threads', 2)
        self.hash_size = self.config.get('analysis', {}).get('hash_size', 256)
        
        self.engine = None
        logger.info(f"Stockfish manager initialized with: {self.engine_path}")
    
    def _get_engine_path(self) -> str:
        """Get Stockfish executable path - SIMPLIFIED."""
        # 1. Try config path
        config_path = self.config.get('analysis', {}).get('engine_path', '')
        if config_path:
            # Try with different separators
            paths_to_try = [
                config_path,
                config_path.replace('/', '\\'),
                config_path.replace('\\', '/'),
                os.path.join(os.getcwd(), config_path)
            ]
            
            for path in paths_to_try:
                if os.path.exists(path):
                    logger.info(f"Using configured path: {path}")
                    return path
        
        # 2. Try auto-detection
        logger.info("Auto-detecting Stockfish...")
        detected_path = find_stockfish_windows()
        
        if detected_path:
            logger.info(f"Auto-detected: {detected_path}")
            return detected_path
        
        # 3. Last resort: check common locations
        common_paths = [
            "stockfish\\stockfish-windows-x86-64.exe",
            "stockfish/stockfish-windows-x86-64.exe",
            ".\\stockfish\\stockfish-windows-x86-64.exe",
            "stockfish.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found at common path: {path}")
                return path
        
        raise FileNotFoundError(
            "Stockfish not found. Please ensure:\n"
            "1. 'stockfish' folder exists with 'stockfish-windows-x86-64.exe'\n"
            "2. Or set correct engine_path in config.yaml"
        )
    
    def _verify_engine(self) -> None:
        """Verify Stockfish installation - LENIENT VERSION."""
        logger.info("Verifying Stockfish...")
        
        # Just check if file exists
        if not os.path.exists(self.engine_path):
            raise FileNotFoundError(f"Stockfish not found at: {self.engine_path}")
        
        logger.info(f"✅ Stockfish found: {self.engine_path}")
        
        # Try to get version info
        try:
            # Stockfish 16 uses '--help'
            result = subprocess.run([self.engine_path, "--help"],
                                  capture_output=True,
                                  text=True,
                                  timeout=3)
            
            if "Stockfish" in result.stdout:
                import re
                match = re.search(r'Stockfish (\d+)', result.stdout)
                if match:
                    logger.info(f"✅ Stockfish {match.group(1)} verified")
                else:
                    logger.info("✅ Stockfish verified")
            else:
                logger.warning("⚠️  Could not verify Stockfish version")
                
        except Exception as e:
            logger.warning(f"⚠️  Version check failed: {e}")
            logger.info("⚠️  Will try to use engine anyway")
    
    def start_engine(self) -> chess.engine.SimpleEngine:
        """Start Stockfish engine."""
        try:
            logger.info(f"Starting Stockfish engine...")
            
            # Configure engine options
            engine_options = {
                'Threads': self.threads,
                'Hash': self.hash_size,
            }
            
            # Start engine
            engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            
            # Configure engine
            engine.configure(engine_options)
            
            logger.info("✅ Stockfish engine started successfully")
            return engine
            
        except Exception as e:
            logger.error(f"Failed to start Stockfish engine: {e}")
            raise
    
    def analyze_position(
        self, 
        board: chess.Board, 
        depth: Optional[int] = None,
        movetime: Optional[int] = None
    ) -> EngineResult:
        """
        Analyze a single chess position.
        
        Args:
            board: Current board position
            depth: Analysis depth (overrides config)
            movetime: Maximum time in milliseconds
        
        Returns:
            EngineResult with analysis
        """
        if depth is None:
            depth = self.engine_depth
        
        import time
        start_time = time.time()
        result = EngineResult(depth=depth)
        
        try:
            # Get engine instance
            if not self.engine:
                self.engine = self.start_engine()
            
            # Configure analysis limits
            limits = chess.engine.Limit(depth=depth)
            if movetime:
                limits = chess.engine.Limit(time=movetime / 1000)
            
            # Analyze position
            analysis = self.engine.analyse(board, limits)
            
            # Extract results
            if analysis.get('pv'):
                result.best_move = analysis['pv'][0]
            result.score = analysis.get('score')
            result.pv = analysis.get('pv', [])
            result.time_used = time.time() - start_time
            
            logger.debug(f"Analyzed position. Best: {result.best_move}, Score: {result.centipawns}")
            
            return result
            
        except chess.engine.EngineTerminatedError:
            logger.error("Stockfish engine terminated")
            # Try to restart
            self.engine = None
            return self.analyze_position(board, depth, movetime)
        except Exception as e:
            logger.error(f"Error analyzing position: {e}")
            result.time_used = time.time() - start_time
            return result
    
    def analyze_game(self, game: chess.pgn.Game) -> Dict[str, Any]:
        """
        Analyze all positions in a game.
        
        Args:
            game: chess.pgn.Game object
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing game: {game.headers.get('White', '?')} vs {game.headers.get('Black', '?')}")
        
        board = game.board()
        analysis_data = {
            'positions': [],
            'moves': [],
            'summary': {}
        }
        
        move_count = 0
        
        try:
            # Start fresh engine for this game
            engine = self.start_engine()
            
            # Go through each move
            for move in game.mainline_moves():
                move_count += 1
                
                # Analyze current position
                analysis = engine.analyse(board, chess.engine.Limit(depth=self.engine_depth))
                
                # Check if player's move matches engine's best move
                best_move = analysis.get('pv', [board.peek()])[0] if analysis.get('pv') else None
                player_moved_best = (best_move == move)
                
                position_data = {
                    'move_number': move_count,
                    'move': str(move),
                    'fen': board.fen(),
                    'best_move': str(best_move) if best_move else None,
                    'score_cp': analysis['score'].white().score(mate_score=10000) if 'score' in analysis else None,
                    'player_moved_best': player_moved_best
                }
                
                analysis_data['positions'].append(position_data)
                
                # Make the move
                board.push(move)
            
            # Calculate engine correlation
            if analysis_data['positions']:
                best_moves = sum(1 for pos in analysis_data['positions'] if pos.get('player_moved_best', False))
                total_positions = len(analysis_data['positions'])
                engine_correlation = (best_moves / total_positions * 100) if total_positions > 0 else 0
                
                analysis_data['engine_correlation'] = engine_correlation
                analysis_data['summary'] = {
                    'total_moves': move_count,
                    'engine_correlation': engine_correlation,
                    'positions_analyzed': total_positions
                }
            
            # Close engine
            try:
                engine.quit()
            except:
                pass
            
            logger.info(f"Game analysis complete: {move_count} moves, {engine_correlation:.1f}% engine correlation")
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error analyzing game: {e}")
            
            # Try to close engine
            try:
                if 'engine' in locals():
                    engine.quit()
            except:
                pass
            
            return {'error': str(e), 'positions': [], 'engine_correlation': 0}
    
    def cleanup(self) -> None:
        """Clean up engine instances."""
        logger.info("Cleaning up Stockfish engine...")
        
        if self.engine:
            try:
                self.engine.quit()
                logger.info("Stockfish engine stopped")
            except:
                pass
            self.engine = None