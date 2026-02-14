"""
Integration Guide for Enhanced Analysis Modules.

Shows how to integrate the new analysis modules into existing workflows.
"""

# EXAMPLE 1: Using Advanced Cheat Detection
# ==========================================
from chess_analyzer.advanced_detection import AdvancedCheatDetector, create_suspicion_report

def example_advanced_detection():
    """Example: Analyze a player for suspicious activity."""
    detector = AdvancedCheatDetector()
    
    # Prepare game metrics
    game_metrics = {
        'player_name': 'suspicious_player',
        'games_analyzed': 25,
        'avg_cpl': 15.5,  # Very low
        'engine_correlation': 96.2,  # Very high
        'game_evaluations': [12, 18, 14, 22, 16, 19, 13],  # Centipawn losses
        'move_times': [2.1, 2.3, 2.0, 2.4, 2.2, 2.1, 2.0],  # Very consistent
        'move_classifications': {
            'best': 180,
            'good': 12,
            'inaccuracy': 2,
            'mistake': 0,
            'blunder': 0
        }
    }
    
    # Compute suspicion score
    suspicion = detector.compute_suspicion_score(game_metrics, player_rating=2000)
    
    # Generate report
    report = create_suspicion_report(suspicion)
    print(report)


# EXAMPLE 2: Opponent Analysis with Vulnerability Detection
# ==========================================================
from chess_analyzer.opponent_analysis import OpponentAnalyzer

def example_opponent_analysis():
    """Example: Build opponent profile and find vulnerabilities."""
    
    opponent_games = [
        {
            'rating': 1850,
            'result': 'loss',
            'cpl': 45,
            'accuracy': 62,
            'opening': 'Sicilian Defense',
            'eco': 'B20'
        },
        {
            'rating': 1820,
            'result': 'draw',
            'cpl': 38,
            'accuracy': 68,
            'opening': 'French Defense',
            'eco': 'C00'
        },
        # ... more games
    ]
    
    profile = OpponentAnalyzer.build_profile(opponent_games, 'opponent_name')
    vulnerabilities = OpponentAnalyzer.get_vulnerability_summary(profile)
    
    print(f"Opponent weaknesses: {vulnerabilities}")


# EXAMPLE 3: Strength Profile Analysis
# =====================================
from chess_analyzer.strength_profile import StrengthProfileAnalyzer

def example_strength_profile():
    """Example: Analyze player's multi-dimensional skill profile."""
    
    games = [
        {
            'accuracy': 78,
            'cpl': 28,
            'phase_scores': {
                'opening': 85,
                'tactical': 72,
                'endgame': 65,
                'opening_cpl': 15,
                'endgame_cpl': 35
            },
            'move_times': [2.1, 1.9, 2.3, 2.0]
        },
        # ... more games
    ]
    
    profile = StrengthProfileAnalyzer.build_skill_profile(
        games, 'player', official_rating=1800
    )
    
    # Get radar chart data
    radar_data = profile.compute_radar_data()
    print(f"Skill dimensions: {radar_data}")


# EXAMPLE 4: Fatigue Detection
# =============================
from chess_analyzer.fatigue_detector import FatigueDetector

def example_fatigue_analysis():
    """Example: Detect fatigue patterns in session."""
    
    games = [
        {'accuracy': 85, 'timestamp': '2024-01-15T10:00:00'},
        {'accuracy': 82, 'timestamp': '2024-01-15T10:45:00'},
        {'accuracy': 79, 'timestamp': '2024-01-15T11:30:00'},
        {'accuracy': 73, 'timestamp': '2024-01-15T12:15:00'},
        # Clear decline through session
    ]
    
    analysis = FatigueDetector.analyze_fatigue(games, 'player')
    
    if analysis.session_fatigue_detected:
        print(f"Session fatigue: -{analysis.session_decline:.1f}% accuracy decline")


# EXAMPLE 5: Network Analysis
# ============================
from chess_analyzer.network_analyzer import NetworkAnalyzer

def example_network_analysis():
    """Example: Detect suspicious player networks and collusion."""
    
    player_games = {
        'player_a': [
            {'opponent': 'player_b', 'accuracy': 94, 'opening': 'Ruy Lopez'},
            {'opponent': 'player_c', 'accuracy': 96, 'opening': 'Ruy Lopez'},
        ],
        'player_b': [
            {'opponent': 'player_a', 'accuracy': 92, 'opening': 'Ruy Lopez'},
            {'opponent': 'player_d', 'accuracy': 88, 'opening': 'Sicilian'},
        ],
        # ... more players
    }
    
    network = NetworkAnalyzer.build_network(player_games, opponent_cutoff=2)
    
    if network.colluding_pairs_found > 0:
        print(f"⚠️ Found {network.colluding_pairs_found} suspicious player pairs")


# EXAMPLE 6: Comprehensive Player Report
# =======================================
from chess_analyzer.report_generator import ReportGenerator, ReportMetadata

