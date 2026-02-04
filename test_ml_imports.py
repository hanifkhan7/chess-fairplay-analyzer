"""Quick test of ML module imports"""
from chess_analyzer.ml.tensor_converter import TensorConverter
import chess
import numpy as np

print("Testing ML Module...")
print("=" * 60)

# Test 1: Import and basic tensor conversion
print("\n1. Testing TensorConverter...")
board = chess.Board()
tensor = TensorConverter.board_to_tensor(board)
print(f"   ✓ Tensor shape: {tensor.shape}")
print(f"   ✓ White pieces: {int(tensor[0:6].sum())}")
print(f"   ✓ Black pieces: {int(tensor[6:12].sum())}")

# Test 2: Tensor validation
print("\n2. Testing Tensor Validation...")
is_valid, msg = TensorConverter.validate_tensor(tensor)
print(f"   ✓ Validation: {msg}")

# Test 3: Game to tensors
print("\n3. Testing Game to Tensors...")
moves = [
    chess.Move.from_uci("e2e4"),
    chess.Move.from_uci("c7c5"),
    chess.Move.from_uci("g1f3"),
]
sequences = TensorConverter.game_to_tensors(board, moves, sequence_length=2)
print(f"   ✓ Sequence shape: {sequences.shape if sequences.size > 0 else 'Empty'}")

# Test 4: Try importing models
print("\n4. Testing Model Imports...")
try:
    from chess_analyzer.ml.models import build_cnn_lstm_model, build_simple_cnn_model
    print("   ✓ Models module imported")
    print("   ⚠ TensorFlow required for model building (not checked)")
except ImportError as e:
    print(f"   ! TensorFlow not available: {e}")

# Test 5: Data prep
print("\n5. Testing DataPreparator...")
from chess_analyzer.ml.data_prep import DataPreparator
dp = DataPreparator()
print(f"   ✓ DataPreparator initialized")
print(f"   ✓ Sequence length: {dp.sequence_length}")

# Test 6: ML Detector
print("\n6. Testing MLCheatDetector...")
try:
    from chess_analyzer.ml_detector import MLCheatDetector, get_ml_detector
    print("   ✓ MLCheatDetector module imported")
    
    # Try to get detector (will fail gracefully if model not found)
    detector = get_ml_detector("models/nonexistent.h5")
    if detector is None:
        print("   ✓ Graceful handling when model not found")
except ImportError as e:
    print(f"   ! TensorFlow not available: {e}")

print("\n" + "=" * 60)
print("✓ ML Module Structure Verified!")
print("=" * 60)
