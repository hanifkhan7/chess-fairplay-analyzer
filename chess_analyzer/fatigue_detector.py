"""
Fatigue Detection & Endurance Analysis.

Detects performance degradation patterns:
- Within-game fatigue (declining performance across moves)
- Session fatigue (declining over multiple games)
- Time-of-day effects
- Consistency analysis
"""

import statistics
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class FatigueMetric:
    """Single fatigue indicator."""
    metric_type: str  # 'within_game', 'session', 'daily', 'time_pressure'
    severity: float  # 0-100, higher = more fatigue
    confidence: float  # 0-1.0
    evidence: str  # Description of findings
    affected_games: int
    recommended_action: str

@dataclass
class FatigueAnalysis:
    """Comprehensive fatigue assessment."""
    username: str
    games_analyzed: int
    
    # Within-game fatigue
    within_game_fatigue_detected: bool
    within_game_severity: float  # 0-100
    early_game_accuracy: float
    late_game_accuracy: float
    accuracy_decline: float
    
    # Session fatigue
    session_fatigue_detected: bool
    session_severity: float  # 0-100
    first_game_accuracy: float
    last_game_accuracy: float
    session_decline: float
    
    # Time-of-day patterns
    time_distribution: Dict[str, float] = None  # hour -> avg_accuracy
    time_of_day_effect: bool = False
    best_playing_time: str = ""
    worst_playing_time: str = ""
    
    # Consistency
    overall_consistency: float  # 0-100, higher = more consistent
    game_to_game_variance: float
    
    # Indicators
    overwork_likely: bool = False  # Too many games without rest
    systematic_decline: bool = False
    recovery_pattern: bool = False  # Performance recovers after rest
    
    fatigue_metrics: List[FatigueMetric] = None
    
    def __post_init__(self):
        if self.time_distribution is None:
            self.time_distribution = {}
        if self.fatigue_metrics is None:
            self.fatigue_metrics = []

