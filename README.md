# ♟️ Chess Detective v2.2.1

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Chess.com API](https://img.shields.io/badge/API-Chess.com-orange)](https://www.chess.com/news/view/published-data-api)
[![Stockfish](https://img.shields.io/badge/Engine-Stockfish%2016-red)](https://stockfishchess.org/)

A comprehensive, production-ready forensic analysis tool for detecting potential computer assistance in chess games and analyzing player behavior using advanced statistical techniques similar to Chess.com's Fair Play detection system.

> ⚠️ **IMPORTANT**: This tool provides statistical indicators only, not proof of cheating. Final judgment always rests with Chess.com's Fair Play team and relevant authorities.

---

## 🎯 What's New in v2.2.1

### Major Enhancement: "Exploit Your Opponent" Feature ⭐
Completely rewritten with **300+ lines** of detailed analysis code:

- **Comprehensive Opening Analysis**: Detailed breakdown of all openings (ECO codes) with win rates
- **Weakness Detection**: Automatically identifies exploitable weaknesses (< 30-40% win rate)
- **Phase-Based Strategies**: Opening, Middlegame, Endgame strength analysis with tactical recommendations
- **Time Control Exploitation**: Identifies which time controls expose player weaknesses
- **Color-Based Strategy**: Shows which color the player struggles with
- **Severity Classification**: Marks weaknesses as CRITICAL (< 30%), WEAK (< 40%), or VULNERABLE
- **Specific Exploitation Strategies**: Tactical advice for each identified weakness

### All Other Features - Improved for v2.2.1
- Enhanced Multi-Player Comparison with better outlier detection
- Improved Fatigue Detection with more granular metrics
- Advanced Network Analysis with pattern detection
- Upgraded Visual Dashboard for better insights
- Additional Account Metrics and behavioral analysis

**See [README_v2.2.1.md](README_v2.2.1.md) for complete documentation**

#### 1. **Analyze Player** - Detect Suspicious Activity
- Comprehensive cheating detection across 50+ games
- Three analysis speed options: Fast (depth 12), Standard (depth 14), Thorough (depth 16)
- Exports suspicious games to PGN and ZIP formats
- Statistical thresholds customizable in settings
- Real-time progress tracking

#### 2. **Download All Games** - Export Game History
- Export complete player game history in 4 formats:
  - **Individual PGN** - Each game as separate file
  - **Combined PGN** - All games in single file
  - **CSV** - Spreadsheet-compatible analysis data
  - **ZIP Archive** - All formats combined
- Choose: Most recent games OR oldest first
- Choose: All games OR specific count
- Automatic timestamp naming for organization

#### 3. **PlayerBrain** - Player Profile & Style Analysis
- Comprehensive player personality assessment
- Opening repertoire analysis with ECO codes
- Win rate tracking by opening
- **Phase Strength Analysis**: Opening, Middlegame, Endgame performance
- Overall statistics: Wins/Losses/Draws with percentages
- Playing style classification and recommendations

#### 4. **Strength Profile** - Skill Level Analysis
- Estimated skill level classification (Super-GM to Beginner)
- Performance metrics by time control (Blitz, Rapid, Classical, etc.)
- Average opponent strength assessment
- Consistency rating across formats
- Playing style insights and recommendations

#### 5. **Accuracy Report** - Move Accuracy & Consistency
- Comprehensive move accuracy analysis (30+ games)
- Accuracy by game phase, result, and opponent strength
- Error analysis: Blunders vs inaccuracies
- Consistency trends and improvement tracking
- AI-generated recommendations

#### 6. **View Reports** - Report Management
- Browse and manage all generated reports
- Quick access to HTML and JSON analysis
- Report organization and filtering

#### 7. **Settings** - Full Configuration Menu
- Engine configuration, cache management, report settings
- Chess.com API customization
- View current configuration and reset to defaults

---

## 📊 Features Overview

### Core Capabilities
- ✅ **Game Analysis**: Move-by-move Stockfish evaluation (depth 12-16)
- ✅ **Statistical Detection**: Engine correlation, ACPL, consistency metrics
- ✅ **Multi-Format Export**: PGN, CSV, JSON, ZIP archives
- ✅ **Player Profiling**: 5 unique analysis perspectives per player
- ✅ **Real-time Feedback**: Progress bars, time estimates, live results
- ✅ **Configurable Analysis**: Speed presets, customizable thresholds
- ✅ **Cache System**: Automatic game caching to speed up repeated analysis

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+**
- **Stockfish 16** (included)
- **Chess.com Account** (for public game data)

### Quick Start (Windows)

```powershell
# 1. Clone repository
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the menu
python run_menu.py
```

### macOS/Linux

```bash
# 1. Clone repository
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run the menu
python3 run_menu.py
```

---

## 📖 Usage Guide

### Running the Application

```bash
python run_menu.py
```

### Main Menu Options

```
MAIN MENU
==================================================
1. Analyze Player (Detect Suspicious Activity)
2. Download All Games (Export Game History)
3. PlayerBrain (Player Profile & Style Analysis)
4. Strength Profile (Skill Level Analysis)
5. Accuracy Report (Move Accuracy & Consistency)
6. View Reports
7. Settings
8. Exit
==================================================
```

### Usage Examples

#### Example 1: Analyze Player for Suspicious Activity
```
Select option (1-8): 1
Enter Chess.com username: magnuscarlsen
Games to analyze (default 50): 50

[Analyzing... Progress: 50/50]
✓ Analysis complete!

SUSPICIOUS INDICATORS FOUND:
- Engine Correlation: 94.2% (⚠️ Red Flag)
- ACPL Difference: 18.5 (⚠️ Red Flag)

Suspicious games exported to: exports/suspicious_magnuscarlsen.pgn
```

#### Example 2: Download Player's Games
```
Select option (1-8): 2
Enter Chess.com username: hansniemann

Choose export format:
1. Individual PGN files
2. Combined PGN file
3. CSV spreadsheet
4. ZIP archive (all formats)
Choose (1-4): 4

✓ Retrieved 150 games
✓ Exported to: exports/hansniemann_games_20260117.zip
```

#### Example 3: PlayerBrain Analysis
```
Select option (1-8): 3
Enter Chess.com username: penguingm

PLAYERBRAIN ANALYSIS
==================================================

📊 OVERALL STATISTICS (30 games)
  Wins: 18 (60.0%)
  Losses: 8 (26.7%)
  Draws: 4 (13.3%)

💪 PHASE STRENGTH
  Opening: 72.5% accuracy
  Middlegame: 68.3% accuracy
  Endgame: 75.1% accuracy

🎯 OPENING REPERTOIRE
  1. Sicilian Defense (C99): 6 games, 66.7% win rate
  2. French Defense (C11): 4 games, 75.0% win rate
  3. Ruy Lopez (C80): 3 games, 100.0% win rate
```

#### Example 4: Strength Profile
```
Select option (1-8): 4
Enter Chess.com username: alireza2003

🏆 ESTIMATED SKILL LEVEL: Super-GM (2700+)

📊 OVERALL METRICS
  Average Opponent ELO: 2485
  Overall Win Rate: 68.4%

⏱️  PERFORMANCE BY TIME CONTROL
  Blitz: 62.1% win rate
  Rapid: 71.3% win rate
  Classical: 75.8% win rate
```

#### Example 5: Accuracy Report
```
Select option (1-8): 5
Enter Chess.com username: levon_aronian

🎯 OVERALL ACCURACY
  Average Accuracy: 76.3%
  Best Game: 92.5%
  Worst Game: 48.1%
  Rating: ✓ Very Good

📊 ACCURACY BY GAME PHASE
  OPENING: 82.1%
  MIDDLEGAME: 74.5%
  ENDGAME: 72.8%
```

---

## ⚙️ Configuration

### config.yaml

```yaml
chess_com:
  api_base: "https://api.chess.com/pub/player"
  request_delay: 1.0
  max_games: 100
  cache_enabled: true
  cache_dir: "cache"

analysis:
  use_lichess: false
  engine_depth: 14
  engine_path: "stockfish/stockfish-windows-x86-64.exe"
  threads: 2
  hash_size: 256
  thresholds:
    engine_correlation_red_flag: 92.0
    avg_centipawn_loss_red_flag: 15.0
    accuracy_fluctuation_red_flag: 25.0
    min_games_for_analysis: 5

report:
  default_format: "html"
  output_dir: "reports"
  highlight_suspicious: true
  save_analysis_data: true
```

---

## 📁 Project Structure

```
chess-fairplay-analyzer/
├── chess_analyzer/
│   ├── analyzer.py           # Core analysis engine
│   ├── engine.py             # Stockfish integration
│   ├── fetcher.py            # Chess.com API client
│   ├── menu.py               # Interactive menu system ⭐ v2.0
│   ├── reporter.py           # Report generation
│   ├── stats.py              # Statistical calculations
│   └── utils/
│       └── helpers.py        # Utility functions
├── stockfish/
│   └── stockfish-windows-x86-64.exe
├── config.yaml               # Configuration
├── run_menu.py               # ⭐ v2.0 Menu launcher
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

---

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_syntax.py
```

### Testing

```bash
# Test imports and basic functionality
python test_syntax.py

# Test specific features
python test_quick.py           # Quick analysis test
python test_multi_game.py      # Multi-game analysis
python test_menu.py            # Menu interface test
```

---

## ⚙️ Analysis Details

### Detection Metrics

1. **Engine Move Correlation**: % of moves matching Stockfish's top choice
2. **Average Centipawn Loss (ACPL)**: Average evaluation loss per move
3. **Performance Consistency**: Standard deviation of accuracy across games
4. **Time Control Analysis**: Performance across different time controls

### Performance Metrics

- **Fast Mode (Depth 12)**: ~40 seconds per game
- **Standard Mode (Depth 14)**: ~60-90 seconds per game
- **Thorough Mode (Depth 16)**: ~120-180 seconds per game

---

## 🐛 Troubleshooting

### Issue: Stockfish Not Found
**Solution**: 
- Ensure `stockfish-windows-x86-64.exe` exists in `stockfish/` directory
- Or set `engine_path` in `config.yaml`

### Issue: Chess.com API Rate Limiting
**Solution**:
- Increase `request_delay` in `config.yaml`
- Wait a few minutes and retry

### Issue: Out of Memory
**Solution**:
- Reduce `hash_size` in `config.yaml`
- Analyze fewer games at once

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Credits

- **Stockfish**: Chess engine by Tord Romstad, Marco Costalba, Joona Kiiski, Gary Linscott
- **Chess.com**: Public API for game data
- **python-chess**: Python chess library

---

## 🤝 Contributing

Contributions are welcome! Fork, create a feature branch, commit your changes, and open a Pull Request.

---

## 📞 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/hanifkhan7/chess-fairplay-analyzer/issues)
- **Email**: hnfitsme@gmail.com

---

## ⚖️ Legal & Ethical Statement

This tool is designed for:
- ✅ Personal chess analysis and improvement
- ✅ Research and educational purposes
- ✅ Supporting Chess.com's Fair Play investigations (with authorization)

This tool should NOT be used for:
- ❌ Harassing or defaming chess players
- ❌ Making unfounded public accusations
- ❌ Circumventing Chess.com's terms of service

**Remember**: Statistical indicators are not proof. Always respect the integrity of chess and the rights of all players.

---

**Last Updated**: January 19, 2026  
**Version**: 2.2.1  
**Status**: Production Ready ✅
