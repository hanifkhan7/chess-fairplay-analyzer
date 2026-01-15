# ♟️ Chess Fairplay Analyzer

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Chess.com API](https://img.shields.io/badge/API-Chess.com-orange)](https://www.chess.com/news/view/published-data-api)

A modern forensic analysis tool for detecting potential computer assistance in chess games using advanced statistical techniques similar to Chess.com's Fair Play detection system.

⚠️ **IMPORTANT**: This tool provides statistical indicators only, not proof of cheating. Final judgment always rests with Chess.com's Fair Play team.

## ✨ Features

- **📥 Game Fetching**: Retrieve player's complete public game history from Chess.com API
- **🤖 Engine Analysis**: Integrates with Stockfish for move-by-move analysis
- **📊 Statistical Detection**: Calculates key cheating indicators:
  - Engine Move Correlation (% of moves matching Stockfish's top choice)
  - Average Centipawn Loss (ACPL)
  - Performance Consistency Analysis
  - Time Control Performance Comparison
- **📄 Multi-Format Reports**: Generate HTML, text, or JSON reports
- **⚡ Parallel Processing**: Analyze multiple games simultaneously
- **🔒 Ethical Design**: No automated reporting - analysis only for human review

## 📸 Screenshots

### HTML Report Preview
![HTML Report](https://via.placeholder.com/800x400.png?text=HTML+Report+with+Charts+and+Visualizations)

### Command Line Interface
```bash
chess-analyzer magnuscarlsen --games 50 --format html
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Stockfish chess engine
- Chess.com account (for accessing public games)

### Installation

#### Windows
```powershell
# Clone the repository
git clone https://github.com/yourusername/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# Install Python dependencies
pip install -r requirements.txt

# Install Stockfish (download from https://stockfishchess.org/download/)
# Extract to C:\Users\YourUsername\stockfish\

# Install the analyzer package
pip install -e .
```

#### Linux/macOS
```bash
# Install system dependencies
sudo apt-get install stockfish  # Debian/Ubuntu
# or
brew install stockfish          # macOS

# Install Python package
pip install -e .
```

## 📖 Usage

### Basic Analysis
```bash
# Analyze a player's recent games
chess-analyzer magnuscarlsen --games 50

# Specify output format
chess-analyzer hikaru --games 100 --format html --output report_hikaru

# Increase analysis depth
chess-analyzer your_username --games 30 --depth 22 --verbose
```

### Command Line Options
```
Usage: chess-analyzer [OPTIONS] [USERNAME]

Arguments:
  USERNAME  Chess.com username to analyze

Options:
  --games, -g INTEGER        Maximum games to analyze (default: 50)
  --format, -f [html|text|json|all]
                             Output format (default: html)
  --output, -o TEXT          Output file/directory name
  --config, -c PATH          Path to configuration file
  --depth, -d INTEGER        Stockfish analysis depth (overrides config)
  --verbose, -v              Enable verbose logging
  --list-formats             List available output formats
  --check-stockfish          Check Stockfish installation
  --help                     Show this message and exit
  --version                  Show version information
```

## 🔧 Configuration

Edit `config.yaml` to customize analysis parameters:

```yaml
analysis:
  engine_depth: 18           # Stockfish analysis depth
  thresholds:
    engine_correlation_red_flag: 95.0    # % of moves matching engine
    avg_centipawn_loss_red_flag: 15.0    # Lower = stronger play
    accuracy_fluctuation_red_flag: 30.0   # Consistency threshold

chess_com:
  request_delay: 0.5         # Delay between API requests (seconds)
  max_games: 100             # Maximum games to fetch (0 = all)
```

## 📁 Project Structure

```
chess-fairplay-analyzer/
├── chess_analyzer/
│   ├── __init__.py          # Package definition
│   ├── cli.py              # Command-line interface
│   ├── fetcher.py          # Chess.com API client
│   ├── engine.py           # Stockfish integration
│   ├── analyzer.py         # Core analysis logic
│   ├── reporter.py         # Report generation
│   ├── stats.py           # Statistical functions
│   └── utils/
│       ├── __init__.py
│       └── helpers.py      # Utility functions
├── templates/
│   └── report_template.html # HTML report template
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── setup.py               # Package installation
├── install.ps1            # Windows installer
└── README.md              # This file
```

## 📊 Analysis Methodology

The analyzer evaluates several key metrics:

### 1. Engine Move Correlation
Percentage of player's moves that match Stockfish's top recommendation at depth 18+. Human players typically achieve 50-80% correlation; consistent scores above 90% are suspicious.

### 2. Average Centipawn Loss (ACPL)
Measures how many "centipawns" (1/100th of a pawn) are lost per move on average. Strong human players maintain 20-50 ACPL; consistently below 15 is suspicious.

### 3. Performance Consistency
Standard deviation of accuracy across games. Inconsistent performance (wild fluctuations) can indicate selective assistance.

### 4. Time Control Analysis
Compares performance across different time controls (blitz, rapid, classical). Unnatural consistency across time controls is suspicious.

## ⚠️ Ethical Considerations

This tool is designed with strict ethical boundaries:

1. **No Automated Reporting**: The tool only provides analysis; human judgment is required for any action.
2. **Rate Limiting**: Built-in delays respect Chess.com's servers.
3. **Transparency**: Clear disclaimer in all reports emphasizing statistical nature.
4. **Privacy**: Only accesses publicly available game data.

**Remember**: Statistical anomalies do not equal proof of cheating. Many legitimate factors can influence these metrics.

## 🐛 Troubleshooting

### Common Issues

#### Stockfish Not Found
```bash
# On Windows, ensure Stockfish is in the correct location
# Default: C:\Users\YourUsername\stockfish\stockfish.exe

# Update config.yaml with the correct path:
# engine_path: "C:\\Users\\YourUsername\\stockfish\\stockfish.exe"
```

#### API Rate Limiting
If you encounter rate limits, increase the delay in `config.yaml`:
```yaml
chess_com:
  request_delay: 1.0  # Increase to 1 second between requests
```

#### Module Import Errors
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or install specific missing packages
pip install numpy python-chess requests
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone and setup
git clone https://github.com/yourusername/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Chess.com](https://www.chess.com) for their public API
- [Stockfish](https://stockfishchess.org/) chess engine
- [python-chess](https://python-chess.readthedocs.io/) library
- The chess community for fair play advocacy

## 📞 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an [Issue](https://github.com/yourusername/chess-fairplay-analyzer/issues)
3. Provide your configuration and error logs

---

**Disclaimer**: This tool is for educational and analytical purposes only. The authors are not responsible for any misuse. Always respect Chess.com's Terms of Service.
```

## **Additional Files You Should Create:**

### **1. LICENSE File** (Create as `LICENSE` in root)
```text
MIT License

Copyright (c) 2025 Muhammad Hanif

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### **2. .gitignore** (If not already created)
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Output
*.log
*.report.html
*.report.json
*.report.txt
reports/
cache/
tmp/

# Config overrides
config.local.yaml
secrets.yaml
```

### **3. CHANGELOG.md** (Optional but recommended)
```markdown
# Changelog

## [1.0.0] - 2025-01-14
### Added
- Initial release of Chess Fairplay Analyzer
- Chess.com API integration with rate limiting
- Stockfish engine integration
- Statistical analysis engine (ACPL, correlation, consistency)
- Multi-format reporting (HTML, text, JSON)
- Command-line interface with progress bars
- Configuration system with YAML support
- Windows installer script
- Comprehensive documentation

### Features
- Fetch up to 1000 games per player
- Analyze games in parallel
- Generate interactive HTML reports
- Respectful API usage with delays
- Ethical design - analysis only, no auto-reporting
```

## **Next Steps After Installation:**

Once `numpy` finishes installing, run:

```powershell
# 1. Test the installation
python -m chess_analyzer.cli --check-stockfish

# 2. Try a quick analysis (just 2 games to test)
python -m chess_analyzer.cli magnuscarlsen --games 2 --verbose

# 3. If successful, push to GitHub:
git add .
git commit -m "Initial commit: Chess Fairplay Analyzer v1.0"
git remote add origin https://github.com/YOUR_USERNAME/chess-fairplay-analyzer.git
git push -u origin main
```