"""
Fatigue detection system for Chess Detective v2.2
Analyze player performance degradation over long sessions.
"""

from typing import List, Dict, Tuple
from datetime import datetime
import statistics


class FatigueDetector:
    """Detect fatigue patterns in player performance."""
    
    def __init__(self, games: List, username: str):
        """
        Initialize fatigue detector.
        
        Args:
            games: List of chess game objects
            username: Player username
        """
        self.games = games
        self.username = username.lower()
        self.game_sessions = []
        self._organize_games_into_sessions()
    
    def _organize_games_into_sessions(self):
        """Organize games into playing sessions (games within 2 hours are same session)."""
        if not self.games:
            return
        
        # Extract dates and times
        game_times = []
        for game in self.games:
            headers = game.headers
            date_str = headers.get('Date', '2000.01.01')
            time_str = headers.get('Time', '00:00:00')
            
            try:
                dt_str = f"{date_str} {time_str}".replace('.', '-')
                game_time = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                game_times.append((game_time, game))
            except:
                continue
        
        # Sort by time
        game_times.sort(key=lambda x: x[0])
        
        # Group into sessions (2-hour gaps = new session)
        current_session = []
        last_time = None
        
        for game_time, game in game_times:
            if last_time is None:
                current_session = [game]
                last_time = game_time
            else:
                time_diff = (game_time - last_time).total_seconds() / 3600  # Hours
                if time_diff < 2:  # Within 2 hours = same session
                    current_session.append(game)
                else:  # New session
                    if current_session:
                        self.game_sessions.append(current_session)
                    current_session = [game]
                
                last_time = game_time
        
        if current_session:
            self.game_sessions.append(current_session)
    
    def detect_fatigue_by_session(self) -> Dict[int, Dict]:
        """
        Detect fatigue within playing sessions.
        
        Returns:
            Dictionary with fatigue metrics per session
        """
        session_fatigue = {}
        
        for session_idx, session in enumerate(self.game_sessions):
            if len(session) < 2:
                continue
            
            accuracies = []
            move_times = []
            time_spent = []
            
            for game in session:
                headers = game.headers
                white = headers.get("White", "").lower()
                black = headers.get("Black", "").lower()
                is_player_white = white == self.username
                
                # Get move count (proxy for time)
                move_count = len(list(game.mainline_moves()))
                if move_count > 0:
                    move_times.append(move_count)
                
                # Time control indicates time per game
                time_control = headers.get('TimeControl', '0+0')
                try:
                    tc_parts = time_control.split('+')
                    base_time = int(tc_parts[0])
                    time_spent.append(base_time)
                except:
                    pass
            
            if not move_times:
                continue
            
            # Calculate fatigue indicators
            early_avg = statistics.mean(move_times[:len(move_times)//2]) if len(move_times) > 1 else 0
            late_avg = statistics.mean(move_times[len(move_times)//2:]) if len(move_times) > 1 else 0
            
            # Degradation score
            if early_avg > 0:
                degradation = ((early_avg - late_avg) / early_avg * 100)
            else:
                degradation = 0
            
            session_fatigue[session_idx] = {
                'games_in_session': len(session),
                'early_avg_moves': early_avg,
                'late_avg_moves': late_avg,
                'degradation_percent': degradation,
                'total_time_spent': sum(time_spent),
                'is_fatigued': degradation > 15  # >15% degradation = fatigued
            }
        
        return session_fatigue
    
    def detect_fatigue_progression(self) -> Dict:
        """
        Detect fatigue progression over all games.
        
        Returns:
            Dictionary with overall fatigue trends
        """
        if len(self.games) < 5:
            return {'insufficient_data': True}
        
        move_counts = []
        accuracies = []
        
        for game in self.games:
            move_count = len(list(game.mainline_moves()))
            if move_count > 0:
                move_counts.append(move_count)
        
        if not move_counts or len(move_counts) < 5:
            return {'insufficient_data': True}
        
        # Split into quarters
        quarter_size = len(move_counts) // 4
        if quarter_size < 1:
            quarter_size = 1
        
        quarters = [
            move_counts[:quarter_size],
            move_counts[quarter_size:quarter_size*2],
            move_counts[quarter_size*2:quarter_size*3],
            move_counts[quarter_size*3:]
        ]
        
        quarter_avgs = [statistics.mean(q) if q else 0 for q in quarters]
        
        # Calculate trend
        trend_values = []
        for i in range(len(quarter_avgs) - 1):
            if quarter_avgs[i] > 0:
                change = ((quarter_avgs[i+1] - quarter_avgs[i]) / quarter_avgs[i] * 100)
                trend_values.append(change)
        
        avg_trend = statistics.mean(trend_values) if trend_values else 0
        
        return {
            'insufficient_data': False,
            'quarter_1_avg': quarter_avgs[0],
            'quarter_2_avg': quarter_avgs[1],
            'quarter_3_avg': quarter_avgs[2],
            'quarter_4_avg': quarter_avgs[3],
            'overall_trend': avg_trend,
            'trend_direction': 'declining' if avg_trend < -5 else 'stable' if abs(avg_trend) <= 5 else 'improving',
            'is_fatigued': avg_trend < -10
        }
    
    def detect_consistency_drops(self) -> Dict[str, List[int]]:
        """
        Detect sudden drops in performance consistency.
        
        Returns:
            Dictionary with game indices where drops occur
        """
        if len(self.games) < 10:
            return {'insufficient_data': True}
        
        move_counts = []
        for game in self.games:
            move_count = len(list(game.mainline_moves()))
            if move_count > 0:
                move_counts.append(move_count)
        
        if len(move_counts) < 10:
            return {'insufficient_data': True}
        
        # Calculate rolling average
        window = 5
        drops = []
        
        for i in range(window, len(move_counts)):
            before_avg = statistics.mean(move_counts[i-window:i])
            after = move_counts[i]
            
            # Drop detection: >20% sudden drop
            if before_avg > 0 and ((before_avg - after) / before_avg * 100) > 20:
                drops.append(i)
        
        return {
            'insufficient_data': False,
            'consistency_drops': drops,
            'num_drops': len(drops),
            'drop_rate': (len(drops) / len(move_counts) * 100) if move_counts else 0
        }
    
    def get_fatigue_report(self) -> Dict:
        """
        Get comprehensive fatigue analysis report.
        
        Returns:
            Dictionary with complete fatigue analysis
        """
        return {
            'player': self.username,
            'total_games': len(self.games),
            'total_sessions': len(self.game_sessions),
            'session_analysis': self.detect_fatigue_by_session(),
            'progression_analysis': self.detect_fatigue_progression(),
            'consistency_analysis': self.detect_consistency_drops()
        }


def display_fatigue_analysis(games, username: str):
    """
    Display enhanced fatigue analysis results with detailed degradation scoring.
    
    Args:
        games: List of chess games
        username: Player username
    """
    print("\n" + "="*90)
    print(f"  FATIGUE DETECTION ANALYSIS - {username.upper()}")
    print("="*90 + "\n")
    
    detector = FatigueDetector(games, username)
    report = detector.get_fatigue_report()
    
    print(f"Total Games Analyzed: {report['total_games']}")
    print(f"Playing Sessions Found: {report['total_sessions']}\n")
    
    # Session Analysis
    if report['session_analysis']:
        print("-"*90)
        print("  SESSION FATIGUE ANALYSIS")
        print("-"*90)
        fatigued_sessions = 0
        total_degradation = 0
        num_valid_sessions = 0
        critical_sessions = 0
        
        for session_idx, session_data in report['session_analysis'].items():
            games_count = session_data['games_in_session']
            degradation = session_data['degradation_percent']
            is_fatigued = session_data['is_fatigued']
            
            if is_fatigued:
                fatigued_sessions += 1
            
            if degradation > 30:
                critical_sessions += 1
            
            total_degradation += abs(degradation)
            num_valid_sessions += 1
            
            # Enhanced status with severity
            if degradation > 30:
                status = "🔴 CRITICAL FATIGUE"
            elif degradation > 15:
                status = "🟡 MODERATE FATIGUE"
            elif is_fatigued:
                status = "🟠 MILD FATIGUE"
            else:
                status = "✓ STABLE"
            
            print(f"\n  Session {session_idx + 1}: {games_count} games")
            print(f"    Performance Degradation: {degradation:.1f}% {status}")
            print(f"    Early Games Avg Moves: {session_data['early_avg_moves']:.1f}")
            print(f"    Late Games Avg Moves: {session_data['late_avg_moves']:.1f}")
        
        if num_valid_sessions > 0:
            fatigue_rate = (fatigued_sessions / num_valid_sessions * 100)
            avg_degradation = total_degradation / num_valid_sessions
            
            print(f"\n  SESSION SUMMARY:")
            print(f"    Fatigue Rate: {fatigue_rate:.1f}% ({fatigued_sessions}/{num_valid_sessions} sessions)")
            print(f"    Avg Degradation: {avg_degradation:.1f}%")
            print(f"    Critical Sessions: {critical_sessions}")
            
            if critical_sessions > 0:
                print(f"    ⚠️  ALERT: {critical_sessions} sessions with severe fatigue detected")
    
    # Progression Analysis
    if not report['progression_analysis'].get('insufficient_data', False):
        print("\n" + "-"*90)
        print("  OVERALL FATIGUE PROGRESSION (BY QUARTER)")
        print("-"*90)
        prog = report['progression_analysis']
        
        quarters = [
            ('Q1', prog['quarter_1_avg']),
            ('Q2', prog['quarter_2_avg']),
            ('Q3', prog['quarter_3_avg']),
            ('Q4', prog['quarter_4_avg'])
        ]
        
        print(f"\n  Quarterly Performance Trend:")
        for q_label, q_avg in quarters:
            print(f"    {q_label}: {q_avg:.1f} avg moves", end="")
            if q_avg < 15:
                print(" 📉 (possible fatigue)", end="")
            print()
        
        print(f"\n  Overall Trend: {prog['overall_trend']:.1f}% change")
        print(f"  Direction: {prog['trend_direction'].upper()}")
        
        if prog['is_fatigued']:
            severity = "SEVERE" if abs(prog['overall_trend']) > 25 else "MODERATE"
            print(f"  Status: 🔴 {severity} FATIGUE DETECTED")
            print(f"     (Performance declining over time)")
        else:
            print(f"  Status: ✓ No significant fatigue pattern detected")
    
    # Consistency Analysis
    if not report['consistency_analysis'].get('insufficient_data', False):
        cons = report['consistency_analysis']
        print("\n" + "-"*90)
        print("  PERFORMANCE CONSISTENCY & DROPS")
        print("-"*90)
        print(f"\n  Sudden Performance Drops: {cons['num_drops']}")
        print(f"  Drop Rate: {cons['drop_rate']:.1f}%")
        
        if cons['drop_rate'] > 20:
            print(f"  🔴 SEVERE: Frequent sudden drops in performance")
        elif cons['drop_rate'] > 10:
            print(f"  🟡 MODERATE: Regular performance inconsistencies")
        elif cons['num_drops'] > 0:
            print(f"  🟠 MILD: Occasional performance fluctuations")
        else:
            print(f"  ✓ STABLE: Consistent performance throughout")
        
        if cons['num_drops'] > 0:
            print(f"\n  ⚠️  Interpretation:")
            print(f"     • {cons['num_drops']} instances of >20% performance drop")
            print(f"     • May indicate: Fatigue, tilt, or external disruptions")
            print(f"     • Monitor play patterns for consistency")
    
    print("\n" + "="*90 + "\n")
