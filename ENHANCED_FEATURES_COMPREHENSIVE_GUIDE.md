# Chess Fairplay Analyzer v3.3+ - Enhanced Features Guide

## Overview

This guide documents the comprehensive enhancements to the Chess Fairplay Analyzer, implementing modern multi-metric cheat detection and advanced player analysis based on Chess.com Fair Play and Ken Regan's research.

---

## Table of Contents

1. [Multi-Metric Cheat Detection](#multi-metric-cheat-detection)
2. [Opponent Analysis](#opponent-analysis)
3. [Strength Profile Analysis](#strength-profile-analysis)
4. [Fatigue Detection](#fatigue-detection)
5. [Network Analysis](#network-analysis)
6. [Comprehensive Reporting](#comprehensive-reporting)
7. [Multi-Player Comparison](#multi-player-comparison)
8. [Usage Examples](#usage-examples)
9. [Interpretation Guide](#interpretation-guide)
10. [Limitations & Disclaimers](#limitations--disclaimers)

---

## Multi-Metric Cheat Detection

### Overview

The advanced detection system combines **five independent signals** instead of relying on a single metric, significantly reducing false positives.

### Key Metrics

#### 1. **Intrinsic Performance Rating (IPR) vs Official Rating**

- **What it measures**: The skill level implied by move quality (centipawn loss)
- **Formula**: Estimated from empirical CPL-to-Elo mapping
- **Interpretation**:
  - IPR ~= Official Rating: Normal, consistent play
  - IPR > Official Rating + 150: Suspicious, suggests performance above expected
  - IPR > Official Rating + 300: Highly suspicious, 1-in-100,000 likelihood
- **Confidence**: Higher for stable, recent play; lower for recent improvement
- **False Positive Risk**: Can indicate natural temporary peak performance

#### 2. **Centipawn Loss (CPL) Z-Score**

- **What it measures**: How exceptional is the player's average centipawn loss compared to peers?
- **Regan's Threshold**: Z ≈ 4.5 = 1 in 300,000 games
- **Interpretation**:
  - Z < 2.5: Normal variation
  - Z = 2.5-3.5: Moderately unusual
  - Z > 4.5: Highly suspicious (statistical impossibility)
- **Important Note**: Even Z > 4 can occur with legitimate superhuman play
- **Confidence**: Increases with more games analyzed; increases with peer comparison data

#### 3. **Engine Move Correlation with Confidence Interval**

- **What it measures**: Percentage of moves matching engine's top choice
- **Expected by Rating**:
  - 1500-1700 Elo: ~70-75%
  - 1700-2000 Elo: ~75-80%
  - 2000-2400 Elo: ~80-85%
  - 2400+ Elo: ~85-90%
- **Suspicious Range**: >95% correlation in sudden spike
- **Importance**: Accounts for game length uncertainty with statistical CI
- **Confidence**: Higher for longer games (more moves = more precise estimate)

#### 4. **Move Timing Consistency**

- **What it measures**: Coefficient of Variation in move times
- **Human Pattern**: CV typically 0.7-1.5 (high variation)
- **Engine Pattern**: CV typically 0.1-0.3 (very consistent)
- **Interpretation**:
  - CV > 1.0: Natural human variation ✓
  - CV = 0.5-0.7: Borderline (may indicate time management issues)
  - CV < 0.3: Engine-like consistency ⚠️
- **Context**: Time control matters (blitz shows more variation than classical)

#### 5. **Error Pattern Analysis**

- **What it measures**: Frequency of tactical mistakes and blunders
- **Normal Human Rates**:
  - 1000 Elo: ~15% mistakes/blunders
  - 1500 Elo: ~10% mistakes/blunders
  - 2000 Elo: ~5% mistakes/blunders
  - 2400+ Elo: ~2-3% mistakes/blunders
- **Suspicious Pattern**: <1% error rate while maintaining reasonable accuracy
- **Interpretation**: Humans make mistakes; no mistakes + high accuracy = suspicious

### Suspicion Scoring

**Formula**: Weighted combination of all five metrics
- IPR Gap: 25% weight
- CPL Z-Score: 30% weight (highest impact)
- Engine Correlation: 25% weight
- Timing Consistency: 12% weight
- Error Pattern: 8% weight

**Scoring Scale**:
- 0-30: Low suspicion (normal play)
- 30-50: Moderate suspicion (worth monitoring)
- 50-70: High suspicion (recommend review)
- 70-100: Very high suspicion (likely violation)

### Confidence Levels

Instead of binary "cheater/not cheater" labels, the system reports:

```
Suspicion Score: 78.5/100
Confidence: 82%
Likelihood: "1 in 10,000 chance of occurring naturally"
95% Confidence Interval: 69.2 - 87.8
False Positive Risk: 8%
```

This transparency allows human experts to weigh the evidence properly.

---

## Opponent Analysis

### Building a Comprehensive Opponent Profile

The system aggregates metrics across all games against an opponent:

```python
from chess_analyzer.opponent_analysis import OpponentAnalyzer

profile = OpponentAnalyzer.build_profile(opponent_games, opponent_name)
```

### Profile Components

#### 1. **Aggregated Metrics**
- Overall win/draw/loss rates
- Average rating trend
- Accuracy consistency (standard deviation)
- Average centipawn loss

#### 2. **Opening Performance Analysis**
- Win rate by opening
- Weak openings (where opponent scores <40%)
- Strong openings (where opponent scores >60%)
- Repertoire diversity (Shannon entropy)

#### 3. **Phase-by-Phase Breakdown**
- Opening accuracy vs middlegame vs endgame
- Where opponent tends to struggle
- Time management across game phases

#### 4. **Vulnerability Detection**
```python
vulnerabilities = OpponentAnalyzer.get_vulnerability_summary(profile)
```

Returns:
- Openings where opponent underperforms
- Game phases with weakness
- Performance gaps between phases
- Sensitivity to stronger/weaker opponents

### Usage in Championship Preparation

Use opponent profiles to:
1. Identify weak openings to exploit
2. Understand opponent's time management
3. Detect sudden pattern changes (possible coaching/computers)
4. Build targeted opening repertoire

---

## Strength Profile Analysis

### Multi-Dimensional Skill Breakdown

The system estimates skill across 6 dimensions:

```python
profile = StrengthProfileAnalyzer.build_skill_profile(games, username, official_rating)

# Access skill dimensions
print(profile.opening_strength.value)      # 0-100
print(profile.tactical_sharpness.value)    # 0-100
print(profile.endgame_technique.value)     # 0-100
print(profile.strategy_understanding.value)# 0-100
print(profile.time_management.value)       # 0-100
print(profile.consistency.value)           # 0-100
```

### Skill Radar Chart

Visualized as a radar/spider chart showing:
- Relative strengths across dimensions
- Skill imbalances (e.g., strong openings, weak endings)
- Comparison to baseline for rating

### IPR vs Official Rating

- **IPR**: Estimated rating from move quality alone
- **Official Rating**: Reported rating on platform
- **Gap Analysis**:
  - Small gap (<50): Rating accurate
  - Medium gap (50-150): Possible recent improvement or rating lag
  - Large gap (>150): Suspicious, suggests underrated or artificially inflated rating

### Coherence Analysis

"Skill Coherence" measures consistency across dimensions:
- High coherence (0.8-1.0): Balanced player profile (normal)
- Low coherence (<0.6): Imbalanced skills (possible enhancement in specific areas)

---

## Fatigue Detection

### Four Types of Fatigue Analysis

#### 1. **Within-Game Fatigue**

Detects declining performance _within_ a single game:

```python
analysis = FatigueDetector.analyze_fatigue(games, username)

if analysis.within_game_fatigue_detected:
    print(f"Accuracy drops {analysis.accuracy_decline:.1f}% from early to late game")
```

- **Early game accuracy**: Opening moves
- **Late game accuracy**: Endgame moves
- **Decline threshold**: >3% is significant

#### 2. **Session Fatigue**

Detects declining performance across a playing session:

- Assumes games within 8 hours are in same session
- Compares first game accuracy to last game accuracy
- Threshold: >2.5% decline is significant

#### 3. **Time-of-Day Effects**

Identifies when player performs best/worst:

```python
analysis.time_distribution  # Dict: "14:00-15:00" -> 78.5 accuracy
analysis.best_playing_time   # "10:00-11:00"
analysis.worst_playing_time  # "22:00-23:00"
```

Useful for:
- Understanding player's circadian rhythm
- Scheduling important games
- Detecting time zone changes (suggests account sharing?)

#### 4. **Overwork Detection**

Flags days with excessive playing:
- Alerts if >10 games played in single day
- Correlates with declining accuracy
- Suggests possible account sharing or automated play

### Interpretation

Fatigue patterns are **normal** but:
- **Persistent decline** across all metrics is suspicious
- **Sudden sharp drops** may indicate distraction, connection issues, or rapid-fire loses
- **Perfect consistency** (no fatigue) in marathon sessions is suspicious

---

## Network Analysis

### Collusion Detection

The system identifies suspicious groupings:

```python
network = NetworkAnalyzer.build_network(player_games, opponent_cutoff=3)

for clustering in network.clusters:
    print(f"Cluster: {clustering.players}")
    print(f"Density: {clustering.density:.1%}")  # Highly connected?
    print(f"Central player: {clustering.central_player}")
```

### What to Look For

**Suspicious Indicators**:
1. Players who play each other frequently but rarely others
2. Identical opening choices in cross-games
3. Performance correlation (one's accuracy directly matches another's)
4. Consistent color distribution (always same color against same player)

**Individual Metrics**:
- `correlation_coefficient`: Pearson correlation of play quality (>0.85 = suspicious)
- `opening_overlap`: Percentage of shared opening repertoire (>60% = unusual)
- `pattern_similarity`: Overall similarity of play style (>0.8 = suspicious)

### Example Scenario

```
Player A vs Player B:
- 15 mutual games (unusual frequency)
- Opening overlap: 85% (very high)
- Correlation: 0.92 (almost perfect)
- In 8/15 games, one player clearly tanks

Assessment: Highly suspicious collaboration
```

### Clusters & Communities

Detects groups where:
- All members play each other frequently
- Performance metrics are highly correlated
- May indicate circle of coordinated accounts

---

## Comprehensive Reporting

### Report Components

#### 1. **Executive Summary**
- Overall suspicion score (0-100) with gauge
- Confidence level
- Likelihood ratio
- Key recommendation

#### 2. **Individual Metric Breakdown**
Table showing for each metric:
- Value
- Percentile among peers
- Z-score
- Confidence level
- False positive risk
- Detailed context

#### 3. **Skill Profile Section**
- Skill radar chart
- Comparison to expected values
- Imbalance detection
- Tier classification (Beginner-Grandmaster)

#### 4. **Fatigue Analysis**
- Within-game and session trends
- Time-of-day heatmap
- Consistency assessment
- Recommendations for improvement

#### 5. **Comprehensive Disclaimer**

All reports include:
- "Statistical nature, cannot prove violations"
- "High scores may reflect legitimate skill"
- "All conclusions require expert human review"
- "False positives are possible"
- "Final judgment rests with Chess.com/Lichess"

### Output Formats

1. **HTML Report**: Professional, formatted for web/PDF export
2. **Text Report**: Console-friendly summary
3. **JSON Export**: Programmatic access to all metrics

---

## Multi-Player Comparison

### Comparing Two Players

```python
comparison = MultiPlayerAnalyzer.compare_two_players(
    player1_data,
    player2_data,
    "Player A",
    "Player B"
)

for advantage in comparison.advantage_indicators:
    print(f"• {advantage}")
```

**Output**:
```
• Player A better on centipawn_loss
• Player B better on win_rate
• Player A better on consistency
```

### Comparing Multiple Players

```python
players_data = {
    'player1': {'rating': 2000, 'accuracy': 76, ...},
    'player2': {'rating': 1950, 'accuracy': 82, ...},
    'player3': {'rating': 2100, 'accuracy': 75, ...}
}

comparison = MultiPlayerAnalyzer.compare_multiple_players(players_data)
```

**Results Include**:
- Rankings on each metric
- Clustering (groups of similar-strength players)
- Outliers (players significantly different from group)

### Tournament Performance Analysis

```python
stats = MultiPlayerAnalyzer.assess_tournament_performance(
    tournament_games,
    players_list
)

for player, stats in stats.items():
    print(f"{player}: Score {stats['score']}/{stats['games']}, Rating {stats['performance_rating']}")
```

---

## Usage Examples

### Example 1: Basic Player Suspicion Analysis

```python
from chess_analyzer import fetcher, analyzer
from chess_analyzer.advanced_detection import AdvancedCheatDetector

# Fetch games
games = fetcher.fetch_lichess_games('suspicious_player', num_games=20)

# Analyze
game_metrics = analyzer.analyze_games_fast(games)

# Detect suspicion
detector = AdvancedCheatDetector()
suspicion = detector.compute_suspicion_score(game_metrics, player_rating=1950)

print(f"Suspicion: {suspicion.overall_suspicion:.1f}%")
print(f"Recommendation: {suspicion.recommendation}")
```

### Example 2: Opponent Analysis for Championship

```python
from chess_analyzer.opponent_analysis import OpponentAnalyzer

# Get all games against opponent
opponent_games = fetcher.get_opponent_games('my_username', 'opponent_name')

# Build profile
profile = OpponentAnalyzer.build_profile(opponent_games, 'opponent_name')

# Find weaknesses
weaknesses = OpponentAnalyzer.get_vulnerability_summary(profile)

print(f"Weak openings: {weaknesses['weak_openings']}")
print(f"Weak phases: {weaknesses['weak_phases']}")
```

### Example 3: Tournament Fairness Analysis

```python
from chess_analyzer.multi_player_analysis import MultiPlayerAnalyzer

# Analyze all tournament games
tournament_data = load_tournament_pgn('tournament.pgn')

# Get stats for each player
player_stats = {}
for player in tournament_data.players:
    p_games = [g for g in tournament_data.games if player in [g.white, g.black]]
    player_stats[player] = analyze_player_games(p_games)

# Compare all players
comparison = MultiPlayerAnalyzer.compare_multiple_players(player_stats)

# Check for outliers/suspicious players
for player in comparison.outliers:
    print(f"⚠️ {player} is an outlier in this tournament")
```

### Example 4: Network Analysis for Collusion

```python
from chess_analyzer.network_analyzer import NetworkAnalyzer

# Load games from multiple accounts
player_games = {
    'account1': fetch_games('account1'),
    'account2': fetch_games('account2'),
    'account3': fetch_games('account3'),
    # ... more accounts
}

# Build network
network = NetworkAnalyzer.build_network(player_games, opponent_cutoff=2)

if network.colluding_pairs_found > 0:
    print(f"Suspicious pairs: {len(network.suspicious_edges)}")
    
    for edge in network.suspicious_edges[:5]:
        print(f"\n{edge.player1} ↔ {edge.player2}")
        print(f"  Correlation: {edge.correlation_coefficient:.2f}")
        print(f"  Opening overlap: {edge.opening_overlap:.1%}")
        print(f"  Games: {edge.mutual_games}")
```

---

## Interpretation Guide

### When to Trust High Suspicion Scores

✅ **Suspicious score is reliable when**:
- Multiple metrics (3+) are flagged
- Confidence level > 70%
- Sample size > 15 games
- Metrics are independent (not just high CPL causing all issues)
- Recent pattern (not old data)

### When to Discount High Scores

⚠️ **Be cautious when**:
- Small sample size (<10 games)
- Single metric is flagged
- Confidence < 60%
- False positive risk > 20%
- Recent rating improvement (could be natural)
- Time control difference (blitz vs classical)

### Natural vs Suspicious Patterns

**NATURAL**:
- Random variance in accuracy (±5-10%)
- Gradual rating improvement
- Opening specialization
- Strong games interspersed with weaker ones
- Better performance vs lower-rated opponents
- Fatigue in marathon sessions

**SUSPICIOUS**:
- Sudden +200 rating jump in weeks
- Consistent >95% engine correlation
- Perfect error avoidance (<0.5% mistakes)
- All games follow identical opening/strategy
- Superhuman consistency across 30+ games
- Impossible move timing (< 0.2 seconds for complex positions)

### False Positive Examples

High suspicion doesn't always mean cheating:

1. **Tournament Victory**: GM crushes field → high metrics but legitimate
2. **Preparation**: Study in strong opening → high accuracy in matches
3. **Rating Inflation**: Player inflated from initial games, appears to improve
4. **Surge After Break**: Rested player plays well for a week
5. **Against Lower Opposition**: Player performs spectacularly vs weaker opponents

---

## Limitations & Disclaimers

### Important Limitations

1. **Statistical, Not Definitive**: All metrics are probabilistic, not proof
2. **Context Dependency**: Same metrics mean different things in different contexts
3. **Small Sample Size**: <10 games carry high false positive risk
4. **Time Control Matters**: Patterns in blitz ≠ classical
5. **Rating Calibration**: System calibrated to Chess.com/Lichess, not all platforms
6. **No Psychological Factors**: Cannot detect motivation, tilt, distraction
7. **Engine Strength Varies**: Different Stockfish depths give different correlations

### False Positive Risks

According to research:
- Single metric: **20-40% false positive rate**
- Two independent metrics: **5-10% false positive rate**
- Three+ independent metrics: **<5% false positive rate**

### What This Tool CANNOT Do

❌ Prove rule violations (only Statistical indicators)
❌ Distinguish between improvement and cheating
❌ Account for coaching or preparation
❌ Detect subtle collusion patterns
❌ Determine engine choice/strength
❌ Prove who is using computer on an account
❌ Make final rulings (only provides evidence)

### What This Tool CAN Do

✅ Flag suspicious patterns for expert review
✅ Provide multiple independent signals
✅ Quantify confidence and uncertainty
✅ Identify anomalies in data
✅ Support professional investigations
✅ Reduce false positives vs single-metric systems
✅ Provide transparency in methodology

---

## References & Sources

1. **Ken Regan's Research**: Rybka Controversy analysis, pattern recognition
2. **Chess.com Fair Play**: Modern detection methodology
3. **Lichess Anti-Cheat**: Statistical approaches to cheat detection
4. **Academic Papers**: Probabilistic detection methods in competitive games

---

## Contact & Support

For questions about interpretation or methodology:
- Consult the research papers mentioned above
- Review confidence intervals and false positive risk
- Always involve domain experts for final decisions
- Remember: This tool provides statistical evidence, not proof

**Last Updated**: February 7, 2026
**Version**: 3.3+
