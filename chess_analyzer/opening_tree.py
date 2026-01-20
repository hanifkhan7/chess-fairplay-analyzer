"""
Opening Repertoire Inspector
Analyzes opponent's opening choices, patterns, and vulnerabilities
Provides visual opening trees and exploitation blueprints
"""

import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import chess
import chess.pgn
from io import StringIO


class OpeningTreeAnalyzer:
    """Analyzes and visualizes opponent's opening repertoire"""
    
    # ECO Classification codes (simplified)
    ECO_OPENINGS = {
        "1.e4 e5": "Open Games",
        "1.e4 c5": "Sicilian Defense",
        "1.e4 e6": "French Defense",
        "1.e4 c6": "Caro-Kann Defense",
        "1.d4 d5": "Queen's Gambit / Closed Games",
        "1.d4 Nf6": "Indian Games",
        "1.c4": "English Opening / Flank Games",
    }
    
    MAIN_LINE_NAMES = {
        "1.e4 e5 2.Nf3 Nc6 3.Bb5": "Ruy Lopez (Spanish)",
        "1.e4 e5 2.Nf3 Nc6 3.Bc4": "Italian Game",
        "1.e4 e5 2.Nf3 Nf6 3.Bb5": "Scandinavian-style positions",
        "1.e4 c5 2.Nf3": "Sicilian Defense",
        "1.d4 d5 2.c4": "Queen's Gambit",
        "1.d4 Nf6 2.c4": "Indian Games",
        "1.c4 e5": "English Opening",
    }
    
    def __init__(self, games: List, username: str):
        self.games = games
        self.username = username.lower()
        self.opening_tree = defaultdict(lambda: {
            'count': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'your_wins': 0,
            'your_losses': 0,
            'moves': [],
            'elos': [],
            'child_moves': defaultdict(lambda: {'count': 0, 'wins': 0, 'losses': 0})
        })
        self.position_clusters = defaultdict(list)
        self.all_opening_moves = []
        self._analyze_games()
    
    def _analyze_games(self):
        """Extract opening moves and statistics from all games"""
        for game in self.games:
            try:
                white = game.headers.get("White", "").lower()
                black = game.headers.get("Black", "").lower()
                result = game.headers.get("Result", "*")
                white_elo = game.headers.get("WhiteElo", "?")
                black_elo = game.headers.get("BlackElo", "?")
                
                # Determine if player is white or black and outcome
                is_player_white = white == self.username
                if result == "1-0":
                    player_won = is_player_white
                elif result == "0-1":
                    player_won = not is_player_white
                else:
                    player_won = None
                
                # Extract opening moves (up to 10 moves = 20 half-moves)
                board = chess.Board()
                opening_uci = []
                move_count = 0
                elo = int(white_elo) if is_player_white and white_elo != "?" else (int(black_elo) if black_elo != "?" else 0)
                
                for move in game.mainline_moves():
                    if move_count >= 20:  # 10 moves
                        break
                    opening_uci.append(move.uci())
                    board.push(move)
                    move_count += 1
                
                # Store opening sequence
                opening_key = " ".join(opening_uci)
                self.all_opening_moves.append({
                    'uci': opening_uci,
                    'moves_text': self._uci_to_san(opening_uci),
                    'opponent_elo': elo,
                    'result': result,
                    'player_won': player_won,
                    'full_game': game
                })
                
                # Build tree at each depth
                current_key = ""
                for i, uci in enumerate(opening_uci):
                    current_key = current_key + " " + uci if current_key else uci
                    self.opening_tree[current_key]['count'] += 1
                    self.opening_tree[current_key]['elos'].append(elo)
                    
                    if result == "1-0":
                        if is_player_white:
                            self.opening_tree[current_key]['wins'] += 1
                            self.opening_tree[current_key]['your_wins'] += 1
                        else:
                            self.opening_tree[current_key]['losses'] += 1
                            self.opening_tree[current_key]['your_losses'] += 1
                    elif result == "0-1":
                        if is_player_white:
                            self.opening_tree[current_key]['losses'] += 1
                            self.opening_tree[current_key]['your_losses'] += 1
                        else:
                            self.opening_tree[current_key]['wins'] += 1
                            self.opening_tree[current_key]['your_wins'] += 1
                    else:
                        self.opening_tree[current_key]['draws'] += 1
                    
                    # Track moves
                    if i < len(opening_uci) - 1:
                        next_move = opening_uci[i + 1]
                        self.opening_tree[current_key]['child_moves'][next_move]['count'] += 1
                        if result == "1-0":
                            winner = is_player_white
                        elif result == "0-1":
                            winner = not is_player_white
                        else:
                            winner = None
                        
                        if winner == (i % 2 == 0):  # Check if this side won
                            self.opening_tree[current_key]['child_moves'][next_move]['wins'] += 1
                        elif winner is not None:
                            self.opening_tree[current_key]['child_moves'][next_move]['losses'] += 1
            except Exception as e:
                continue
    
    def _uci_to_san(self, uci_moves: List[str]) -> str:
        """Convert UCI moves to standard algebraic notation"""
        board = chess.Board()
        san_moves = []
        try:
            for uci in uci_moves[:20]:  # Limit to 20 half-moves
                move = chess.Move.from_uci(uci)
                san = board.san(move)
                san_moves.append(san)
                board.push(move)
        except:
            pass
        return " ".join(san_moves) if san_moves else ""
    
    def _cluster_positions(self):
        """Cluster similar opening positions"""
        for opening_data in self.all_opening_moves:
            # Cluster by first 6 moves
            key = " ".join(opening_data['uci'][:12])  # 6 moves = 12 half-moves
            self.position_clusters[key].append(opening_data)
    
    def get_repertoire_summary(self) -> Dict:
        """Get top openings and their statistics"""
        summary = []
        for opening_key, stats in sorted(self.opening_tree.items(), 
                                         key=lambda x: x[1]['count'], 
                                         reverse=True)[:10]:
            if stats['count'] < 2:  # Skip rare lines
                continue
            
            total = stats['count']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            your_win_rate = (stats['your_wins'] / total * 100) if total > 0 else 0
            avg_elo = sum(stats['elos']) / len(stats['elos']) if stats['elos'] else 0
            
            summary.append({
                'opening': opening_key,
                'moves_san': self._uci_to_san(opening_key.split()),
                'count': total,
                'win_rate': win_rate,
                'your_win_rate': your_win_rate,
                'avg_opponent_elo': int(avg_elo),
                'stats': stats
            })
        
        return sorted(summary, key=lambda x: x['count'], reverse=True)
    
    def get_exploitation_blueprint(self) -> List[Dict]:
        """Generate specific exploitation recommendations"""
        self._cluster_positions()
        
        blueprint = []
        
        # Find weakest openings
        for opening_key, stats in self.opening_tree.items():
            if stats['count'] < 2:
                continue
            
            total = stats['count']
            win_rate = (stats['wins'] / total * 100) if total > 0 else 0
            
            # Flag weak openings (low win rate)
            if win_rate < 35 or stats['your_wins'] / total > 0.6:
                blueprint.append({
                    'opening': opening_key,
                    'moves_san': self._uci_to_san(opening_key.split()),
                    'frequency': stats['count'],
                    'opponent_win_rate': win_rate,
                    'your_win_rate': (stats['your_wins'] / total * 100),
                    'weakness_level': 'CRITICAL' if win_rate < 25 else ('HIGH' if win_rate < 35 else 'MODERATE'),
                    'recommendation': self._generate_recommendation(opening_key, stats)
                })
        
        return sorted(blueprint, key=lambda x: x['frequency'], reverse=True)
    
    def _generate_recommendation(self, opening_key: str, stats: Dict) -> str:
        """Generate specific recommendations for exploitation"""
        moves = opening_key.split()
        
        # Basic recommendations based on move patterns
        if "e2e4" in opening_key or "e4" in opening_key:
            if "e7e5" in opening_key or "e5" in opening_key:
                recommendations = [
                    "Opponent plays Open Games - try aggressive Ruy Lopez or Italian",
                    "Focus on early piece development and central control",
                    "Look for tactics in the kingside after early castling"
                ]
            elif "c7c5" in opening_key or "c5" in opening_key:
                recommendations = [
                    "Sicilian Defense detected - prepare your main system",
                    "Study critical positions in your chosen variation",
                    "Exploit any sideline preferences"
                ]
            else:
                recommendations = [
                    "Flexible response to 1.e4 - study opponent's main systems",
                    "Prepare solid, well-tested defenses",
                    "Look for opportunities to transpose to favorable structures"
                ]
        elif "d2d4" in opening_key or "d4" in opening_key:
            recommendations = [
                "Opponent uses Queen's Gambit or Queen's pawn openings",
                "Consider closed game structures",
                "Study pawn break ideas (e.g., ...e5 or ...c5)"
            ]
        else:
            recommendations = [
                "Opponent uses flank or unusual openings",
                "Prepare solid, classical responses",
                "Focus on controlling the center early"
            ]
        
        return recommendations[0] if recommendations else "Study this opening further"
    
    def get_vulnerability_scorecard(self) -> Dict:
        """Assess opening phase vulnerabilities"""
        if not self.all_opening_moves:
            return {}
        
        # Analyze opening phase metrics
        early_moves_scores = []
        mid_opening_scores = []
        pattern_weaknesses = defaultdict(int)
        
        for opening in self.all_opening_moves:
            # Score first 6 moves (opening)
            early_key = " ".join(opening['uci'][:12]) if len(opening['uci']) >= 12 else " ".join(opening['uci'])
            
            if early_key in self.opening_tree:
                total = self.opening_tree[early_key]['count']
                wins = self.opening_tree[early_key]['wins']
                
                if total > 0:
                    win_rate = wins / total
                    early_moves_scores.append(win_rate)
                    
                    # Detect patterns
                    if "h6" in str(opening['moves_text']).lower():
                        pattern_weaknesses['Premature ...h6'] += 1
                    if opening['moves_text'].count('a6') > 1:
                        pattern_weaknesses['Overextension on queenside'] += 1
        
        # Calculate average scores
        avg_opening_score = sum(early_moves_scores) / len(early_moves_scores) if early_moves_scores else 0.5
        
        # Rate from 1-5
        opening_rating = int(avg_opening_score * 5)
        opening_rating = max(1, min(5, opening_rating))
        
        # Middlegame transition (games with 30+ moves)
        long_games = [g for g in self.all_opening_moves if len(g['uci']) > 20]
        transition_scores = []
        for game in long_games:
            if game['player_won'] is not None:
                transition_scores.append(1.0 if game['player_won'] else 0.0)
        
        avg_transition = sum(transition_scores) / len(transition_scores) if transition_scores else 0.5
        transition_rating = int(avg_transition * 5)
        transition_rating = max(1, min(5, transition_rating))
        
        return {
            'opening_phase_rating': opening_rating,
            'opening_phase_description': self._rate_text(opening_rating),
            'transition_rating': transition_rating,
            'transition_description': self._rate_text(transition_rating),
            'common_weaknesses': dict(sorted(pattern_weaknesses.items(), 
                                            key=lambda x: x[1], reverse=True)[:5]),
            'overall_vulnerability': (opening_rating + transition_rating) / 2
        }
    
    def _rate_text(self, rating: int) -> str:
        """Convert rating to descriptive text"""
        texts = {
            1: "Very Weak - Significant opportunities",
            2: "Weak - Multiple exploitable patterns",
            3: "Average - Some vulnerabilities",
            4: "Strong - Few weaknesses",
            5: "Very Strong - Solid opening play"
        }
        return texts.get(rating, "Average")


