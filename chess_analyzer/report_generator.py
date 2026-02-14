"""
Comprehensive Reporting Engine.

Generates professional reports integrating all analysis modules with:
- Executive summaries with confidence metrics
- Visual charts and graphs (data for visualization)
- Detailed metric breakdowns
- Transparency about limitations and false-positive risks
- Professional formatting and styling
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReportMetadata:
    """Report metadata."""
    title: str
    analysis_date: str
    analyst_name: str = "Chess Fairplay Analyzer v3.3"
    requested_by: str = "User"
    player_names: List[str] = None
    report_type: str = "Player Analysis"
    
    def __post_init__(self):
        if self.player_names is None:
            self.player_names = []

class ReportGenerator:
    """Generate comprehensive analysis reports."""
    
    @staticmethod
    def generate_player_report(suspicion_score: Any,  # CheatSuspicionScore
                              strength_profile: Any,  # SkillProfile
                              opponent_profile: Any,  # OpponentProfile
                              fatigue_analysis: Any,  # FatigueAnalysis
                              metadata: ReportMetadata) -> str:
        """
        Generate comprehensive player analysis report.
        
        Args:
            suspicion_score: Advanced cheat detection results
            strength_profile: Skill profile analysis
            opponent_profile: Opponent metrics (if applicable)
            fatigue_analysis: Fatigue/endurance analysis
            metadata: Report metadata
            
        Returns:
            HTML report string
        """
        
        html = []
        html.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chess Fairplay Analysis Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        header {
            border-bottom: 4px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        h2 { color: #34495e; font-size: 1.8em; margin-top: 30px; margin-bottom: 15px; border-left: 4px solid #3498db; padding-left: 15px; }
        h3 { color: #7f8c8d; font-size: 1.3em; margin-top: 20px; margin-bottom: 10px; }
        
        .metadata {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
        }
        .metadata-row { display: flex; justify-content: space-between; padding: 8px 0; }
        .metadata-label { font-weight: bold; color: #2c3e50; }
        .metadata-value { color: #7f8c8d; }
        
        .executive-summary {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        
        .suspicion-gauge {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .gauge-visual {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            font-weight: bold;
            color: white;
        }
        
        .gauge-low { background: linear-gradient(135deg, #2ecc71, #27ae60); }
        .gauge-medium { background: linear-gradient(135deg, #f39c12, #e67e22); }
        .gauge-high { background: linear-gradient(135deg, #e74c3c, #c0392b); }
        
        .metric-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-table th {
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }
        
        .metric-table td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .metric-table tr:hover { background: #f8f9fa; }
        
        .flag-warned { background: #fee; color: #c33; font-weight: bold; }
        .flag-ok { background: #efe; color: #3c3; font-weight: bold; }
        .flag-alert { background: #ffd700; color: #333; font-weight: bold; }
        
        .text-success { color: #27ae60; }
        .text-warning { color: #f39c12; }
        .text-danger { color: #e74c3c; }
        
        .confidence-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .confidence-high { background: #d4edda; color: #155724; }
        .confidence-medium { background: #fff3cd; color: #856404; }
        .confidence-low { background: #f8d7da; color: #721c24; }
        
        .chart-placeholder {
            background: #f8f9fa;
            border: 2px dashed #bdc3c7;
            padding: 40px;
            text-align: center;
            border-radius: 5px;
            margin: 20px 0;
            color: #7f8c8d;
        }
        
        .disclaimer {
            background: #f8d7da;
            border-left: 4px solid #e74c3c;
            padding: 20px;
            margin-top: 30px;
            border-radius: 5px;
            color: #721c24;
        }
        
        .footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        
        .metric-card h4 { color: #2c3e50; margin-bottom: 10px; }
        .metric-card .value { font-size: 2em; font-weight: bold; color: #3498db; }
        .metric-card .unit { color: #7f8c8d; font-size: 0.9em; }
        
        .signature {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
        
        @media print {
            body { background: white; }
            .container { box-shadow: none; }
        }
    </style>
</head>
<body>
<div class="container">
""")
        
        # Header
        html.append(f"""
<header>
    <h1>Chess Fairplay Analysis Report</h1>
    <p style="color: #7f8c8d;">Professional Cheat Detection & Player Analysis</p>
</header>

<div class="metadata">
    <div>
        <div class="metadata-row">
            <span class="metadata-label">Report Type:</span>
            <span class="metadata-value">{metadata.report_type}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Analysis Date:</span>
            <span class="metadata-value">{metadata.analysis_date}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Analyst:</span>
            <span class="metadata-value">{metadata.analyst_name}</span>
        </div>
    </div>
    <div>
        <div class="metadata-row">
            <span class="metadata-label">Players Analyzed:</span>
            <span class="metadata-value">{', '.join(metadata.player_names)}</span>
        </div>
        <div class="metadata-row">
            <span class="metadata-label">Requested By:</span>
            <span class="metadata-value">{metadata.requested_by}</span>
        </div>
    </div>
</div>
""")
        
        # Executive Summary with Suspicion Score
        if suspicion_score:
            html.append("""
<section class="executive-summary">
    <h2>Executive Summary</h2>
""")
            
            # Suspicion gauge
            gauge_class = 'gauge-low' if suspicion_score.overall_suspicion < 40 else \
                         'gauge-medium' if suspicion_score.overall_suspicion < 70 else 'gauge-high'
            
            html.append(f"""
    <div class="suspicion-gauge">
        <div class="gauge-visual {gauge_class}">
            {suspicion_score.overall_suspicion:.1f}%
        </div>
        <div>
            <h3>Suspicion Score: {suspicion_score.overall_suspicion:.1f}/100</h3>
            <p><strong>Confidence:</strong> <span class="confidence-badge confidence-{'high' if suspicion_score.confidence_level > 0.7 else 'medium' if suspicion_score.confidence_level > 0.5 else 'low'}">
                {suspicion_score.confidence_level:.1%}
            </span></p>
            <p><strong>Likelihood Ratio:</strong> {suspicion_score.likelihood_ratio}</p>
            <p><strong>Confidence Interval (95%):</strong> {suspicion_score.confidence_interval[0]:.1f} - {suspicion_score.confidence_interval[1]:.1f}</p>
            <p><strong>Recommendation:</strong> {suspicion_score.recommendation}</p>
        </div>
    </div>
</section>
""")
        
        # Individual Metrics Analysis
        if suspicion_score and suspicion_score.individual_metrics:
            html.append("""
<section>
    <h2>Detailed Metric Analysis</h2>
    <table class="metric-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Percentile</th>
                <th>Z-Score</th>
                <th>Confidence</th>
                <th>FP Risk</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
""")
            
            for metric in suspicion_score.individual_metrics:
                status_class = 'flag-warned' if metric.is_flagged else 'flag-ok'
                status_text = '⚠️ FLAGGED' if metric.is_flagged else '✓ OK'
                
                html.append(f"""
            <tr class="{status_class}">
                <td><strong>{metric.metric_name}</strong></td>
                <td>{metric.value:.2f}</td>
                <td>{metric.percentile:.0f}%</td>
                <td>{metric.z_score:.2f}</td>
                <td><span class="confidence-badge confidence-{'high' if metric.confidence > 0.7 else 'medium' if metric.confidence > 0.5 else 'low'}">
                    {metric.confidence:.0%}
                </span></td>
                <td>{metric.false_positive_risk:.1%}</td>
                <td>{status_text}</td>
            </tr>
            <tr>
                <td colspan="7" style="background: #f8f9fa; padding: 10px; font-size: 0.9em; color: #7f8c8d;">
                    {metric.context}
                </td>
            </tr>
""")
            
            html.append("""
        </tbody>
    </table>
</section>
""")
        
        # Strength Profile
        if strength_profile:
            html.append(f"""
<section>
    <h2>Skill Profile Analysis</h2>
    <div class="metric-grid">
        <div class="metric-card">
            <h4>Official Rating</h4>
            <div class="value">{strength_profile.official_rating}</div>
            <div class="unit">Rating</div>
        </div>
        <div class="metric-card">
            <h4>Intrinsic Performance Rating (IPR)</h4>
            <div class="value">{strength_profile.intrinsic_rating:.0f}</div>
            <div class="unit">Estimated from move quality</div>
        </div>
        <div class="metric-card">
            <h4>Rating Gap (IPR - Official)</h4>
            <div class="value" style="color: {'#27ae60' if strength_profile.rating_gap < 50 else '#f39c12' if strength_profile.rating_gap < 150 else '#e74c3c'};">
                {strength_profile.rating_gap:+.0f}
            </div>
            <div class="unit">Points difference</div>
        </div>
        <div class="metric-card">
            <h4>Skill Coherence</h4>
            <div class="value">{strength_profile.skill_coherence:.0%}</div>
            <div class="unit">How balanced are skills</div>
        </div>
    </div>
    
    <h3>Skill Dimensions</h3>
    <p><strong>Note:</strong> These represent estimated skill levels in different chess aspects, not proof of ability.</p>
    <table class="metric-table">
        <thead>
            <tr>
                <th>Skill</th>
                <th>Score</th>
                <th>Estimated Elo</th>
                <th>vs. Expected</th>
                <th>Assessment</th>
            </tr>
        </thead>
        <tbody>
""")
            
            skills = [
                strength_profile.opening_strength,
                strength_profile.tactical_sharpness,
                strength_profile.endgame_technique,
                strength_profile.strategy_understanding,
                strength_profile.time_management,
                strength_profile.consistency
            ]
            
            for skill in skills:
                html.append(f"""
            <tr>
                <td><strong>{skill.name}</strong></td>
                <td>{skill.value:.1f}/100</td>
                <td>{skill.estimated_elo:.0f}</td>
                <td><span class="text-{'success' if skill.deviation > 0 else 'danger' if skill.deviation < 0 else 'warning'}">
                    {skill.deviation:+.1f}
                </span></td>
                <td>{skill.strength_level}</td>
            </tr>
""")
            
            html.append("""
        </tbody>
    </table>
    <p style="margin-top: 15px; font-size: 0.9em; color: #7f8c8d;">
        <strong>Chart for Skill Profile:</strong> Visualizing these metrics as a radar/spider chart would show relative strengths across dimensions.
    </p>
</section>
""")
        
        # Fatigue Analysis
        if fatigue_analysis:
            html.append(f"""
<section>
    <h2>Fatigue & Endurance Analysis</h2>
    
    <h3>Within-Game Fatigue</h3>
    <div class="metric-grid">
        <div class="metric-card">
            <h4>Early Game Accuracy</h4>
            <div class="value">{fatigue_analysis.early_game_accuracy:.1f}%</div>
        </div>
        <div class="metric-card">
            <h4>Late Game Accuracy</h4>
            <div class="value">{fatigue_analysis.late_game_accuracy:.1f}%</div>
        </div>
        <div class="metric-card">
            <h4>Accuracy Decline</h4>
            <div class="value" style="color: {'#27ae60' if fatigue_analysis.accuracy_decline < 3 else '#f39c12' if fatigue_analysis.accuracy_decline < 6 else '#e74c3c'};">
                {fatigue_analysis.accuracy_decline:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <h4>Fatigue Detected</h4>
            <div class="value" style="color: {'#e74c3c' if fatigue_analysis.within_game_fatigue_detected else '#27ae60'};">
                {'Yes' if fatigue_analysis.within_game_fatigue_detected else 'No'}
            </div>
        </div>
    </div>
    
    <h3>Session Fatigue</h3>
    <div class="metric-grid">
        <div class="metric-card">
            <h4>First Game Accuracy</h4>
            <div class="value">{fatigue_analysis.first_game_accuracy:.1f}%</div>
        </div>
        <div class="metric-card">
            <h4>Last Game Accuracy</h4>
            <div class="value">{fatigue_analysis.last_game_accuracy:.1f}%</div>
        </div>
        <div class="metric-card">
            <h4>Session Decline</h4>
            <div class="value" style="color: {'#27ae60' if fatigue_analysis.session_decline < 2 else '#f39c12' if fatigue_analysis.session_decline < 5 else '#e74c3c'};">
                {fatigue_analysis.session_decline:.1f}%
            </div>
        </div>
        <div class="metric-card">
            <h4>Consistency</h4>
            <div class="value">{fatigue_analysis.overall_consistency:.1f}%</div>
        </div>
    </div>
    
    <h3>Fatigue Indicators</h3>
    <ul>
""")
            
            for metric in fatigue_analysis.fatigue_metrics:
                html.append(f"""
        <li>
            <strong>{metric.metric_type.replace('_', ' ').title()}:</strong>
            Severity {metric.severity:.0f}% - {metric.evidence}
            <br><em>Recommendation: {metric.recommended_action}</em>
        </li>
""")
            
            html.append("""
    </ul>
</section>
""")
        
        # Disclaimer
        html.append("""
<section class="disclaimer">
    <h2>⚠️ Important Disclaimer & Limitations</h2>
    <ul style="margin-left: 20px;">
        <li><strong>Statistical Nature:</strong> This analysis is based on statistical patterns and cannot prove rule violations.</li>
        <li><strong>False Positives:</strong> High suspicion scores may reflect extraordinary legitimate skill, especially in small sample sizes.</li>
        <li><strong>Context Required:</strong> All conclusions require expert human review and contextual understanding.</li>
        <li><strong>Not Definitive:</strong> Individual metrics alone (even engine correlation) do not prove cheating.</li>
        <li><strong>Sample Size Matters:</strong> Analyses based on fewer than 10-15 games carry higher false-positive risk.</li>
        <li><strong>Multi-Metric Approach:</strong> Suspicion is only significant when multiple independent metrics align.</li>
        <li><strong>Final Authority:</strong> Only Chess.com, Lichess, and relevant authorities can make binding determinations.</li>
    </ul>
</section>

<section class="signature">
    <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    <p><strong>System:</strong> Chess Fairplay Analyzer v3.3</p>
    <p style="color: #7f8c8d; font-size: 0.9em;">
        Based on research by Ken Regan (Rybka Controversy analysis) and Chess.com's Fair Play detection system.
        <br>This tool is for analytic purposes only. All results are probabilistic indicators, not accusations.
    </p>
</section>

</div>
</body>
</html>
""")
        
        return "\\n".join(html)
    
    @staticmethod
    def generate_text_report(suspicion_score: Any,
                            strength_profile: Any,
                            fatigue_analysis: Any,
                            player_name: str = "Player") -> str:
        """Generate text-based report for console/file output."""
        
        lines = [
            "=" * 80,
            "CHESS FAIRPLAY ANALYSIS - COMPREHENSIVE REPORT",
            "=" * 80,
            f"\\nPlayer: {player_name}",
            f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "\\n" + "-" * 80,
            "SUSPICION ASSESSMENT",
            "-" * 80,
        ]
        
        if suspicion_score:
            lines.extend([
                f"Overall Suspicion Score: {suspicion_score.overall_suspicion:.1f}/100",
                f"Confidence Level: {suspicion_score.confidence_level:.1%}",
                f"Likelihood Ratio: {suspicion_score.likelihood_ratio}",
                f"95% Confidence Interval: {suspicion_score.confidence_interval[0]:.1f} - {suspicion_score.confidence_interval[1]:.1f}",
                f"False Positive Risk: {suspicion_score.false_positive_risk:.1%}",
                f"Flagged Metrics: {suspicion_score.flagged_metric_count}",
                f"\\nRecommendation: {suspicion_score.recommendation}",
                f"\\nDetailed Metrics:",
            ])
            
            for metric in suspicion_score.individual_metrics:
                lines.append(f"  • {metric.metric_name}: {metric.value:.2f} (Z={metric.z_score:.2f}, Confidence={metric.confidence:.0%})")
                lines.append(f"    {metric.context}")
        
        if strength_profile:
            lines.extend([
                "\\n" + "-" * 80,
                "SKILL PROFILE",
                "-" * 80,
                f"Official Rating: {strength_profile.official_rating}",
                f"Intrinsic Performance Rating (IPR): {strength_profile.intrinsic_rating:.0f}",
                f"Rating Gap: {strength_profile.rating_gap:+.0f} ({strength_profile.rating_gap/strength_profile.official_rating*100:+.1f}%)",
                f"Overall Skill Coherence: {strength_profile.skill_coherence:.1%}",
                f"\\nSkill Dimensions:",
                f"  Opening Knowledge: {strength_profile.opening_strength.value:.1f}/100",
                f"  Tactical Sharpness: {strength_profile.tactical_sharpness.value:.1f}/100",
                f"  Endgame Technique: {strength_profile.endgame_technique.value:.1f}/100",
                f"  Strategic Understanding: {strength_profile.strategy_understanding.value:.1f}/100",
                f"  Time Management: {strength_profile.time_management.value:.1f}/100",
                f"  Consistency: {strength_profile.consistency.value:.1f}/100",
            ])
        
        if fatigue_analysis:
            lines.extend([
                "\\n" + "-" * 80,
                "FATIGUE & ENDURANCE ANALYSIS",
                "-" * 80,
                f"Within-Game Fatigue Detected: {'Yes' if fatigue_analysis.within_game_fatigue_detected else 'No'}",
                f"Session Fatigue Detected: {'Yes' if fatigue_analysis.session_fatigue_detected else 'No'}",
                f"Overall Consistency: {fatigue_analysis.overall_consistency:.1f}/100",
            ])
        
        lines.extend([
            "\\n" + "=" * 80,
            "IMPORTANT DISCLAIMER",
            "=" * 80,
            "",
            "• This analysis is statistical in nature and cannot prove rule violations.",
            "• High suspicion scores may reflect extraordinary but legitimate skill.",
            "• All conclusions require expert human review.",
            "• False positives are possible, especially with small sample sizes (<10 games).",
            "• Final judgment rests with Chess.com, Lichess, and relevant authorities.",
            "",
            "=" * 80,
        ])
        
        return "\\n".join(lines)
    
    @staticmethod
    def export_json(suspicion_score: Any, strength_profile: Any, 
                   fatigue_analysis: Any, player_name: str) -> str:
        """Export analysis as JSON for programmatic use."""
        
        data = {
            'player': player_name,
            'analysis_date': datetime.now().isoformat(),
            'suspicion_assessment': None,
            'skill_profile': None,
            'fatigue_analysis': None
        }
        
        if suspicion_score:
            data['suspicion_assessment'] = {
                'overall_suspicion': suspicion_score.overall_suspicion,
                'confidence_level': suspicion_score.confidence_level,
                'likelihood_ratio': suspicion_score.likelihood_ratio,
                'confidence_interval': list(suspicion_score.confidence_interval),
                'false_positive_risk': suspicion_score.false_positive_risk,
                'recommendation': suspicion_score.recommendation,
                'metrics': [
                    {
                        'name': m.metric_name,
                        'value': m.value,
                        'z_score': m.z_score,
                        'confidence': m.confidence,
                        'false_positive_risk': m.false_positive_risk,
                        'flagged': m.is_flagged,
                        'context': m.context
                    }
                    for m in suspicion_score.individual_metrics
                ]
            }
        
        if strength_profile:
            data['skill_profile'] = {
                'official_rating': strength_profile.official_rating,
                'intrinsic_rating': strength_profile.intrinsic_rating,
                'rating_gap': strength_profile.rating_gap,
                'overall_tier': strength_profile.overall_skill_level.name,
                'skill_coherence': strength_profile.skill_coherence,
                'skills': {
                    'opening': strength_profile.opening_strength.value,
                    'tactics': strength_profile.tactical_sharpness.value,
                    'endgame': strength_profile.endgame_technique.value,
                    'strategy': strength_profile.strategy_understanding.value,
                    'time_management': strength_profile.time_management.value,
                    'consistency': strength_profile.consistency.value
                }
            }
        
        if fatigue_analysis:
            data['fatigue_analysis'] = {
                'within_game_fatigue': fatigue_analysis.within_game_fatigue_detected,
                'session_fatigue': fatigue_analysis.session_fatigue_detected,
                'overall_consistency': fatigue_analysis.overall_consistency,
                'accuracy_decline_in_game': fatigue_analysis.accuracy_decline,
                'accuracy_decline_in_session': fatigue_analysis.session_decline
            }
        
        return json.dumps(data, indent=2)
