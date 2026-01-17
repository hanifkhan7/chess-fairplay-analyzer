# Installation Guide

## Quick Installation

### Windows
```powershell
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
choco install stockfish  # or download from stockfishchess.org
python -m chess_analyzer.cli hikaru --games 1
```

### macOS
```bash
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
brew install stockfish
python -m chess_analyzer.cli hikaru --games 1
```

### Linux/Ubuntu/Debian
```bash
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
python3 -m venv venv
source venv/bin/activate
sudo apt-get install -y stockfish
pip install -r requirements.txt
python -m chess_analyzer.cli hikaru --games 1
```

---

## **Kali Linux Installation (Comprehensive)**

Kali Linux is a penetration testing distribution based on Debian. This guide ensures full compatibility.

### Prerequisites Check
```bash
uname -a  # Should show Kali Linux
python3 --version  # Should be 3.8+
```

### Step-by-Step Installation

#### Step 1: Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get dist-upgrade -y
```

#### Step 2: Install Development Tools
```bash
sudo apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-dev \
  build-essential \
  git \
  curl
```

#### Step 3: Install Stockfish
```bash
# Method 1: Preferred (from package manager)
sudo apt-get install -y stockfish

# Verify installation
which stockfish
stockfish --version

# If not found, check alternative location
sudo find / -name "stockfish" 2>/dev/null

# Create symlink if needed
sudo ln -s /usr/games/stockfish /usr/local/bin/stockfish 2>/dev/null || true
```

#### Step 4: Clone Repository
```bash
# Clone to home directory
cd ~
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer

# Or with SSH (if configured)
# git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
```

#### Step 5: Setup Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your prompt
```

#### Step 6: Upgrade pip and Install Dependencies
```bash
# Upgrade pip to latest version
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Verify key packages installed
python3 -c "import chess; import requests; import numpy; print('Dependencies OK')"
```

#### Step 7: Verify Installation
```bash
# Check Stockfish
which stockfish
stockfish --version

# Check Python packages
pip list | grep -E "python-chess|requests|pyyaml|numpy|tqdm"

# Test the analyzer
python -m chess_analyzer.cli hikaru --games 1 --verbose
```

#### Step 8: Optional - Compile Stockfish from Source (for latest version)
```bash
# Clone Stockfish repository
git clone https://github.com/official-stockfish/Stockfish.git
cd Stockfish/src

# Compile
make build ARCH=x86-64-modern

# Install globally
sudo cp stockfish /usr/local/bin/stockfish

# Verify
stockfish --version

# Return to analyzer directory
cd ~/chess-fairplay-analyzer
```

### Troubleshooting Kali Linux

#### Problem: "stockfish: command not found"
```bash
# Solution 1: Create symlink
sudo ln -s /usr/games/stockfish /usr/local/bin/stockfish

# Solution 2: Add to PATH
echo 'export PATH="/usr/games:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Solution 3: Full path in config
# Edit config.yaml:
# engine_path: "/usr/games/stockfish"
```

#### Problem: "Permission denied" for venv
```bash
# Fix permissions
chmod -R u+w venv/

# Or recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

#### Problem: Module import errors
```bash
# Clear pip cache and reinstall
pip cache purge
pip install --no-cache-dir -r requirements.txt

# Or reinstall specific package
pip install --upgrade --force-reinstall python-chess
```

#### Problem: "numpy not found"
```bash
# Install build dependencies
sudo apt-get install -y python3-numpy python3-dev

# Or reinstall
pip install --upgrade numpy

# Check installation
python3 -c "import numpy; print(numpy.__version__)"
```

#### Problem: Chess.com API timeout
```bash
# Check internet connection
ping chess.com

# Increase timeout in config.yaml:
chess_com:
  request_delay: 2.0  # Increase from 1.0
```

### Root vs Non-root Installation

**Recommended: Non-root (safer)**
```bash
# As regular user
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**If you must use root (not recommended)**
```bash
sudo su
cd /root
git clone https://github.com/hanifkhan7/chess-fairplay-analyzer.git
cd chess-fairplay-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
exit
```

---

## Docker Installation (Kali Linux)

### Option 1: Docker Container
```bash
# Build image
docker build -t chess-analyzer .

# Run analysis
docker run -it chess-analyzer hikaru --games 10

# Save reports locally
docker run -v $(pwd)/reports:/app/reports chess-analyzer magnuscarlsen --games 20
```

### Option 2: Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  chess-analyzer:
    build: .
    volumes:
      - ./reports:/app/reports
      - ./cache:/app/cache
    environment:
      - PYTHONUNBUFFERED=1
    command: hikaru --games 10
```

Run with:
```bash
docker-compose up
```

---

## Testing Installation

### Basic Test
```bash
# Should complete in 2-3 minutes
python -m chess_analyzer.cli hikaru --games 1
```

### Verbose Test
```bash
# Shows all logs
python -m chess_analyzer.cli hikaru --games 1 --verbose
```

### Check Stockfish
```bash
# Should show version and settings
stockfish

# Type "quit" to exit
quit
```

### Check Python Dependencies
```bash
python3 << EOF
import chess
import chess.engine
import requests
import numpy
import yaml
print("All dependencies OK!")
EOF
```

---

## Performance Optimization

### For Slower Systems
Edit `config.yaml`:
```yaml
analysis:
  engine_depth: 16      # Lower from 18 (faster but less accurate)
  threads: 2            # Reduce from 4
  hash_size: 128        # Reduce from 256

chess_com:
  request_delay: 2.0    # Increase for stability
```

### For Faster Systems
```yaml
analysis:
  engine_depth: 20      # Increase from 18 (more accurate)
  threads: 8            # Use more threads
  hash_size: 512        # More memory
```

---

## Next Steps After Installation

1. **Test with different players:**
   ```bash
   python -m chess_analyzer.cli rohan_asif --games 5
   python -m chess_analyzer.cli Quantum-Chesss --games 5
   ```

2. **Generate full reports:**
   ```bash
   python -m chess_analyzer.cli magnuscarlsen --games 30 --format all
   ```

3. **Check reports:**
   ```bash
   # Open HTML report
   xdg-open reports/report_magnuscarlsen.html

   # View JSON
   cat reports/report_magnuscarlsen.json | jq .

   # View text
   cat reports/report_magnuscarlsen.txt
   ```

4. **Configure for your needs:**
   - Edit `config.yaml`
   - Adjust depth, threads, caching
   - Set API delays

---

## Uninstall

```bash
# Deactivate virtual environment
deactivate

# Remove directory
cd ~
rm -rf chess-fairplay-analyzer

# Or keep code but remove venv
rm -rf chess-fairplay-analyzer/venv
```

---

## Support

If you encounter issues:

1. Check this guide again
2. Verify Stockfish: `which stockfish && stockfish --version`
3. Verify Python: `python3 --version && python3 -m pip --version`
4. Check internet: `ping chess.com`
5. Open an issue on GitHub with:
   - Your OS/version
   - Python version
   - Error message
   - Installation method used

---

## System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| RAM | 2GB | 4GB+ |
| Disk | 500MB | 2GB |
| Python | 3.8 | 3.10+ |
| Stockfish | 14 | 16+ |
| Connection | 1 Mbps | 5 Mbps |
| CPU | 2-core | 4+ cores |

---

## Additional Resources

- [Python-chess docs](https://python-chess.readthedocs.io/)
- [Stockfish docs](https://stockfishchess.org/)
- [Chess.com API](https://www.chess.com/news/view/published-data-api)
- [Kali Linux docs](https://docs.kali.org/)

Good luck with your installation! 🚀
