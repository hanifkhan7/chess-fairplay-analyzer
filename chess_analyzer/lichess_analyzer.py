"""
Lichess API integration for fast game analysis.
Uses Lichess's cloud analysis instead of local Stockfish.
"""
import requests
import chess
import chess.pgn
import logging
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)

class LichessAnalyzer:
    """Analyze games using Lichess API instead of local Stockfish."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Lichess analyzer with OAuth token."""
        self.config = config or {}
        self.base_url = "https://lichess.org/api"
        self.session = requests.Session()
        
        # Add OAuth authentication
        lichess_config = self.config.get('lichess', {})
        api_token = lichess_config.get('api_token', '')
        
        if api_token:
            self.session.headers.update({
                'Accept': 'application/json',
                'Authorization': f'Bearer {api_token}'
            })
            logger.info(f"Lichess API authenticated")
        else:
            self.session.headers.update({'Accept': 'application/json'})
            logger.warning("Lichess API token not configured")
        
    def analyze_game(self, game: chess.pgn.Game) -> Dict[str, Any]:
        """
        Analyze a game using Lichess API.
        
        Args:
            game: chess.pgn.Game object
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Get PGN string
            import io
            pgn_io = io.StringIO()
            exporter = chess.pgn.FileExporter(pgn_io)
            game.accept(exporter)
            pgn_str = pgn_io.getvalue()
            
            logger.info(f"Requesting Lichess analysis for game...")
            
            # Request analysis from Lichess - use authenticated endpoint
            response = self.session.post(
                f"{self.base_url}/analysis/batch",
                data={"pgn": pgn_str},
                timeout=120  # Increased timeout for cloud analysis
            )
            
            if response.status_code not in [200, 202]:
                logger.warning(f"Lichess API error: {response.status_code} - {response.text[:200]}")
                return {'error': f'Lichess API error: {response.status_code}', 'positions': []}
            
            # 202 means request accepted but still processing
            if response.status_code == 202:
                logger.info("Analysis request accepted, waiting for results...")
                time.sleep(2)  # Wait briefly for processing
                return {'status': 'processing', 'positions': []}

            
            # Parse the response
            lines = response.text.strip().split('\n')
            if not lines:
                return {'error': 'No analysis from Lichess', 'positions': []}
            
            analysis_data = self._parse_lichess_analysis(lines[0], game)
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error with Lichess analysis: {e}")
            return {'error': str(e), 'positions': []}
    
    def _parse_lichess_analysis(self, response_str: str, game: chess.pgn.Game) -> Dict[str, Any]:
        """Parse Lichess analysis response."""
        import json
        
        try:
            analysis_obj = json.loads(response_str)
        except json.JSONDecodeError:
            logger.error("Failed to parse Lichess response")
            return {'error': 'Invalid response from Lichess', 'positions': []}
        
        # Extract moves and analysis
        positions = []
        move_count = 0
        board = game.board()
        
        if 'moves' not in analysis_obj:
            logger.warning("No moves in Lichess response")
            return {'error': 'No moves in response', 'positions': []}
        
        moves_data = analysis_obj['moves']
        player_moves = list(game.mainline_moves())
        
        for i, move_analysis in enumerate(moves_data):
            move_count = i + 1
            
            if i >= len(player_moves):
                break
            
            player_move = player_moves[i]
            
            # Get best move(s) from analysis
            best_move = None
            if 'best' in move_analysis:
                try:
                    best_move = chess.Move.from_uci(move_analysis['best'])
                except:
                    best_move = None
            
            # Get evaluation
            score_cp = 0
            if 'eval' in move_analysis:
                eval_data = move_analysis['eval']
                if 'cp' in eval_data:
                    score_cp = eval_data['cp']
                elif 'mate' in eval_data:
                    # Mate in N moves
                    score_cp = 10000 if eval_data['mate'] > 0 else -10000
            
            player_moved_best = (best_move == player_move) if best_move else False
            
            position_data = {
                'move_number': move_count,
                'move': str(player_move),
                'fen': board.fen(),
                'best_move': str(best_move) if best_move else None,
                'score_cp': score_cp,
                'player_moved_best': player_moved_best,
                'depth': move_analysis.get('depth', 20)
            }
            
            positions.append(position_data)
            board.push(player_move)
        
        # Calculate engine correlation
        if positions:
            best_moves_count = sum(1 for p in positions if p.get('player_moved_best', False))
            total_moves = len(positions)
            engine_correlation = (best_moves_count / total_moves * 100) if total_moves > 0 else 0
        else:
            engine_correlation = 0
        
        return {
            'positions': positions,
            'engine_correlation': engine_correlation,
            'summary': {
                'total_moves': move_count,
                'engine_correlation': engine_correlation,
                'positions_analyzed': len(positions),
                'source': 'lichess'
            }
        }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.session:
            self.session.close()
