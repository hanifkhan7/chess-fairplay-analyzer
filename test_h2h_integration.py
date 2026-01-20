#!/usr/bin/env python
"""
Integration test for Head-to-Head Matchup Analyzer
Simulates menu option 12 with test data
"""
import sys
sys.path.insert(0, '.')

from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer
import chess.pgn
import io

# Create sample games for two players
sample_games_p1 = """[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.20"]
[Round "-"]
[White "player1"]
[Black "opponent_a"]
[WhiteElo "1700"]
[BlackElo "1650"]
[Result "1-0"]
[Opening "Sicilian Defense"]

1. e4 c5 2. Nf3 d6 1-0

[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.19"]
[Round "-"]
[White "opponent_b"]
[Black "player1"]
[WhiteElo "1680"]
[BlackElo "1700"]
[Result "0-1"]
[Opening "Italian Game"]

1. e4 e5 2. Nf3 Nc6 0-1

[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.18"]
[Round "-"]
[White "player1"]
[Black "opponent_c"]
[WhiteElo "1700"]
[BlackElo "1700"]
[Result "1/2-1/2"]
[Opening "French Defense"]

1. e4 e6 2. d4 d5 1/2-1/2"""

sample_games_p2 = """[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.20"]
[Round "-"]
[White "player2"]
[Black "opponent_x"]
[WhiteElo "1750"]
[BlackElo "1700"]
[Result "1-0"]
[Opening "Sicilian Defense"]

1. e4 c5 2. Nf3 d6 1-0

[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.19"]
[Round "-"]
[White "opponent_y"]
[Black "player2"]
[WhiteElo "1700"]
[BlackElo "1750"]
[Result "0-1"]
[Opening "Caro-Kann Defense"]

1. d4 d5 0-1"""

# Parse games
games1 = []
games2 = []

for pgn_text in sample_games_p1.split('[Event'):
    if pgn_text.strip():
        pgn = '[Event' + pgn_text
        game = chess.pgn.read_game(io.StringIO(pgn))
        if game:
            games1.append(game)

for pgn_text in sample_games_p2.split('[Event'):
    if pgn_text.strip():
        pgn = '[Event' + pgn_text
        game = chess.pgn.read_game(io.StringIO(pgn))
        if game:
            games2.append(game)

print(f"Loaded {len(games1)} games for player1 and {len(games2)} games for player2")

# Generate report
analyzer = HeadToHeadAnalyzer()
report = analyzer.generate_matchup_report(
    'player1', 1700, games1,
    'player2', 1750, games2
)

print("\n" + "="*80)
print("Generated Report Summary:")
print("="*80)
print(f"ELO Probability: {report['elo_probability'][0]:.1f}% vs {report['elo_probability'][1]:.1f}%")
print(f"Performance Probability: {report['performance_probability'][0]:.1f}% vs {report['performance_probability'][1]:.1f}%")
print(f"H2H Games: {report['h2h_games']['total_games']}")
print(f"Combined Probability: {report['combined_probability'][0]:.1f}% vs {report['combined_probability'][1]:.1f}%")
print(f"Prediction: {report['prediction']}")
print(f"Confidence: {report['confidence']:.1f}%")

# Display the report
print("\n" + "="*80)
print("Formatted Display:")
print("="*80)
analyzer.display_matchup_report(report)

print("\n✓ Integration test completed successfully!")
