"""
Generate reports from analysis results.
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import jinja2

# Local imports
from .utils.helpers import create_directory

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate various report formats from analysis results."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize report generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.template_dir = self._setup_templates()
        self.output_dir = self.config.get('report', {}).get('output_dir', 'reports')
        
        # Create output directory
        create_directory(self.output_dir)
        
        logger.info(f"ReportGenerator initialized, output directory: {self.output_dir}")
    
    def _setup_templates(self) -> Path:
        """Setup template directory and files."""
        template_dir = Path("templates")
        template_dir.mkdir(exist_ok=True)
        
        # Create default HTML template if it doesn't exist
        html_template = template_dir / "report_template.html"
        if not html_template.exists():
            self._create_default_templates(template_dir)
        
        return template_dir
    
    def _create_default_templates(self, template_dir: Path) -> None:
        """Create default templates."""
        # HTML template
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chess Fairplay Analysis: {{ username }}</title>
            <style>
                :root {
                    --primary-color: #2c3e50;
                    --secondary-color: #3498db;
                    --danger-color: #e74c3c;
                    --warning-color: #f39c12;
                    --success-color: #27ae60;
                    --light-color: #ecf0f1;
                    --dark-color: #2c3e50;
                }
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f7fa;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    padding: 30px;
                }
                
                header {
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid var(--light-color);
                }
                
                h1 {
                    color: var(--primary-color);
                    margin-bottom: 10px;
                    font-size: 2.5em;
                }
                
                .subtitle {
                    color: #7f8c8d;
                    font-size: 1.1em;
                }
                
                .risk-badge {
                    display: inline-block;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    margin-left: 10px;
                    font-size: 0.9em;
                }
                
                .risk-high { background-color: var(--danger-color); color: white; }
                .risk-moderate { background-color: var(--warning-color); color: white; }
                .risk-low { background-color: var(--success-color); color: white; }
                .risk-minimal { background-color: #95a5a6; color: white; }
                
                .summary-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .card {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                    border-left: 4px solid var(--secondary-color);
                }
                
                .card h3 {
                    color: var(--primary-color);
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }
                
                .card .value {
                    font-size: 2em;
                    font-weight: bold;
                    color: var(--dark-color);
                }
                
                .card .label {
                    color: #7f8c8d;
                    font-size: 0.9em;
                    margin-top: 5px;
                }
                
                .score-bar {
                    height: 20px;
                    background: #ecf0f1;
                    border-radius: 10px;
                    margin: 10px 0;
                    overflow: hidden;
                }
                
                .score-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--success-color), var(--warning-color), var(--danger-color));
                    border-radius: 10px;
                    width: {{ suspicion_score }}%;
                }
                
                .section {
                    margin-bottom: 40px;
                }
                
                .section h2 {
                    color: var(--primary-color);
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid var(--light-color);
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                
                th, td {
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                
                th {
                    background-color: var(--light-color);
                    color: var(--primary-color);
                    font-weight: 600;
                }
                
                tr:hover {
                    background-color: #f9f9f9;
                }
                
                .suspicious {
                    background-color: #ffeaea;
                }
                
                .pattern-list {
                    list-style-type: none;
                }
                
                .pattern-list li {
                    padding: 10px;
                    margin: 5px 0;
                    background: #fff3cd;
                    border-left: 4px solid var(--warning-color);
                    border-radius: 4px;
                }
                
                .pattern-list li.high {
                    background: #f8d7da;
                    border-left-color: var(--danger-color);
                }
                
                .pattern-list li.low {
                    background: #d4edda;
                    border-left-color: var(--success-color);
                }
                
                .recommendations {
                    background: #e8f4fd;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid var(--secondary-color);
                }
                
                .recommendations li {
                    margin: 10px 0;
                }
                
                footer {
                    margin-top: 40px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    padding-top: 20px;
                    border-top: 1px solid var(--light-color);
                }
                
                .disclaimer {
                    background: #fff3cd;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    border-left: 4px solid var(--warning-color);
                }
                
                @media (max-width: 768px) {
                    .summary-cards {
                        grid-template-columns: 1fr;
                    }
                    
                    .container {
                        padding: 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>♟️ Chess Fairplay Analysis</h1>
                    <p class="subtitle">Statistical analysis for fair play detection</p>
                    <h2>{{ username }}
                        <span class="risk-badge risk-{{ risk_level.lower().replace(' ', '-') }}">
                            {{ risk_level }} RISK
                        </span>
                    </h2>
                </header>
                
                <div class="disclaimer">
                    <strong>⚠️ IMPORTANT DISCLAIMER:</strong>
                    This report provides statistical indicators only, not proof of cheating. 
                    Use results responsibly. Final judgment rests with Chess.com's Fair Play team.
                </div>
                
                <div class="section">
                    <h2>📊 Summary</h2>
                    <div class="summary-cards">
                        <div class="card">
                            <h3>Suspicion Score</h3>
                            <div class="value">{{ suspicion_score }}/100</div>
                            <div class="score-bar">
                                <div class="score-fill"></div>
                            </div>
                            <div class="label">Higher score indicates more suspicious patterns</div>
                        </div>
                        
                        <div class="card">
                            <h3>Engine Correlation</h3>
                            <div class="value">{{ avg_engine_correlation }}%</div>
                            <div class="label">Average % of moves matching engine's top choice</div>
                        </div>
                        
                        <div class="card">
                            <h3>Avg Centipawn Loss</h3>
                            <div class="value">{{ avg_centipawn_loss }}</div>
                            <div class="label">Lower values indicate stronger play (human avg: 20-50)</div>
                        </div>
                        
                        <div class="card">
                            <h3>Games Analyzed</h3>
                            <div class="value">{{ games_analyzed }}</div>
                            <div class="label">{{ suspicious_games }} suspicious games detected</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Performance by Time Control</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Time Control</th>
                                <th>Games</th>
                                <th>Avg Engine Correlation</th>
                                <th>Avg CPL</th>
                                <th>Consistency</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for tc, stats in performance_by_tc.items() %}
                            <tr>
                                <td>{{ tc }}</td>
                                <td>{{ stats.game_count }}</td>
                                <td>{{ "%.1f"|format(stats.avg_engine_correlation) }}%</td>
                                <td>{{ "%.1f"|format(stats.avg_cpl) }}</td>
                                <td>{{ "%.1f"|format(stats.consistency) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                {% if game_details %}
                <div class="section">
                    <h2>🎮 Recent Games Analysis</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Game</th>
                                <th>Result</th>
                                <th>Engine Correlation</th>
                                <th>Avg CPL</th>
                                <th>Time Control</th>
                                <th>Suspicious</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for game in game_details %}
                            <tr class="{{ 'suspicious' if game.is_suspicious else '' }}">
                                <td>{{ game.game_number }}</td>
                                <td>{{ game.result }}</td>
                                <td>{{ "%.1f"|format(game.engine_correlation) }}%</td>
                                <td>{{ "%.1f"|format(game.avg_cpl) }}</td>
                                <td>{{ game.time_control }}</td>
                                <td>{{ '⚠️ Yes' if game.is_suspicious else 'No' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endif %}
                
                {% if suspicious_patterns %}
                <div class="section">
                    <h2>⚠️ Detected Patterns</h2>
                    <ul class="pattern-list">
                        {% for pattern in suspicious_patterns %}
                        <li class="{{ pattern.severity }}">
                            <strong>{{ pattern.pattern|replace('_', ' ')|title }}:</strong>
                            {{ pattern.description }}
                        </li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                {% if recommendations %}
                <div class="section">
                    <h2>📋 Recommendations</h2>
                    <div class="recommendations">
                        <ul>
                            {% for rec in recommendations %}
                            <li>{{ rec }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endif %}
                
                <div class="section">
                    <h2>⚙️ Analysis Details</h2>
                    <div class="card">
                        <p><strong>Generated:</strong> {{ generated_at }}</p>
                        <p><strong>Analysis Thresholds:</strong></p>
                        <ul>
                            <li>Engine Correlation Red Flag: {{ thresholds.engine_correlation_red_flag }}%</li>
                            <li>Avg CPL Red Flag: {{ thresholds.avg_centipawn_loss_red_flag }}</li>
                            <li>Accuracy Fluctuation Red Flag: {{ thresholds.accuracy_fluctuation_red_flag }}%</li>
                        </ul>
                    </div>
                </div>
                
                <footer>
                    <p>Generated by Chess Fairplay Analyzer v1.0.0</p>
                    <p>This analysis is for informational purposes only.</p>
                </footer>
            </div>
            
            <script>
                // Simple chart for suspicion score
                document.addEventListener('DOMContentLoaded', function() {
                    const scoreFill = document.querySelector('.score-fill');
                    const suspicionScore = {{ suspicion_score }};
                    
                    // Color based on score
                    if (suspicionScore >= 70) {
                        scoreFill.style.background = '#e74c3c';
                    } else if (suspicionScore >= 40) {
                        scoreFill.style.background = '#f39c12';
                    } else {
                        scoreFill.style.background = '#27ae60';
                    }
                    
                    // Add tooltips to suspicious games
                    document.querySelectorAll('.suspicious').forEach(row => {
                        row.title = 'This game shows suspicious patterns';
                    });
                });
            </script>
        </body>
        </html>
        """
        
        with open(template_dir / "report_template.html", "w", encoding="utf-8") as f:
            f.write(html_template)
        
        logger.info("Created default HTML template")
    
    def generate_html_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """
        Generate HTML report from analysis data.
        
        Args:
            analysis_data: Analysis results dictionary
            username: Chess.com username
        
        Returns:
            HTML report as string
        """
        try:
            # Prepare template data
            template_data = {
                'username': username,
                'suspicion_score': analysis_data.get('summary', {}).get('suspicion_score', 0),
                'risk_level': analysis_data.get('summary', {}).get('risk_level', 'MINIMAL'),
                'avg_engine_correlation': analysis_data.get('summary', {}).get('avg_engine_correlation', 0),
                'avg_centipawn_loss': analysis_data.get('summary', {}).get('avg_centipawn_loss', 0),
                'games_analyzed': analysis_data.get('summary', {}).get('games_analyzed', 0),
                'suspicious_games': analysis_data.get('summary', {}).get('suspicious_games', 0),
                'performance_by_tc': analysis_data.get('performance_by_time_control', {}),
                'game_details': analysis_data.get('game_details', []),
                'suspicious_patterns': analysis_data.get('suspicious_patterns', []),
                'recommendations': analysis_data.get('recommendations', []),
                'thresholds': analysis_data.get('thresholds', {}),
                'generated_at': analysis_data.get('generated_at', datetime.now().isoformat())
            }
            
            # Format numbers
            template_data['suspicion_score'] = round(template_data['suspicion_score'], 1)
            template_data['avg_engine_correlation'] = round(template_data['avg_engine_correlation'], 1)
            template_data['avg_centipawn_loss'] = round(template_data['avg_centipawn_loss'], 1)
            
            # Load and render template
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.template_dir)))
            template = env.get_template("report_template.html")
            html_output = template.render(**template_data)
            
            logger.info(f"Generated HTML report for {username}")
            return html_output
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            # Return a simple error report
            return self._generate_error_html(username, str(e))
    
    def _generate_error_html(self, username: str, error: str) -> str:
        """Generate error HTML when report generation fails."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Chess Fairplay Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; }}
                .error {{ background: #ffebee; padding: 20px; border-radius: 5px; border-left: 4px solid #f44336; }}
            </style>
        </head>
        <body>
            <h1>⚠️ Report Generation Error</h1>
            <div class="error">
                <p><strong>Username:</strong> {username}</p>
                <p><strong>Error:</strong> {error}</p>
                <p>Please check the logs for more details.</p>
            </div>
        </body>
        </html>
        """
    
    def generate_text_report(self, analysis_data: Dict[str, Any], username: str) -> str:
        """
        Generate plain text report from analysis data.
        
        Args:
            analysis_data: Analysis results dictionary
            username: Chess.com username
        
        Returns:
            Text report as string
        """
        summary = analysis_data.get('summary', {})
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"CHESS FAIRPLAY ANALYSIS REPORT")
        report_lines.append(f"Player: {username}")
        report_lines.append(f"Generated: {analysis_data.get('generated_at', 'N/A')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Summary section
        report_lines.append("📊 SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Games Analyzed: {summary.get('games_analyzed', 0)}")
        report_lines.append(f"Suspicion Score: {summary.get('suspicion_score', 0):.1f}/100")
        report_lines.append(f"Risk Level: {summary.get('risk_level', 'MINIMAL')}")
        report_lines.append(f"Avg Engine Correlation: {summary.get('avg_engine_correlation', 0):.1f}%")
        report_lines.append(f"Avg Centipawn Loss: {summary.get('avg_centipawn_loss', 0):.1f}")
        report_lines.append(f"Suspicious Games: {summary.get('suspicious_games', 0)}")
        report_lines.append(f"Extremely Accurate Games: {summary.get('extremely_accurate_games', 0)}")
        report_lines.append("")
        
        # Time control performance
        tc_data = analysis_data.get('performance_by_time_control', {})
        if tc_data:
            report_lines.append("📈 PERFORMANCE BY TIME CONTROL")
            report_lines.append("-" * 40)
            for tc, stats in tc_data.items():
                report_lines.append(f"{tc}:")
                report_lines.append(f"  Games: {stats.get('game_count', 0)}")
                report_lines.append(f"  Avg Engine Correlation: {stats.get('avg_engine_correlation', 0):.1f}%")
                report_lines.append(f"  Avg CPL: {stats.get('avg_cpl', 0):.1f}")
                report_lines.append(f"  Consistency: {stats.get('consistency', 0):.1f}")
                report_lines.append("")
        
        # Suspicious patterns
        patterns = analysis_data.get('suspicious_patterns', [])
        if patterns:
            report_lines.append("⚠️ DETECTED PATTERNS")
            report_lines.append("-" * 40)
            for pattern in patterns:
                report_lines.append(f"• {pattern.get('description', '')} [{pattern.get('severity', '').upper()}]")
            report_lines.append("")
        
        # Game details (first 5)
        game_details = analysis_data.get('game_details', [])[:5]
        if game_details:
            report_lines.append("🎮 RECENT GAMES")
            report_lines.append("-" * 40)
            report_lines.append(f"{'Game':<6} {'Result':<10} {'Engine%':<10} {'CPL':<8} {'TC':<10} {'Suspicious':<12}")
            report_lines.append("-" * 60)
            
            for game in game_details:
                suspicious = "⚠️" if game.get('is_suspicious', False) else "No"
                report_lines.append(
                    f"{game.get('game_number', 0):<6} "
                    f"{game.get('result', ''):<10} "
                    f"{game.get('engine_correlation', 0):<9.1f}% "
                    f"{game.get('avg_cpl', 0):<8.1f} "
                    f"{game.get('time_control', ''):<10} "
                    f"{suspicious:<12}"
                )
            report_lines.append("")
        
        # Recommendations
        recommendations = analysis_data.get('recommendations', [])
        if recommendations:
            report_lines.append("📋 RECOMMENDATIONS")
            report_lines.append("-" * 40)
            for rec in recommendations:
                report_lines.append(f"• {rec}")
            report_lines.append("")
        
        # Thresholds
        thresholds = analysis_data.get('thresholds', {})
        if thresholds:
            report_lines.append("⚙️ ANALYSIS THRESHOLDS")
            report_lines.append("-" * 40)
            report_lines.append(f"Engine Correlation Red Flag: {thresholds.get('engine_correlation_red_flag', 95)}%")
            report_lines.append(f"Avg CPL Red Flag: {thresholds.get('avg_centipawn_loss_red_flag', 15)}")
            report_lines.append(f"Accuracy Fluctuation Red Flag: {thresholds.get('accuracy_fluctuation_red_flag', 30)}%")
            report_lines.append("")
        
        # Disclaimer
        report_lines.append("=" * 60)
        report_lines.append("⚠️ IMPORTANT DISCLAIMER")
        report_lines.append("-" * 40)
        report_lines.append("This report provides statistical indicators only, not proof")
        report_lines.append("of cheating. Use results responsibly. Final judgment rests")
        report_lines.append("with Chess.com's Fair Play team.")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def generate_json_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate JSON report from analysis data.
        
        Args:
            analysis_data: Analysis results dictionary
        
        Returns:
            JSON report as string
        """
        try:
            # Pretty print JSON
            json_output = json.dumps(analysis_data, indent=2, default=str)
            logger.info("Generated JSON report")
            return json_output
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def save_report(self, content: str, username: str, format: str, 
                   output_file: Optional[str] = None) -> str:
        """
        Save report to file.
        
        Args:
            content: Report content
            username: Chess.com username
            format: Report format (html, text, json)
            output_file: Optional custom output file path
        
        Returns:
            Path to saved file
        """
        # Determine filename
        if output_file:
            if not output_file.endswith(f".{format}"):
                output_file = f"{output_file}.{format}"
            filepath = Path(self.output_dir) / output_file
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{username}_{timestamp}.{format}"
            filepath = Path(self.output_dir) / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Report saved to: {filepath}")
        return str(filepath)
    
    def generate_report(self, analysis_data: Dict[str, Any], username: str, 
                       format: str = "html", output_file: Optional[str] = None,
                       config: Optional[Dict] = None) -> str:
        """
        Generate and save report in specified format.
        
        Args:
            analysis_data: Analysis results dictionary
            username: Chess.com username
            format: Report format (html, text, json)
            output_file: Optional custom output file path
            config: Configuration dictionary
        
        Returns:
            Path to saved report file
        """
        if config:
            self.config = config
        
        logger.info(f"Generating {format.upper()} report for {username}")
        
        # Generate report content
        if format.lower() == "html":
            content = self.generate_html_report(analysis_data, username)
        elif format.lower() == "text":
            content = self.generate_text_report(analysis_data, username)
        elif format.lower() == "json":
            content = self.generate_json_report(analysis_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Save to file
        filepath = self.save_report(content, username, format, output_file)
        
        # Also generate a summary log
        self._generate_summary_log(analysis_data, username, filepath)
        
        return filepath
    
    def _generate_summary_log(self, analysis_data: Dict[str, Any], username: str, 
                             report_path: str) -> None:
        """Generate a summary log entry."""
        summary = analysis_data.get('summary', {})
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'suspicion_score': summary.get('suspicion_score', 0),
            'risk_level': summary.get('risk_level', 'MINIMAL'),
            'games_analyzed': summary.get('games_analyzed', 0),
            'report_path': report_path
        }
        
        # Append to log file
        log_file = Path(self.output_dir) / "analysis_log.json"
        
        try:
            # Read existing log
            log_data = []
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    try:
                        log_data = json.load(f)
                        if not isinstance(log_data, list):
                            log_data = []
                    except json.JSONDecodeError:
                        log_data = []
            
            # Add new entry
            log_data.append(log_entry)
            
            # Keep only last 100 entries
            if len(log_data) > 100:
                log_data = log_data[-100:]
            
            # Save log
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Could not save summary log: {e}")

# Helper function for quick reporting
def generate_report(analysis_data: Dict[str, Any], username: str, 
                   format: str = "html", output_file: Optional[str] = None,
                   config: Optional[Dict] = None) -> str:
    """
    Quick report generation function.
    
    Args:
        analysis_data: Analysis results dictionary
        username: Chess.com username
        format: Report format
        output_file: Output file path
        config: Configuration dictionary
    
    Returns:
        Path to saved report file
    """
    generator = ReportGenerator(config)
    return generator.generate_report(analysis_data, username, format, output_file)

# Test function
if __name__ == "__main__":
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Testing Report Generator...")
    
    # Create sample analysis data
    sample_data = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'games_analyzed': 25,
            'suspicion_score': 65.5,
            'risk_level': 'HIGH',
            'avg_engine_correlation': 88.7,
            'avg_centipawn_loss': 12.3,
            'suspicious_games': 8,
            'extremely_accurate_games': 3
        },
        'performance_by_time_control': {
            'blitz': {
                'game_count': 15,
                'avg_engine_correlation': 91.2,
                'avg_cpl': 10.8,
                'consistency': 8.5
            },
            'rapid': {
                'game_count': 10,
                'avg_engine_correlation': 84.3,
                'avg_cpl': 15.2,
                'consistency': 12.1
            }
        },
        'game_details': [
            {
                'game_number': 1,
                'result': '1-0',
                'engine_correlation': 95.2,
                'avg_cpl': 8.5,
                'time_control': 'blitz',
                'is_suspicious': True,
                'suspicious_moves_count': 3
            },
            {
                'game_number': 2,
                'result': '0-1',
                'engine_correlation': 82.1,
                'avg_cpl': 18.7,
                'time_control': 'rapid',
                'is_suspicious': False,
                'suspicious_moves_count': 0
            }
        ],
        'suspicious_patterns': [
            {
                'pattern': 'sudden_improvement',
                'description': 'Engine correlation improved from 75% to 92% over 10 games',
                'severity': 'high'
            }
        ],
        'recommendations': [
            'Review games with >95% engine correlation',
            'Check for pattern of perfect play in complex positions',
            'Monitor future games for consistency'
        ],
        'thresholds': {
            'engine_correlation_red_flag': 95,
            'avg_centipawn_loss_red_flag': 15,
            'accuracy_fluctuation_red_flag': 30
        }
    }
    
    # Generate reports
    generator = ReportGenerator()
    
    print("\n📄 Generating sample reports...")
    
    try:
        # HTML report
        html_file = generator.generate_report(sample_data, "TestPlayer123", "html", "sample_report")
        print(f"✅ HTML report: {html_file}")
        
        # Text report
        text_file = generator.generate_report(sample_data, "TestPlayer123", "text", "sample_report")
        print(f"✅ Text report: {text_file}")
        
        # JSON report
        json_file = generator.generate_report(sample_data, "TestPlayer123", "json", "sample_report")
        print(f"✅ JSON report: {json_file}")
        
        print(f"\n📁 Reports saved in: {generator.output_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()