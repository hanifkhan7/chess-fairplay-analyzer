"""
Visual Dashboard for Chess Detective v2.2
Matplotlib/Plotly integration for charts and graphs.
"""

from typing import List, Dict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import statistics


class VisualDashboard:
    """Create visual charts and dashboards for player analysis."""
    
    def __init__(self, username: str, games: List, analysis_data: Dict = None):
        """
        Initialize visual dashboard.
        
        Args:
            username: Player username
            games: List of chess games
            analysis_data: Pre-computed analysis data (optional)
        """
        self.username = username
        self.games = games
        self.analysis_data = analysis_data or {}
        self.figure_count = 0
    
    def create_rating_trend_chart(self) -> plt.Figure:
        """Create rating progression chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ratings = []
        for game in self.games:
            headers = game.headers
            white = headers.get("White", "").lower()
            black = headers.get("Black", "").lower()
            is_player_white = white == self.username.lower()
            
            player_elo = headers.get("WhiteElo" if is_player_white else "BlackElo")
            try:
                if player_elo:
                    ratings.append(int(player_elo))
            except:
                pass
        
        if ratings:
            ax.plot(range(len(ratings)), ratings, linewidth=2, marker='o', markersize=4, color='#1f77b4')
            ax.fill_between(range(len(ratings)), ratings, alpha=0.3, color='#1f77b4')
            ax.set_xlabel('Game Number')
            ax.set_ylabel('Rating')
            ax.set_title(f'Rating Progression - {self.username}')
            ax.grid(True, alpha=0.3)
            
            # Add trend line
            if len(ratings) > 1:
                z = statistics.linear_regression([(i, r) for i, r in enumerate(ratings)])[0:2]
                p = [z[0] * i + z[1] for i in range(len(ratings))]
                ax.plot(range(len(ratings)), p, '--', color='red', alpha=0.7, label='Trend')
                ax.legend()
        
        return fig
    
    def create_winrate_chart(self) -> plt.Figure:
        """Create win rate pie chart."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        wins = draws = losses = 0
        
        for game in self.games:
            result = game.headers.get('Result', '*')
            headers = game.headers
            white = headers.get("White", "").lower()
            black = headers.get("Black", "").lower()
            is_player_white = white == self.username.lower()
            
            if result == '1-0':
                if is_player_white:
                    wins += 1
                else:
                    losses += 1
            elif result == '0-1':
                if is_player_white:
                    losses += 1
                else:
                    wins += 1
            else:
                draws += 1
        
        sizes = [wins, draws, losses]
        labels = [f'Wins ({wins})', f'Draws ({draws})', f'Losses ({losses})']
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title(f'Game Results - {self.username}')
        
        return fig
    
    def create_opening_distribution_chart(self) -> plt.Figure:
        """Create opening variety distribution chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        openings = {}
        for game in self.games:
            headers = game.headers
            eco = headers.get('ECO', 'Unknown')
            opening = headers.get('Opening', 'Unknown')
            
            if eco != 'Unknown' and opening != 'Unknown':
                opening_key = f"{eco}"
            elif eco != 'Unknown':
                opening_key = eco
            else:
                opening_key = opening
            
            openings[opening_key] = openings.get(opening_key, 0) + 1
        
        if openings:
            # Get top 10 openings
            top_openings = sorted(openings.items(), key=lambda x: x[1], reverse=True)[:10]
            names = [o[0] for o in top_openings]
            counts = [o[1] for o in top_openings]
            
            bars = ax.bar(range(len(names)), counts, color='#3498db')
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.set_ylabel('Games')
            ax.set_title(f'Top 10 Openings - {self.username}')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def create_performance_by_timecontrol(self) -> plt.Figure:
        """Create performance breakdown by time control."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        time_controls = {}
        for game in self.games:
            headers = game.headers
            tc = headers.get('TimeControl', 'Unknown')
            result = headers.get('Result', '*')
            white = headers.get("White", "").lower()
            black = headers.get("Black", "").lower()
            is_player_white = white == self.username.lower()
            
            if tc not in time_controls:
                time_controls[tc] = {'wins': 0, 'draws': 0, 'losses': 0}
            
            if result == '1-0':
                if is_player_white:
                    time_controls[tc]['wins'] += 1
                else:
                    time_controls[tc]['losses'] += 1
            elif result == '0-1':
                if is_player_white:
                    time_controls[tc]['losses'] += 1
                else:
                    time_controls[tc]['wins'] += 1
            else:
                time_controls[tc]['draws'] += 1
        
        if time_controls:
            tcs = list(time_controls.keys())
            wins = [time_controls[tc]['wins'] for tc in tcs]
            draws = [time_controls[tc]['draws'] for tc in tcs]
            losses = [time_controls[tc]['losses'] for tc in tcs]
            
            x = range(len(tcs))
            width = 0.25
            
            ax.bar([i - width for i in x], wins, width, label='Wins', color='#2ecc71')
            ax.bar(x, draws, width, label='Draws', color='#f39c12')
            ax.bar([i + width for i in x], losses, width, label='Losses', color='#e74c3c')
            
            ax.set_ylabel('Games')
            ax.set_title(f'Performance by Time Control - {self.username}')
            ax.set_xticks(x)
            ax.set_xticklabels(tcs)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig
    
    def show_all_charts(self):
        """Display all charts."""
        try:
            fig1 = self.create_rating_trend_chart()
            fig2 = self.create_winrate_chart()
            fig3 = self.create_opening_distribution_chart()
            fig4 = self.create_performance_by_timecontrol()
            
            plt.show()
            
        except Exception as e:
            print(f"Error creating charts: {e}")
    
    def save_all_charts(self, output_dir: str = "reports"):
        """Save all charts to files."""
        try:
            figs = [
                (self.create_rating_trend_chart(), f"{output_dir}/chart_rating_trend.png"),
                (self.create_winrate_chart(), f"{output_dir}/chart_winrate.png"),
                (self.create_opening_distribution_chart(), f"{output_dir}/chart_openings.png"),
                (self.create_performance_by_timecontrol(), f"{output_dir}/chart_performance_tc.png"),
            ]
            
            for fig, path in figs:
                fig.savefig(path, dpi=300, bbox_inches='tight')
                print(f"✓ Saved: {path}")
            
            print(f"\n✓ All charts saved to {output_dir}/")
            
        except Exception as e:
            print(f"Error saving charts: {e}")


def display_visual_dashboard(games, username: str, save_to_file: bool = True):
    """
    Display visual dashboard.
    
    Args:
        games: List of chess games
        username: Player username
        save_to_file: Whether to save charts to file or display
    """
    print("\n" + "="*80)
    print(f"  VISUAL DASHBOARD - {username.upper()}")
    print("="*80 + "\n")
    
    dashboard = VisualDashboard(username, games)
    
    if save_to_file:
        print("Generating charts...")
        dashboard.save_all_charts()
    else:
        print("Displaying charts (close windows to continue)...")
        dashboard.show_all_charts()
    
    print("\n" + "="*80 + "\n")
