#!/usr/bin/env python
"""Test game conversion with a local PGN"""
import sys
import io
sys.path.insert(0, '.')

import chess.pgn
from chess_analyzer.head_to_head_analyzer import HeadToHeadAnalyzer

# Create a test PGN game
pgn_text = """[Event "Live Blitz"]
[Site "Lichess.org"]
[Date "2025.01.20"]
[Round "-"]
[White "hikaru"]
[Black "opponent_name"]
[WhiteElo "2800"]
[BlackElo "2600"]
[Result "1-0"]
[Opening "Italian Game"]
[ECO "C50"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d3 Nf6 5. O-O d6 6. h3 a6 7. Be3 Bxe3 8. fxe3 O-O 9. Nbd2 Be6 10. Rf2 Bxc4 11. Nxc4 Nh5 12. Rf1 Nf4 13. N4e3 Nxe3 14. Nxe3 Nf6 15. Qe2 Kh8 16. Rf1 Kg7 17. Rf1 a5 18. Rf2 Bd7 19. Rff1 Be6 20. Bd2 a4 21. Bf4 Qd7 22. Re1 Rfe8 23. Re1 Kg7 24. h4 Bd7 25. Bg3 Nh7 26. Qf3 Ng5 27. Qf4 Nf7 28. h5 Qe7 29. Nf5+ Kh8 30. Qxf7 Qxf7 31. Nxf7+ Kg7 32. Nxe5 Bxf5 33. Qg5+ Kh7 34. Qxf5+ Kg7 35. Qf4 Bg8 36. h6+ Kh7 37. Qh4+ Kg6 38. h7 Bxh7 39. Qxh7# 1-0"""

game = chess.pgn.read_game(io.StringIO(pgn_text))

print("PGN Headers:")
for key in ['White', 'Black', 'WhiteElo', 'BlackElo', 'Result', 'Opening']:
    print(f"  {key}: {game.headers.get(key)}")

print("\nTesting conversion:")
analyzer = HeadToHeadAnalyzer()
game_dict = analyzer._convert_game_to_dict(game)

print("Converted result:")
for key in ['result', 'opponent', 'opponent_elo', 'opening', 'moves', 'username']:
    print(f"  {key}: {game_dict.get(key)}")

# Test with player as Black
pgn_text2 = pgn_text.replace('[White "hikaru"]', '[White "opponent_name"]').replace('[Black "opponent_name"]', '[Black "hikaru"]').replace('[Result "1-0"]', '[Result "0-1"]')

game2 = chess.pgn.read_game(io.StringIO(pgn_text2))
print("\n\nWhen hikaru plays Black (and loses):")
game_dict2 = analyzer._convert_game_to_dict(game2)
for key in ['result', 'opponent', 'opponent_elo', 'username']:
    print(f"  {key}: {game_dict2.get(key)}")