def example_comprehensive_report():
    """Example: Generate full HTML report with all analyses."""
    
    # Assume you've already run all analyses
    suspicion_score = ...  # From AdvancedCheatDetector
    strength_profile = ...  # From StrengthProfileAnalyzer
    opponent_profile = ...  # From OpponentAnalyzer
    fatigue_analysis = ...  # From FatigueDetector
    
    metadata = ReportMetadata(
        title='Player Analysis Report',
        analysis_date='2024-01-15',
        analyst_name='Chess Fairplay Analyzer v3.3',
        player_names=['player_name'],
        report_type='Comprehensive Fair Play Analysis'
    )
    
    html_report = ReportGenerator.generate_player_report(
        suspicion_score,
        strength_profile,
        opponent_profile,
        fatigue_analysis,
        metadata
    )
    
    # Save to file
    with open('player_report.html', 'w') as f:
        f.write(html_report)


# EXAMPLE 7: Multi-Player Comparison
# ===================================
from chess_analyzer.multi_player_analysis import MultiPlayerAnalyzer

def example_multi_player_comparison():
    """Example: Compare multiple players side-by-side."""
    
    players_data = {
        'player_a': {
            'rating': 2000,
            'accuracy': 78,
            'centipawn_loss': 28,
            'win_rate': 52.5,
            'intrinsic_rating': 2050,
            'suspicion_score': 35
        },
        'player_b': {
            'rating': 1950,
            'accuracy': 82,
            'centipawn_loss': 22,
            'win_rate': 58.0,
            'intrinsic_rating': 1980,
            'suspicion_score': 42
        },
        'player_c': {
            'rating': 2100,
            'accuracy': 75,
            'centipawn_loss': 35,
            'win_rate': 45.0,
            'intrinsic_rating': 2080,
            'suspicion_score': 28
        }
    }
    
    comparison = MultiPlayerAnalyzer.compare_multiple_players(players_data)
    summary = MultiPlayerAnalyzer.create_comparison_summary(comparison)
    print(summary)


# EXAMPLE 8: Visualization Data Generation
# =========================================
from chess_analyzer.visualization_helper import VisualizationHelper

def example_visualization():
    """Example: Generate chart data for reporting."""
    
    # Skill profile radar chart
    radar_chart = VisualizationHelper.create_radar_chart(strength_profile)
    
    # Accuracy trend line chart
    trend_chart = VisualizationHelper.create_accuracy_trend_chart(games)
    
    # Metrics bar chart
    metrics_chart = VisualizationHelper.create_metrics_bar_chart(suspicion_score)
    
    # Export to JSON for frontend rendering
    chart_json = VisualizationHelper.export_chart_to_json(radar_chart)


# INTEGRATION WITH EXISTING MENU
# ==============================

def add_enhanced_detection_to_menu(menu_options):
    """
    Add enhanced detection options to the existing menu system.
    
    Call this in chess_analyzer/menu.py to add the new features.
    """
    
    new_options = {
        "16": {
            "name": "Analyze Player (Advanced Detection)",
            "description": "Multi-metric cheat detection with confidence scoring",
            "function": "run_advanced_player_analysis",
            "required_input": "username",
            "outputs": ["suspicion_score", "skill_profile", "report_html"]
        },
        "17": {
            "name": "Compare Multiple Players",
            "description": "Side-by-side comparison with clustering and outlier detection",
            "function": "run_multi_player_comparison",
            "required_input": ["username1", "username2", "username3_optional"],
            "outputs": ["comparison_matrix", "rankings", "clusters"]
        },
        "18": {
            "name": "Network Analysis (Collusion Detection)",
            "description": "Detect colluding player networks and suspicious patterns",
            "function": "run_network_analysis",
            "required_input": ["usernames"],
            "outputs": ["network_graph", "clusters", "suspicious_edges"]
        },
        "19": {
            "name": "Tournament Inspector (Enhanced)",
            "description": "Analyze tournament with fairness metrics and individual analysis",
            "function": "run_tournament_analysis_enhanced",
            "required_input": "tournament_data",
            "outputs": ["player_reports", "suspicion_matrix", "tournament_summary"]
        },
        "20": {
            "name": "Generate Comprehensive Report",
            "description": "Create full HTML report combining all analyses",
            "function": "run_comprehensive_report",
            "required_input": ["analysis_data"],
            "outputs": ["report_html", "report_json", "report_text"]
        }
    }
    
    return {**menu_options, **new_options}


# CONFIGURATION FOR ACCURACY BENCHMARKS
# =====================================

# Add to config.yaml:
ENHANCED_DETECTION_CONFIG = {
    'enable_advanced_detection': True,
    'confidence_threshold': 0.65,  # Minimum confidence for flagging
    'regan_z_threshold': 4.5,  # Regan's suspicious threshold
    'false_positive_risk_max': 0.15,  # Max acceptable false positive risk
    'min_games_for_analysis': 5,  # Minimum games before analysis
    'peer_comparison_enabled': True,
    'network_analysis_enabled': True,
    'visualization_type': 'chart.js',  # or 'd3', 'highcharts'
    'report_format': 'html',  # or 'pdf', 'json'
    'include_confidence_intervals': True,
    'include_false_positive_warnings': True,
    'show_disclaimer': True
}

print(__doc__)