def display_opening_tree_analysis(games: List, username: str):
    """Display comprehensive opening repertoire analysis"""
    
    if not games:
        print("No games to analyze")
        return
    
    analyzer = OpeningTreeAnalyzer(games, username)
    
    print("\n" + "="*80)
    print(f"🎯 OPENING REPERTOIRE INSPECTOR - {username.upper()}")
    print(f"Games Analyzed: {len(games)} | Analysis Depth: Full Game Openings")
    print("="*80)
    
    # SECTION 1: OPENING REPERTOIRE MAP
    print("\n\n1️⃣  OPENING REPERTOIRE MAP")
    print("-"*80)
    print("Top openings played and their win rates:\n")
    
    repertoire = analyzer.get_repertoire_summary()
    
    for i, opening in enumerate(repertoire[:8], 1):
        moves_san = opening['moves_san'] if opening['moves_san'] else opening['opening']
        count = opening['count']
        percentage = (count / len(games) * 100)
        win_rate = opening['win_rate']
        your_wr = opening['your_win_rate']
        
        # Visual bars
        bar_length = int(percentage / 2)
        bar = "█" * bar_length + "░" * (25 - bar_length)
        
        print(f"  {i}. {moves_san[:60]}")
        print(f"     Frequency: {count} games ({percentage:.0f}%) {bar}")
        print(f"     Opponent win rate: {win_rate:.0f}% | Your win rate: {your_wr:.0f}%")
        print(f"     Avg opponent strength: {opening['avg_opponent_elo']} Elo\n")
    
    # SECTION 2: PATTERN LIBRARY
    print("\n2️⃣  PATTERN LIBRARY & CLUSTERING")
    print("-"*80)
    print("Similar position groupings:\n")
    
    analyzer._cluster_positions()
    clusters_sorted = sorted(analyzer.position_clusters.items(), 
                            key=lambda x: len(x[1]), reverse=True)[:5]
    
    for cluster_idx, (position_key, games_in_cluster) in enumerate(clusters_sorted, 1):
        moves_san = analyzer._uci_to_san(position_key.split()[:10])
        
        # Analyze patterns in this cluster
        move_choices = defaultdict(int)
        result_outcomes = {"wins": 0, "losses": 0, "draws": 0}
        
        for game in games_in_cluster:
            if len(game['uci']) > 10:
                next_move = game['uci'][10]
                move_choices[next_move] += 1
            
            if game['result'] == "1-0":
                if not game['player_won']:
                    result_outcomes['losses'] += 1
                else:
                    result_outcomes['wins'] += 1
            elif game['result'] == "0-1":
                if game['player_won']:
                    result_outcomes['losses'] += 1
                else:
                    result_outcomes['wins'] += 1
            else:
                result_outcomes['draws'] += 1
        
        consistency = max(move_choices.values()) / len(games_in_cluster) if move_choices else 0
        
        print(f"  GROUP {chr(64+cluster_idx)}: {moves_san[:50]}")
        print(f"  Frequency: {len(games_in_cluster)} games in cluster")
        print(f"  Consistency: {consistency*100:.0f}% play same next move")
        
        if result_outcomes['wins'] > 0 or result_outcomes['losses'] > 0:
            total_decisive = result_outcomes['wins'] + result_outcomes['losses']
            opponent_wr = result_outcomes['losses'] / total_decisive * 100 if total_decisive > 0 else 0
            print(f"  Your success rate: {(result_outcomes['wins'] / (total_decisive if total_decisive else 1) * 100):.0f}%")
        
        # Most common continuation
        if move_choices:
            most_common = sorted(move_choices.items(), key=lambda x: x[1], reverse=True)[0]
            print(f"  Preferred continuation: {most_common[0]} ({most_common[1]} times)")
        
        print()
    
    # SECTION 3: EXPLOITATION BLUEPRINT
    print("\n3️⃣  EXPLOITATION BLUEPRINT")
    print("-"*80)
    print("Identified weaknesses and recommended strategies:\n")
    
    blueprint = analyzer.get_exploitation_blueprint()
    
    if blueprint:
        for idx, weak_opening in enumerate(blueprint[:5], 1):
            moves = weak_opening['moves_san'] if weak_opening['moves_san'] else weak_opening['opening']
            wr = weak_opening['opponent_win_rate']
            your_wr = weak_opening['your_win_rate']
            weakness = weak_opening['weakness_level']
            
            weakness_emoji = "🔴" if weakness == "CRITICAL" else ("🟠" if weakness == "HIGH" else "🟡")
            
            print(f"  {weakness_emoji} WEAKNESS #{idx}: {weakness} Level")
            print(f"     Opening: {moves[:60]}")
            print(f"     Frequency: {weak_opening['frequency']} games")
            print(f"     Opponent performance: {wr:.0f}% win rate")
            print(f"     Your advantage: {100-wr:.0f}% (winning {your_wr:.0f}% of these)")
            print(f"     Recommendation: {weak_opening['recommendation']}")
            print()
    else:
        print("  ✓ No critical weaknesses detected - opponent plays balanced repertoire\n")
    
    # SECTION 4: VULNERABILITY SCORECARD
    print("\n4️⃣  VULNERABILITY SCORECARD")
    print("-"*80)
    
    scorecard = analyzer.get_vulnerability_scorecard()
    
    if scorecard:
        opening_rating = scorecard['opening_phase_rating']
        transition_rating = scorecard['transition_rating']
        overall = scorecard['overall_vulnerability']
        
        # Rating display
        rating_bar = lambda r: ("⭐" * r) + ("☆" * (5 - r))
        
        print(f"\n  Opening Phase (Moves 1-10): {rating_bar(opening_rating)} ({opening_rating}/5)")
        print(f"  → {scorecard['opening_phase_description']}")
        
        print(f"\n  Transition to Middlegame: {rating_bar(transition_rating)} ({transition_rating}/5)")
        print(f"  → {scorecard['transition_description']}")
        
        if scorecard['common_weaknesses']:
            print(f"\n  Common Weaknesses:")
            for weakness, count in list(scorecard['common_weaknesses'].items())[:3]:
                print(f"    • {weakness}: appears in {count} games")
        
        print(f"\n  Overall Opening Vulnerability: {rating_bar(int(overall))} ({overall:.1f}/5)")
    
    print("\n" + "="*80)
    print("💡 STRATEGIC INSIGHTS:")
    print("-"*80)
    
    # Generate insights
    insights = []
    
    if repertoire:
        most_played = repertoire[0]
        insights.append(f"• Most-played opening: {most_played['moves_san'][:50]}")
        if most_played['your_win_rate'] > 55:
            insights.append(f"  → You have {most_played['your_win_rate']:.0f}% win rate! Keep using this line.")
        elif most_played['your_win_rate'] < 40:
            insights.append(f"  → You're only scoring {most_played['your_win_rate']:.0f}%. Avoid or prepare deeper")
    
    if blueprint:
        worst = blueprint[0]
        insights.append(f"• Critical weakness: {worst['weakness_level']} in {worst['moves_san'][:40]}")
        insights.append(f"  → Attack this opening - your win rate is {worst['your_win_rate']:.0f}%")
    
    if scorecard and scorecard['opening_phase_rating'] <= 2:
        insights.append(f"• Opening phase is weak (⭐{scorecard['opening_phase_rating']}/5) - target early positions")
    
    if len(repertoire) > 4:
        insights.append(f"• Opponent plays diverse repertoire ({len(repertoire)} different openings)")
    else:
        insights.append(f"• Opponent is predictable - only {len(repertoire)} main openings")
    
    for insight in insights[:5]:
        print(insight)
    
    print("\n" + "="*80)
