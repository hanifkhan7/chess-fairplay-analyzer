"""
Core analysis logic for detecting fair play violations - ENHANCED DETECTIVE MODE.
"""
import chess
import chess.pgn
import logging
import statistics
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Local imports
from .engine import StockfishManager

logger = logging.getLogger(__name__)

@dataclass
class GameAnalysis:
    """Analysis results for a single game."""
    game: chess.pgn.Game
    engine_correlation: float  # Percentage of moves matching engine's top choice
    avg_centipawn_loss: float  # Average centipawn loss per move (lower = stronger)
    accuracy_score: float  # Derived accuracy percentage
    suspicious_moves: List[Dict]  # Moves that look suspicious
    time_controls: Dict[str, Any]
    analysis_time: float
    metadata: Dict[str, Any]
    
    # Enhanced analysis
    opening_accuracy: float = 0.0  # Accuracy in opening phase
    middlegame_accuracy: float = 0.0  # Accuracy in middlegame phase
    endgame_accuracy: float = 0.0  # Accuracy in endgame phase
    opening_book_depth: int = 0  # How far into opening book
    blunder_count: int = 0  # Moves losing >200 centipawns
    critical_move_accuracy: float = 0.0  # Accuracy in critical positions
    time_pressure_accuracy: float = 0.0  # Accuracy when low on time
    performance_vs_rating: float = 0.0  # Performance rating vs reported rating
    
    # Modern detector metrics
    move_time_consistency: float = 0.0  # How consistent are move times (0-100, high = suspicious)
    probability_correlation: float = 0.0  # Likelihood of finding best moves (modern chess.com metric)
    win_loss_rate: float = 0.0  # Win percentage
    draw_rate: float = 0.0  # Draw percentage
    loss_rate: float = 0.0  # Loss percentage
    superhuman_score: float = 0.0  # IM+ level indicator (0-100)
    rating_differential_score: float = 0.0  # Performance vs opponent ratings
    
    @property
    def is_suspicious(self) -> bool:
        """Check if game shows suspicious patterns - MODERN DETECTION."""
        return (
            self.engine_correlation > 95.0 or  # Too many engine moves
            self.avg_centipawn_loss < 10.0 or  # Too few mistakes
            len(self.suspicious_moves) > 5 or  # Multiple suspicious moves
            self.critical_move_accuracy > 98.0 or  # Too perfect in critical positions
            self.opening_accuracy > 99.0 or  # Perfect opening play
            self.move_time_consistency > 85.0 or  # Engine-like timing
            self.probability_correlation > 94.0  # Statistical impossibility
        )

