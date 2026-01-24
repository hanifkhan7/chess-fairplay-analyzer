"""
Professional report generation for all analysis features.
Generates HTML reports for each feature with modern styling and comprehensive data visualization.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)


class FeatureReporter:
    """Generate professional HTML reports for all analysis features."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize feature reporter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"FeatureReporter initialized with output directory: {output_dir}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _get_html_header(self, title: str, subtitle: str = "") -> str:
        """Get HTML report header with styling."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            border-left: 4px solid #667eea;
            padding-left: 20px;
        }}
        
        .section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .section h3 {{
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        th {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            transition: width 0.3s;
        }}
        
        .insight {{
            background: #e8f4f8;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        
        .insight strong {{
            color: #2c3e50;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
            font-size: 0.9em;
        }}
        
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>♟️ {title}</h1>
            <p>{subtitle}</p>
            <p style="font-size: 0.9em; margin-top: 15px;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        <div class="content">
"""
    
    def _get_html_footer(self) -> str:
        """Get HTML report footer."""
        return """        </div>
        <footer>
            <p>♟️ Chess Fairplay Analyzer v3.2 | Professional Fair-Play Detection & Analysis</p>
            <p style="margin-top: 10px;">⚠️ DISCLAIMER: This report provides statistical indicators only, not proof of cheating.</p>
            <p>Final judgment always rests with Chess.com/Lichess Fair Play teams and relevant authorities.</p>
        </footer>
    </div>
</body>
</html>
"""
    
    def generate_analyze_player_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate comprehensive player analysis report."""
        html = self._get_html_header(
            f"Player Analysis Report: {username}",
            "Forensic Detection & Fair-Play Analysis"
        )
        
        # Safely extract summary data
        summary = analysis_data.get('summary', {}) if isinstance(analysis_data.get('summary'), dict) else {}
        games_analyzed = int(summary.get('games_analyzed', 0) or 0)
        suspicion_score = float(summary.get('suspicion_score', 0) or 0)
        risk_level = str(summary.get('risk_level', 'LOW RISK'))
        
        # Risk color coding
        risk_color = {
            'LOW RISK': '#27ae60',
            'MEDIUM RISK': '#f39c12',
            'HIGH RISK': '#e74c3c'
        }.get(risk_level, '#666')
        
        suspicious_games = int(summary.get('suspicious_games', 0) or 0)
        avg_engine_rate = float(summary.get('avg_engine_match_rate', 0) or 0)
        avg_cpl = float(summary.get('avg_centipawn_loss', 0) or 0)
        avg_accuracy = float(summary.get('avg_accuracy', 0) or 0)
        avg_blunder_rate = float(summary.get('avg_blunder_rate', 0) or 0)
        win_rate = float(summary.get('win_rate', 0) or 0)
        
        html += f"""
        <section class="section">
            <h2>📊 Executive Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Suspicion Score</div>
                    <div class="metric-value" style="color: {risk_color};">{suspicion_score:.1f}/100</div>
                    <div class="badge" style="background: {risk_color}20; color: {risk_color};">{risk_level}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Games Analyzed</div>
                    <div class="metric-value">{games_analyzed}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Suspicious Games</div>
                    <div class="metric-value">{suspicious_games}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Engine Correlation</div>
                    <div class="metric-value">{avg_engine_rate:.1f}%</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎯 Key Metrics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Average Centipawn Loss (CPL)</td>
                        <td>{avg_cpl:.1f}</td>
                        <td><span class="badge badge-info">Evaluation</span></td>
                    </tr>
                    <tr>
                        <td>Average Accuracy</td>
                        <td>{avg_accuracy:.1f}%</td>
                        <td><span class="badge badge-info">Consistency</span></td>
                    </tr>
                    <tr>
                        <td>Blunder Rate</td>
                        <td>{avg_blunder_rate:.1f}%</td>
                        <td><span class="badge badge-warning">Attention</span></td>
                    </tr>
                    <tr>
                        <td>Win Rate</td>
                        <td>{win_rate:.1f}%</td>
                        <td><span class="badge badge-success">Performance</span></td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>📈 Analysis Details</h2>
            <div class="insight">
                <strong>Platform Breakdown:</strong><br>
                {str(summary.get('platform_breakdown', 'N/A'))}
            </div>
            <div class="insight">
                <strong>Analysis Settings:</strong><br>
                Time Control: {str(summary.get('analysis_settings', {}).get('time_control', 'N/A'))}<br>
                Engine Depth: {str(summary.get('analysis_settings', {}).get('depth', 'N/A'))}<br>
                Analysis Mode: {str(summary.get('analysis_settings', {}).get('mode', 'N/A'))}
            </div>
        </section>
        
        <section class="section">
            <h2>✅ Recommendations</h2>
            <ul style="margin-left: 20px;">
                {self._get_risk_recommendations(risk_level)}
            </ul>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_exploit_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate opening & style analysis report."""
        html = self._get_html_header(
            f"Opening & Style Analysis: {username}",
            "Strategic Weaknesses & Opportunity Analysis"
        )
        
        # Safely extract data
        openings = analysis_data.get('openings', {})
        if not isinstance(openings, dict):
            openings = {}
        
        weaknesses = analysis_data.get('weaknesses', [])
        if not isinstance(weaknesses, list):
            weaknesses = []
        
        strengths = analysis_data.get('strengths', [])
        if not isinstance(strengths, list):
            strengths = []
        
        html += """
        <section class="section">
            <h2>🎯 Favorite Openings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Opening Name</th>
                        <th>Frequency</th>
                        <th>Win Rate</th>
                        <th>Avg Elo</th>
                    </tr>
                </thead>
                <tbody>
