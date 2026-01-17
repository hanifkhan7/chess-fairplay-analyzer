#!/usr/bin/env python3
import yaml
import logging
logging.basicConfig(level=logging.DEBUG)

config = yaml.safe_load(open('config.yaml'))
from chess_analyzer.lichess_analyzer import LichessAnalyzer

analyzer = LichessAnalyzer(config)
print("Lichess Analyzer created")
print("Session headers:", analyzer.session.headers)
print("Base URL:", analyzer.base_url)