class FatigueDetector:
    """Analyze fatigue patterns in player performance."""
    
    @staticmethod
    def analyze_fatigue(games: List[Dict[str, Any]], 
                       username: str,
                       time_control: str = '') -> FatigueAnalysis:
        """
        Analyze fatigue patterns across games.
        
        Args:
            games: List of game dicts with 'accuracy', 'cpl', 'timestamp', 'moves'
            username: Player username
            time_control: Time control for context (e.g., 'blitz', 'rapid')
            
        Returns:
            FatigueAnalysis with detailed fatigue assessment
        """
        
        if not games:
            return FatigueAnalysis(
                username=username,
                games_analyzed=0,
                within_game_fatigue_detected=False,
                within_game_severity=0,
                early_game_accuracy=0,
                late_game_accuracy=0,
                accuracy_decline=0,
                session_fatigue_detected=False,
                session_severity=0,
                first_game_accuracy=0,
                last_game_accuracy=0,
                session_decline=0,
                overall_consistency=50
            )
        
        # Within-game fatigue analysis
        within_game = FatigueDetector._detect_within_game_fatigue(games)
        
        # Session fatigue analysis
        session = FatigueDetector._detect_session_fatigue(games)
        
        # Time-of-day analysis
        time_data = FatigueDetector._analyze_time_of_day(games)
        
        # Overall consistency
        accuracies = [g.get('accuracy', 50) for g in games if 'accuracy' in g]
        if len(accuracies) > 1:
            try:
                stdev = statistics.stdev(accuracies)
                consistency = max(0, 100 - stdev * 2)  # Inverse of variance
                game_variance = stdev
            except statistics.StatisticsError:
                consistency = 50
                game_variance = 0
        else:
            consistency = 50
            game_variance = 0
        
        # Detect overwork
        overwork = FatigueDetector._detect_overwork(games)
        
        # Build metrics list
        metrics = []
        if within_game['detected']:
            metrics.append(FatigueMetric(
                metric_type='within_game',
                severity=within_game['severity'],
                confidence=0.75,
                evidence=f"Accuracy drops {within_game['decline']:.1f}% within games",
                affected_games=within_game['affected_games'],
                recommended_action="Consider 10-minute breaks between moves"
            ))
        
        if session['detected']:
            metrics.append(FatigueMetric(
                metric_type='session',
                severity=session['severity'],
                confidence=0.70,
                evidence=f"Accuracy drops {session['decline']:.1f}% across session",
                affected_games=session['affected_games'],
                recommended_action="Limit session to 5-10 games; take substantial breaks"
            ))
        
        if time_data['effect_detected']:
            metrics.append(FatigueMetric(
                metric_type='time_of_day',
                severity=time_data['severity'],
                confidence=0.60,
                evidence=f"Best at {time_data['best_time']}, Worst at {time_data['worst_time']}",
                affected_games=len([g for g in games if 'timestamp' in g]),
                recommended_action=f"Schedule important games during {time_data['best_time']}"
            ))
        
        if overwork['detected']:
            metrics.append(FatigueMetric(
                metric_type='overwork',
                severity=overwork['severity'],
                confidence=0.65,
                evidence=overwork['evidence'],
                affected_games=overwork['affected_games'],
                recommended_action="Increase rest between sessions"
            ))
        
        analysis = FatigueAnalysis(
            username=username,
            games_analyzed=len(games),
            within_game_fatigue_detected=within_game['detected'],
            within_game_severity=within_game['severity'],
            early_game_accuracy=within_game['early_accuracy'],
            late_game_accuracy=within_game['late_accuracy'],
            accuracy_decline=within_game['decline'],
            session_fatigue_detected=session['detected'],
            session_severity=session['severity'],
            first_game_accuracy=session['first_accuracy'],
            last_game_accuracy=session['last_accuracy'],
            session_decline=session['decline'],
            time_distribution=time_data['hourly_accuracy'],
            time_of_day_effect=time_data['effect_detected'],
            best_playing_time=time_data['best_time'],
            worst_playing_time=time_data['worst_time'],
            overall_consistency=consistency,
            game_to_game_variance=game_variance,
            overwork_likely=overwork['detected'],
            systematic_decline=within_game['detected'] or session['detected'],
            fatigue_metrics=metrics
        )
        
        return analysis
    
    @staticmethod
    def _detect_within_game_fatigue(games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect fatigue within individual games (early vs late moves)."""
        early_accuracies = []
        late_accuracies = []
        affected_games = 0
        
        for game in games:
            if 'moves_by_phase' in game:
                phases = game['moves_by_phase']
                # First quarter and last quarter
                if 'opening' in phases and phases['opening'].get('accuracy'):
                    early_accuracies.append(phases['opening']['accuracy'])
                if 'endgame' in phases and phases['endgame'].get('accuracy'):
                    late_accuracies.append(phases['endgame']['accuracy'])
            
            # Alternative: divide moves into early/late
            elif 'move_accuracies' in game and game['move_accuracies']:
                accs = game['move_accuracies']
                if len(accs) >= 10:
                    quarter_point = len(accs) // 2
                    early = statistics.mean(accs[:quarter_point])
                    late = statistics.mean(accs[quarter_point:])
                    early_accuracies.append(early)
                    late_accuracies.append(late)
        
        if early_accuracies and late_accuracies:
            early_avg = statistics.mean(early_accuracies)
            late_avg = statistics.mean(late_accuracies)
            decline = early_avg - late_avg
            
            detected = decline > 3  # >3% decline is significant
            severity = min(100, max(0, decline * 10))  # Scale to 0-100
            affected = sum(1 for e, l in zip(early_accuracies, late_accuracies) if e - l > 3)
            
            return {
                'detected': detected,
                'severity': severity,
                'early_accuracy': early_avg,
                'late_accuracy': late_avg,
                'decline': decline,
                'affected_games': affected
            }
        
        return {
            'detected': False,
            'severity': 0,
            'early_accuracy': 0,
            'late_accuracy': 0,
            'decline': 0,
            'affected_games': 0
        }
    
    @staticmethod
    def _detect_session_fatigue(games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect fatigue across games in a session."""
        accuracies = []
        timestamps = []
        
        for game in games:
            if 'accuracy' in game:
                accuracies.append(game['accuracy'])
            if 'timestamp' in game:
                timestamps.append(game['timestamp'])
        
        if not accuracies or len(accuracies) < 3:
            return {
                'detected': False,
                'severity': 0,
                'first_accuracy': 0,
                'last_accuracy': 0,
                'decline': 0,
                'affected_games': 0
            }
        
        # Check if games are in same session (within 8 hours)
        in_session = True
        if len(timestamps) >= 2:
            time_span = timestamps[-1] - timestamps[0]
            in_session = time_span < timedelta(hours=8)
        
        if not in_session:
            return {
                'detected': False,
                'severity': 0,
                'first_accuracy': 0,
                'last_accuracy': 0,
                'decline': 0,
                'affected_games': 0
            }
        
        # Detect trend using simple linear regression
        first_third = statistics.mean(accuracies[:len(accuracies)//3])
        last_third = statistics.mean(accuracies[-len(accuracies)//3:])
        decline = first_third - last_third
        
        detected = decline > 2.5  # >2.5% decline
        severity = min(100, max(0, decline * 15))
        affected = sum(1 for i in range(len(accuracies)-1) if accuracies[i] - accuracies[i+1] > 2)
        
        return {
            'detected': detected,
            'severity': severity,
            'first_accuracy': first_third,
            'last_accuracy': last_third,
            'decline': decline,
            'affected_games': affected
        }
    
    @staticmethod
    def _analyze_time_of_day(games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by time of day."""
        hourly_data = {}
        
        for game in games:
            if 'timestamp' in game:
                ts = game['timestamp']
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except:
                        continue
                
                hour = ts.hour
                hour_str = f"{hour:02d}:00-{hour+1:02d}:00"
                
                if hour_str not in hourly_data:
                    hourly_data[hour_str] = []
                
                if 'accuracy' in game:
                    hourly_data[hour_str].append(game['accuracy'])
        
        if not hourly_data:
            return {
                'hourly_accuracy': {},
                'effect_detected': False,
                'severity': 0,
                'best_time': 'Unknown',
                'worst_time': 'Unknown'
            }
        
        # Calculate averages
        hourly_avg = {}
        for hour, accs in hourly_data.items():
            hourly_avg[hour] = statistics.mean(accs) if accs else 50
        
        # Find best and worst
        best_time = max(hourly_avg, key=hourly_avg.get)
        worst_time = min(hourly_avg, key=hourly_avg.get)
        diff = hourly_avg[best_time] - hourly_avg[worst_time]
        
        effect_detected = diff > 2.5 and len(hourly_avg) >= 3
        severity = min(100, max(0, diff * 15))
        
        return {
            'hourly_accuracy': hourly_avg,
            'effect_detected': effect_detected,
            'severity': severity,
            'best_time': best_time,
            'worst_time': worst_time
        }
    
    @staticmethod
    def _detect_overwork(games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect signs of overwork (too many games without rest)."""
        if not games or len(games) < 5:
            return {
                'detected': False,
                'severity': 0,
                'evidence': '',
                'affected_games': 0
            }
        
        # Estimate games per day if timestamps available
        timestamps = []
        for game in games:
            if 'timestamp' in game:
                ts = game['timestamp']
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        timestamps.append(ts)
                    except:
                        pass
        
        if not timestamps:
            return {
                'detected': False,
                'severity': 0,
                'evidence': 'Insufficient timestamp data',
                'affected_games': 0
            }
        
        # Count games per day
        games_per_day = defaultdict(int)
        for ts in timestamps:
            day = ts.date()
            games_per_day[day] += 1
        
        # Check for problem days
        high_volume_days = [count for count in games_per_day.values() if count >= 10]
        
        detected = len(high_volume_days) > 0
        severity = min(100, len(high_volume_days) * 20) if detected else 0
        evidence = f"{len(high_volume_days)} days with 10+ games" if detected else ""
        
        return {
            'detected': detected,
            'severity': severity,
            'evidence': evidence,
            'affected_games': sum(high_volume_days)
        }

from collections import defaultdict