@dataclass
class PlayerAnalysis:
    """Aggregated analysis results for a player."""
    username: str
    games_analyzed: int
    total_games_fetched: int
    game_analyses: List[GameAnalysis]
    
    # Statistics
    avg_engine_correlation: float
    avg_centipawn_loss: float
    accuracy_consistency: float  # Standard deviation of accuracy
    
    # Suspicion indicators
    suspicious_game_count: int
    extremely_accurate_games: int  # Games with >97% engine correlation
    
    # Time control analysis
    performance_by_tc: Dict[str, Dict[str, float]]
    
    # Enhanced detective metrics
    opening_preparation_score: float = 0.0  # How much opening preparation
    endgame_mastery_score: float = 0.0  # Endgame strength vs rating
    critical_position_handling: float = 0.0  # How well handling critical moves
    blunder_avoidance_score: float = 0.0  # Suspicious avoidance of blunders
    win_rate_anomaly: float = 0.0  # Win rate compared to rating expectation
    move_time_suspicion: float = 0.0  # Suspicion from move time patterns
    rating_jump_detection: List[float] = None  # Detected rating jumps
    win_rate_data: Dict = None  # Win rate analysis data
    
    # Modern detection metrics (Chess.com style)
    avg_move_time_consistency: float = 0.0  # Engine-like timing (0-100)
    avg_probability_correlation: float = 0.0  # Likelihood of best moves (0-100)
    avg_win_rate: float = 0.0  # Actual win percentage
    avg_draw_rate: float = 0.0  # Draw percentage
    avg_loss_rate: float = 0.0  # Loss percentage
    avg_superhuman_score: float = 0.0  # IM+ level indicator
    rating_differential_anomaly: float = 0.0  # Performance vs opponents
    avg_time_scramble_accuracy: float = 0.0  # Accuracy in time pressure
    
    def __post_init__(self):
        if self.rating_jump_detection is None:
            self.rating_jump_detection = []
        if self.win_rate_data is None:
            self.win_rate_data = {}
    
    @property
    def suspicion_score(self) -> float:
        """Calculate overall suspicion score (0-100) - MODERN DETECTION."""
        if self.games_analyzed == 0:
            return 0.0
        
        score = 0.0
        
        # Engine correlation weight: 22%
        if self.avg_engine_correlation > 90:
            score += 22 * (self.avg_engine_correlation - 90) / 10
        
        # Centipawn loss weight: 16%
        if self.avg_centipawn_loss < 20:
            score += 16 * (20 - self.avg_centipawn_loss) / 20
        
        # Consistency weight: 10%
        if self.accuracy_consistency < 15:
            score += 10 * (15 - self.accuracy_consistency) / 15
        
        # MODERN: Probability correlation: 15%
        if self.avg_probability_correlation > 80:
            score += 15 * min(1.0, (self.avg_probability_correlation - 80) / 20)
        
        # MODERN: Move time consistency (engine-like timing): 12%
        if self.avg_move_time_consistency > 70:
            score += 12 * min(1.0, (self.avg_move_time_consistency - 70) / 30)
        
        # Extremely accurate games: 8%
        extremely_accurate_ratio = self.extremely_accurate_games / max(1, self.games_analyzed)
        score += 8 * min(1.0, extremely_accurate_ratio)
        
        # Critical position handling: 8%
        if self.critical_position_handling > 95:
            score += 8 * (self.critical_position_handling - 95) / 5
        
        # MODERN: Superhuman performance: 6%
        if self.avg_superhuman_score > 60:
            score += 6 * min(1.0, (self.avg_superhuman_score - 60) / 40)
        
        # Opening preparation: 5%
        if self.opening_preparation_score > 85:
            score += 5 * (self.opening_preparation_score - 85) / 15
        
        # Win rate anomaly: 3%
        score += 3 * min(1.0, self.win_rate_anomaly / 50)
        
        # Rating jump detection: 2%
        rating_jump_score = len(self.rating_jump_detection) * 20 if self.rating_jump_detection else 0
        score += 2 * min(1.0, rating_jump_score / 100)
        
        # Move time suspicion: 2%
        score += 2 * min(1.0, self.move_time_suspicion / 100)
        
        return min(100.0, score)
    
    @property
    def risk_level(self) -> str:
        """Get risk level based on suspicion score."""
        score = self.suspicion_score
        
        if score >= 80:
            return "VERY HIGH"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MODERATE"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"

