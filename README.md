# ♟️ Chess Fairplay Analyzer v3.4

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Lichess API](https://img.shields.io/badge/API-Lichess-blue)](https://lichess.org/api)
[![Chess.com API](https://img.shields.io/badge/API-Chess.com-orange)](https://www.chess.com/news/view/published-data-api)
[![Stockfish](https://img.shields.io/badge/Engine-Stockfish%2016-red)](https://stockfishchess.org/)
[![TensorFlow](https://img.shields.io/badge/ML-TensorFlow%202.13-orange)](https://www.tensorflow.org/)

**Production-Ready Chess Analysis Platform with ML-Powered Cheat Detection, Forensic Analysis & Strategic Insights**

A comprehensive, production-ready tool for analyzing player behavior, detecting suspicious activity patterns, and predicting match outcomes using AI-powered analysis similar to Chess.com's Fair Play detection system.

> ⚠️ **IMPORTANT**: This tool provides statistical indicators only. Final judgment always rests with Chess.com/Lichess Fair Play teams and relevant authorities.

---

## 🚀 Quick Start

### Installation (All Platforms)

#### **Windows**
```bash
# 1. Clone repository
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run setup (downloads Stockfish)
python setup.py

# 5. Start the analyzer
python run_menu.py
```

#### **Linux/macOS**
```bash
# 1. Clone repository
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run setup (downloads Stockfish)
python setup.py

# 5. Start the analyzer
python run_menu.py
```

#### **Termux (Android)**
```bash
# 1. Install Python and dependencies
pkg install python python-pip git clang make

# 2. Clone repository
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate

# 4. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 5. Download Stockfish for Termux (ARM64)
mkdir -p stockfish
cd stockfish
wget https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-android
chmod +x stockfish-android
cd ..

# 6. Update config.yaml
# Set STOCKFISH_PATH: stockfish/stockfish-android

# 7. Start the analyzer
python run_menu.py
```

---

## 📋 Features (15 Menu Options)

### Analysis Features
1. **Analyze Player** - Detect suspicious activity patterns
2. **Download & Analyze Games** - Export and analyze game history
3. **Exploit Your Opponent** - Opening & style analysis(modified)
4. **Strength Profile** - Skill level assessment
5. **Accuracy Report** - Move-by-move accuracy analysis
6. **Account Metrics Dashboard** - Quick statistical overview
7. **Multi-Player Comparison** - Compare multiple players side-by-side
8. **Fatigue Detection** - Identify performance degradation patterns
9. **Network Analysis** - Opponent network mapping
10. **Opening Repertoire & Player DNA** ⭐ - Deep opening analysis + statistical DNA(modified)
11. **Tournament Inspector** - Head-to-Head Analysis
12. **Head-to-Head Matchup** - Predict match outcomes with 5-factor analysis
13. **View Reports** - Browse generated reports
14. **Settings** - Configuration management
15. **Anti-Repertoire Builder** - Build specialized repertoires against opponent weaknesses
16. **Exit** - Quit program

### Opening Repertoire & Player DNA ⭐ (ENHANCED)
Choose between two powerful opening analyses:

**Option 1: Traditional Opening Repertoire**
- Opening tree visualization
- Win rates by opening
- Performance statistics
- D3.js interactive tree
- Exportable CSV/Excel

**Option 2: Player DNA (NEW)**
Comprehensive opening intelligence system:
- Merges 1000+ games into statistical tree
- Shows exactly how player actually plays openings
- Move statistics: frequency, win rate, draw %, loss %
- Professional PGN generation with annotations
- Tree depth: Full detail until move 15, medium until 20
- Identifies: Most trusted openings, surprise weapons, weak lines, favorite variations
- **Output**: PGN file + text report showing complete opening identity

#### 4. **Strength Profile** - Skill Level Analysis
- Estimated skill level classification
- Performance metrics by time control
- Average opponent strength assessment
- Consistency rating across formats

#### 5. **Accuracy Report** - Move Accuracy & Consistency
- Comprehensive move accuracy analysis
- Accuracy by game phase
- Error analysis: Blunders vs inaccuracies
- Consistency trends and improvement tracking

#### 6. **Account Metrics Dashboard** - Quick View
- Behavioral analysis summary
- Rating progression patterns
- Move timing analysis
- Opponent strength anomalies

#### 7. **Multi-Player Comparison** - Compare Multiple Players
- Side-by-side comparison
- Anomaly detection and outlier identification
- Performance ranking and metrics
- Statistical significance testing

#### 8. **Fatigue Detection** - Identify Playing Patterns
- Session-based degradation scoring
- Performance decline tracking
- Fatigue severity classification
- Time-based pattern analysis

#### 9. **Network Analysis** - Opponent Connections
- Opponent concentration analysis
- Suspicious pattern detection
- Relationship mapping
- Network connectivity metrics

#### 10. **Opening Repertoire Inspector** - Deep Opening Analysis
- Opening repertoire map with win rates
- Pattern library and strategy clustering
- Exploitation recommendations
- Vulnerability scorecard

#### 11. **Leaderboard Browser** - Browse Top Players
- Lichess top players by country
- Quick filtering and sorting
- Direct player analysis

#### 12. **View Reports** - Report Management
- Browse and manage all generated reports
- Quick access to HTML and JSON analysis

#### 13. **Settings** - Configuration Menu
- Engine configuration and cache management
- API customization
- View current configuration

---

## 🎯 Key Features

### Game Analysis
- ✅ Stockfish engine integration (depth 12-16 configurable)
- ✅ Move-by-move accuracy evaluation
- ✅ Engine correlation detection
- ✅ Blunder and critical move analysis
- ✅ Opening, middlegame, endgame phase analysis

### Player Profiling
- ✅ Win rate by time control
- ✅ Opening repertoire analysis
- ✅ Performance metrics tracking
- ✅ Rating progression analysis
- ✅ Opponent strength assessment

### Multi-Player Tools
- ✅ Side-by-side comparison
- ✅ Head-to-head matchup prediction
- ✅ Network analysis and clustering
- ✅ Fatigue pattern detection
- ✅ Leaderboard browsing

### Export & Reporting
- ✅ PGN export (single/batch)
- ✅ CSV spreadsheets
- ✅ JSON reports
- ✅ ZIP archives
- ✅ Suspicious game flagging

---

## ⚙️ System Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| Python | 3.8+ | Required |
| RAM | 2GB min (4GB rec) | More for batch analysis |
| Disk | 500MB+ | For Stockfish + cache |
| Internet | Required | API calls to Lichess/Chess.com |
| Stockfish | 16+ | Auto-downloaded in setup |

### Platform Support

| Platform | Support | Notes |
|----------|---------|-------|
| Windows | ✅ | 10/11, x86-64 & ARM64 |
| Linux | ✅ | Ubuntu, Debian, Fedora |
| macOS | ✅ | Intel & Apple Silicon |
| Termux | ✅ | Android (ARM64) |
| WSL2 | ✅ | Use Linux instructions |

---

## 🔧 Configuration

### `config.yaml`
```yaml
DEFAULT_PLATFORM: 'lichess'
STOCKFISH_PATH: 'stockfish/stockfish-16-64-bmi2'
ANALYSIS_DEPTH: 14
THREADS: 4
CACHE_DIR: 'cache'
MAX_CACHE_SIZE: 500
EXPORT_FORMAT: 'json'
REPORT_DIR: 'reports'
```

---

## 📦 Dependencies

Automatically installed via `requirements.txt`:
- requests - API calls
- chess - Game handling
- pyyaml - Configuration
- pandas - Data analysis (optional)

---

## 💡 Usage Examples

### Analyze a Player
```bash
python run_menu.py
# Select 1: Analyze Player
# Enter username: hikaru
# Choose analysis speed
```

### Head-to-Head Matchup
```bash
python run_menu.py
# Select 12: Head-to-Head Matchup
# Player 1: hikaru
# Player 2: gmhikaru
# Games to analyze: 50
```

### Download Games
```bash
python run_menu.py
# Select 2: Download All Games
# Enter username: alireza2003
# Choose export format: 4 (ZIP all)
```

---

## 📊 Output Example

```
┌─ PLAYER 1 STATISTICS ──────────────────────────────────────────────────────┐
│ Username: hikaru                                                                  │
│ Rating: ~2800                                                                    │
│ Games Analyzed: 50                                                        │
│ Win Rate: 78.0%  Wins: 39 | Losses: 9 | Draws: 2                              │
│ Favorite Openings:                                                           │
│   Italian Game                     8 games (87.5% WR) │
│   Sicilian Defense                 12 games (83.3% WR) │
│   French Defense                   6 games (66.7% WR) │
└────────────────────────────────────────────────────────────────────────────┘

┌─ PREDICTION ───────────────────────────────────────────────────────────────┐
│ PREDICTED WINNER: hikaru                                                     │
│ CONFIDENCE LEVEL: 78.5%                                                          │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 Performance

### Analysis Speed (per player, 50 games)
- Fast Mode: ~2-3 minutes
- Standard Mode: ~5-8 minutes
- Thorough Mode: ~15-20 minutes

### API Rate Limiting
- Lichess: 40 req/min (automatic throttling)
- Chess.com: 20 req/sec (implemented)
- Caching enabled to minimize calls

---

## 🐛 Troubleshooting

### Stockfish not found
```bash
python setup.py
# Or update config.yaml with correct path
```

### API rate limited
```bash
# Use cached games or wait 60 seconds
# Check status for API quota
```

### Termux issues
```bash
# Verify ARM64:
uname -m  # Should show aarch64

# Check permissions:
chmod +x stockfish/stockfish-android

# Update config with direct path
```

---

## 📁 File Structure

```
chess-fairplay-analyzer/
├── chess_analyzer/
│   ├── analyzer_v3.py
│   ├── head_to_head_analyzer.py
│   ├── dual_fetcher.py
│   ├── menu.py
│   └── ...
├── stockfish/
├── cache/
├── reports/
├── config.yaml
├── requirements.txt
├── setup.py
├── run_menu.py
└── README.md
```

---

## 🔐 Privacy & Security

- No data stored externally
- Analysis runs locally
- No credentials saved
- Cache is local only
- Open source transparency

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📞 Support

- **Issues**: GitHub Issues
- **API Docs**: https://lichess.org/api
- **API Docs**: https://www.chess.com/news/view/published-data-api

---

## 🙏 Acknowledgments

- [Lichess.org](https://lichess.org) - Free chess API
- [Chess.com](https://chess.com) - Game API
- [Stockfish](https://stockfishchess.org/) - Chess engine
- [python-chess](https://python-chess.readthedocs.io/) - Chess library

---

**Built with ♟️ for the chess community**

*v3.4 - Released March 2026*
