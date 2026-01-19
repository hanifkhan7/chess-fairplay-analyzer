# ♟️ Chess Detective v2.2

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Chess.com API](https://img.shields.io/badge/API-Chess.com-orange)](https://www.chess.com/news/view/published-data-api)
[![Stockfish](https://img.shields.io/badge/Engine-Stockfish%2016-red)](https://stockfishchess.org/)

A comprehensive, production-ready forensic analysis tool for detecting potential computer assistance in chess games and analyzing player behavior using advanced statistical techniques similar to Chess.com's Fair Play detection system.

> ⚠️ **IMPORTANT**: This tool provides statistical indicators only, not proof of cheating. Final judgment always rests with Chess.com's Fair Play team and relevant authorities.

---

## 🎯 What's New in v2.2

### Advanced Analytics & Network Analysis
- **Multi-Player Comparison**: Compare statistics across multiple players
- **Fatigue Detection**: Detect performance degradation over long sessions
- **Network Analysis**: Analyze opponent networks and playing patterns
- **Visual Dashboard**: Generate publication-quality charts and graphs

---

## 📋 Complete Feature List

### 🎮 **Core Features (v2.0-2.1)**

#### 1. **Analyze Player** - Detect Suspicious Activity
- Comprehensive cheating detection analysis
- Three analysis speed options: Fast (depth 12), Standard (depth 14), Thorough (depth 16)
- Exports suspicious games to PGN and ZIP formats
- Statistical thresholds customizable in settings
- Real-time progress tracking with engine analysis

#### 2. **Download All Games** - Export Game History
- Export complete player game history in 4 formats:
  - Individual PGN files
  - Combined PGN file
  - CSV spreadsheet
  - ZIP archive with all formats
- Options for game ordering (recent first or oldest first)
- Batch download with automatic naming

#### 3. **Exploit your opponent** - Opening & Style Analysis
- Comprehensive player personality assessment
- Opening repertoire analysis with ECO codes
- Win rate tracking by opening type
- Phase strength analysis (Opening, Middlegame, Endgame)
- Playing style classification
- Strategic recommendations

#### 4. **Strength Profile** - Skill Level Analysis
- Estimated skill level classification (Super-GM to Beginner)
- Performance metrics by time control
- Average opponent strength assessment
- Format consistency evaluation
- Playing style insights

#### 5. **Accuracy Report** - Move Accuracy & Consistency
- Comprehensive move accuracy analysis
- Accuracy breakdown by game phase and result
- Error classification (Blunders vs inaccuracies)
- Consistency trend tracking
- Performance recommendations

#### 6. **Account Metrics Dashboard** - Quick View
- Real-time account summary (games, wins, draws, losses)
- Rating volatility analysis with trend detection
- Time management breakdown by control type
- Opening variety analysis with diversity scoring
- Opponent strength anomaly detection
- Game clustering and playing pattern analysis

---

### 🚀 **Advanced Features (v2.2)**

#### 7. **Multi-Player Comparison**
Compare up to multiple players simultaneously:

**Analysis Metrics:**
- Rating comparison (average, min, max)
- Win rate analysis across all players
- Rating volatility and trend comparison
- Opening repertoire diversity scoring
- Time control preference analysis
- Automatic anomaly detection

**Output:**
- Sorted player rankings by metric
- Comparative statistics tables
- Red flag highlighting for outliers
- Anomaly severity classification

**Use Cases:**
- Compare tournament competitors
- Analyze team performance
- Identify outliers in player pools
- Detect suspicious player clusters

#### 8. **Fatigue Detection**
Analyze performance degradation over long sessions:

**Detection Methods:**
1. **Session Analysis**
   - Groups games into playing sessions (2-hour windows)
   - Measures performance degradation within sessions
   - Calculates move quality changes
   - Reports fatigue indicators

2. **Progression Analysis**
   - Quarterly trend breakdown across all games
   - Overall trend direction (improving/stable/declining)
   - Long-term fatigue patterns
   - Performance consistency scoring

3. **Consistency Analysis**
   - Detects sudden performance drops (>20%)
   - Identifies game indices with drops
   - Calculates drop rate percentage
   - Highlights unusual patterns

**Output:**
- Session-by-session degradation percentages
- Fatigue rates and thresholds
- Trend direction with percentage change
- Consistency drop reports
- Severity classification

**Interpretation:**
- Fatigued sessions show >15% performance degradation
- Significant fatigue detected with >10% overall trend decline
- Sudden drops indicate possible tilt or external factors

#### 9. **Network Analysis**
Analyze opponent networks and playing patterns:

**Network Metrics:**
- Top 10 most frequently played opponents
- Win/loss/draw statistics against each opponent
- Playing circle detection by time control
- Opponent concentration levels

**Suspicious Pattern Detection:**
1. **High Concentration**: Too many games vs same opponent
   - Flags when >20% of games are vs single opponent
   - Severity levels: Medium (10-15%) / High (>15%)

2. **Unusual Win Rates**: Extreme win/loss ratios
   - Detects >80% win rate against specific opponents
   - Detects <20% loss rate patterns
   - Severity classification based on game count

3. **Limited Playing Circle**: Restricted opponent pool
   - Alerts if <5 unique opponents in 20+ games
   - Reports average games per opponent ratio
   - Indicates potential smurf accounts or limited access

**Output:**
- Top opponent rankings
- Playing circle grouping
- Concentration level visualization
- Anomaly severity classification
- Pattern-specific alerts

#### 10. **Visual Dashboard**
Generate publication-quality analysis charts:

**Chart Types:**
1. **Rating Trend Chart**
   - Line graph with trend line
   - Shows rating progression over games
   - Visual trend detection

2. **Win Rate Pie Chart**
   - Color-coded win/draw/loss distribution
   - Percentage labels
   - Overall score visualization

3. **Opening Distribution**
   - Bar chart of top 10 openings
   - Frequency counts
   - ECO code integration

4. **Performance by Time Control**
   - Stacked bar chart comparison
   - Wins/draws/losses by format
   - Format-specific performance analysis

**Output Format:**
- PNG export at 300 DPI (publication quality)
- Saved to `/reports/` directory
- Interactive display or batch export
- Professional formatting with color coding

---

## 💻 Installation & Setup

### Requirements
```bash
Python 3.8+
Chess.com API (free, no key required)
Stockfish 16 engine
```

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/hanifkhan7/chess-detective.git
cd chess-detective
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python run_menu.py
```

### Configuration
Edit `config.yaml` to customize:
- Engine depth (12-20 for analysis)
- API request delays
- Cache settings
- Report output formats
- Logging levels

---

## 🎯 Usage Guide

### Analyzing a Single Player
1. Select **Option 1: Analyze Player**
2. Enter Chess.com username
3. Choose number of games to analyze
4. Select analysis depth (Fast/Standard/Thorough)
5. Wait for engine analysis and report generation

### Comparing Multiple Players
1. Select **Option 7: Multi-Player Comparison**
2. Enter comma-separated usernames (e.g., `player1, player2, player3`)
3. Specify games per player to analyze
4. Review comparison tables and anomalies

### Detecting Fatigue
1. Select **Option 8: Fatigue Detection**
2. Enter player username
3. Choose game count
4. Analyze session-by-session degradation
5. Review fatigue trends and drop reports

### Analyzing Networks
1. Select **Option 9: Network Analysis**
2. Enter player username
3. Specify game count
4. Review opponent statistics
5. Check for suspicious patterns

### Generating Charts
1. Use **Option 6: Account Metrics Dashboard** to generate data
2. Charts auto-save to `/reports/` directory
3. Open PNG files in any image viewer
4. Share reports with colleagues/moderators

---

## 📊 Menu Structure

```
MAIN MENU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Analyze Player (Detect Suspicious Activity)
2. Download All Games (Export Game History)
3. Exploit your opponent (Opening & Style Analysis)
4. Strength Profile (Skill Level Analysis)
5. Accuracy Report (Move Accuracy & Consistency)
6. Account Metrics Dashboard (Quick View)
━━━━━━━━━━━━━━━━━ Advanced Analysis ━━━━━
7. Multi-Player Comparison
8. Fatigue Detection
9. Network Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. View Reports
11. Settings
12. Exit
```

---

## 🔍 Analysis Thresholds

### Cheating Detection (Option 1)
- **Engine Correlation**: >92% = Red Flag
- **Centipawn Loss**: >15 = Concern
- **Accuracy Fluctuation**: >25% = Suspicious

### Fatigue Detection (Option 8)
- **Session Degradation**: >15% = Fatigued
- **Overall Trend**: >-10% = Significant Fatigue
- **Consistency Drop**: >20% = Sudden Drop

### Network Analysis (Option 9)
- **High Concentration**: >10% games vs single opponent
- **Unusual Win Rate**: >80% or <20% against opponent
- **Limited Circle**: <5 opponents in 20+ games

### Rating Volatility (Option 6)
- **Very Stable**: <2% coefficient of variation
- **Stable**: 2-5% variation
- **Moderate**: 5-10% variation
- **Volatile**: >10% variation

---

## 📈 Statistical Methods

### Rating Progression
- Linear regression trend detection
- Quarterly trend analysis
- Confidence interval calculations
- Volatility scoring (0-100)

### Move Time Patterns
- Coefficient of variation analysis
- Repeated timing detection
- Distribution pattern analysis
- Anomaly identification

### Opponent Network
- Connection graph analysis
- Clustering coefficient calculation
- Network density measurement
- Community detection

### Fatigue Patterns
- Moving average degradation
- Quarterly breakdown analysis
- Sudden drop detection (>20%)
- Session-based pattern recognition

---

## 🛠️ Technical Details

### Project Structure
```
chess-detective/
├── chess_analyzer/
│   ├── __init__.py
│   ├── analyzer.py          # Core cheating detection
│   ├── account_metrics.py   # Account analysis
│   ├── comparison.py        # Multi-player comparison
│   ├── dashboard.py         # Metrics dashboard
│   ├── fatigue.py          # Fatigue detection
│   ├── network.py          # Network analysis
│   ├── visual_dashboard.py # Chart generation
│   ├── menu.py             # Menu system
│   ├── fetcher.py          # Chess.com API
│   ├── stats.py            # Statistical functions
│   └── utils/
│       └── helpers.py       # Utility functions
├── stockfish/              # Engine binaries
├── reports/                # Generated reports
├── cache/                  # Cached game data
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
└── README.md              # This file
```

### Dependencies
- `python-chess`: PGN parsing and analysis
- `requests`: Chess.com API requests
- `matplotlib`: Chart generation
- `numpy`: Statistical calculations
- `pyyaml`: Configuration management

---

## 🔐 Data Privacy

- All analysis is **local only**
- No data sent to external servers (except Chess.com API for public game data)
- Configuration file contains no sensitive information
- Reports saved locally in `/reports/` directory
- Cache stored in `/cache/` directory (can be cleared anytime)

---

## 📝 Output Examples

### Multi-Player Comparison Output
```
RATING COMPARISON
Player          Avg Rating    Min      Max      Games
player1         2150          2100     2200     50
player2         2080          2050     2150     50
player3         2200          2150     2280     50

WIN RATE COMPARISON
Player          Win %    Wins    Draws    Losses    Games
player1         55.0%    27      6        17        50
player2         52.0%    26      0        24        50
player3         58.0%    29      0        21        50
```

### Fatigue Detection Output
```
SESSION FATIGUE ANALYSIS
Session 1: 10 games
  Performance Degradation: 8.5% ✓ Normal
  Early Session Avg Moves: 42.3
  Late Session Avg Moves: 38.6

DETECTED ANOMALIES & OUTLIERS
⚠️  No significant anomalies detected
```

### Network Analysis Output
```
TOP OPPONENTS
Rank    Opponent         Games    W-D-L        Win %
1       opponent1        15       10-1-4       66.7%
2       opponent2        12       8-2-2        66.7%
3       opponent3        11       7-1-3        63.6%

SUSPICIOUS PATTERNS DETECTED
⚠️  High Concentration:
  • opponent1: 15 games (30%) [HIGH]
```

---

## 🚀 Performance

- **Analysis Speed**: 40-180 seconds per game (depends on depth)
- **Memory Usage**: ~500MB for 100 games
- **Concurrent Players**: Can analyze 1 at a time (API limited)
- **Storage**: ~100KB per 50 games (PGN files)

---

## 🐛 Troubleshooting

### No games found for player
- Check username spelling (case-insensitive)
- Player may have no public games
- Try increasing game count limit

### Engine analysis very slow
- Reduce engine depth in settings (12 vs 16)
- Close other applications
- Check Stockfish path in config.yaml

### Chart generation fails
- Ensure matplotlib is installed: `pip install matplotlib`
- Check disk space in `/reports/` directory
- Verify write permissions

### API rate limiting
- Add delay between requests in config.yaml
- Limit concurrent analyses
- Cache is automatically used for repeated queries

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push and create pull request

---

## 📞 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check documentation
- Review config.yaml settings

---

## ⚠️ Legal Disclaimer

This tool is for **educational and authorized analysis only**. Users are responsible for ensuring they have permission to analyze player games and data. Misuse of this tool for unauthorized analysis or harassment is prohibited.

**Chess.com's Terms of Service**: All data is subject to Chess.com's API terms. This tool respects fair use principles and does not violate Chess.com policies.

---

## 🎓 Educational Resources

- [Chess.com API Documentation](https://www.chess.com/news/view/published-data-api)
- [Stockfish Documentation](https://stockfishchess.org/)
- [Python Chess Library](https://python-chess.readthedocs.io/)

---

**Version**: 2.2.0  
**Last Updated**: January 19, 2026  
**Status**: Production Ready ✓
