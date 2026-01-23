#!/usr/bin/env python3
"""Test asdict on AccuracyMetrics"""

from dataclasses import asdict, dataclass

@dataclass
class AccuracyMetrics:
    opening_accuracy: float = 0.0
    middlegame_accuracy: float = 0.0
    endgame_accuracy: float = 0.0
    overall_accuracy: float = 0.0
    consistency_std_dev: float = 0.0

# Create instance
acc = AccuracyMetrics(overall_accuracy=73.5)

print(f"Original object: {acc}")
print(f"Type: {type(acc)}")

# Convert to dict
acc_dict = asdict(acc)

print(f"\nDict: {acc_dict}")
print(f"Type: {type(acc_dict)}")
print(f"overall_accuracy from dict: {acc_dict.get('overall_accuracy')}")

# Try nested
@dataclass
class GameAnalysis:
    accuracy: AccuracyMetrics = None

game = GameAnalysis(accuracy=acc)
game_dict = asdict(game)

print(f"\nNested dict: {game_dict}")
print(f"accuracy field: {game_dict.get('accuracy')}")
print(f"overall_accuracy from nested: {game_dict.get('accuracy', {}).get('overall_accuracy')}")