"""
        if openings:
            for opening, data in list(openings.items())[:10]:
                if isinstance(data, dict):
                    freq = int(data.get('frequency', 0) or 0)
                    wr = float(data.get('win_rate', 0) or 0)
                    elo = int(data.get('avg_elo', 0) or 0)
                    html += f"""
                    <tr>
                        <td>{opening}</td>
                        <td>{freq} games</td>
                        <td><strong>{wr:.1f}%</strong></td>
                        <td>{elo}</td>
                    </tr>
"""
        else:
            html += '<tr><td colspan="4">No opening data available</td></tr>'
        
        html += """
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>💪 Playing Strengths</h2>
"""
        if strengths:
            for strength in strengths[:5]:
                if isinstance(strength, dict):
                    area = str(strength.get('area', 'N/A'))
                    desc = str(strength.get('description', 'N/A'))
                    html += f"""
            <div class="insight">
                <strong>✓ {area}</strong><br>
                {desc}
            </div>
"""
        else:
            html += '<p>No strength data available</p>'
        
        html += """
        </section>
        
        <section class="section">
            <h2>⚠️ Exploitable Weaknesses</h2>
"""
        if weaknesses:
            for weakness in weaknesses[:5]:
                if isinstance(weakness, dict):
                    area = str(weakness.get('area', 'N/A'))
                    desc = str(weakness.get('description', 'N/A'))
                    counter = str(weakness.get('counter', 'N/A'))
                    html += f"""
            <div class="insight" style="background: #fef5f5; border-left-color: #e74c3c;">
                <strong>✗ {area}</strong><br>
                {desc}<br>
                <em style="color: #e74c3c;">Counter Strategy: {counter}</em>
            </div>