class ChessAnalyzer:
    """Main analyzer class for detecting fair play violations - FIXED FOR MULTI-GAME ANALYSIS."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.engine_manager = StockfishManager(config)
        self.thresholds = self.config.get('analysis', {}).get('thresholds', {})
        
        logger.info("ChessAnalyzer initialized")
    
    def analyze_games(self, games: List[chess.pgn.Game]) -> PlayerAnalysis:
        """
        Analyze MULTIPLE games for a player - FIXED TO ANALYZE ALL GAMES.
        
        Args:
            games: List of games to analyze
        
        Returns:
            PlayerAnalysis with aggregated results
        """
        if not games:
            raise ValueError("No games to analyze")
        
        logger.info(f"Starting analysis of {len(games)} games")
        
        game_analyses = []
        total_analysis_time = 0.0
        analyzed_count = 0
        
        # Analyze each game
        for i, game in enumerate(games, 1):
            logger.info(f"Analyzing game {i}/{len(games)}")
            
            try:
                game_analysis = self._analyze_single_game(game)
                game_analyses.append(game_analysis)
                total_analysis_time += game_analysis.analysis_time
                analyzed_count += 1
                
                logger.info(f"  Game {i}: {game_analysis.engine_correlation:.1f}% engine correlation, "
                           f"{game_analysis.avg_centipawn_loss:.1f} avg CPL")
                
            except Exception as e:
                logger.error(f"Failed to analyze game {i}: {e}")
                continue
        
        # Aggregate results
        if analyzed_count > 0:
            player_analysis = self._aggregate_analyses(game_analyses)
            player_analysis.total_games_fetched = len(games)
            player_analysis.analysis_time = total_analysis_time
            
            logger.info(f"Analysis complete: {analyzed_count}/{len(games)} games analyzed "
                       f"in {total_analysis_time:.1f}s")
            logger.info(f"Suspicion score: {player_analysis.suspicion_score:.1f} "
                       f"({player_analysis.risk_level} risk)")
        else:
            # Create empty analysis if no games could be analyzed
            player_analysis = PlayerAnalysis(
                username=games[0].headers.get('White', 'Unknown').split()[0] if games else 'Unknown',
                games_analyzed=0,
                total_games_fetched=len(games),
                game_analyses=[],
                avg_engine_correlation=0.0,
                avg_centipawn_loss=999.0,
                accuracy_consistency=0.0,
                suspicious_game_count=0,
                extremely_accurate_games=0,
                performance_by_tc={}
            )
            logger.warning("No games could be analyzed")
        
        return player_analysis
    
    def _analyze_single_game(self, game: chess.pgn.Game) -> GameAnalysis:
        """
        Analyze a single chess game - ENHANCED DETECTIVE MODE.
        
        Args:
            game: chess.pgn.Game object
        
        Returns:
            GameAnalysis with detailed results
        """
        import time
        start_time = time.time()
        
        # Get game metadata
        metadata = self._extract_game_metadata(game)
        
        # Analyze with engine
        engine_analysis = self.engine_manager.analyze_game(game)
        
        # Calculate statistics
        engine_correlation = engine_analysis.get('engine_correlation', 0.0)
        
        # Calculate average CPL from positions
        positions = engine_analysis.get('positions', [])
        cpl_values = []
        previous_score = None
        blunder_count = 0
        
        for pos in positions:
            score_cp = pos.get('score_cp')
            if score_cp is not None:
                if previous_score is not None:
                    cpl = abs(score_cp - previous_score)
                    cpl_values.append(cpl)
                    # Count blunders (loss of >200 centipawns)
                    if cpl > 200:
                        blunder_count += 1
                previous_score = -score_cp  # Negate for opponent's perspective
        
        avg_cpl = statistics.mean(cpl_values) if cpl_values else 999.0
        
        # Calculate accuracy (simplified)
        accuracy = 100 - min(avg_cpl / 2, 100) if avg_cpl < 200 else 50.0
        accuracy = max(0.0, min(100.0, accuracy))
        
        # ENHANCED: Analyze by game phases
        board = game.board()
        move_count = 0
        opening_moves = []
        middlegame_moves = []
        endgame_moves = []
        critical_moves = []
        
        for pos in positions:
            move_count = pos.get('move_number', move_count)
            
            # Phase detection
            piece_count = len(board.pieces(chess.PAWN, chess.WHITE)) + len(board.pieces(chess.PAWN, chess.BLACK))
            piece_count += len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))
            piece_count += len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))
            piece_count += len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))
            
            if move_count <= 10:
                opening_moves.append(pos)
            elif piece_count <= 6:
                endgame_moves.append(pos)
            else:
                middlegame_moves.append(pos)
            
            # Detect critical positions (large score swings)
            score_cp = pos.get('score_cp', 0)
            if abs(score_cp) > 300:
                critical_moves.append(pos)
        
        # Calculate phase-specific accuracies
        opening_accuracy = self._calculate_phase_accuracy(opening_moves)
        middlegame_accuracy = self._calculate_phase_accuracy(middlegame_moves)
        endgame_accuracy = self._calculate_phase_accuracy(endgame_moves)
        critical_move_accuracy = self._calculate_phase_accuracy(critical_moves)
        
        # ENHANCED: Identify suspicious moves
        suspicious_moves = []
        for pos in positions:
            if pos.get('player_moved_best', False):
                score_cp = pos.get('score_cp', 0)
                if abs(score_cp) < 200:  # Complex position
                    suspicious_moves.append({
                        'move_number': pos.get('move_number', 0),
                        'move': pos.get('move', ''),
                        'best_move': pos.get('best_move', ''),
                        'score_cp': score_cp
                    })
        
        # Time control info
        time_controls = {
            'time_class': metadata.get('time_class', 'unknown'),
            'time_control': metadata.get('time_control', 'unknown'),
            'rated': metadata.get('rated', False)
        }
        
        # MODERN DETECTION: Calculate move time consistency (engine-like timing)
        move_times = engine_analysis.get('move_times', [])
        move_time_consistency = self._calculate_move_time_consistency(move_times)
        
        # MODERN DETECTION: Calculate probability correlation
        # This is the likelihood of finding the best moves consistently
        probability_correlation = self._calculate_probability_correlation(
            engine_correlation, positions, critical_moves
        )
        
        # MODERN DETECTION: Extract game result and calculate win/draw/loss
        result = metadata.get('result', '?')
        win_rate = 1.0 if result == '1-0' else (0.5 if result == '1/2-1/2' else 0.0)
        draw_rate = 1.0 if result == '1/2-1/2' else 0.0
        loss_rate = 1.0 if result == '0-1' else 0.0
        
        # MODERN DETECTION: Superhuman performance indicator
        # Check if performance matches IM+ level (2400+) at lower rating
        superhuman_score = self._calculate_superhuman_indicator(
            opening_accuracy, middlegame_accuracy, endgame_accuracy,
            critical_move_accuracy, engine_correlation
        )
        
        # Time pressure accuracy (if game went to endgame with low time)
        time_pressure_accuracy = endgame_accuracy  # Proxy for time pressure
        
        analysis_time = time.time() - start_time
        
        game_analysis = GameAnalysis(
            game=game,
            engine_correlation=engine_correlation,
            avg_centipawn_loss=avg_cpl,
            accuracy_score=accuracy,
            suspicious_moves=suspicious_moves[:10],  # Limit to 10
            time_controls=time_controls,
            analysis_time=analysis_time,
            metadata=metadata,
            opening_accuracy=opening_accuracy,
            middlegame_accuracy=middlegame_accuracy,
            endgame_accuracy=endgame_accuracy,
            blunder_count=blunder_count,
            critical_move_accuracy=critical_move_accuracy,
            time_pressure_accuracy=time_pressure_accuracy,
            move_time_consistency=move_time_consistency,
            probability_correlation=probability_correlation,
            win_loss_rate=win_rate,
            draw_rate=draw_rate,
            loss_rate=loss_rate,
            superhuman_score=superhuman_score
        )
        
        return game_analysis
    
    def _calculate_phase_accuracy(self, positions: List[Dict]) -> float:
        """Calculate accuracy for a specific game phase."""
        if not positions:
            return 0.0
        
        phase_cpl_values = []
        for pos in positions:
            score_cp = pos.get('score_cp')
            if score_cp is not None:
                phase_cpl_values.append(abs(score_cp))
        
        if not phase_cpl_values:
            return 0.0
        
        avg_phase_cpl = statistics.mean(phase_cpl_values)
        accuracy = 100 - min(avg_phase_cpl / 2, 100) if avg_phase_cpl < 200 else 50.0
        return max(0.0, min(100.0, accuracy))
    
    def _extract_game_metadata(self, game: chess.pgn.Game) -> Dict[str, Any]:
        """Extract metadata from game headers."""
        metadata = {}
        
        # Standard headers
        standard_headers = ['White', 'Black', 'Result', 'Date', 'Event', 'Site', 'Round']
        for header in standard_headers:
            if header in game.headers:
                metadata[header.lower()] = game.headers[header]
        
        # Chess.com specific headers
        chess_com_headers = ['time_control', 'time_class', 'rated', 'end_time']
        for header in chess_com_headers:
            if header in game.headers:
                metadata[header] = game.headers[header]
        
        # Calculate game length
        board = game.board()
        move_count = sum(1 for _ in game.mainline_moves())
        metadata['move_count'] = move_count
        
        return metadata
    
    def _aggregate_analyses(self, game_analyses: List[GameAnalysis]) -> PlayerAnalysis:
        """Aggregate multiple game analyses into player analysis - ENHANCED DETECTIVE."""
        if not game_analyses:
            raise ValueError("No game analyses to aggregate")
        
        # Get username from first game
        first_game = game_analyses[0].game
        username = first_game.headers.get('White', '').split()[0] or 'Unknown'
        
        # Extract statistics
        engine_correlations = [ga.engine_correlation for ga in game_analyses]
        cpl_values = [ga.avg_centipawn_loss for ga in game_analyses]
        accuracy_scores = [ga.accuracy_score for ga in game_analyses]
        opening_accuracies = [ga.opening_accuracy for ga in game_analyses]
        endgame_accuracies = [ga.endgame_accuracy for ga in game_analyses]
        critical_accuracies = [ga.critical_move_accuracy for ga in game_analyses]
        blunder_counts = [ga.blunder_count for ga in game_analyses]
        
        # Calculate averages
        avg_engine_correlation = statistics.mean(engine_correlations) if engine_correlations else 0
        avg_centipawn_loss = statistics.mean(cpl_values) if cpl_values else 999
        accuracy_consistency = statistics.stdev(accuracy_scores) if len(accuracy_scores) > 1 else 0
        
        # Count suspicious games
        suspicious_game_count = sum(1 for ga in game_analyses if ga.is_suspicious)
        extremely_accurate_games = sum(1 for ec in engine_correlations if ec > 97.0)
        
        # Analyze by time control
        performance_by_tc = self._analyze_performance_by_time_control(game_analyses)
        
        # ENHANCED: Calculate detective metrics
        avg_opening_accuracy = statistics.mean(opening_accuracies) if opening_accuracies else 0
        avg_endgame_accuracy = statistics.mean(endgame_accuracies) if endgame_accuracies else 0
        avg_critical_accuracy = statistics.mean(critical_accuracies) if critical_accuracies else 0
        total_blunders = sum(blunder_counts)
        expected_blunders = len(game_analyses) * 2  # Rough estimate
        blunder_avoidance = max(0, 100 - (total_blunders / max(expected_blunders, 1) * 100))
        
        # Opening preparation score (perfect openings are suspicious)
        opening_prep_score = self._analyze_opening_preparation(game_analyses)
        
        # Endgame mastery (if much better than middlegame, suspicious)
        endgame_vs_middle = avg_endgame_accuracy - statistics.mean([ga.middlegame_accuracy for ga in game_analyses]) if game_analyses else 0
        endgame_mastery = max(0, min(endgame_vs_middle * 10, 100))  # Scale the difference
        
        # NEW: Rating progression analysis
        rating_jumps = self._analyze_rating_progression(game_analyses)
        rating_jump_suspicion = min(100, len(rating_jumps) * 20) if rating_jumps else 0.0
        
        # NEW: Win rate analysis
        win_rate_analysis = self._calculate_win_rate_analysis(game_analyses)
        win_rate_anomaly = win_rate_analysis.get('anomaly_score', 0.0)
        
        # MODERN DETECTION: Calculate move time consistency
        move_times_all = []
        for ga in game_analyses:
            if 'move_times' in ga.metadata:
                move_times_all.extend(ga.metadata.get('move_times', []))
        avg_move_time_consistency = self._calculate_move_time_consistency(move_times_all) if move_times_all else 0.0
        
        # MODERN DETECTION: Average probability correlation
        prob_correlations = [ga.probability_correlation for ga in game_analyses]
        avg_probability_correlation = statistics.mean(prob_correlations) if prob_correlations else 0.0
        
        # MODERN DETECTION: Win/Draw/Loss rates
        wins = sum(1 for ga in game_analyses if ga.win_loss_rate == 1.0)
        draws = sum(1 for ga in game_analyses if ga.draw_rate == 1.0)
        losses = sum(1 for ga in game_analyses if ga.loss_rate == 1.0)
        total = len(game_analyses)
        
        avg_win_rate = (wins / total * 100) if total > 0 else 0.0
        avg_draw_rate = (draws / total * 100) if total > 0 else 0.0
        avg_loss_rate = (losses / total * 100) if total > 0 else 0.0
        
        # MODERN DETECTION: Average superhuman score
        superhuman_scores = [ga.superhuman_score for ga in game_analyses]
        avg_superhuman_score = statistics.mean(superhuman_scores) if superhuman_scores else 0.0
        
        # MODERN DETECTION: Time scramble accuracy
        time_scramble_accuracies = [ga.time_pressure_accuracy for ga in game_analyses]
        avg_time_scramble_accuracy = statistics.mean(time_scramble_accuracies) if time_scramble_accuracies else 0.0
        
        # Move time suspicion (placeholder, uses tqdm pattern)
        move_time_suspicion = 0.0  # Enhanced in reporter if available
        
        player_analysis = PlayerAnalysis(
            username=username,
            games_analyzed=len(game_analyses),
            total_games_fetched=len(game_analyses),  # Will be updated by caller
            game_analyses=game_analyses,
            avg_engine_correlation=avg_engine_correlation,
            avg_centipawn_loss=avg_centipawn_loss,
            accuracy_consistency=accuracy_consistency,
            suspicious_game_count=suspicious_game_count,
            extremely_accurate_games=extremely_accurate_games,
            performance_by_tc=performance_by_tc,
            opening_preparation_score=opening_prep_score,
            endgame_mastery_score=endgame_mastery,
            critical_position_handling=avg_critical_accuracy,
            blunder_avoidance_score=blunder_avoidance,
            move_time_suspicion=move_time_suspicion,
            win_rate_anomaly=win_rate_anomaly,
            rating_jump_detection=rating_jumps,
            avg_move_time_consistency=avg_move_time_consistency,
            avg_probability_correlation=avg_probability_correlation,
            avg_win_rate=avg_win_rate,
            avg_draw_rate=avg_draw_rate,
            avg_loss_rate=avg_loss_rate,
            avg_superhuman_score=avg_superhuman_score,
            avg_time_scramble_accuracy=avg_time_scramble_accuracy
        )
        
        # Store win rate analysis in performance_by_tc for reporter
        player_analysis.win_rate_data = win_rate_analysis
        
        return player_analysis
    
    def _analyze_performance_by_time_control(self, game_analyses: List[GameAnalysis]) -> Dict:
        """Analyze performance differences across time controls."""
        tc_groups = {}
        
        for ga in game_analyses:
            tc = ga.time_controls.get('time_class', 'unknown')
            
            if tc not in tc_groups:
                tc_groups[tc] = {
                    'games': 0,
                    'engine_correlations': [],
                    'cpl_values': [],
                }
            
            tc_groups[tc]['games'] += 1
            tc_groups[tc]['engine_correlations'].append(ga.engine_correlation)
            tc_groups[tc]['cpl_values'].append(ga.avg_centipawn_loss)
        
        # Calculate statistics for each time control
        results = {}
        for tc, data in tc_groups.items():
            if data['games'] > 0:
                results[tc] = {
                    'game_count': data['games'],
                    'avg_engine_correlation': statistics.mean(data['engine_correlations']) if data['engine_correlations'] else 0,
                    'avg_cpl': statistics.mean(data['cpl_values']) if data['cpl_values'] else 999,
                }
        
        return results
    
    def generate_detailed_report(self, player_analysis: PlayerAnalysis) -> Dict[str, Any]:
        """Generate detailed report dictionary."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'username': player_analysis.username,
            'summary': {
                'total_games_fetched': player_analysis.total_games_fetched,
                'games_analyzed': player_analysis.games_analyzed,
                'suspicion_score': player_analysis.suspicion_score,
                'risk_level': player_analysis.risk_level,
                'avg_engine_correlation': player_analysis.avg_engine_correlation,
                'avg_centipawn_loss': player_analysis.avg_centipawn_loss,
                'accuracy_consistency': player_analysis.accuracy_consistency,
                'suspicious_games': player_analysis.suspicious_game_count,
                'extremely_accurate_games': player_analysis.extremely_accurate_games
            },
            'thresholds': self.thresholds,
            'performance_by_time_control': player_analysis.performance_by_tc,
            'game_details': [],
            'suspicious_patterns': self._detect_suspicious_patterns(player_analysis),
            'recommendations': self._generate_recommendations(player_analysis)
        }
        
        # Add individual game details (limit to 20 games)
        for i, ga in enumerate(player_analysis.game_analyses[:20]):
            report['game_details'].append({
                'game_number': i + 1,
                'players': f"{ga.metadata.get('white', '?')} vs {ga.metadata.get('black', '?')}",
                'result': ga.metadata.get('result', '?'),
                'engine_correlation': ga.engine_correlation,
                'avg_cpl': ga.avg_centipawn_loss,
                'accuracy': ga.accuracy_score,
                'time_control': ga.time_controls.get('time_class', 'unknown'),
                'is_suspicious': ga.is_suspicious,
                'suspicious_moves_count': len(ga.suspicious_moves)
            })
        
        return report
    
    def _detect_suspicious_patterns(self, player_analysis: PlayerAnalysis) -> List[Dict]:
        """Detect suspicious patterns across games."""
        patterns = []
        
        if player_analysis.games_analyzed >= 10:
            # Pattern 1: Sudden improvement
            games = player_analysis.game_analyses
            if len(games) >= 10:
                first_half = games[:5]
                last_half = games[-5:]
                
                if first_half and last_half:
                    first_avg = statistics.mean([ga.engine_correlation for ga in first_half])
                    last_avg = statistics.mean([ga.engine_correlation for ga in last_half])
                    
                    if last_avg - first_avg > 20:
                        patterns.append({
                            'pattern': 'sudden_improvement',
                            'description': f'Engine correlation improved from {first_avg:.1f}% to {last_avg:.1f}%',
                            'severity': 'high'
                        })
        
        # Pattern 2: Too many perfect games
        perfect_threshold = self.thresholds.get('engine_correlation_red_flag', 95)
        perfect_games = sum(1 for ga in player_analysis.game_analyses 
                          if ga.engine_correlation > perfect_threshold)
        
        if perfect_games > player_analysis.games_analyzed * 0.3:
            patterns.append({
                'pattern': 'excessive_perfect_games',
                'description': f'{perfect_games}/{player_analysis.games_analyzed} games >{perfect_threshold}% engine correlation',
                'severity': 'high'
            })
        
        return patterns
    
    def _generate_recommendations(self, player_analysis: PlayerAnalysis) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        score = player_analysis.suspicion_score
        
        if player_analysis.games_analyzed == 0:
            recommendations.append("⚠️ No games could be analyzed.")
            return recommendations
        
        if score >= 70:
            recommendations.append("⚠️ HIGH RISK: Player shows multiple strong indicators of potential assistance.")
            recommendations.append("Recommend detailed manual review of games with >95% engine correlation.")
        elif score >= 40:
            recommendations.append("⚠️ MODERATE RISK: Some suspicious patterns detected.")
            recommendations.append("Review games with highest engine correlation individually.")
        else:
            recommendations.append("✅ LOW RISK: No strong indicators detected.")
        
        # Specific recommendations
        if player_analysis.avg_centipawn_loss < 15:
            recommendations.append(f"Note: Very low average CPL ({player_analysis.avg_centipawn_loss:.1f})")
        
        if player_analysis.extremely_accurate_games > 0:
            recommendations.append(f"Found {player_analysis.extremely_accurate_games} games with >97% engine correlation.")
        
        if player_analysis.critical_position_handling > 95:
            recommendations.append(f"Critical position handling: {player_analysis.critical_position_handling:.1f}% (suspiciously high)")
        
        if player_analysis.opening_preparation_score > 90:
            recommendations.append(f"Opening preparation appears unusually strong: {player_analysis.opening_preparation_score:.1f}%")
        
        return recommendations
    
    def _analyze_opening_preparation(self, game_analyses: List[GameAnalysis]) -> float:
        """Detect suspicious opening preparation depth."""
        if not game_analyses:
            return 0.0
        
        opening_scores = []
        for ga in game_analyses:
            # If opening accuracy is near perfect (>95%), it's suspicious
            if ga.opening_accuracy > 95:
                opening_scores.append(100)
            elif ga.opening_accuracy > 85:
                opening_scores.append(ga.opening_accuracy)
            else:
                opening_scores.append(0)
        
        if opening_scores:
            avg_prep = statistics.mean(opening_scores)
            # Scale to 0-100
            return min(100, avg_prep)
        return 0.0
    
    def _analyze_rating_progression(self, game_analyses: List[GameAnalysis]) -> List[float]:
        """Detect suspicious rating jumps from game wins/losses."""
        if len(game_analyses) < 2:
            return []
        
        rating_jumps = []
        estimated_rating = 1600  # Starting point
        
        for ga in game_analyses:
            # Extract result
            result = ga.metadata.get('result', '?')
            
            if result == '1-0':
                # Win: +/-32 Elo points (standard)
                estimated_rating += 32
            elif result == '0-1':
                # Loss: -32 Elo points
                estimated_rating -= 32
            elif result == '1/2-1/2':
                # Draw: 0
                pass
            
            rating_jumps.append(estimated_rating)
        
        # Detect anomalies (sudden jumps)
        anomalies = []
        for i in range(1, len(rating_jumps)):
            jump = abs(rating_jumps[i] - rating_jumps[i-1])
            if jump > 50:  # Large jump
                anomalies.append(jump)
        
        return anomalies
    
    def _calculate_win_rate_analysis(self, game_analyses: List[GameAnalysis]) -> Dict[str, float]:
        """Calculate win rate and compare to expected based on ratings."""
        if not game_analyses:
            return {
                'win_rate': 0.0,
                'expected_win_rate': 0.0,
                'anomaly_score': 0.0
            }
        
        wins = 0
        losses = 0
        draws = 0
        opponent_ratings = []
        player_ratings = []
        
        for ga in game_analyses:
            result = ga.metadata.get('result', '?')
            
            # Get ratings from game headers
            white_rating = int(ga.game.headers.get('WhiteElo', 1600))
            black_rating = int(ga.game.headers.get('BlackElo', 1600))
            
            # Assume player is white for simplicity (could be either)
            player_ratings.append(white_rating)
            opponent_ratings.append(black_rating)
            
            if result == '1-0':
                wins += 1
            elif result == '0-1':
                losses += 1
            elif result == '1/2-1/2':
                draws += 1
        
        total_games = wins + losses + draws
        if total_games == 0:
            return {
                'win_rate': 0.0,
                'expected_win_rate': 0.0,
                'anomaly_score': 0.0
            }
        
        # Calculate actual win rate
        actual_win_rate = (wins + draws * 0.5) / total_games * 100
        
        # Calculate expected win rate (based on Elo)
        avg_opponent_rating = statistics.mean(opponent_ratings) if opponent_ratings else 1600
        avg_player_rating = statistics.mean(player_ratings) if player_ratings else 1600
        rating_diff = avg_player_rating - avg_opponent_rating
        
        # Elo formula: expected_score = 1 / (1 + 10^(-rating_diff/400))
        expected_win_rate = 1 / (1 + 10 ** (-rating_diff / 400)) * 100
        
        # Calculate anomaly (how much better than expected)
        anomaly_score = max(0, actual_win_rate - expected_win_rate)
        
        return {
            'win_rate': actual_win_rate,
            'expected_win_rate': expected_win_rate,
            'anomaly_score': anomaly_score,
            'avg_opponent_rating': avg_opponent_rating,
            'avg_player_rating': avg_player_rating
        }
    
    def _calculate_move_time_consistency(self, move_times: List[float]) -> float:
        """
        MODERN DETECTION: Calculate how consistent move times are.
        High consistency (70-90% of moves taking similar time) is suspicious.
        Engines think consistently, humans vary.
        
        Returns: Score 0-100, higher = more engine-like
        """
        if len(move_times) < 5:
            return 0.0
        
        # Group move times by 0.2 second buckets
        time_groups = {}
        for t in move_times:
            bucket = round(t / 0.2) * 0.2
            time_groups[bucket] = time_groups.get(bucket, 0) + 1
        
        # Find most common time bucket
        max_group = max(time_groups.values()) if time_groups else 0
        consistency = (max_group / len(move_times)) * 100
        
        # High consistency is suspicious (>70%)
        # But not impossibly so (allow up to 90%)
        suspicious_consistency = max(0, consistency - 40) if consistency > 40 else 0
        
        return min(100, suspicious_consistency)
    
    def _calculate_probability_correlation(
        self, engine_correlation: float, positions: List[Dict], 
        critical_moves: List[Dict]
    ) -> float:
        """
        MODERN DETECTION: Calculate probability correlation.
        This estimates the likelihood that a player found best moves
        by chance vs. engine use. Modern cheating detectors use Bayesian
        probability analysis.
        
        Returns: Score 0-100, higher = more likely to be engine-assisted
        """
        if not positions:
            return 0.0
        
        # Base probability of finding best move
        # At critical positions, this becomes exponentially less likely
        base_probability = engine_correlation / 100.0
        
        # If player found too many best moves in critical positions
        critical_accuracy = (len(critical_moves) / max(len(positions), 1)) * 100 if critical_moves else 0
        
        # Probability calculation: 
        # Very high accuracy at critical positions is exponentially suspicious
        prob_score = 0.0
        
        if engine_correlation > 90:
            # At 90%+ correlation, probability of achieving by chance
            # becomes astronomically low
            prob_score = min(100, (engine_correlation - 90) * 5)  # Extra weighting
        
        if critical_accuracy > 95 and len(critical_moves) > 3:
            # Finding best moves in complex positions consistently
            prob_score += 20
        
        return min(100, prob_score)
    
    def _calculate_superhuman_indicator(
        self, opening_acc: float, middlegame_acc: float, 
        endgame_acc: float, critical_acc: float, engine_corr: float
    ) -> float:
        """
        MODERN DETECTION: Detect IM+ (2400+) level play at lower ratings.
        
        Superhuman indicators:
        - 95%+ accuracy in middlegame
        - 90%+ accuracy in all phases
        - 95%+ critical position accuracy
        - 90%+ engine correlation
        
        Returns: Score 0-100, higher = more superhuman
        """
        score = 0.0
        
        # IM level play is 95%+ accuracy consistently
        if middlegame_acc > 95:
            score += 30
        elif middlegame_acc > 90:
            score += 15
        
        if critical_acc > 95:
            score += 25
        elif critical_acc > 90:
            score += 12
        
        if endgame_acc > 95:
            score += 20
        elif endgame_acc > 90:
            score += 10
        
        if opening_acc > 95:
            score += 15
        
        # High engine correlation is another indicator
        if engine_corr > 92:
            score += 15
        
        return min(100, score)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.engine_manager.cleanup()
        logger.info("Analyzer cleaned up")