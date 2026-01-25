"""
Professional report generation for all analysis features.
Generates HTML reports for each feature with modern styling and comprehensive data visualization.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

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
    
    def _get_base_css(self) -> str:
        """Get base CSS styling for all reports."""
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }
            
            header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .section {
                margin-bottom: 40px;
                border-left: 4px solid #667eea;
                padding-left: 20px;
            }
            
            .section h2 {
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            
            .section h3 {
                color: #34495e;
                margin-top: 20px;
                margin-bottom: 10px;
                font-size: 1.3em;
            }
            
            .metric-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            
            .metric-card {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
            }
            
            .metric-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
                margin: 10px 0;
            }
            
            .metric-label {
                font-size: 0.9em;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                overflow: hidden;
            }
            
            th {
                background: #2c3e50;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }
            
            td {
                padding: 12px 15px;
                border-bottom: 1px solid #e0e0e0;
            }
            
            tr:hover {
                background: #f8f9fa;
            }
            
            .badge {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }
            
            .badge-success {
                background: #d4edda;
                color: #155724;
            }
            
            .badge-warning {
                background: #fff3cd;
                color: #856404;
            }
            
            .badge-danger {
                background: #f8d7da;
                color: #721c24;
            }
            
            .badge-info {
                background: #d1ecf1;
                color: #0c5460;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
                overflow: hidden;
                margin: 10px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 4px;
            }
            
            .insight {
                background: #e8f4f8;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }
            
            .insight strong {
                color: #2c3e50;
            }
            
            footer {
                background: #f8f9fa;
                padding: 20px 40px;
                text-align: center;
                color: #666;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
            }
        </style>
        """
    
    def _get_html_header(self, title: str, subtitle: str = "") -> str:
        """Get HTML report header with styling."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {self._get_base_css()}
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
    
    def generate_strength_profile_report(self, profile_data: Dict[str, Any], username: str) -> str:
        """Generate skill level analysis report with specific template."""
        html = self._get_html_header(
            f"Strength Profile: {username}",
            "Comprehensive Skill Level & Performance Analysis"
        )
        
        # Extract data safely - handle nested 'profile' key
        profile = profile_data.get('profile', {})
        current_elo = profile.get('current_elo', profile_data.get('current_elo', 'N/A'))
        peak_elo = profile.get('peak_elo', profile_data.get('peak_elo', 'N/A'))
        skill_level = profile.get('skill_level', profile_data.get('skill_level', 'Intermediate'))
        total_games = profile.get('total_games', profile_data.get('total_games', 0))
        overall_win_rate = profile.get('overall_win_rate', profile_data.get('overall_win_rate', 0))
        
        # Get time controls from nested structure
        by_time_control = profile.get('by_time_control', {})
        
        html += f"""
        <section class="section">
            <h2>📊 Overall Rating</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Current Rating</div>
                    <div class="metric-value">{current_elo}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Peak Rating</div>
                    <div class="metric-value">{peak_elo}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Skill Classification</div>
                    <div class="metric-value" style="font-size: 1.3em;">{skill_level}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Games Analyzed</div>
                    <div class="metric-value">{total_games}</div>
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
                        <th>Draw Rate</th>
                        <th>Loss Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for tc_name, tc_data in by_time_control.items():
            games = tc_data.get('games', 0)
            win_rate = tc_data.get('win_rate', 0)
            draw_rate = tc_data.get('draw_rate', 0)
            loss_rate = tc_data.get('loss_rate', 0)
            
            html += f"""
                    <tr>
                        <td><strong>{tc_name}</strong></td>
                        <td>{games}</td>
                        <td>{win_rate:.1f}%</td>
                        <td>{draw_rate:.1f}%</td>
                        <td>{loss_rate:.1f}%</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>📈 Analysis Summary</h2>
"""
        
        # Add insights based on skill level
        insights = {
            'Super-GM Level (2200+)': 'Exceptional player competing at the highest levels of chess.',
            'Grandmaster Level (2000-2200)': 'Master-class player with advanced strategic understanding.',
            'International Master Level (1800-2000)': 'Very strong player with deep chess knowledge.',
            'Master Level (1600-1800)': 'Strong player with solid fundamentals and strategy.',
            'Expert Level (1400-1600)': 'Advanced amateur with good tactical awareness.',
            'Intermediate (1200-1400)': 'Competent player with sound basic technique.',
            'Beginner (Below 1200)': 'Learning player developing chess skills.'
        }
        
        insight_text = insights.get(skill_level, 'Player analysis in progress.')
        html += f"""
            <div class="insight">
                <strong>Skill Assessment:</strong><br>
                {insight_text}
            </div>
            <div class="insight">
                <strong>Performance Stability:</strong><br>
                Average Win Rate: {overall_win_rate:.1f}%<br>
                Consistency: {'Excellent' if by_time_control else 'Good'}
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_accuracy_report(self, accuracy_data: Dict[str, Any], username: str) -> str:
        """Generate move accuracy and consistency report."""
        html = self._get_html_header(
            f"Accuracy Report: {username}",
            "Move Accuracy & Consistency Analysis"
        )
        
        overall_accuracy = accuracy_data.get('overall_accuracy', 0)
        avg_cpl = accuracy_data.get('avg_cpl', 0)
        games_analyzed = accuracy_data.get('games_analyzed', 0)
        
        html += f"""
        <section class="section">
            <h2>📊 Accuracy Metrics</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Overall Accuracy</div>
                    <div class="metric-value">{overall_accuracy:.1f}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {overall_accuracy}%"></div>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Centipawn Loss</div>
                    <div class="metric-value">{avg_cpl:.1f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Games Analyzed</div>
                    <div class="metric-value">{games_analyzed}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Accuracy Rating</div>
                    <div class="metric-value">
                        {'Excellent' if overall_accuracy > 85 else 'Very Good' if overall_accuracy > 75 else 'Good' if overall_accuracy > 65 else 'Fair'}
                    </div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎯 Performance Analysis</h2>
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Assessment</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Accuracy Percentage</td>
                        <td><strong>{overall_accuracy:.1f}%</strong></td>
                        <td><span class="badge badge-info">Performance</span></td>
                    </tr>
                    <tr>
                        <td>Average CPL</td>
                        <td><strong>{avg_cpl:.1f}</strong></td>
                        <td><span class="badge badge-success">Evaluation</span></td>
                    </tr>
                    <tr>
                        <td>Best Game CPL</td>
                        <td><strong>{accuracy_data.get('best_cpl', 'N/A')}</strong></td>
                        <td><span class="badge badge-success">Peak</span></td>
                    </tr>
                    <tr>
                        <td>Worst Game CPL</td>
                        <td><strong>{accuracy_data.get('worst_cpl', 'N/A')}</strong></td>
                        <td><span class="badge badge-warning">Low Point</span></td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>💡 Recommendations</h2>
            <div class="insight">
                <strong>Accuracy Analysis:</strong><br>
                {'Your moves align very closely with optimal chess strategy. Excellent tactical and positional understanding.' if overall_accuracy > 80 else 'Good move selection with solid understanding of chess principles. Keep practicing endgame techniques.' if overall_accuracy > 70 else 'Solid fundamentals. Consider studying tactical patterns and positional strategy.' if overall_accuracy > 60 else 'Focus on improving move calculation and tactical awareness.'}
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_account_metrics_report(self, metrics_data: Dict[str, Any], username: str) -> str:
        """Generate account metrics dashboard report."""
        html = self._get_html_header(
            f"Account Metrics: {username}",
            "Quick Overview & Key Statistics"
        )
        
        total_games = metrics_data.get('total_games', 0)
        wins = metrics_data.get('wins', 0)
        draws = metrics_data.get('draws', 0)
        losses = metrics_data.get('losses', 0)
        
        if total_games > 0:
            win_rate = (wins / total_games * 100)
            draw_rate = (draws / total_games * 100)
            loss_rate = (losses / total_games * 100)
        else:
            win_rate = draw_rate = loss_rate = 0
        
        html += f"""
        <section class="section">
            <h2>📊 Account Overview</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{total_games}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">{win_rate:.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Draw Rate</div>
                    <div class="metric-value">{draw_rate:.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Loss Rate</div>
                    <div class="metric-value">{loss_rate:.1f}%</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎮 Game Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Result</th>
                        <th>Games</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Wins</strong></td>
                        <td>{wins}</td>
                        <td><span class="badge badge-success">{win_rate:.1f}%</span></td>
                    </tr>
                    <tr>
                        <td><strong>Draws</strong></td>
                        <td>{draws}</td>
                        <td><span class="badge badge-info">{draw_rate:.1f}%</span></td>
                    </tr>
                    <tr>
                        <td><strong>Losses</strong></td>
                        <td>{losses}</td>
                        <td><span class="badge badge-warning">{loss_rate:.1f}%</span></td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>🏆 Performance Summary</h2>
            <div class="insight">
                <strong>Overall Performance:</strong><br>
                You have a strong competitive record with consistent results across your games.
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_opening_repertoire_report(self, opening_data: Dict[str, Any], username: str) -> str:
        """Generate opening repertoire inspector report."""
        html = self._get_html_header(
            f"Opening Repertoire: {username}",
            "Comprehensive Opening Analysis & Statistics"
        )
        
        openings = opening_data.get('openings', {})
        total_games = opening_data.get('total_games', 0)
        
        html += """
        <section class="section">
            <h2>♟️ Favorite Openings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Opening Name</th>
                        <th>ECO Code</th>
                        <th>Games</th>
                        <th>Win Rate</th>
                        <th>Frequency</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for opening_name, opening_stats in list(openings.items())[:20]:
            games = opening_stats.get('games', 0)
            win_rate = opening_stats.get('win_rate', 0)
            eco = opening_stats.get('eco', 'N/A')
            frequency = (games / total_games * 100) if total_games > 0 else 0
            
            html += f"""
                    <tr>
                        <td>{opening_name}</td>
                        <td><code>{eco}</code></td>
                        <td>{games}</td>
                        <td>{win_rate:.1f}%</td>
                        <td>{frequency:.1f}%</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>📊 Repertoire Summary</h2>
"""
        
        html += f"""
            <div class="insight">
                <strong>Total Games Analyzed:</strong> {total_games}<br>
                <strong>Unique Openings:</strong> {len(openings)}<br>
                <strong>Most Popular Opening:</strong> {list(openings.keys())[0] if openings else 'N/A'}
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_exploit_report(self, exploit_data: Dict[str, Any], username: str) -> str:
        """Generate opening & style analysis report with modern design."""
        html = self._get_html_header(
            f"Opponent Analysis: {username}",
            "Strategic Weaknesses & Exploitation Guide"
        )
        
        openings = exploit_data.get('openings', {})
        weaknesses = exploit_data.get('weaknesses', [])
        strengths = exploit_data.get('strengths', [])
        
        # Summary stats
        html += f"""
        <section class="section">
            <h2>📊 Analysis Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Favorite Openings</div>
                    <div class="metric-value">{len(openings)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Identified Strengths</div>
                    <div class="metric-value">{len(strengths)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Weak Areas</div>
                    <div class="metric-value">{len(weaknesses)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Opponent</div>
                    <div class="metric-value" style="font-size: 1.1em;">{username}</div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>🎯 Favorite Openings ({len(openings)} total)</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 50%;">Opening Name</th>
                            <th style="width: 25%;">Games Played</th>
                            <th style="width: 25%;">Win Rate</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        if openings:
            for idx, (opening_name, opening_stats) in enumerate(list(openings.items())[:15], 1):
                freq = opening_stats.get('frequency', 0)
                wr = opening_stats.get('win_rate', 0)
                # Color code win rates
                if wr > 55:
                    wr_color = '#d4edda'
                    wr_text = '#28a745'
                elif wr > 45:
                    wr_color = '#e7f3ff'
                    wr_text = '#0066cc'
                else:
                    wr_color = '#fef5f5'
                    wr_text = '#e74c3c'
                html += f"""
                        <tr>
                            <td><strong>{idx}. {opening_name}</strong></td>
                            <td>{freq} games</td>
                            <td style="background-color: {wr_color}; color: {wr_text}; font-weight: bold;">{wr:.1f}%</td>
                        </tr>
"""
        else:
            html += '<tr><td colspan="3" style="text-align: center; padding: 20px; color: #999;">No opening data available</td></tr>'
        
        html += """
                    </tbody>
                </table>
            </div>
        </section>

        <section class="section">
            <h2>💪 Playing Strengths</h2>
            <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
"""
        
        if strengths:
            for idx, strength in enumerate(strengths[:8], 1):
                html += f"""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c8e6c9 100%); 
                            padding: 15px 20px; border-radius: 6px; border-left: 4px solid #28a745;">
                    <strong style="color: #155724;">✓ {strength}</strong>
                </div>
"""
        else:
            html += '<div style="text-align: center; padding: 20px; color: #999;">No strengths data identified</div>'
        
        html += """
            </div>
        </section>

        <section class="section">
            <h2>⚠️ Exploitable Weaknesses</h2>
            <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
"""
        
        if weaknesses:
            for idx, weakness in enumerate(weaknesses[:8], 1):
                html += f"""
                <div style="background: linear-gradient(135deg, #fef5f5 0%, #ffebee 100%); 
                            padding: 15px 20px; border-radius: 6px; border-left: 4px solid #e74c3c;">
                    <strong style="color: #c82333;">✗ {weakness}</strong>
                </div>
"""
        else:
            html += '<div style="text-align: center; padding: 20px; color: #999;">No critical weaknesses identified</div>'
        
        html += """
            </div>
        </section>

        <section class="section">
            <h2>🎲 Exploitation Strategy</h2>
            <div class="insight" style="background: #f0f7ff; border-left-color: #0066cc;">
                <h4>How to Exploit:</h4>
                <ul style="margin: 10px 0; padding-left: 20px;">
"""
        
        if weaknesses:
            html += f"<li>Target {weaknesses[0].split(':')[0].lower()} openings where the opponent struggles</li>"
        if strengths:
            html += f"<li>Avoid {strengths[0].split(':')[0].lower()} - opponent is very strong here</li>"
        
        html += """
                    <li>Prepare deep preparation in weak openings</li>
                    <li>Play patiently in areas where opponent has weaknesses</li>
                    <li>Force simplifications in positions opponent doesn't know well</li>
                </ul>
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_tournament_report(self, tournament_data: Dict[str, Any], tournament_name: str) -> str:
        """Generate tournament forensics report."""
        html = self._get_html_header(
            f"Tournament Analysis: {tournament_name}",
            "Comprehensive Tournament Statistics & Analysis"
        )
        
        html += f"""
        <section class="section">
            <h2>🏆 Tournament Overview</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Participants</div>
                    <div class="metric-value">{tournament_data.get('participants', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{tournament_data.get('total_games', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Time Control</div>
                    <div class="metric-value" style="font-size: 1.1em;">{tournament_data.get('time_control', 'N/A')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Status</div>
                    <div class="metric-value" style="font-size: 1.1em;">Complete</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>📊 Tournament Analysis</h2>
            <div class="insight">
                <strong>Tournament Summary:</strong><br>
                Comprehensive analysis of player performances and game statistics.
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html
    
    def generate_h2h_report(self, h2h_data: Dict[str, Any], player1: str, player2: str) -> str:
        """Generate head-to-head matchup report."""
        html = self._get_html_header(
            f"Head-to-Head: {player1} vs {player2}",
            "Matchup Prediction & Historical Analysis"
        )
        
        player1_score = h2h_data.get('player1_score', 0)
        player2_score = h2h_data.get('player2_score', 0)
        total_games = h2h_data.get('total_games', 0)
        draws = total_games - int(player1_score) - int(player2_score) if total_games > 0 else 0
        
        html += f"""
        <section class="section">
            <h2>📊 Matchup Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">{player1}</div>
                    <div class="metric-value">{player1_score}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Draws</div>
                    <div class="metric-value">{draws}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">{player2}</div>
                    <div class="metric-value">{player2_score}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{total_games}</div>
                </div>
            </div>
        </section>
        
        <section class="section">
            <h2>🎯 Head-to-Head Record</h2>
            <table>
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Wins</th>
                        <th>Win %</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>{player1}</strong></td>
                        <td>{int(player1_score)}</td>
                        <td>{(int(player1_score) / total_games * 100) if total_games > 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Draw</strong></td>
                        <td>{draws}</td>
                        <td>{(draws / total_games * 100) if total_games > 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>{player2}</strong></td>
                        <td>{int(player2_score)}</td>
                        <td>{(int(player2_score) / total_games * 100) if total_games > 0 else 0:.1f}%</td>
                    </tr>
                </tbody>
            </table>
        </section>
"""
        html += self._get_html_footer()
        return html
    
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
    
    def generate_multi_player_comparison_report(self, comparison_data: Dict[str, Any], player_names: List[str]) -> str:
        """Generate detailed multi-player comparison report with modern design."""
        html = self._get_html_header(
            f"Multi-Player Comparison",
            f"Detailed Analysis of {len(player_names)} Players"
        )
        
        # Summary stats
        ratings = comparison_data.get('rating_comparison', {})
        winrates = comparison_data.get('winrate_comparison', {})
        volatility = comparison_data.get('volatility_comparison', {})
        openings = comparison_data.get('opening_comparison', {})
        iq_scores = comparison_data.get('iq_scores', {})
        
        player_count = len(player_names)
        
        html += f"""
        <section class="section">
            <h2>📊 Comparison Overview</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Players Analyzed</div>
                    <div class="metric-value">{player_count}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Games</div>
                    <div class="metric-value">{sum(r.get('games_with_rating', 0) for r in ratings.values())}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Rating</div>
                    <div class="metric-value">{int(sum(r.get('avg_rating', 0) for r in ratings.values()) / max(1, len(ratings)))}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Analysis Date</div>
                    <div class="metric-value" style="font-size: 0.9em;">Jan 25, 2026</div>
                </div>
            </div>
        </section>

        <section class="section">
            <h2>🎯 Rating Comparison</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 30%;">Player</th>
                            <th style="width: 20%;">Avg Rating</th>
                            <th style="width: 20%;">Rating Range</th>
                            <th style="width: 15%;">Games</th>
                            <th style="width: 15%;">Trend</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        if ratings:
            sorted_ratings = sorted(ratings.items(), key=lambda x: x[1].get('avg_rating', 0), reverse=True)
            for player, data in sorted_ratings:
                avg_r = data.get('avg_rating', 0)
                min_r = data.get('min_rating', 0)
                max_r = data.get('max_rating', 0)
                games = data.get('games_with_rating', 0)
                
                # Color based on rating
                if avg_r >= 2000:
                    color = '#d4edda'
                elif avg_r >= 1600:
                    color = '#d1ecf1'
                elif avg_r >= 1200:
                    color = '#fff3cd'
                else:
                    color = '#f8d7da'
                
                html += f"""
                        <tr style="background-color: {color};">
                            <td><strong>{player}</strong></td>
                            <td style="font-weight: bold; text-align: center;">{int(avg_r)}</td>
                            <td style="text-align: center;">{int(min_r)} - {int(max_r)}</td>
                            <td style="text-align: center;">{games}</td>
                            <td style="text-align: center;">📈</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </section>

        <section class="section">
            <h2>🏆 Win Rate & Performance</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 25%;">Player</th>
                            <th style="width: 15%;">Win Rate</th>
                            <th style="width: 20%;">Record (W-D-L)</th>
                            <th style="width: 15%;">Score</th>
                            <th style="width: 25%;">Performance Bar</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        if winrates:
            sorted_wr = sorted(winrates.items(), key=lambda x: x[1].get('win_rate', 0), reverse=True)
            for player, data in sorted_wr:
                wr = data.get('win_rate', 0)
                wins = data.get('wins', 0)
                draws = data.get('draws', 0)
                losses = data.get('losses', 0)
                score = data.get('score', 0)
                
                # Bar visualization
                bar_pct = min(100, max(0, wr))
                bar_color = '#28a745' if wr > 50 else '#ffc107' if wr > 45 else '#e74c3c'
                
                html += f"""
                        <tr>
                            <td><strong>{player}</strong></td>
                            <td style="font-weight: bold; color: {bar_color}; text-align: center;">{wr:.1f}%</td>
                            <td style="text-align: center;">{int(wins)}-{int(draws)}-{int(losses)}</td>
                            <td style="text-align: center; font-weight: bold;">{score:.1f}</td>
                            <td>
                                <div style="background: #f0f0f0; border-radius: 4px; height: 24px; overflow: hidden;">
                                    <div style="width: {bar_pct}%; height: 100%; background: linear-gradient(90deg, {bar_color}, {bar_color}99); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 12px;">
                                        {wr:.0f}%
                                    </div>
                                </div>
                            </td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </section>

        <section class="section">
            <h2>⚡ Rating Volatility Analysis</h2>
            <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
"""
        
        if volatility:
            sorted_vol = sorted(volatility.items(), key=lambda x: x[1].get('volatility_score', 0), reverse=True)
            for player, data in sorted_vol:
                vol = data.get('volatility_score', 0)
                std_dev = data.get('std_deviation', 0)
                trend = data.get('trend_direction', 'Stable')
                
                # Volatility interpretation
                if vol > 100:
                    vol_desc = "Very High (Inconsistent)"
                    vol_color = '#f8d7da'
                elif vol > 70:
                    vol_desc = "High (Variable)"
                    vol_color = '#fff3cd'
                elif vol > 40:
                    vol_desc = "Moderate (Consistent)"
                    vol_color = '#d1ecf1'
                else:
                    vol_desc = "Low (Very Consistent)"
                    vol_color = '#d4edda'
                
                trend_emoji = "📈" if trend == "Upward" else "📉" if trend == "Downward" else "➡️"
                
                html += f"""
                <div style="background: {vol_color}; padding: 15px 20px; border-radius: 6px; border-left: 4px solid #666;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 1.1em;">{player}</strong><br>
                            <span style="color: #666;">{vol_desc}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.3em; font-weight: bold;">{vol:.1f}</div>
                            <div style="color: #666; font-size: 0.9em;">Volatility Score</div>
                            <div style="margin-top: 8px; font-size: 1.2em;">{trend_emoji} {trend}</div>
                        </div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </section>

        <section class="section">
            <h2>🎲 Opening Repertoire Diversity</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width: 30%;">Player</th>
                            <th style="width: 20%;">Unique Openings</th>
                            <th style="width: 20%;">Diversity Score</th>
                            <th style="width: 30%;">Flexibility Level</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        if openings:
            sorted_open = sorted(openings.items(), key=lambda x: x[1].get('diversity', 0), reverse=True)
            for player, data in sorted_open:
                unique = data.get('unique_openings', 0)
                diversity = data.get('diversity', 0)
                
                if diversity > 75:
                    flex = "🟢 Highly Flexible"
                    color = '#d4edda'
                elif diversity > 50:
                    flex = "🟡 Moderately Flexible"
                    color = '#d1ecf1'
                elif diversity > 25:
                    flex = "🟠 Limited Repertoire"
                    color = '#fff3cd'
                else:
                    flex = "🔴 Narrow Repertoire"
                    color = '#f8d7da'
                
                html += f"""
                        <tr style="background-color: {color};">
                            <td><strong>{player}</strong></td>
                            <td style="text-align: center;">{int(unique)}</td>
                            <td style="text-align: center; font-weight: bold;">{diversity:.1f}/100</td>
                            <td style="text-align: center;">{flex}</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </section>

        <section class="section">
            <h2>🧠 Estimated Chess IQ</h2>
            <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
"""
        
        if iq_scores:
            sorted_iq = sorted(iq_scores.items(), key=lambda x: x[1].get('estimated_iq', 0), reverse=True)
            for player, data in sorted_iq:
                iq = data.get('estimated_iq', 100)
                
                if iq >= 180:
                    category = "🌟 GENIUS"
                    color = '#6f42c1'
                elif iq >= 160:
                    category = "🏆 VERY SUPERIOR"
                    color = '#007bff'
                elif iq >= 140:
                    category = "⭐ SUPERIOR"
                    color = '#28a745'
                elif iq >= 120:
                    category = "✓ HIGH AVERAGE"
                    color = '#17a2b8'
                elif iq >= 100:
                    category = "→ AVERAGE"
                    color = '#ffc107'
                else:
                    category = "! BELOW AVERAGE"
                    color = '#e74c3c'
                
                html += f"""
                <div style="background: linear-gradient(135deg, {color}20 0%, {color}40 100%); 
                            padding: 20px; border-radius: 8px; border-left: 5px solid {color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 1.1em; font-weight: bold;">{player}</div>
                            <div style="color: #666; margin-top: 4px;">Chess Intelligence Score</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 2.2em; font-weight: bold; color: {color};">{int(iq)}</div>
                            <div style="color: {color}; font-weight: bold;">{category}</div>
                        </div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </section>

        <section class="section">
            <h2>📈 Key Insights</h2>
            <div style="display: grid; grid-template-columns: 1fr; gap: 12px;">
                <div style="background: #e7f3ff; padding: 15px 20px; border-radius: 6px; border-left: 4px solid #0066cc;">
                    <strong>Strongest Player:</strong> Rated highest overall with consistent performance
                </div>
                <div style="background: #d4edda; padding: 15px 20px; border-radius: 6px; border-left: 4px solid #28a745;">
                    <strong>Most Consistent:</strong> Lowest volatility indicates stable skill level
                </div>
                <div style="background: #fff3cd; padding: 15px 20px; border-radius: 6px; border-left: 4px solid #ffc107;">
                    <strong>Most Flexible:</strong> Highest opening diversity shows adaptability
                </div>
                <div style="background: #f8d7da; padding: 15px 20px; border-radius: 6px; border-left: 4px solid #e74c3c;">
                    <strong>Competitive Ranking:</strong> Based on win rate and skill metrics
                </div>
            </div>
        </section>
"""
        html += self._get_html_footer()
        return html

    def generate_h2h_report(self, matchup_data: Dict[str, Any]) -> str:
        """Generate professional Head-to-Head Matchup report."""
        p1 = matchup_data.get('players', {}).get('player1', {})
        p2 = matchup_data.get('players', {}).get('player2', {})
        
        p1_name = p1.get('name', 'Player 1').upper()
        p2_name = p2.get('name', 'Player 2').upper()
        p1_elo = p1.get('elo', 0)
        p2_elo = p2.get('elo', 0)
        
        elo_probs = matchup_data.get('elo_probability', [50, 50])
        perf_probs = matchup_data.get('performance_probability', [50, 50])
        h2h_probs = matchup_data.get('h2h_probability', [50, 50])
        combined_probs = matchup_data.get('combined_probability', [50, 50])
        prediction = matchup_data.get('prediction', 'UNDETERMINED').upper()
        confidence = matchup_data.get('confidence', 50)
        
        h2h_games = matchup_data.get('h2h_games', {})
        h2h_total = h2h_games.get('total_games', 0)
        h2h_p1_wins = h2h_games.get('player1_wins', 0)
        h2h_p2_wins = h2h_games.get('player2_wins', 0)
        h2h_draws = h2h_games.get('draws', 0)
        
        history = matchup_data.get('history_analysis', {})
        p1_history = history.get('player1', {})
        p2_history = history.get('player2', {})
        
        p1_wins = p1_history.get('wins', 0)
        p1_losses = p1_history.get('losses', 0)
        p1_draws = p1_history.get('draws', 0)
        p1_total = p1_history.get('total_games', 0)
        p1_wr = p1_history.get('win_rate', 0)
        
        p2_wins = p2_history.get('wins', 0)
        p2_losses = p2_history.get('losses', 0)
        p2_draws = p2_history.get('draws', 0)
        p2_total = p2_history.get('total_games', 0)
        p2_wr = p2_history.get('win_rate', 0)
        
        p1_openings = matchup_data.get('player1_openings', {})
        p2_openings = matchup_data.get('player2_openings', {})
        
        suspicious = matchup_data.get('suspicious_activity', {})
        p1_flags = suspicious.get('player1', [])
        p2_flags = suspicious.get('player2', [])
        
        # Determine color scheme based on prediction
        if prediction == p1_name:
            predict_color = '#28a745'
            predict_bg = '#d4edda'
        elif prediction == p2_name:
            predict_color = '#e74c3c'
            predict_bg = '#f8d7da'
        else:
            predict_color = '#0066cc'
            predict_bg = '#e7f3ff'
        
        html = self._get_html_header("Head-to-Head Matchup Analysis")
        html += self._get_base_css()
        html += """
        <style>
            .h2h-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .h2h-card {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }
            
            .h2h-card.p1 {
                border-color: #3498db;
                background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
            }
            
            .h2h-card.p2 {
                border-color: #e74c3c;
                background: linear-gradient(135deg, #fde9e9 0%, #ffffff 100%);
            }
            
            .h2h-name {
                font-size: 28px;
                font-weight: bold;
                margin: 15px 0;
                color: #2c3e50;
            }
            
            .h2h-elo {
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }
            
            .h2h-card.p2 .h2h-elo {
                color: #e74c3c;
            }
            
            .metric-row {
                display: flex;
                justify-content: space-around;
                margin: 15px 0;
                padding: 15px 0;
                border-top: 1px solid #ddd;
            }
            
            .metric-item {
                text-align: center;
                flex: 1;
            }
            
            .metric-label {
                font-size: 12px;
                color: #7f8c8d;
                text-transform: uppercase;
                margin-bottom: 5px;
            }
            
            .metric-value {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
            }
            
            .prediction-box {
                background: """ + predict_bg + """;
                border: 3px solid """ + predict_color + """;
                border-radius: 10px;
                padding: 25px;
                text-align: center;
                margin: 20px 0;
            }
            
            .prediction-title {
                font-size: 14px;
                color: #7f8c8d;
                text-transform: uppercase;
                margin-bottom: 10px;
            }
            
            .prediction-winner {
                font-size: 32px;
                font-weight: bold;
                color: """ + predict_color + """;
                margin: 10px 0;
            }
            
            .confidence-bar {
                width: 100%;
                height: 30px;
                background: #ecf0f1;
                border-radius: 15px;
                overflow: hidden;
                margin-top: 15px;
            }
            
            .confidence-fill {
                height: 100%;
                background: linear-gradient(90deg, """ + predict_color + """ 0%, #2ecc71 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            
            .probability-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px 0;
            }
            
            .prob-card {
                background: white;
                border: 2px solid #ecf0f1;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
            }
            
            .prob-title {
                font-size: 12px;
                color: #7f8c8d;
                text-transform: uppercase;
                margin-bottom: 10px;
            }
            
            .prob-values {
                display: flex;
                justify-content: space-around;
                gap: 10px;
            }
            
            .prob-value {
                flex: 1;
                padding: 10px;
                border-radius: 5px;
                background: #f8f9fa;
                font-weight: bold;
            }
            
            .prob-value.p1 {
                color: #3498db;
                border-left: 3px solid #3498db;
            }
            
            .prob-value.p2 {
                color: #e74c3c;
                border-left: 3px solid #e74c3c;
            }
            
            .h2h-section {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                border: 1px solid #ecf0f1;
            }
            
            .section-title {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #3498db;
            }
            
            .opening-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            
            .opening-item {
                background: #f8f9fa;
                padding: 12px;
                border-radius: 6px;
                border-left: 4px solid #3498db;
            }
            
            .opening-name {
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }
            
            .opening-stats {
                font-size: 12px;
                color: #7f8c8d;
            }
            
            .fair-play-indicator {
                padding: 15px;
                border-radius: 6px;
                margin: 10px 0;
                font-weight: 500;
            }
            
            .fair-play-indicator.clean {
                background: #d4edda;
                border-left: 4px solid #28a745;
                color: #155724;
            }
            
            .fair-play-indicator.flagged {
                background: #f8d7da;
                border-left: 4px solid #e74c3c;
                color: #721c24;
            }
            
            .comparison-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            
            .comparison-table th {
                background: #ecf0f1;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                color: #2c3e50;
                border-bottom: 2px solid #bdc3c7;
            }
            
            .comparison-table td {
                padding: 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            
            .comparison-table tr:hover {
                background: #f8f9fa;
            }
            
            .comparison-table .value-p1 {
                color: #3498db;
                font-weight: bold;
            }
            
            .comparison-table .value-p2 {
                color: #e74c3c;
                font-weight: bold;
            }
        </style>
        
        <div class="container">
            <h1 style="text-align: center; margin-bottom: 30px;">
                🎯 Head-to-Head Matchup Analysis
            </h1>
            
            <!-- Players Overview -->
            <div class="h2h-container">
                <div class="h2h-card p1">
                    <div class="h2h-name">""" + p1_name + """</div>
                    <div class="h2h-elo">⭐ """ + str(p1_elo) + """ ELO</div>
                    <div class="metric-row">
                        <div class="metric-item">
                            <div class="metric-label">Games</div>
                            <div class="metric-value">""" + str(p1_total) + """</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Win Rate</div>
                            <div class="metric-value">""" + str(round(p1_wr, 1)) + """%</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Record</div>
                            <div class="metric-value">""" + str(p1_wins) + """-""" + str(p1_losses) + """-""" + str(p1_draws) + """</div>
                        </div>
                    </div>
                </div>
                
                <div class="h2h-card p2">
                    <div class="h2h-name">""" + p2_name + """</div>
                    <div class="h2h-elo">⭐ """ + str(p2_elo) + """ ELO</div>
                    <div class="metric-row">
                        <div class="metric-item">
                            <div class="metric-label">Games</div>
                            <div class="metric-value">""" + str(p2_total) + """</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Win Rate</div>
                            <div class="metric-value">""" + str(round(p2_wr, 1)) + """%</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Record</div>
                            <div class="metric-value">""" + str(p2_wins) + """-""" + str(p2_losses) + """-""" + str(p2_draws) + """</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Matchup Prediction -->
            <div class="prediction-box">
                <div class="prediction-title">🏆 Predicted Winner</div>
                <div class="prediction-winner">""" + prediction + """</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: """ + str(confidence) + """%;">
                        """ + str(round(confidence, 1)) + """% Confidence
                    </div>
                </div>
            </div>
            
            <!-- Probability Analysis -->
            <div class="h2h-section">
                <div class="section-title">📊 Probability Analysis</div>
                <div class="probability-grid">
                    <div class="prob-card">
                        <div class="prob-title">ELO-Based Probability</div>
                        <div class="prob-values">
                            <div class="prob-value p1">""" + str(round(elo_probs[0], 1)) + """%</div>
                            <div class="prob-value p2">""" + str(round(elo_probs[1], 1)) + """%</div>
                        </div>
                    </div>
                    
                    <div class="prob-card">
                        <div class="prob-title">Performance-Based Probability</div>
                        <div class="prob-values">
                            <div class="prob-value p1">""" + str(round(perf_probs[0], 1)) + """%</div>
                            <div class="prob-value p2">""" + str(round(perf_probs[1], 1)) + """%</div>
                        </div>
                    </div>
                    
                    <div class="prob-card">
                        <div class="prob-title">Head-to-Head History</div>
                        <div class="prob-values">
                            <div class="prob-value p1">""" + str(round(h2h_probs[0], 1)) + """%</div>
                            <div class="prob-value p2">""" + str(round(h2h_probs[1], 1)) + """%</div>
                        </div>
                    </div>
                    
                    <div class="prob-card">
                        <div class="prob-title">Combined Score</div>
                        <div class="prob-values">
                            <div class="prob-value p1">""" + str(round(combined_probs[0], 1)) + """%</div>
                            <div class="prob-value p2">""" + str(round(combined_probs[1], 1)) + """%</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Head-to-Head History -->
            <div class="h2h-section">
                <div class="section-title">🎲 Direct Head-to-Head History</div>
                <div style="text-align: center;">
                    <div style="font-size: 18px; color: #7f8c8d; margin-bottom: 15px;">
                        Total Games: <strong style="color: #2c3e50; font-size: 24px;">""" + str(h2h_total) + """</strong>
                    </div>
                    <table class="comparison-table">
                        <tr>
                            <th>Result</th>
                            <th class="value-p1">""" + p1_name + """</th>
                            <th class="value-p2">""" + p2_name + """</th>
                        </tr>
                        <tr>
                            <td><strong>Wins</strong></td>
                            <td class="value-p1">""" + str(h2h_p1_wins) + """</td>
                            <td class="value-p2">""" + str(h2h_p2_wins) + """</td>
                        </tr>
                        <tr>
                            <td><strong>Draws</strong></td>
                            <td colspan="2" style="text-align: center;">""" + str(h2h_draws) + """</td>
                        </tr>
                    </table>
                </div>
                """ + (f"""
                <div style="text-align: center; margin-top: 20px; font-size: 16px; color: #3498db; font-weight: bold;">
                    These players have not played each other yet
                </div>
                """ if h2h_total == 0 else "") + """
            </div>
            
            <!-- Opening Repertoires -->
            <div class="h2h-section">
                <div class="section-title">🏁 Opening Repertoires</div>
                <div class="opening-grid">
                    <div>
                        <h4 style="color: #3498db; margin-bottom: 15px;">""" + p1_name + """'s Openings</h4>
                        """ + ("".join([
                            f"""
                            <div class="opening-item">
                                <div class="opening-name">{opening}</div>
                                <div class="opening-stats">
                                    Games: {data.get('count', 0)} | Win Rate: {data.get('win_rate', 0):.1f}%
                                </div>
                            </div>
                            """
                            for opening, data in sorted(p1_openings.items(), key=lambda x: x[1].get('count', 0), reverse=True)[:5]
                        ]) if p1_openings else "<div style='color: #7f8c8d;'>No opening data</div>") + """
                    </div>
                    <div>
                        <h4 style="color: #e74c3c; margin-bottom: 15px;">""" + p2_name + """'s Openings</h4>
                        """ + ("".join([
                            f"""
                            <div class="opening-item" style="border-left-color: #e74c3c;">
                                <div class="opening-name">{opening}</div>
                                <div class="opening-stats">
                                    Games: {data.get('count', 0)} | Win Rate: {data.get('win_rate', 0):.1f}%
                                </div>
                            </div>
                            """
                            for opening, data in sorted(p2_openings.items(), key=lambda x: x[1].get('count', 0), reverse=True)[:5]
                        ]) if p2_openings else "<div style='color: #7f8c8d;'>No opening data</div>") + """
                    </div>
                </div>
            </div>
            
            <!-- Fair Play Assessment -->
            <div class="h2h-section">
                <div class="section-title">🛡️ Fair Play Assessment</div>
                """ + (f"""
                <div class="fair-play-indicator clean">
                    ✅ <strong>{p1_name}</strong> - No suspicious activity detected
                </div>
                """ if not p1_flags else f"""
                <div class="fair-play-indicator flagged">
                    ⚠️ <strong>{p1_name}</strong> - {len(p1_flags)} suspicious indicator(s):
                    {', '.join(p1_flags)}
                </div>
                """) + """
                
                """ + (f"""
                <div class="fair-play-indicator clean">
                    ✅ <strong>{p2_name}</strong> - No suspicious activity detected
                </div>
                """ if not p2_flags else f"""
                <div class="fair-play-indicator flagged">
                    ⚠️ <strong>{p2_name}</strong> - {len(p2_flags)} suspicious indicator(s):
                    {', '.join(p2_flags)}
                </div>
                """) + """
            </div>
            
            <!-- Key Insights -->
            <div class="h2h-section">
                <div class="section-title">💡 Key Insights</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="background: #e7f3ff; padding: 15px; border-radius: 6px; border-left: 4px solid #0066cc;">
                        <strong>ELO Advantage:</strong>
                        """ + (p1_name if p1_elo > p2_elo else p2_name) + """ leads by """ + str(abs(p1_elo - p2_elo)) + """ points
                    </div>
                    <div style="background: #d4edda; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745;">
                        <strong>Performance:</strong>
                        """ + (p1_name if p1_wr > p2_wr else p2_name) + """ has higher win rate (""" + str(round(max(p1_wr, p2_wr), 1)) + """%%)
                    </div>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107;">
                        <strong>Match Type:</strong>
                        """ + ("Rematch" if h2h_total > 0 else "First Time Matchup") + """
                    </div>
                    <div style="background: #e9ecef; padding: 15px; border-radius: 6px; border-left: 4px solid #6c757d;">
                        <strong>Prediction Confidence:</strong>
                        """ + ("High" if confidence >= 70 else "Medium" if confidence >= 50 else "Low") + """ (""" + str(round(confidence, 1)) + """%)
                    </div>
                </div>
            </div>
        </div>
"""
        html += self._get_html_footer()
        return html


if __name__ == "__main__":
    # Test
    reporter = FeatureReporter()
    print("✅ FeatureReporter initialized successfully")
