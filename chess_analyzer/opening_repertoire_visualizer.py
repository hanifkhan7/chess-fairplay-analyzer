"""
Opening Repertoire Visualization Module
Generates X-Y graphs for statistical analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import numpy as np


class OpeningStatisticsVisualizer:
    """Generate statistical visualizations for opening analysis"""
    
    def __init__(self, analyzer):
        """
        Initialize visualizer
        
        Args:
            analyzer: OpeningRepertoireAnalyzer instance
        """
        self.analyzer = analyzer
        self.df = analyzer.get_opening_summary()
        
        # Set style
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (14, 6)
    
    def plot_win_loss_draw_rates(self, top_n: int = 10) -> None:
        """
        Bar chart: Win/Loss/Draw rates per opening
        
        Args:
            top_n: Show top N openings by frequency
        """
        df_top = self.df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        x = np.arange(len(df_top))
        width = 0.25
        
        ax.bar(x - width, df_top['Win_Rate_%'], width, label='Win %', color='#2ecc71')
        ax.bar(x, df_top['Draw_Rate_%'], width, label='Draw %', color='#f39c12')
        ax.bar(x + width, df_top['Loss_Rate_%'], width, label='Loss %', color='#e74c3c')
        
        ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'Opening Performance - Top {top_n} by Frequency', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels([opening[:30] for opening in df_top['Opening']], 
                           rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_white_vs_black_performance(self, top_n: int = 10) -> None:
        """
        Comparison chart: White vs Black performance for same opening
        
        Args:
            top_n: Show top N openings
        """
        df_top = self.df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Calculate White and Black win rates
        white_win_rates = []
        black_win_rates = []
        openings = []
        
        for _, row in df_top.iterrows():
            white_freq = row['White_Freq']
            black_freq = row['Black_Freq']
            
            white_wr = (row['White_Wins'] / white_freq * 100) if white_freq > 0 else 0
            black_wr = (row['Black_Wins'] / black_freq * 100) if black_freq > 0 else 0
            
            white_win_rates.append(white_wr)
            black_win_rates.append(black_wr)
            openings.append(row['Opening'][:30])
        
        x = np.arange(len(openings))
        width = 0.35
        
        ax.bar(x - width/2, white_win_rates, width, label='White Win %', color='#3498db')
        ax.bar(x + width/2, black_win_rates, width, label='Black Win %', color='#9b59b6')
        
        ax.set_ylabel('Win Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Color Comparison - Win Rates by Opening', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(openings, rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_opening_frequency(self, top_n: int = 15) -> None:
        """
        Frequency chart: Top N most played openings
        
        Args:
            top_n: Number of openings to display
        """
        df_top = self.df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = ['#2ecc71' if wr >= 55 else '#f39c12' if wr >= 45 else '#e74c3c' 
                  for wr in df_top['Win_Rate_%']]
        
        ax.barh(range(len(df_top)), df_top['Frequency'], color=colors)
        ax.set_yticks(range(len(df_top)))
        ax.set_yticklabels([opening[:40] for opening in df_top['Opening']], fontsize=9)
        ax.set_xlabel('Number of Games', fontsize=12, fontweight='bold')
        ax.set_title(f'Most Played Openings - Top {top_n}', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (freq, wr) in enumerate(zip(df_top['Frequency'], df_top['Win_Rate_%'])):
            ax.text(freq + 0.5, i, f'{int(freq)} ({wr:.0f}%)', 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def plot_performance_vs_move_number(self) -> None:
        """
        Performance trend: Win rate vs game length (opening phase)
        """
        # Categorize games by length
        bins = [15, 20, 25, 30, 40, 50, 100]
        categories = ['15-20', '20-25', '25-30', '30-40', '40-50', '50+']
        
        win_rates = []
        frequencies = []
        
        for i in range(len(bins) - 1):
            games_in_range = [
                g for g in self.analyzer.filtered_games 
                if bins[i] <= g[3] < bins[i+1]
            ]
            
            if games_in_range:
                wins = sum(1 for g in games_in_range if g[2] == 'win')
                freq = len(games_in_range)
                win_rates.append(wins / freq * 100)
                frequencies.append(freq)
            else:
                win_rates.append(0)
                frequencies.append(0)
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Win rate line
        ax1.plot(categories, win_rates, marker='o', linewidth=2, 
                markersize=8, color='#3498db', label='Win Rate')
        ax1.set_ylabel('Win Rate (%)', fontsize=12, fontweight='bold', color='#3498db')
        ax1.set_ylim(0, 100)
        ax1.tick_params(axis='y', labelcolor='#3498db')
        ax1.grid(axis='y', alpha=0.3)
        
        # Frequency bar (secondary axis)
        ax2 = ax1.twinx()
        ax2.bar(categories, frequencies, alpha=0.3, color='#95a5a6', label='Game Count')
        ax2.set_ylabel('Number of Games', fontsize=12, fontweight='bold', color='#95a5a6')
        ax2.tick_params(axis='y', labelcolor='#95a5a6')
        
        ax1.set_xlabel('Move Range (Game Length)', fontsize=12, fontweight='bold')
        ax1.set_title('Performance vs Game Length (Opening Phase)', 
                      fontsize=14, fontweight='bold', pad=20)
        
        fig.legend(['Win Rate', 'Game Count'], loc='upper right', bbox_to_anchor=(0.99, 0.99))
        
        plt.tight_layout()
        return fig
    
    def plot_opening_distribution_pie(self, top_n: int = 10) -> None:
        """
        Pie chart: Distribution of top openings
        
        Args:
            top_n: Top N openings to show
        """
        df_top = self.df.head(top_n)
        other_freq = self.df[top_n:]['Frequency'].sum()
        
        data = df_top['Frequency'].tolist()
        labels = [opening[:25] for opening in df_top['Opening'].tolist()]
        
        if other_freq > 0:
            data.append(other_freq)
            labels.append(f'Other ({len(self.df) - top_n} openings)')
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
        
        wedges, texts, autotexts = ax.pie(data, labels=labels, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Opening Distribution', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def save_all_plots(self, output_dir: str = 'reports') -> bool:
        """
        Generate and save all visualizations
        
        Args:
            output_dir: Directory to save plots
        
        Returns:
            True if successful
        """
        import os
        from datetime import datetime
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        player_name = self.analyzer.player_name.replace(' ', '_')
        
        plots = [
            ('win_loss_draw', self.plot_win_loss_draw_rates()),
            ('white_vs_black', self.plot_white_vs_black_performance()),
            ('frequency', self.plot_opening_frequency()),
            ('performance_vs_length', self.plot_performance_vs_move_number()),
            ('distribution', self.plot_opening_distribution_pie())
        ]
        
        try:
            for plot_name, fig in plots:
                filename = f"{output_dir}/{player_name}_{plot_name}_{timestamp}.png"
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"[OK] Saved: {filename}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save plots: {e}")
            return False
    
    def display_all_plots(self) -> None:
        """Display all plots interactively"""
        plots = [
            ('Win/Loss/Draw Rates', self.plot_win_loss_draw_rates()),
            ('White vs Black Performance', self.plot_white_vs_black_performance()),
            ('Opening Frequency', self.plot_opening_frequency()),
            ('Performance vs Game Length', self.plot_performance_vs_move_number()),
            ('Opening Distribution', self.plot_opening_distribution_pie())
        ]
        
        for name, fig in plots:
            print(f"\nDisplaying: {name}")
            plt.show()


class OpeningTreeVisualizer:
    """Visualize opening trees using matplotlib"""
    
    @staticmethod
    def plot_tree_network(analyzer, color: str = 'white', max_depth: int = 4):
        """
        Visualize opening tree as network graph
        
        Args:
            analyzer: OpeningRepertoireAnalyzer instance
            color: 'white' or 'black'
            max_depth: Maximum depth to visualize
        """
        try:
            import networkx as nx
        except ImportError:
            print("[WARN] networkx not installed. Install with: pip install networkx")
            return None
        
        tree = analyzer.white_tree if color == 'white' else analyzer.black_tree
        
        G = nx.DiGraph()
        pos = {}
        
        def build_graph(node, parent=None, depth=0, x=0, y=0, layer_width=1):
            if depth > max_depth:
                return
            
            node_id = f"{node.move}_{depth}_{x}"
            G.add_node(node_id, label=node.move, freq=node.frequency, win_rate=node.win_rate())
            
            if parent:
                G.add_edge(parent, node_id)
            
            pos[node_id] = (x, -depth)
            
            children = list(node.children.values())
            if children:
                start_x = x - (len(children) - 1) * layer_width / 2
                for i, child in enumerate(children):
                    child_x = start_x + i * layer_width
                    build_graph(child, node_id, depth + 1, child_x, y - 1, layer_width / 2)
        
        build_graph(tree)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Node colors based on win rate
        node_colors = []
        for node_id in G.nodes():
            win_rate = G.nodes[node_id]['win_rate']
            if win_rate >= 60:
                node_colors.append('#2ecc71')  # Green
            elif win_rate >= 45:
                node_colors.append('#f39c12')  # Yellow
            else:
                node_colors.append('#e74c3c')  # Red
        
        # Node sizes based on frequency
        node_sizes = [max(300, G.nodes[node_id]['freq'] * 50) for node_id in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, ax=ax)
        nx.draw_networkx_labels(G, pos, {node_id: G.nodes[node_id]['label'] 
                                         for node_id in G.nodes()}, ax=ax)
        
        ax.set_title(f'Opening Tree Network - {color.upper()}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        return fig
