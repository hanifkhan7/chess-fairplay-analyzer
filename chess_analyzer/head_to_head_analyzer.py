"""
Head-to-Head Matchup Analyzer
Analyzes two players on the same platform to predict match outcomes
Features: ELO-based probability, game history analysis, opening stats, suspicious activity detection
"""

import requests
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from statistics import mean, stdev

logger = logging.getLogger(__name__)

class HeadToHeadAnalyzer:
    """Analyzes matchups between two players."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.player1_games = []
        self.player2_games = []
    
    def _convert_game_to_dict(self, game) -> Dict:
        """
        Convert a Game object to dictionary format.
        Handles both dictionary and Game object inputs.
        
        Args:
            game: Game object or dict
            
        Returns:
            Dictionary with game data
        """
        try:
            # If it's already a dict, return it
            if isinstance(game, dict):
                return game
            
            # Convert Game object to dict
            game_dict = {
                'result': getattr(game, 'result', 'unknown').lower() if hasattr(game, 'result') else 'unknown',
                'opponent': getattr(game, 'opponent', 'unknown'),
                'opponent_elo': getattr(game, 'opponent_elo', 1600),
                'opening': getattr(game, 'opening', 'Unknown'),
                'accuracy': getattr(game, 'accuracy', 0),
                'moves': getattr(game, 'moves', 0),
                'duration': getattr(game, 'duration', 0),
                'date': getattr(game, 'date', ''),
                'username': getattr(game, 'username', ''),
                'url': getattr(game, 'url', ''),
                'eco': getattr(game, 'eco', ''),
                'rated': getattr(game, 'rated', False),
                'time_control': getattr(game, 'time_control', '')
            }
            return game_dict
        except Exception as e:
            logger.error(f"Error converting game to dict: {e}")
            return {
                'result': 'unknown',
                'opponent': 'unknown',
                'opening': 'Unknown',
                'accuracy': 0
            }
    
    def calculate_elo_probability(self, player1_elo: int, player2_elo: int) -> Tuple[float, float]:
        """
        Calculate win probability based on ELO rating difference.
        Uses standard ELO rating system formula.
        
        Args:
            player1_elo: Player 1 ELO rating
            player2_elo: Player 2 ELO rating
            
        Returns:
            Tuple of (player1_win_prob, player2_win_prob) as percentages
        """
        try:
            elo_diff = player2_elo - player1_elo
            
            # Standard ELO formula: P = 1 / (1 + 10^(-d/400))
            # where d is the rating difference
            player1_prob = 1 / (1 + 10 ** (elo_diff / 400))
            player2_prob = 1 - player1_prob
            
            return (player1_prob * 100, player2_prob * 100)
            
        except Exception as e:
            logger.error(f"Error calculating ELO probability: {e}")
            return (50.0, 50.0)
    
    def analyze_game_history(self, games1: List[Dict], games2: List[Dict]) -> Dict:
        """
        Analyze game history of both players to calculate performance-based probability.
        
        Args:
            games1: Player 1's games list
            games2: Player 2's games list
            
        Returns:
            Analysis dict with statistics
        """
        try:
            analysis = {
                'player1': {
                    'total_games': len(games1),
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'win_rate': 0,
                    'avg_opponent_rating': 0,
                    'accuracy': []
                },
                'player2': {
                    'total_games': len(games2),
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'win_rate': 0,
                    'avg_opponent_rating': 0,
                    'accuracy': []
                }
            }
            
            # Analyze player 1
            for game in games1:
                game_dict = self._convert_game_to_dict(game)
                result = game_dict.get('result', '').lower()
                if result == 'won':
                    analysis['player1']['wins'] += 1
                elif result == 'lost':
                    analysis['player1']['losses'] += 1
                elif result == 'draw':
                    analysis['player1']['draws'] += 1
                
                # Track accuracy if available
                if game_dict.get('accuracy'):
                    analysis['player1']['accuracy'].append(game_dict.get('accuracy'))
            
            # Analyze player 2
            for game in games2:
                game_dict = self._convert_game_to_dict(game)
                result = game_dict.get('result', '').lower()
                if result == 'won':
                    analysis['player2']['wins'] += 1
                elif result == 'lost':
                    analysis['player2']['losses'] += 1
                elif result == 'draw':
                    analysis['player2']['draws'] += 1
                
                if game_dict.get('accuracy'):
                    analysis['player2']['accuracy'].append(game_dict.get('accuracy'))
            
            # Calculate win rates
            if analysis['player1']['total_games'] > 0:
                analysis['player1']['win_rate'] = (analysis['player1']['wins'] / analysis['player1']['total_games']) * 100
                if analysis['player1']['accuracy']:
                    analysis['player1']['avg_accuracy'] = mean(analysis['player1']['accuracy'])
            
            if analysis['player2']['total_games'] > 0:
                analysis['player2']['win_rate'] = (analysis['player2']['wins'] / analysis['player2']['total_games']) * 100
                if analysis['player2']['accuracy']:
                    analysis['player2']['avg_accuracy'] = mean(analysis['player2']['accuracy'])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing game history: {e}")
            return {}
    
    def find_head_to_head_games(self, games1: List[Dict], games2: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Find games where player 1 played against player 2.
        
        Args:
            games1: Player 1's games
            games2: Player 2's games
            
        Returns:
            Tuple of (matching_games, h2h_stats)
        """
        try:
            h2h_games = []
            h2h_stats = {
                'total_games': 0,
                'player1_wins': 0,
                'player2_wins': 0,
                'draws': 0,
                'player1_win_rate': 0,
                'openings': {}
            }
            
            # Find games where players faced each other
            for game1 in games1:
                game1_dict = self._convert_game_to_dict(game1)
                opponent1 = game1_dict.get('opponent', '')
                for game2 in games2:
                    game2_dict = self._convert_game_to_dict(game2)
                    opponent2 = game2_dict.get('opponent', '')
                    
                    # Check if they played each other
                    if opponent1.lower() == game2_dict.get('username', '').lower() and \
                       opponent2.lower() == game1_dict.get('username', '').lower():
                        
                        h2h_games.append(game1_dict)
                        h2h_stats['total_games'] += 1
                        
                        # Track results
                        result = game1_dict.get('result', '').lower()
                        if result == 'won':
                            h2h_stats['player1_wins'] += 1
                        elif result == 'lost':
                            h2h_stats['player2_wins'] += 1
                        else:
                            h2h_stats['draws'] += 1
                        
                        # Track openings
                        opening = game1_dict.get('opening', 'Unknown')
                        if opening not in h2h_stats['openings']:
                            h2h_stats['openings'][opening] = {
                                'games': 0,
                                'player1_wins': 0,
                                'player2_wins': 0,
                                'draws': 0
                            }
                        
                        h2h_stats['openings'][opening]['games'] += 1
                        if result == 'won':
                            h2h_stats['openings'][opening]['player1_wins'] += 1
                        elif result == 'lost':
                            h2h_stats['openings'][opening]['player2_wins'] += 1
                        else:
                            h2h_stats['openings'][opening]['draws'] += 1
            
            # Calculate win rate
            if h2h_stats['total_games'] > 0:
                h2h_stats['player1_win_rate'] = (h2h_stats['player1_wins'] / h2h_stats['total_games']) * 100
            
            return (h2h_games, h2h_stats)
            
        except Exception as e:
            logger.error(f"Error finding head-to-head games: {e}")
            return ([], {})
    
    def analyze_opening_repertoire(self, games: List[Dict]) -> Dict:
        """
        Analyze opening repertoire from games.
        
        Args:
            games: List of games
            
        Returns:
            Opening statistics
        """
        try:
            openings = {}
            
            for game in games:
                game_dict = self._convert_game_to_dict(game)
                opening = game_dict.get('opening', 'Unknown')
                if opening not in openings:
                    openings[opening] = {'count': 0, 'wins': 0, 'losses': 0, 'draws': 0}
                
                openings[opening]['count'] += 1
                result = game_dict.get('result', '').lower()
                if result == 'won':
                    openings[opening]['wins'] += 1
                elif result == 'lost':
                    openings[opening]['losses'] += 1
                else:
                    openings[opening]['draws'] += 1
            
            # Calculate win rates per opening
            for opening in openings:
                total = openings[opening]['count']
                if total > 0:
                    openings[opening]['win_rate'] = (openings[opening]['wins'] / total) * 100
            
            # Sort by frequency
            sorted_openings = sorted(openings.items(), key=lambda x: x[1]['count'], reverse=True)
            
            return dict(sorted_openings[:10])  # Top 10 openings
            
        except Exception as e:
            logger.error(f"Error analyzing opening repertoire: {e}")
            return {}
    
    def detect_suspicious_activity(self, games1: List[Dict], games2: List[Dict]) -> Dict:
        """
        Check for suspicious activity in games.
        
        Args:
            games1: Player 1's games
            games2: Player 2's games
            
        Returns:
            Suspicious activity flags
        """
        try:
            flags = {
                'player1': [],
                'player2': []
            }
            
            # Check for unusually high accuracy
            p1_accuracies = [self._convert_game_to_dict(g).get('accuracy', 0) for g in games1 if self._convert_game_to_dict(g).get('accuracy')]
            p2_accuracies = [self._convert_game_to_dict(g).get('accuracy', 0) for g in games2 if self._convert_game_to_dict(g).get('accuracy')]
            
            if p1_accuracies and mean(p1_accuracies) > 95:
                flags['player1'].append(f"Unusually high accuracy: {mean(p1_accuracies):.1f}%")
            
            if p2_accuracies and mean(p2_accuracies) > 95:
                flags['player2'].append(f"Unusually high accuracy: {mean(p2_accuracies):.1f}%")
            
            # Check for extreme rating performance
            p1_wins = sum(1 for g in games1 if self._convert_game_to_dict(g).get('result') == 'won')
            p1_losses = sum(1 for g in games1 if self._convert_game_to_dict(g).get('result') == 'lost')
            p1_total = len(games1)
            
            p2_wins = sum(1 for g in games2 if self._convert_game_to_dict(g).get('result') == 'won')
            p2_losses = sum(1 for g in games2 if self._convert_game_to_dict(g).get('result') == 'lost')
            p2_total = len(games2)
            
            if p1_total > 0 and p1_wins / p1_total > 0.9:
                flags['player1'].append(f"Extremely high win rate: {(p1_wins/p1_total)*100:.1f}%")
            
            if p2_total > 0 and p2_wins / p2_total > 0.9:
                flags['player2'].append(f"Extremely high win rate: {(p2_wins/p2_total)*100:.1f}%")
            
            return flags
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return {'player1': [], 'player2': []}
    
    def calculate_performance_probability(self, analysis: Dict) -> Tuple[float, float]:
        """
        Calculate win probability based on performance metrics.
        
        Args:
            analysis: Game history analysis dict
            
        Returns:
            Tuple of (player1_prob, player2_prob) as percentages
        """
        try:
            p1_wr = analysis['player1']['win_rate']
            p2_wr = analysis['player2']['win_rate']
            
            # Normalize win rates to probability
            total = p1_wr + p2_wr if (p1_wr + p2_wr) > 0 else 100
            
            p1_prob = (p1_wr / total) * 100
            p2_prob = (p2_wr / total) * 100
            
            return (p1_prob, p2_prob)
            
        except Exception as e:
            logger.error(f"Error calculating performance probability: {e}")
            return (50.0, 50.0)
    
    def calculate_combined_probability(self, elo_prob: Tuple[float, float], 
                                      perf_prob: Tuple[float, float], 
                                      h2h_prob: Tuple[float, float]) -> Tuple[float, float]:
        """
        Combine multiple probability calculations for final prediction.
        
        Args:
            elo_prob: ELO-based probability (p1, p2)
            perf_prob: Performance-based probability (p1, p2)
            h2h_prob: Head-to-head probability (p1, p2)
            
        Returns:
            Combined probability (p1, p2)
        """
        try:
            # Weight the probabilities
            # 40% ELO, 40% Performance, 20% Head-to-head
            p1_combined = (elo_prob[0] * 0.4) + (perf_prob[0] * 0.4) + (h2h_prob[0] * 0.2)
            p2_combined = (elo_prob[1] * 0.4) + (perf_prob[1] * 0.4) + (h2h_prob[1] * 0.2)
            
            return (p1_combined, p2_combined)
            
        except Exception as e:
            logger.error(f"Error calculating combined probability: {e}")
            return (50.0, 50.0)
    
    def generate_matchup_report(self, player1_name: str, player1_elo: int, games1: List[Dict],
                               player2_name: str, player2_elo: int, games2: List[Dict]) -> Dict:
        """
        Generate comprehensive matchup report.
        
        Args:
            player1_name: Player 1 username
            player1_elo: Player 1 ELO
            games1: Player 1's games
            player2_name: Player 2 username
            player2_elo: Player 2 ELO
            games2: Player 2's games
            
        Returns:
            Comprehensive matchup report
        """
        try:
            print("\n[MATCHUP] Analyzing matchup between {} and {}...".format(player1_name, player2_name))
            
            # Calculate various probabilities
            elo_prob = self.calculate_elo_probability(player1_elo, player2_elo)
            print("[ANALYSIS] ELO-based probability: {:.1f}% vs {:.1f}%".format(elo_prob[0], elo_prob[1]))
            
            # Analyze game history
            history_analysis = self.analyze_game_history(games1, games2)
            perf_prob = self.calculate_performance_probability(history_analysis)
            print("[ANALYSIS] Performance-based probability: {:.1f}% vs {:.1f}%".format(perf_prob[0], perf_prob[1]))
            
            # Find head-to-head games
            h2h_games, h2h_stats = self.find_head_to_head_games(games1, games2)
            if h2h_stats['total_games'] > 0:
                h2h_prob = (h2h_stats['player1_win_rate'], 100 - h2h_stats['player1_win_rate'])
                print("[H2H] Found {} previous games between players".format(h2h_stats['total_games']))
                print("[H2H] Head-to-head probability: {:.1f}% vs {:.1f}%".format(h2h_prob[0], h2h_prob[1]))
            else:
                h2h_prob = (50.0, 50.0)
                print("[H2H] No previous head-to-head games found")
            
            # Analyze openings
            p1_openings = self.analyze_opening_repertoire(games1)
            p2_openings = self.analyze_opening_repertoire(games2)
            
            # Check for suspicious activity
            suspicious = self.detect_suspicious_activity(games1, games2)
            
            # Calculate combined probability
            combined_prob = self.calculate_combined_probability(elo_prob, perf_prob, h2h_prob)
            
            report = {
                'players': {
                    'player1': {'name': player1_name, 'elo': player1_elo, 'games': len(games1)},
                    'player2': {'name': player2_name, 'elo': player2_elo, 'games': len(games2)}
                },
                'elo_probability': elo_prob,
                'performance_probability': perf_prob,
                'h2h_games': h2h_stats,
                'h2h_probability': h2h_prob,
                'history_analysis': history_analysis,
                'player1_openings': p1_openings,
                'player2_openings': p2_openings,
                'suspicious_activity': suspicious,
                'combined_probability': combined_prob,
                'prediction': player1_name if combined_prob[0] > 50 else player2_name,
                'confidence': max(combined_prob[0], combined_prob[1])
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating matchup report: {e}")
            return {}
    
    def display_matchup_report(self, report: Dict) -> None:
        """
        Display matchup report in formatted output.
        
        Args:
            report: Matchup report dictionary
        """
        try:
            if not report:
                print("[ERROR] Could not generate report")
                return
            
            p1 = report['players']['player1']
            p2 = report['players']['player2']
            elo_prob = report['elo_probability']
            perf_prob = report['performance_probability']
            h2h_prob = report['h2h_probability']
            combined_prob = report['combined_probability']
            
            print("\n" + "="*80)
            print("HEAD-TO-HEAD MATCHUP ANALYSIS")
            print("="*80)
            
            print("\n┌─ PLAYER STATS ─────────────────────────────────────────────────────────┐")
            print(f"│ {p1['name']:<35} vs {p2['name']:<35} │")
            print(f"│ ELO: {p1['elo']:<32} ELO: {p2['elo']:<32} │")
            print(f"│ Games: {p1['games']:<30} Games: {p2['games']:<30} │")
            print("└────────────────────────────────────────────────────────────────────────────┘")
            
            print("\n┌─ WIN PROBABILITY ANALYSIS ─────────────────────────────────────────────────┐")
            
            # ELO-based
            print(f"│ ELO Rating Analysis                                                        │")
            p1_bar = int(elo_prob[0] / 2)
            p2_bar = int(elo_prob[1] / 2)
            print(f"│ {p1['name']:<35} {'█' * p1_bar:<50} {elo_prob[0]:>5.1f}% │")
            print(f"│ {p2['name']:<35} {'█' * p2_bar:<50} {elo_prob[1]:>5.1f}% │")
            print("│                                                                            │")
            
            # Performance-based
            print(f"│ Game Performance Analysis                                                  │")
            p1_bar = int(perf_prob[0] / 2)
            p2_bar = int(perf_prob[1] / 2)
            print(f"│ {p1['name']:<35} {'█' * p1_bar:<50} {perf_prob[0]:>5.1f}% │")
            print(f"│ {p2['name']:<35} {'█' * p2_bar:<50} {perf_prob[1]:>5.1f}% │")
            print("│                                                                            │")
            
            # Head-to-head
            if report['h2h_games']['total_games'] > 0:
                print(f"│ Head-to-Head Record ({report['h2h_games']['total_games']} games)                                                │")
                p1_bar = int(h2h_prob[0] / 2)
                p2_bar = int(h2h_prob[1] / 2)
                print(f"│ {p1['name']:<35} {'█' * p1_bar:<50} {h2h_prob[0]:>5.1f}% │")
                print(f"│ {p2['name']:<35} {'█' * p2_bar:<50} {h2h_prob[1]:>5.1f}% │")
                print("│                                                                            │")
            
            # Combined prediction
            print(f"│ Combined Prediction (40% ELO, 40% Perf, 20% H2H)                           │")
            p1_bar = int(combined_prob[0] / 2)
            p2_bar = int(combined_prob[1] / 2)
            print(f"│ {p1['name']:<35} {'█' * p1_bar:<50} {combined_prob[0]:>5.1f}% │")
            print(f"│ {p2['name']:<35} {'█' * p2_bar:<50} {combined_prob[1]:>5.1f}% │")
            print("└────────────────────────────────────────────────────────────────────────────┘")
            
            print("\n┌─ PREDICTION ───────────────────────────────────────────────────────────────┐")
            prediction = report['prediction']
            confidence = report['confidence']
            print(f"│ PREDICTED WINNER: {prediction:<58} │")
            print(f"│ CONFIDENCE LEVEL: {confidence:.1f}%{' ':<57} │")
            print("└────────────────────────────────────────────────────────────────────────────┘")
            
            # Head-to-head details
            if report['h2h_games']['total_games'] > 0:
                h2h = report['h2h_games']
                print("\n┌─ HEAD-TO-HEAD STATISTICS ──────────────────────────────────────────────────┐")
                print(f"│ Total Games: {h2h['total_games']:<64} │")
                print(f"│ {p1['name']:<35} Wins: {h2h['player1_wins']:<44} │")
                print(f"│ {p2['name']:<35} Wins: {h2h['player2_wins']:<44} │")
                print(f"│ Draws: {h2h['draws']:<74} │")
                
                if h2h['openings']:
                    print("│                                                                            │")
                    print("│ Openings Played:                                                           │")
                    for i, (opening, stats) in enumerate(list(h2h['openings'].items())[:5]):
                        win_rate = (stats['player1_wins'] / stats['games'] * 100) if stats['games'] > 0 else 0
                        print(f"│   {opening[:30]:<30} {stats['games']:>2} games ({p1['name']} {win_rate:>5.1f}%) │")
                
                print("└────────────────────────────────────────────────────────────────────────────┘")
            
            # Suspicious activity
            suspicious = report['suspicious_activity']
            if suspicious['player1'] or suspicious['player2']:
                print("\n┌─ SUSPICIOUS ACTIVITY FLAGS ───────────────────────────────────────────────┐")
                if suspicious['player1']:
                    print(f"│ {p1['name']}:                                                    │")
                    for flag in suspicious['player1']:
                        print(f"│   ⚠ {flag:<72} │")
                if suspicious['player2']:
                    print(f"│ {p2['name']}:                                                    │")
                    for flag in suspicious['player2']:
                        print(f"│   ⚠ {flag:<72} │")
                print("└────────────────────────────────────────────────────────────────────────────┘")
            
            print("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"Error displaying matchup report: {e}")
            print(f"[ERROR] Could not display report: {e}")
