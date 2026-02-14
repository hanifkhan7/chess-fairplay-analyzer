"""
Visualization Utilities for Reports.

Provides data structures and helpers for generating:
- Radar/Spider charts (skill profiles)
- Bar charts (metrics, comparisons)
- Line charts (trends, changes over time)
- Heatmaps (phase-by-move analysis)
- Network graphs (player relationships)
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import json

@dataclass
class ChartData:
    """Generic chart data structure."""
    chart_type: str  # 'bar', 'line', 'radar', 'heatmap', 'scatter', 'pie'
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Dict[str, Any] = None

class VisualizationHelper:
    """Generate visualization data for reports."""
    
    @staticmethod
    def create_radar_chart(skill_profile: Any) -> ChartData:
        """
        Create radar/spider chart for skill profile.
        
        Shows 6 dimensions: Opening, Tactics, Endgame, Strategy, Time Mgmt, Consistency
        """
        skills = skill_profile.compute_radar_data()
        
        return ChartData(
            chart_type='radar',
            title='Multi-Dimensional Skill Profile',
            labels=list(skills.keys()),
            datasets=[
                {
                    'label': skill_profile.username,
                    'data': list(skills.values()),
                    'borderColor': '#3498db',
                    'backgroundColor': 'rgba(52, 152, 219, 0.2)',
                    'borderWidth': 2,
                    'fill': True
                }
            ],
            options={
                'scale': {
                    'min': 0,
                    'max': 100,
                    'ticks': {'stepSize': 20}
                },
                'plugins': {
                    'legend': {'display': True},
                    'tooltip': {'enabled': True}
                }
            }
        )
    
    @staticmethod
    def create_metrics_bar_chart(suspicion_score: Any) -> ChartData:
        """Create bar chart of individual metrics."""
        
        metrics = suspicion_score.individual_metrics
        labels = [m.metric_name for m in metrics]
        values = [m.percentile for m in metrics]
        colors = ['#e74c3c' if m.is_flagged else '#27ae60' for m in metrics]
        
        return ChartData(
            chart_type='bar',
            title='Metric Assessment Breakdown',
            labels=labels,
            datasets=[
                {
                    'label': 'Suspicion Percentile',
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': '#333',
                    'borderWidth': 1
                }
            ],
            options={
                'indexAxis': 'y',
                'scales': {
                    'x': {'min': 0, 'max': 100}
                },
                'plugins': {
                    'legend': {'display': False}
                }
            }
        )
    
    @staticmethod
    def create_accuracy_trend_chart(games: List[Dict[str, Any]]) -> ChartData:
        """Create line chart of accuracy over games."""
        
        accuracies = []
        game_numbers = []
        
        for i, game in enumerate(games):
            if 'accuracy' in game:
                accuracies.append(game['accuracy'])
                game_numbers.append(i + 1)
        
        if not accuracies:
            return ChartData(
                chart_type='line',
                title='Accuracy Trend',
                labels=game_numbers,
                datasets=[],
                options={}
            )
        
        # Calculate moving average
        window = 3
        moving_avg = []
        for i in range(len(accuracies)):
            start = max(0, i - window + 1)
            avg = sum(accuracies[start:i+1]) / (i - start + 1)
            moving_avg.append(round(avg, 1))
        
        return ChartData(
            chart_type='line',
            title='Accuracy Trend Across Games',
            labels=game_numbers,
            datasets=[
                {
                    'label': 'Accuracy',
                    'data': accuracies,
                    'borderColor': '#3498db',
                    'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                    'borderWidth': 1,
                    'pointRadius': 3,
                    'fill': False
                },
                {
                    'label': f'{window}-Game Moving Average',
                    'data': moving_avg,
                    'borderColor': '#e74c3c',
                    'borderWidth': 2,
                    'fill': False,
                    'pointRadius': 0,
                    'borderDash': [5, 5]
                }
            ],
            options={
                'scales': {
                    'y': {'min': 0, 'max': 100}
                },
                'plugins': {
                    'legend': {'display': True},
                    'tooltip': {'enabled': True}
                }
            }
        )
    
    @staticmethod
    def create_cpl_distribution_chart(games: List[Dict[str, Any]],
                                     benchmark_cpl: float) -> ChartData:
        """Create histogram of centipawn loss distribution."""
        
        cpls = [g.get('cpl', 50) for g in games if 'cpl' in g]
        if not cpls:
            return ChartData(
                chart_type='bar',
                title='Centipawn Loss Distribution',
                labels=[],
                datasets=[],
                options={}
            )
        
        # Create bins
        bins = [0, 10, 20, 30, 40, 50, 75, 100, 150, 200]
        bin_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-75', '75-100', '100-150', '150+']
        bin_counts = [0] * len(bins)
        
        for cpl in cpls:
            for i, threshold in enumerate(bins[1:]):
                if cpl < threshold:
                    bin_counts[i] += 1
                    break
            else:
                bin_counts[-1] += 1
        
        return ChartData(
            chart_type='bar',
            title='Centipawn Loss Distribution',
            labels=bin_labels,
            datasets=[
                {
                    'label': 'Move Count',
                    'data': bin_counts,
                    'backgroundColor': '#3498db',
                    'borderColor': '#333',
                    'borderWidth': 1
                }
            ],
            options={
                'scales': {
                    'y': {'title': {'display': True, 'text': 'Number of Moves'}}
                },
                'plugins': {
                    'legend': {'display': False},
                    'annotation': {
                        'annotations': {
                            'benchmark': {
                                'type': 'line',
                                'xMin': benchmark_cpl,
                                'xMax': benchmark_cpl,
                                'borderColor': '#e74c3c',
                                'borderWidth': 2,
                                'label': {'content': ['Benchmark'], 'display': True}
                            }
                        }
                    }
                }
            }
        )
    
    @staticmethod
    def create_phase_accuracy_chart(strength_profile: Any) -> ChartData:
        """Create bar chart comparing accuracy by phase."""
        
        if not strength_profile.phase_analysis:
            return ChartData(
                chart_type='bar',
                title='Phase Accuracy (No Data)',
                labels=[],
                datasets=[],
                options={}
            )
        
        phases = strength_profile.phase_analysis
        
        return ChartData(
            chart_type='bar',
            title='Accuracy by Game Phase',
            labels=['Opening', 'Middlegame', 'Endgame'],
            datasets=[
                {
                    'label': 'Accuracy %',
                    'data': [
                        phases.opening_accuracy,
                        phases.middlegame_accuracy,
                        phases.endgame_accuracy
                    ],
                    'backgroundColor': ['#3498db', '#2ecc71', '#f39c12'],
                    'borderColor': '#333',
                    'borderWidth': 1
                }
            ],
            options={
                'scales': {
                    'y': {'min': 0, 'max': 100}
                },
                'plugins': {
                    'legend': {'display': False}
                }
            }
        )
    
    @staticmethod
    def create_opening_performance_chart(opponent_profile: Any) -> ChartData:
        """Create chart of opponent's opening performance."""
        
        if not opponent_profile.opening_performances:
            return ChartData(
                chart_type='bar',
                title='Opening Performance (No Data)',
                labels=[],
                datasets=[],
                options={}
            )
        
        # Get top 10 openings
        openings = sorted(
            opponent_profile.opening_performances,
            key=lambda x: x.times_played,
            reverse=True
        )[:10]
        
        return ChartData(
            chart_type='bar',
            title=f'Top Openings - {opponent_profile.username}',
            labels=[op.opening_name for op in openings],
            datasets=[
                {
                    'label': 'Win %',
                    'data': [op.win_rate for op in openings],
                    'backgroundColor': '#2ecc71',
                    'borderWidth': 1
                },
                {
                    'label': 'Draw %',
                    'data': [op.draw_rate for op in openings],
                    'backgroundColor': '#95a5a6',
                    'borderWidth': 1
                },
                {
                    'label': 'Loss %',
                    'data': [op.loss_rate for op in openings],
                    'backgroundColor': '#e74c3c',
                    'borderWidth': 1
                }
            ],
            options={
                'scales': {
                    'x': {'stacked': True},
                    'y': {'stacked': True, 'min': 0, 'max': 100}
                },
                'plugins': {
                    'legend': {'display': True}
                }
            }
        )
    
    @staticmethod
    def create_time_of_day_heatmap(time_distribution: Dict[str, float]) -> ChartData:
        """Create heatmap of performance by time of day."""
        
        hours = sorted(time_distribution.keys())
        values = [time_distribution[h] for h in hours]
        
        # Normalize to 0-100 for color intensity
        min_val = min(values) if values else 0
        max_val = max(values) if values else 100
        range_val = max_val - min_val or 1
        
        normalized = [(v - min_val) / range_val * 100 for v in values]
        
        # Determine colors based on value
        colors = []
        for norm in normalized:
            if norm > 70:
                colors.append('#27ae60')  # Green - strong
            elif norm > 50:
                colors.append('#f39c12')  # Orange - average
            else:
                colors.append('#e74c3c')  # Red - weak
        
        return ChartData(
            chart_type='bar',
            title='Performance by Time of Day',
            labels=hours,
            datasets=[
                {
                    'label': 'Accuracy %',
                    'data': values,
                    'backgroundColor': colors,
                    'borderColor': '#333',
                    'borderWidth': 1
                }
            ],
            options={
                'scales': {
                    'y': {'min': 0, 'max': 100, 'title': {'display': True, 'text': 'Accuracy %'}}
                },
                'plugins': {
                    'legend': {'display': False}
                }
            }
        )
    
    @staticmethod
    def create_network_visualization_config(network_analysis: Any) -> Dict[str, Any]:
        """Create configuration for D3.js network visualization."""
        
        from .network_analyzer import create_network_visualization_data
        
        vis_data = create_network_visualization_data(network_analysis)
        
        return {
            'type': 'force-directed-graph',
            'title': 'Player Network & Connections',
            'nodes': vis_data['nodes'],
            'links': vis_data['links'],
            'config': {
                'nodeSize': 'size',
                'nodeColor': 'group',
                'linkColor': '#999',
                'linkDistance': 30,
                'chargeStrength': -300,
                'collision': True,
                'forces': {
                    'center': 0.5,
                    'charge': 0.8,
                    'collision': 0.7
                }
            },
            'colorScheme': {
                'normal': '#3498db',
                'suspicious': '#e74c3c',
                'colluding': '#8e44ad'
            }
        }
    
    @staticmethod
    def export_chart_to_json(chart: ChartData) -> str:
        """Export chart data as JSON for client-side rendering."""
        return json.dumps(asdict(chart), default=str)

# Helper for creating HTML chart placeholders with data attributes
def create_chart_html(chart_data: ChartData, container_id: str = None) -> str:
    """Generate HTML div with chart data as JSON attribute."""
    cid = container_id or chart_data.title.lower().replace(' ', '-')
    data_json = json.dumps(asdict(chart_data), default=str)
    
    return f'''
    <div class="chart-container" id="{cid}" data-chart-type="{chart_data.chart_type}" 
         data-chart-data='{data_json}'>
        <div class="chart-placeholder">
            <h3>{chart_data.title}</h3>
            <p>Chart will render here (requires Chart.js or similar library)</p>
        </div>
    </div>
    '''
