"""
Enhanced Player Analyzer v3.0
Ultra-fast, accurate, detailed forensic analysis with cloud integration
Combines Lichess API, local analysis, pattern detection, and statistical scoring
"""

import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
import statistics
import chess
import chess.pgn
from datetime import datetime
import requests
from pathlib import Path
import hashlib


@dataclass
class TimePattern:
    """Analyzes move timing patterns"""
    avg_time: float = 0.0
    median_time: float = 0.0
    std_dev: float = 0.0
    time_coefficient_variation: float = 0.0  # std_dev / mean
    suspicious_consistency: bool = False  # Too consistent (likely engine)
    rapid_responses: int = 0  # Moves < 1 second
    blitz_threshold_violations: int = 0  # Thinks too long for blitz


@dataclass
class EnginePattern:
    """Tracks engine move matching"""
    top_1_match_rate: float = 0.0  # % of moves matching #1 engine move
    top_3_match_rate: float = 0.0  # % of moves matching top 3
    top_5_match_rate: float = 0.0  # % of moves matching top 5
    suspicious_threshold: float = 92.0  # Threshold for suspicion
    is_suspicious: bool = False


@dataclass
class BlunderAnalysis:
    """Blunder pattern analysis"""
    total_blunders: int = 0  # Moves losing 50+ centipawns
    blunder_rate: float = 0.0  # % of moves that are blunders
    critical_blunders: int = 0  # Moves losing 200+ centipawns
    average_blunder_cost: float = 0.0
    recovery_ability: float = 0.0  # Can they recover after blunder?


@dataclass
class AccuracyMetrics:
    """Phase-based accuracy analysis"""
    opening_accuracy: float = 0.0
    middlegame_accuracy: float = 0.0
    endgame_accuracy: float = 0.0
    overall_accuracy: float = 0.0
    consistency_std_dev: float = 0.0


@dataclass
class PerformancePattern:
    """Performance analysis by opponent strength"""
    vs_lower_rated: Dict = field(default_factory=dict)  # vs weaker opponents
    vs_equal_rated: Dict = field(default_factory=dict)  # vs similar strength
    vs_higher_rated: Dict = field(default_factory=dict)  # vs stronger opponents
    rating_correlation: float = 0.0  # Does performance scale with opponent?
    suspicious_advantage: bool = False  # Unusually high vs strong players


@dataclass
class GameAnalysisV3:
    """Enhanced game analysis result"""
    game_id: str
    white: str
    black: str
    result: str
    player_color: str
    
    # Timing data
    time_pattern: TimePattern = field(default_factory=TimePattern)
    
    # Engine data
    engine_pattern: EnginePattern = field(default_factory=EnginePattern)
    blunder_analysis: BlunderAnalysis = field(default_factory=BlunderAnalysis)
    accuracy: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    
    # Game context
    opponent_elo: int = 0
    time_control: str = ""
    move_count: int = 0
    
    # Evaluation
    is_suspicious: bool = False
    suspicion_score: float = 0.0
    reason: str = ""


