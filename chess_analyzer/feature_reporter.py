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
        """Generate opening & style analysis report."""
        html = self._get_html_header(
            f"Opening & Style Analysis: {username}",
            "Strategic Weaknesses & Opportunity Analysis"
        )
        
        openings = exploit_data.get('openings', {})
        weaknesses = exploit_data.get('weaknesses', [])
        strengths = exploit_data.get('strengths', [])
        
        html += """
        <section class="section">
            <h2>🎯 Favorite Openings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Opening</th>
                        <th>Frequency</th>
                        <th>Win Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for opening_name, opening_stats in list(openings.items())[:10]:
            html += f"""
                    <tr>
                        <td>{opening_name}</td>
                        <td>{opening_stats.get('frequency', 0)} games</td>
                        <td><strong>{opening_stats.get('win_rate', 0):.1f}%</strong></td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>💪 Playing Strengths</h2>
"""
        
        if strengths:
            for strength in strengths[:5]:
                html += f"""
            <div class="insight" style="background: #d4edda; border-left-color: #28a745;">
                <strong>✓ {strength}</strong>
            </div>
"""
        else:
            html += '<div class="insight">No specific strengths data available</div>'
        
        html += """
        </section>
        
        <section class="section">
            <h2>⚠️ Exploitable Weaknesses</h2>
"""
        
        if weaknesses:
            for weakness in weaknesses[:5]:
                html += f"""
            <div class="insight" style="background: #fef5f5; border-left-color: #e74c3c;">
                <strong>✗ {weakness}</strong>
            </div>
"""
        else:
            html += '<div class="insight">No specific weaknesses data available</div>'
        
        html += """
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


if __name__ == "__main__":
    # Test
    reporter = FeatureReporter()
    print("✅ FeatureReporter initialized successfully")