"""
        else:
            html += '<p>No weakness data available</p>'
        
        html += """
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_strength_profile_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate skill level analysis report."""
        html = self._get_html_header(
            f"Strength Profile: {username}",
            "Detailed Skill Level & Performance Analysis"
        )
        
        # Safely extract profile data
        profile = analysis_data.get('profile', {}) if isinstance(analysis_data.get('profile'), dict) else {}
        
        # Get current and peak elo with defaults
        current_elo = profile.get('current_elo', 0) or 0
        peak_elo = profile.get('peak_elo', 0) or 0
        skill_level = profile.get('skill_level', 'Intermediate')
        primary_tc = profile.get('primary_tc', 'Rapid')
        
        # Handle different data structures for by_time_control
        by_tc = profile.get('by_time_control', {})
        if not isinstance(by_tc, dict):
            by_tc = {}
        
        html += f"""
        <section class="section">
            <h2>📊 Overall Rating</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Current Elo</div>
                    <div class="metric-value">{int(current_elo)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Peak Elo</div>
                    <div class="metric-value">{int(peak_elo)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Skill Level</div>
                    <div class="metric-value" style="font-size: 1.4em;">{str(skill_level)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Primary Format</div>
                    <div class="metric-value" style="font-size: 1.4em;">{str(primary_tc)}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎮 Performance by Time Control</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time Control</th>
                        <th>Games</th>
                        <th>Win Rate</th>
                        <th>Avg Rating</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
"""
        if by_tc:
            for tc, data in by_tc.items():
                if isinstance(data, dict):
                    games = data.get('games', 0) or 0
                    win_rate = data.get('win_rate', 0) or 0
                    avg_elo = data.get('avg_elo', 0) or 0
                    trend = data.get('trend', 0) or 0
                    trend_symbol = "📈" if trend > 0 else "📉" if trend < 0 else "→"
                    html += f"""
                    <tr>
                        <td>{tc}</td>
                        <td>{int(games)}</td>
                        <td>{float(win_rate):.1f}%</td>
                        <td>{int(avg_elo)}</td>
                        <td>{trend_symbol} {abs(int(trend))}</td>
                    </tr>
"""
        else:
            html += """
                    <tr>
                        <td colspan="5">No time control data available</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_accuracy_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate move accuracy and consistency report."""
        html = self._get_html_header(
            f"Accuracy Report: {username}",
            "Move Accuracy & Consistency Analysis"
        )
        
        # Safely extract metrics
        metrics = analysis_data.get('metrics', {})
        if not isinstance(metrics, dict):
            metrics = {}
        
        overall_acc = float(metrics.get('overall_accuracy', 0) or 0)
        avg_cpl = float(metrics.get('avg_cpl', 0) or 0)
        best_cpl = float(metrics.get('best_cpl', 0) or 0)
        worst_cpl = float(metrics.get('worst_cpl', 0) or 0)
        recent_avg = float(metrics.get('recent_avg', 0) or 0)
        previous_avg = float(metrics.get('previous_avg', 0) or 0)
        trend = float(metrics.get('trend', 0) or 0)
        
        html += f"""
        <section class="section">
            <h2>📊 Accuracy Metrics</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Overall Accuracy</div>
                    <div class="metric-value">{overall_acc:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {overall_acc:.0f}%"></div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Centipawn Loss</div>
                    <div class="metric-value">{avg_cpl:.1f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Best Game CPL</div>
                    <div class="metric-value">{best_cpl:.1f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Worst Game CPL</div>
                    <div class="metric-value">{worst_cpl:.1f}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎯 Consistency Analysis</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time Control</th>
                        <th>Accuracy</th>
                        <th>Consistency</th>
                        <th>CPL Range</th>
                    </tr>
                </thead>
                <tbody>
"""
        by_tc = metrics.get('by_time_control', {})
        if isinstance(by_tc, dict) and by_tc:
            for tc, data in by_tc.items():
                if isinstance(data, dict):
                    acc = float(data.get('accuracy', 0) or 0)
                    consistency = float(data.get('consistency', 0) or 0)
                    cpl_min = float(data.get('cpl_min', 0) or 0)
                    cpl_max = float(data.get('cpl_max', 0) or 0)
                    html += f"""
                    <tr>
                        <td>{tc}</td>
                        <td>{acc:.1f}%</td>
                        <td>{consistency:.1f}%</td>
                        <td>{cpl_min:.0f} - {cpl_max:.0f}</td>
                    </tr>
"""
        else:
            html += '<tr><td colspan="4">No time control breakdown available</td></tr>'
        
        html += f"""
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>📈 Accuracy Trend</h2>
            <div class="insight">
                <strong>Latest 10 Games Average:</strong> {recent_avg:.1f}% accuracy<br>
                <strong>Previous 10 Games Average:</strong> {previous_avg:.1f}% accuracy<br>
                <strong>Trend:</strong> {'Improving' if trend > 0 else 'Declining' if trend < 0 else 'Stable'}
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_account_metrics_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate account metrics dashboard report."""
        html = self._get_html_header(
            f"Account Metrics: {username}",
            "Quick Overview & Key Statistics"
        )
        
        metrics = analysis_data.get('metrics', {})
        
        html += f"""
        <section class="section">
            <h2>📊 Quick Metrics</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{metrics.get('total_games', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">{metrics.get('win_rate', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Draw Rate</div>
                    <div class="metric-value">{metrics.get('draw_rate', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Loss Rate</div>
                    <div class="metric-value">{metrics.get('loss_rate', 0):.1f}%</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎮 Rating Distribution</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time Control</th>
                        <th>Rating</th>
                        <th>RD</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
"""
        for tc, rating in metrics.get('ratings_by_tc', {}).items():
            html += f"""
                    <tr>
                        <td>{tc}</td>
                        <td><strong>{rating.get('rating', 0)}</strong></td>
                        <td>{rating.get('rd', 0)}</td>
                        <td>{rating.get('trend', 'stable')}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_multi_player_report(self, analysis_data: Dict[str, Any], players: List[str]) -> str:
        """Generate multi-player comparison report."""
        html = self._get_html_header(
            "Multi-Player Comparison",
            f"Comparative Analysis of {', '.join(players)}"
        )
        
        comparison = analysis_data.get('comparison', {})
        
        html += """
        <section class="section">
            <h2>📊 Comparative Metrics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Games</th>
                        <th>Win Rate</th>
                        <th>Avg Rating</th>
                        <th>Accuracy</th>
                    </tr>
                </thead>
                <tbody>
"""
        for player, data in comparison.items():
            html += f"""
                    <tr>
                        <td><strong>{player}</strong></td>
                        <td>{data.get('games', 0)}</td>
                        <td>{data.get('win_rate', 0):.1f}%</td>
                        <td>{data.get('avg_rating', 0)}</td>
                        <td>{data.get('accuracy', 0):.1f}%</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_fatigue_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate fatigue detection report."""
        html = self._get_html_header(
            f"Fatigue Detection: {username}",
            "Performance Degradation & Pattern Analysis"
        )
        
        fatigue = analysis_data.get('fatigue', {})
        
        html += f"""
        <section class="section">
            <h2>😴 Fatigue Indicators</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Fatigue Score</div>
                    <div class="metric-value">{fatigue.get('score', 0):.1f}/100</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Performance Drop</div>
                    <div class="metric-value">{fatigue.get('perf_drop', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Accuracy Decline</div>
                    <div class="metric-value">{fatigue.get('accuracy_decline', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Blunder Increase</div>
                    <div class="metric-value">{fatigue.get('blunder_increase', 0):.1f}%</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🔍 Pattern Analysis</h2>
            <div class="insight">
                <strong>Time-of-Day Effect:</strong> {fatigue.get('time_effect', 'No significant pattern detected')}
            </div>
            <div class="insight">
                <strong>Session Length Correlation:</strong> {fatigue.get('session_correlation', 'Not correlated')}
            </div>
            <div class="insight">
                <strong>Recommendation:</strong> {fatigue.get('recommendation', 'Continue monitoring')}
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_network_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate network analysis report."""
        html = self._get_html_header(
            f"Network Analysis: {username}",
            "Connection Patterns & Opponent Network"
        )
        
        network = analysis_data.get('network', {})
        
        html += f"""
        <section class="section">
            <h2>🌐 Network Overview</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Unique Opponents</div>
                    <div class="metric-value">{network.get('unique_opponents', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Most Played vs</div>
                    <div class="metric-value" style="font-size: 1.1em;">{network.get('top_opponent', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Games vs Repeats</div>
                    <div class="metric-value">{network.get('repeat_rate', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Opponent Rating</div>
                    <div class="metric-value">{network.get('avg_opponent_elo', 0)}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>📊 Top Opponents</h2>
            <table>
                <thead>
                    <tr>
                        <th>Opponent</th>
                        <th>Games</th>
                        <th>W-D-L</th>
                        <th>Score %</th>
                    </tr>
                </thead>
                <tbody>
"""
        for opponent, data in list(network.get('opponents', {}).items())[:10]:
            html += f"""
                    <tr>
                        <td>{opponent}</td>
                        <td>{data.get('games', 0)}</td>
                        <td>{data.get('wins', 0)}-{data.get('draws', 0)}-{data.get('losses', 0)}</td>
                        <td>{data.get('score_percent', 0):.1f}%</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_opening_repertoire_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """Generate opening repertoire inspector report."""
        html = self._get_html_header(
            f"Opening Repertoire: {username}",
            "Comprehensive Opening Analysis & Statistics"
        )
        
        repertoire = analysis_data.get('repertoire', {})
        
        html += """
        <section class="section">
            <h2>♟️ Opening Summary</h2>
"""
        for color, openings in repertoire.get('by_color', {}).items():
            html += f"""
            <div style="margin: 20px 0;">
                <h3 style="text-transform: capitalize;">{color} Openings</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Opening Name</th>
                            <th>ECO Code</th>
                            <th>Games</th>
                            <th>Win %</th>
                            <th>Avg Rating</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for opening, data in list(openings.items())[:15]:
                html += f"""
                        <tr>
                            <td>{opening}</td>
                            <td><code>{data.get('eco', 'N/A')}</code></td>
                            <td>{data.get('games', 0)}</td>
                            <td>{data.get('win_rate', 0):.1f}%</td>
                            <td>{data.get('avg_rating', 0)}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""
        html += """
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_tournament_report(self, analysis_data: Dict[str, Any], tournament: str) -> str:
        """Generate tournament forensics report."""
        html = self._get_html_header(
            f"Tournament Forensics: {tournament}",
            "Head-to-Head Analysis & Pattern Detection"
        )
        
        forensics = analysis_data.get('forensics', {})
        
        html += f"""
        <section class="section">
            <h2>🏆 Tournament Overview</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{forensics.get('total_games', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Participants</div>
                    <div class="metric-value">{forensics.get('participants', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Winner</div>
                    <div class="metric-value" style="font-size: 1.1em;">{forensics.get('winner', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Time Control</div>
                    <div class="metric-value" style="font-size: 1.1em;">{forensics.get('time_control', 'N/A')}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>📊 Standings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Points</th>
                        <th>Rating</th>
                        <th>Avg CPL</th>
                    </tr>
                </thead>
                <tbody>
"""
        for rank, player in enumerate(forensics.get('standings', [])[:20], 1):
            html += f"""
                    <tr>
                        <td><strong>#{rank}</strong></td>
                        <td>{player.get('name', 'N/A')}</td>
                        <td>{player.get('points', 0)}</td>
                        <td>{player.get('rating', 0)}</td>
                        <td>{player.get('avg_cpl', 0):.1f}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_h2h_report(self, analysis_data: Dict[str, Any], player1: str, player2: str) -> str:
        """Generate head-to-head matchup report."""
        html = self._get_html_header(
            f"Head-to-Head: {player1} vs {player2}",
            "Matchup Prediction & Historical Analysis"
        )
        
        h2h = analysis_data.get('h2h', {})
        prediction = analysis_data.get('prediction', {})
        
        html += f"""
        <section class="section">
            <h2>📊 Matchup Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{h2h.get('total_games', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">{player1} Score</div>
                    <div class="metric-value">{h2h.get('player1_score', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">{player2} Score</div>
                    <div class="metric-value">{h2h.get('player2_score', 0):.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Draws</div>
                    <div class="metric-value">{h2h.get('draws', 0)}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎯 Prediction</h2>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Win Probability</th>
                        <th>Draw Probability</th>
                        <th>Expected Outcome</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>{player1}</strong></td>
                        <td>{prediction.get('player1_win', 0):.1f}%</td>
                        <td>{prediction.get('draw_prob', 0):.1f}%</td>
                        <td>{'Slight Edge' if prediction.get('player1_win', 0) > 50 else 'Slight Disadvantage'}</td>
                    </tr>
                    <tr>
                        <td><strong>{player2}</strong></td>
                        <td>{prediction.get('player2_win', 0):.1f}%</td>
                        <td>{prediction.get('draw_prob', 0):.1f}%</td>
                        <td>{'Slight Edge' if prediction.get('player2_win', 0) > 50 else 'Slight Disadvantage'}</td>
                    </tr>
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def _get_risk_recommendations(self, risk_level: str) -> str:
        """Get recommendations based on risk level."""
        recommendations = {
            'LOW RISK': [
                '<li>✅ No immediate concerns detected</li>',
                '<li>📊 Continue monitoring for consistency</li>',
                '<li>🎯 Performance appears within normal human limits</li>'
            ],
            'MEDIUM RISK': [
                '<li>⚠️ Some suspicious patterns detected</li>',
                '<li>📊 Recommend further analysis with larger game sample</li>',
                '<li>🎯 Monitor specific time controls or openings</li>',
                '<li>🔍 Investigate inconsistencies with rating changes</li>'
            ],
            'HIGH RISK': [
                '<li>🚨 Multiple red flags detected</li>',
                '<li>📊 Strong correlation with engine recommendations</li>',
                '<li>🎯 Recommend referral to Fair Play team</li>',
                '<li>🔍 Conduct detailed forensic analysis</li>'
            ]
        }
        return ''.join(recommendations.get(risk_level, []))
    
    def save_report(self, html_content: str, identifier: str, report_type: str) -> str:
        """Save report to file and return path."""
        timestamp = self._get_timestamp()
        filename = f"report_{identifier}_{report_type}_{timestamp}.html"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Report saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise
    
    def delete_reports(self, pattern: Optional[str] = None, delete_all: bool = False) -> Dict[str, Any]:
        """Delete specific or all report files."""
        deleted = []
        failed = []
        
        try:
            if delete_all:
                for file in self.output_dir.glob("report_*.html"):
                    try:
                        file.unlink()
                        deleted.append(file.name)
                    except Exception as e:
                        failed.append((file.name, str(e)))
            elif pattern:
                for file in self.output_dir.glob(f"*{pattern}*.html"):
                    try:
                        file.unlink()
                        deleted.append(file.name)
                    except Exception as e:
                        failed.append((file.name, str(e)))
            
            logger.info(f"Deleted {len(deleted)} reports")
            return {
                'deleted': deleted,
                'failed': failed,
                'total_deleted': len(deleted)
            }
        except Exception as e:
            logger.error(f"Error deleting reports: {e}")
            return {'error': str(e)}
    
    def generate_generic_report(self, title: str, subtitle: str, data: Dict[str, Any], 
                               sections: Optional[List[Dict]] = None) -> str:
        """
        Generate a generic professional report from structured data.
        
        Args:
            title: Report title
            subtitle: Report subtitle
            data: Analysis data dictionary
            sections: List of section configurations with keys, titles, etc.
        
        Returns:
            HTML report content as string
        """
        html = self._get_html_header(title, subtitle)
        
        if sections:
            for section in sections:
                section_title = section.get('title', 'Data')
                section_data = data.get(section.get('key', ''), {})
                
                html += f"""
        <section class="section">
            <h2>{section_title}</h2>
"""
                
                if isinstance(section_data, dict):
                    html += """
            <table>
                <thead>
                    <tr>
"""
                    for col in section_data.get('columns', []):
                        html += f"                        <th>{col}</th>\n"
                    
                    html += """
                    </tr>
                </thead>
                <tbody>
"""
                    
                    for row in section_data.get('rows', []):
                        html += "                    <tr>\n"
                        for cell in row:
                            html += f"                        <td>{cell}</td>\n"
                        html += "                    </tr>\n"
                    
                    html += """
                </tbody>
            </table>
"""
                else:
                    html += f"<p>{section_data}</p>\n"
                
                html += "        </section>\n"
        else:
            # Default rendering of data
            html += """
        <section class="section">
            <h2>Analysis Data</h2>
"""
            if isinstance(data, dict):
                html += "            <div class=\"insight\">\n"
                for key, value in data.items():
                    if isinstance(value, (int, float, str)):
                        html += f"                <div><strong>{key}:</strong> {value}</div>\n"
                html += "            </div>\n"
            html += "        </section>\n"
        
        html += self._get_html_footer()
        return html
    
    def generate_multi_comparison_report(self, players_data: Dict[str, Dict], 
                                        metric_columns: List[str], title: str = "Player Comparison") -> str:
        """
        Generate a comprehensive multi-player comparison report.
        
        Args:
            players_data: Dictionary of {player_name: metrics_dict}
            metric_columns: List of metric column names to compare
            title: Report title
        
        Returns:
            HTML report content
        """
        html = self._get_html_header(title, "Comparative Analysis")
        
        html += """
        <section class="section">
            <h2>📊 Comparative Metrics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
"""
        for col in metric_columns:
            html += f"                        <th>{col}</th>\n"
        
        html += """
                    </tr>
                </thead>
                <tbody>
"""
        
        for player, metrics in players_data.items():
            html += f"                    <tr>\n                        <td><strong>{player}</strong></td>\n"
            for col in metric_columns:
                value = metrics.get(col, 'N/A')
                if isinstance(value, float):
                    value = f"{value:.1f}"
                html += f"                        <td>{value}</td>\n"
            html += "                    </tr>\n"
        
        html += """
                </tbody>
            </table>
        </section>
"""
        
        html += self._get_html_footer()
        return html


if __name__ == "__main__":
    # Test
    reporter = FeatureReporter()
    print("✅ FeatureReporter initialized successfully")
