#!/usr/bin/env python
"""
Run the interactive Opening Trainer web application
"""
import os
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


from chess_analyzer.web_trainer import launch_web_trainer

if __name__ == '__main__':
    print("\n" + "="*70)
    print("♟️  OPENING TRAINER - Interactive Web Interface")
    print("="*70)
    print("\n🌐 Starting web server...")
    print("📱 Open your browser and go to: http://127.0.0.1:5000")
    print("\n✅ Press Ctrl+C to stop the server\n")
    launch_web_trainer(port=5000, debug=False)