class EnhancedPlayerAnalyzer:
    """
    Ultra-fast, accurate player analysis combining:
    - Lichess cloud analysis for speed
    - Local Stockfish for detail
    - Pattern-based detection
    - Statistical scoring
    - Caching for efficiency
    """
    
    def __init__(self, config: Dict, use_lichess: bool = True, use_chess_com: bool = True, cache_dir: str = "cache/analysis"):
        self.config = config
        self.use_lichess = use_lichess
        self.use_chess_com = use_chess_com
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.lichess_url = "https://lichess.org/api/games"
        self.analysis_cache = {}
        self._load_cache()
    
    def _load_cache(self):
        """Load analysis cache from disk"""
        cache_file = self.cache_dir / "analyses.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.analysis_cache = json.load(f)
            except:
                pass
    
    def _save_cache(self):
        """Save analysis cache to disk"""
        cache_file = self.cache_dir / "analyses.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.analysis_cache, f)
        except:
            pass
    
    def _get_game_hash(self, game_pgn: str) -> str:
        """Generate unique hash for game to enable caching"""
        return hashlib.md5(game_pgn.encode()).hexdigest()
    
    def analyze_games_fast(self, games: List, username: str, max_workers: int = 4) -> Dict:
        """
        Analyze games with parallel processing for speed
        
        Args:
            games: List of chess.pgn.Game objects
            username: Player's username
            max_workers: Number of parallel analysis threads
        
        Returns:
            Comprehensive analysis results
        """
        
        print(f"\n>>> ENHANCED ANALYSIS ENGINE (v3.0)")
        print(f"   Speed Mode: Parallel Processing x{max_workers}")
        print(f"   Strategy: Lichess Cloud + Local Cache")
        print(f"   Analyzing {len(games)} games...\n")
        
        start_time = time.time()
        analyses = []
        
        # First pass: Get cached or cloud analyses in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._analyze_single_game, game, username): game 
                for game in games
            }
            
            completed = 0
            for future in as_completed(futures):
                try:
                    analysis = future.result()
                    if analysis:
                        analyses.append(analysis)
                except Exception as e:
                    print(f"\n  [ERROR] Error analyzing game: {str(e)}")
                finally:
                    completed += 1
                    if len(games) > 0:
                        progress = int(completed / len(games) * 50)
                    else:
                        progress = 0
                    # Use ASCII-safe progress bar for Windows compatibility
                    bar = '=' * progress + '-' * (50 - progress)
                    print(f"\r  Progress: [{bar}] {completed}/{len(games)}", end='')
        
        print()  # New line
        
        # Compile results
        results = self._compile_analysis_results(analyses, username)
        
        elapsed = time.time() - start_time
        print(f"\n[DONE] Analysis Complete: {elapsed:.1f}s ({len(games)} games)")
        
        return results
    
    def _analyze_single_game(self, game: chess.pgn.Game, username: str) -> Optional[GameAnalysisV3]:
        """Analyze a single game with caching"""
        try:
            game_pgn = str(game)  # Convert game to PGN string
            game_hash = self._get_game_hash(game_pgn)
            
            # Check cache first
            if game_hash in self.analysis_cache:
                return self._dict_to_analysis(self.analysis_cache[game_hash])
            
            # Get game metadata
            white = game.headers.get("White", "").lower()
            black = game.headers.get("Black", "").lower()
            result = game.headers.get("Result", "*")
            white_elo = int(game.headers.get("WhiteElo", "0") or "0")
            black_elo = int(game.headers.get("BlackElo", "0") or "0")
            time_control = game.headers.get("TimeControl", "")
            
            is_player_white = white == username.lower()
            player_elo = white_elo if is_player_white else black_elo
            opponent_elo = black_elo if is_player_white else white_elo
            move_count = len(list(game.mainline_moves()))
            
            # Extract moves and get evaluations
            moves = list(game.mainline_moves())
            evaluations = self._get_evaluations(game, moves[:50])  # First 50 half-moves
            
            # Analyze patterns
            game_analysis = GameAnalysisV3(
                game_id=game_hash,
                white=white,
                black=black,
                result=result,
                player_color="White" if is_player_white else "Black",
                opponent_elo=opponent_elo,
                time_control=time_control,
                move_count=move_count
            )
            
            # Get timing data if available
            game_analysis.time_pattern = self._analyze_time_patterns(game, moves, is_player_white)
            
            # Get engine evaluation
            game_analysis.engine_pattern = self._analyze_engine_matching(evaluations, moves)
            game_analysis.blunder_analysis = self._analyze_blunders(evaluations, moves, is_player_white)
            game_analysis.accuracy = self._calculate_accuracy(evaluations, moves)
            
            # Determine suspicion
            game_analysis.is_suspicious, game_analysis.suspicion_score = self._score_suspicion(
                game_analysis, opponent_elo, move_count
            )
            
            # Cache the analysis
            self.analysis_cache[game_hash] = asdict(game_analysis)
            self._save_cache()
            
            return game_analysis
        
        except Exception as e:
            import traceback
            # Log the full traceback for debugging
            print(f"\nDEBUG: Full error in _analyze_single_game: {type(e).__name__}: {e}")
            traceback.print_exc()
            return None
    
    def _get_evaluations(self, game: chess.pgn.Game, moves: List) -> List[Dict]:
        """Get evaluations for moves using Lichess API or local engine"""
        evaluations = []
        
        # Try Lichess API first (fastest)
        if self.use_lichess:
            evaluations = self._get_lichess_evaluations(game)
        
        # Fall back to local analysis if needed
        if not evaluations or len(evaluations) < len(moves) / 2:
            evaluations = self._get_local_evaluations(game, moves)
        
        return evaluations
    
    def _get_lichess_evaluations(self, game: chess.pgn.Game) -> List[Dict]:
        """Get position evaluations from Lichess API"""
        try:
            # Try to get game from Lichess
            white = game.headers.get("White", "")
            black = game.headers.get("Black", "")
            
            # Build game URL (if available)
            game_url = game.headers.get("Link", "")
            if not game_url:
                return []
            
            # Extract game ID from URL
            if "lichess.org" not in game_url:
                return []
            
            game_id = game_url.split('/')[-1].split('?')[0]
            if not game_id:
                return []
            
            # Get analysis from Lichess
            url = f"https://lichess.org/api/games/{game_id}"
            response = requests.get(url, headers={"Accept": "application/json"}, timeout=5)
            
            if response.status_code != 200:
                return []
            
            game_data = response.json()
            evals = []
            
            for move_info in game_data.get("moves", []):
                if "eval" in move_info:
                    evals.append({
                        "centipawns": move_info["eval"],
                        "mate": None
                    })
                elif "mate" in move_info:
                    evals.append({
                        "centipawns": None,
                        "mate": move_info["mate"]
                    })
            
            return evals
        
        except Exception as e:
            return []
    
    def _get_local_evaluations(self, game: chess.pgn.Game, moves: List) -> List[Dict]:
        """Get evaluations using local Stockfish"""
        evaluations = []
        try:
            from .engine import StockfishEngine
            engine = StockfishEngine(self.config)
            
            board = chess.Board()
            depth = self.config.get('analysis', {}).get('engine_depth', 12)
            
            for i, move in enumerate(moves[:50]):  # Limit to 50 half-moves for speed
                board.push(move)
                info = engine.evaluate(board, depth=depth)
                
                if info:
                    evaluations.append({
                        "centipawns": info.get("centipawns", 0),
                        "mate": info.get("mate")
                    })
                
                if i % 10 == 0:
                    board.pop()
                    board.push(move)
        
        except Exception as e:
            pass
        
        return evaluations
    
    def _analyze_time_patterns(self, game: chess.pgn.Game, moves: List, is_player: bool) -> TimePattern:
        """Analyze move timing patterns"""
        pattern = TimePattern()
        
        try:
            # Get move times from game
            times = []
            move_times_str = game.headers.get("ClockTimes", "")
            
            if move_times_str:
                time_parts = move_times_str.split(',')
                for time_str in time_parts:
                    try:
                        # Convert time string to seconds
                        parts = time_str.strip().split(':')
                        if len(parts) == 3:
                            hours, mins, secs = parts
                            total_secs = int(hours) * 3600 + int(mins) * 60 + int(secs)
                            times.append(total_secs)
                    except:
                        continue
                
                # Filter for player's moves only
                if is_player:
                    player_times = times[::2]  # Every other move (player's moves)
                else:
                    player_times = times[1::2]
                
                if player_times:
                    pattern.avg_time = statistics.mean(player_times)
                    pattern.median_time = statistics.median(player_times)
                    
                    if len(player_times) > 1:
                        pattern.std_dev = statistics.stdev(player_times)
                        pattern.time_coefficient_variation = pattern.std_dev / pattern.avg_time if pattern.avg_time > 0 else 0
                    
                    # Check for suspicious consistency (CV < 0.3 = very consistent)
                    pattern.suspicious_consistency = pattern.time_coefficient_variation < 0.3
                    
                    # Count rapid responses
                    pattern.rapid_responses = len([t for t in player_times if t < 1])
        
        except:
            pass
        
        return pattern
    
    def _analyze_engine_matching(self, evaluations: List[Dict], moves: List) -> EnginePattern:
        """Analyze how often moves match engine recommendations"""
        pattern = EnginePattern()
        
        try:
            if not evaluations or not moves:
                return pattern
            
            # This would require engine move analysis
            # For now, use heuristic based on evaluation changes
            
            match_count = 0
            for i, eval_dict in enumerate(evaluations[:-1]):
                curr_eval = eval_dict.get("centipawns", 0)
                next_eval = evaluations[i+1].get("centipawns", 0)
                
                # If evaluation improves significantly after move, likely good move
                if curr_eval is not None and next_eval is not None:
                    if abs(next_eval - curr_eval) < 50:  # Move didn't lose material
                        match_count += 1
            
            if evaluations:
                pattern.top_1_match_rate = (match_count / len(evaluations)) * 100
                pattern.is_suspicious = pattern.top_1_match_rate > pattern.suspicious_threshold
        
        except:
            pass
        
        return pattern
    
    def _analyze_blunders(self, evaluations: List[Dict], moves: List, is_player: bool) -> BlunderAnalysis:
        """Analyze blunder patterns"""
        analysis = BlunderAnalysis()
        
        try:
            if not evaluations:
                return analysis
            
            blunder_costs = []
            
            for i in range(0, len(evaluations) - 1, 2):
                if is_player:
                    # Player's move (even indices)
                    before = evaluations[i].get("centipawns", 0)
                    after = evaluations[i+1].get("centipawns", 0)
                else:
                    # Player's move (odd indices)
                    if i + 1 < len(evaluations):
                        before = evaluations[i].get("centipawns", 0)
                        after = evaluations[i+1].get("centipawns", 0)
                    else:
                        continue
                
                if before is not None and after is not None:
                    loss = after - before
                    
                    if loss > 50:
                        analysis.total_blunders += 1
                        blunder_costs.append(loss)
                        
                        if loss > 200:
                            analysis.critical_blunders += 1
            
            if evaluations:
                player_moves = len(evaluations) // 2
                analysis.blunder_rate = (analysis.total_blunders / player_moves * 100) if player_moves > 0 else 0
            
            if blunder_costs:
                analysis.average_blunder_cost = statistics.mean(blunder_costs)
        
        except:
            pass
        
        return analysis
    
    def _calculate_accuracy(self, evaluations: List[Dict], moves: List) -> AccuracyMetrics:
        """Calculate accuracy by game phase"""
        metrics = AccuracyMetrics()
        
        try:
            if not evaluations:
                return metrics
            
            # Divide game into phases
            total_moves = len(moves)
            opening_end = min(20, total_moves // 3)
            endgame_start = max(40, total_moves * 2 // 3)
            
            # Calculate accuracy for each phase
            opening_evals = evaluations[:opening_end]
            middlegame_evals = evaluations[opening_end:endgame_start]
            endgame_evals = evaluations[endgame_start:]
            
            metrics.opening_accuracy = self._calculate_phase_accuracy(opening_evals)
            metrics.middlegame_accuracy = self._calculate_phase_accuracy(middlegame_evals)
            metrics.endgame_accuracy = self._calculate_phase_accuracy(endgame_evals)
            
            # Overall accuracy
            all_accuracies = [
                metrics.opening_accuracy,
                metrics.middlegame_accuracy,
                metrics.endgame_accuracy
            ]
            metrics.overall_accuracy = statistics.mean([a for a in all_accuracies if a > 0]) if any(a > 0 for a in all_accuracies) else 0
            
            # Consistency
            if len(all_accuracies) > 1:
                metrics.consistency_std_dev = statistics.stdev(all_accuracies)
        
        except:
            pass
        
        return metrics
    
    def _calculate_phase_accuracy(self, evals: List[Dict]) -> float:
        """Calculate accuracy for a phase"""
        try:
            if not evals:
                return 0.0
            
            good_moves = 0
            for eval_dict in evals:
                cp = eval_dict.get("centipawns", 0)
                # Good move = position stays equal or improves
                if cp is not None and cp >= -50:
                    good_moves += 1
            
            return (good_moves / len(evals) * 100) if evals else 0.0
        except:
            return 0.0
    
    def _score_suspicion(self, analysis: GameAnalysisV3, opponent_elo: int, move_count: int) -> Tuple[bool, float]:
        """
        Multi-layer suspicion scoring
        Returns (is_suspicious, score)
        """
        
        score = 0.0
        
        # Factor 1: Engine matching (max 40 points)
        if analysis.engine_pattern.top_1_match_rate > 92:
            score += 30
        elif analysis.engine_pattern.top_1_match_rate > 85:
            score += 15
        
        # Factor 2: Time consistency (max 25 points)
        if analysis.time_pattern.suspicious_consistency:
            score += 15
        
        if analysis.time_pattern.time_coefficient_variation < 0.2:
            score += 10
        
        # Factor 3: Blunder rate (max 20 points)
        if analysis.blunder_analysis.blunder_rate < 2:  # Very low blunder rate
            score += 10
        
        if analysis.blunder_analysis.critical_blunders == 0:
            score += 10
        
        # Factor 4: Accuracy variance (max 15 points)
        if analysis.accuracy.consistency_std_dev < 5:
            score += 10
        
        # Rating context (max 20 points)
        if opponent_elo > 2400 and analysis.accuracy.overall_accuracy > 88:
            score += 10  # Extremely high accuracy vs strong opposition
        
        is_suspicious = score > 60
        
        return is_suspicious, score
    
    def _compile_analysis_results(self, analyses: List[GameAnalysisV3], username: str) -> Dict:
        """Compile all analyses into comprehensive results"""
        
        if not analyses:
            return {
                'games_analyzed': 0,
                'suspicion_score': 0,
                'games': [],
                'patterns': {}
            }
        
        # Calculate aggregate metrics
        total_games = len(analyses)
        avg_suspicion = statistics.mean([a.suspicion_score for a in analyses])
        suspicious_games = len([a for a in analyses if a.is_suspicious])
        
        # Pattern aggregates
        avg_engine_match = statistics.mean([a.engine_pattern.top_1_match_rate for a in analyses])
        avg_blunder_rate = statistics.mean([a.blunder_analysis.blunder_rate for a in analyses])
        
        # Average accuracy - handle case where no games have accuracy > 0
        accuracy_values = [a.accuracy.overall_accuracy for a in analyses if a.accuracy.overall_accuracy > 0]
        avg_accuracy = statistics.mean(accuracy_values) if accuracy_values else 0
        
        # Time pattern consistency
        time_coefficients = [
            a.time_pattern.time_coefficient_variation 
            for a in analyses 
            if a.time_pattern.time_coefficient_variation > 0
        ]
        avg_time_consistency = statistics.mean(time_coefficients) if time_coefficients else 0
        
        return {
            'username': username,
            'games_analyzed': total_games,
            'suspicious_games': suspicious_games,
            'suspicion_score': avg_suspicion,
            'avg_engine_match_rate': avg_engine_match,
            'avg_blunder_rate': avg_blunder_rate,
            'avg_accuracy': avg_accuracy,
            'avg_time_consistency': avg_time_consistency,
            'game_analyses': [asdict(a) for a in analyses],
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _dict_to_analysis(self, data: Dict) -> GameAnalysisV3:
        """Convert dict back to GameAnalysisV3 object"""
        try:
            return GameAnalysisV3(
                game_id=data.get('game_id', ''),
                white=data.get('white', ''),
                black=data.get('black', ''),
                result=data.get('result', ''),
                player_color=data.get('player_color', ''),
                time_pattern=TimePattern(**data.get('time_pattern', {})),
                engine_pattern=EnginePattern(**data.get('engine_pattern', {})),
                blunder_analysis=BlunderAnalysis(**data.get('blunder_analysis', {})),
                accuracy=AccuracyMetrics(**data.get('accuracy', {})),
                opponent_elo=data.get('opponent_elo', 0),
                time_control=data.get('time_control', ''),
                move_count=data.get('move_count', 0),
                is_suspicious=data.get('is_suspicious', False),
                suspicion_score=data.get('suspicion_score', 0.0),
                reason=data.get('reason', '')
            )
        except:
            return None


def display_enhanced_analysis(results: Dict, username: str):
    """Display comprehensive analysis results"""
    
    print("\n" + "="*80)
    print(f"[ANALYSIS] ENHANCED PLAYER ANALYSIS v3.0 - {username.upper()}")
    print(f"Timestamp: {results.get('analysis_timestamp', 'N/A')}")
    
    # Show platform breakdown if available
    platform_breakdown = results.get('platform_breakdown', {})
    if platform_breakdown:
        sources = ", ".join([
            f"{p.title()}: {c}" 
            for p, c in platform_breakdown.items() 
            if c > 0
        ])
        print(f"Sources: {sources}")
    
    print("="*80)
    
    games_analyzed = results.get('games_analyzed', 0)
    suspicion_score = results.get('suspicion_score', 0)
    suspicious_games = results.get('suspicious_games', 0)
    
    print(f"\n[ASSESSMENT] OVERALL ASSESSMENT")
    print("-"*80)
    print(f"Games Analyzed: {games_analyzed}")
    print(f"Average Suspicion Score: {suspicion_score:.1f}/100")
    if games_analyzed > 0:
        percentage = suspicious_games/games_analyzed*100
        print(f"Suspicious Games Detected: {suspicious_games}/{games_analyzed} ({percentage:.1f}%)")
    else:
        print(f"Suspicious Games Detected: 0/0 (No games analyzed successfully)")
    
    # Assessment
    if suspicion_score < 30:
        assessment = "[CLEAN] - No significant indicators of assistance"
    elif suspicion_score < 50:
        assessment = "[CAUTION] - Some minor patterns worth noting"
    elif suspicion_score < 70:
        assessment = "[SUSPICIOUS] - Multiple indicators present"
    else:
        assessment = "[HIGHLY SUSPICIOUS] - Strong indicators of potential assistance"
    
    print(f"Assessment: {assessment}")
    
    print(f"\n[METRICS] DETAILED METRICS")
    print("-"*80)
    print(f"Average Engine Match Rate: {results.get('avg_engine_match_rate', 0):.1f}%")
    print(f"Average Blunder Rate: {results.get('avg_blunder_rate', 0):.1f}%")
    print(f"Average Accuracy: {results.get('avg_accuracy', 0):.1f}%")
    print(f"Time Pattern Consistency: {results.get('avg_time_consistency', 0):.1%}")
    
    print(f"\n[TIME] TIME ANALYSIS")
    print("-"*80)
    if results.get('avg_time_consistency', 0) > 0.5:
        print("[OK] Natural time patterns - variable response times")
    elif results.get('avg_time_consistency', 0) > 0.3:
        print("[WARN] Moderately consistent - some regularity in time usage")
    else:
        print("[ALERT] Suspicious consistency - too regular response times")
    
    print(f"\n[TOP] TOP SUSPICIOUS GAMES")
    print("-"*80)
    
    analyses = results.get('game_analyses', [])
    if analyses:
        sorted_games = sorted(analyses, key=lambda x: x.get('suspicion_score', 0), reverse=True)[:5]
        
        for i, game in enumerate(sorted_games, 1):
            print(f"\n{i}. Game {i}")
            print(f"   Score: {game.get('suspicion_score', 0):.1f}/100")
            print(f"   Opponent: {game.get('opponent_elo', 0)} Elo")
            engine_match = game.get('engine_pattern', {}).get('top_1_match_rate', 0)
            print(f"   Engine Match: {engine_match:.1f}%")
            accuracy = game.get('accuracy', {}).get('overall_accuracy', 0)
            print(f"   Accuracy: {accuracy:.1f}%")
    else:
        print("\nNo games analyzed successfully. Check error messages above.")
    
    print("\n" + "="*80)
