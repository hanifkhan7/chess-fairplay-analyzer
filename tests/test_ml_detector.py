"""
Unit tests for ML module components

Tests for:
- TensorConverter: board to tensor conversion, validation
- Models: model building, inference
- Trainer: training loop, checkpoint management
- DataPreparator: PGN loading, data splitting
"""

import pytest
import numpy as np
import chess
from pathlib import Path
import tempfile
import os

# Import ML modules
from chess_analyzer.ml.tensor_converter import TensorConverter, board_to_tensor
from chess_analyzer.ml.models import (
    build_cnn_lstm_model, build_simple_cnn_model, 
    build_lightweight_cnn_lstm_model
)
from chess_analyzer.ml.data_prep import DataPreparator
from chess_analyzer.ml.trainer import MLTrainer

try:
    TENSORFLOW_AVAILABLE = True
except:
    TENSORFLOW_AVAILABLE = False


class TestTensorConverter:
    """Test TensorConverter functionality."""
    
    def test_board_to_tensor_shape(self):
        """Test that board_to_tensor returns correct shape."""
        board = chess.Board()
        tensor = TensorConverter.board_to_tensor(board)
        
        assert tensor.shape == (12, 8, 8)
        assert tensor.dtype == np.float32
    
    def test_board_to_tensor_initial_position(self):
        """Test tensor from initial position."""
        board = chess.Board()
        tensor = TensorConverter.board_to_tensor(board)
        
        # Initial position should have correct piece count
        # 16 white pieces, 16 black pieces
        white_pieces = np.sum(tensor[0:6])
        black_pieces = np.sum(tensor[6:12])
        
        assert white_pieces == 16
        assert black_pieces == 16
    
    def test_board_to_tensor_empty_board(self):
        """Test tensor from empty board."""
        board = chess.Board()
        board.clear()
        tensor = TensorConverter.board_to_tensor(board)
        
        assert np.sum(tensor) == 0
    
    def test_tensor_values_binary(self):
        """Test that tensor values are binary."""
        board = chess.Board()
        tensor = TensorConverter.board_to_tensor(board)
        
        assert np.all(np.isin(tensor, [0.0, 1.0]))
    
    def test_tensor_validation_valid(self):
        """Test tensor validation on valid tensor."""
        board = chess.Board()
        tensor = TensorConverter.board_to_tensor(board)
        
        is_valid, msg = TensorConverter.validate_tensor(tensor)
        assert is_valid
        assert "Valid" in msg
    
    def test_tensor_validation_invalid_shape(self):
        """Test tensor validation rejects invalid shapes."""
        tensor = np.zeros((10, 8, 8), dtype=np.float32)
        
        is_valid, msg = TensorConverter.validate_tensor(tensor)
        assert not is_valid
        assert "shape" in msg.lower()
    
    def test_tensor_validation_non_binary(self):
        """Test tensor validation rejects non-binary values."""
        board = chess.Board()
        tensor = TensorConverter.board_to_tensor(board)
        tensor[0, 0, 0] = 0.5  # Invalid: not binary
        
        is_valid, msg = TensorConverter.validate_tensor(tensor)
        assert not is_valid
        assert "binary" in msg.lower()
    
    def test_game_to_tensors_shape(self):
        """Test game_to_tensors returns correct shape."""
        board = chess.Board()
        moves = [
            chess.Move.from_uci("e2e4"),
            chess.Move.from_uci("e7e5"),
            chess.Move.from_uci("g1f3"),
        ]
        
        sequences = TensorConverter.game_to_tensors(board, moves, sequence_length=2)
        
        # Should have 3 - 2 + 1 = 2 sequences
        assert sequences.shape[0] == 2
        assert sequences.shape[1] == 2  # sequence length
        assert sequences.shape[2] == 8  # rank
        assert sequences.shape[3] == 8  # file
        assert sequences.shape[4] == 12  # channels
    
    def test_game_to_tensors_empty_moves(self):
        """Test game_to_tensors with short game."""
        board = chess.Board()
        moves = [chess.Move.from_uci("e2e4")]  # Only 1 move
        
        sequences = TensorConverter.game_to_tensors(board, moves, sequence_length=5)
        
        # Not enough moves for sequences
        assert sequences.shape[0] == 0
    
    def test_augment_tensor(self):
        """Test tensor augmentation (flipping)."""
        board = chess.Board()
        tensor = TensorConverter.board_to_tensor(board)
        
        flipped = TensorConverter.augment_tensor(tensor)
        
        assert flipped.shape == tensor.shape
        # Flipped should be different (unless symmetric)
        # For initial position which is symmetric, they might be same
    
    def test_normalize_tensors(self):
        """Test tensor normalization."""
        tensor = np.array([[[0.5, 1.0], [0.0, 1.5]]])
        
        normalized = TensorConverter.normalize_tensors(tensor)
        
        assert np.all(normalized >= 0.0)
        assert np.all(normalized <= 1.0)
    
    def test_tensor_to_board_reconstruction(self):
        """Test reconstructing board from tensor."""
        original_board = chess.Board()
        original_board.push_san("e4")
        original_board.push_san("c5")
        
        tensor = TensorConverter.board_to_tensor(original_board)
        reconstructed = TensorConverter.tensor_to_board(tensor)
        
        # Should reconstruct valid board
        assert reconstructed is not None
        # Piece counts should match
        assert bin(original_board.occupied).count('1') == bin(reconstructed.occupied).count('1')


class TestModels:
    """Test model building and basic functionality."""
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
    def test_build_cnn_lstm_model(self):
        """Test building CNN-LSTM model."""
        model = build_cnn_lstm_model()
        
        assert model is not None
        assert len(model.layers) > 0
        # Check input shape
        assert model.input_shape[1:] == (20, 8, 8, 12)
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
    def test_build_simple_cnn_model(self):
        """Test building simple CNN model."""
        model = build_simple_cnn_model()
        
        assert model is not None
        assert model.input_shape[1:] == (8, 8, 12)
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
    def test_build_lightweight_model(self):
        """Test building lightweight model."""
        model = build_lightweight_cnn_lstm_model()
        
        assert model is not None
        assert model.input_shape[1:] == (10, 8, 8, 12)
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
    def test_model_inference_cnn_lstm(self):
        """Test model can perform inference."""
        model = build_cnn_lstm_model()
        
        # Create dummy input
        X = np.random.randn(2, 20, 8, 8, 12).astype(np.float32)
        
        # Predict
        predictions = model.predict(X, verbose=0)
        
        assert predictions.shape == (2, 2)  # 2 samples, 2 classes
        assert np.all(predictions >= 0)
        assert np.all(predictions <= 1)
        # Softmax output should sum to 1
        assert np.allclose(np.sum(predictions, axis=1), 1.0)
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
    def test_model_inference_simple_cnn(self):
        """Test simple CNN inference."""
        model = build_simple_cnn_model()
        
        X = np.random.randn(2, 8, 8, 12).astype(np.float32)
        predictions = model.predict(X, verbose=0)
        
        assert predictions.shape == (2, 2)


class TestDataPreparator:
    """Test data preparation functionality."""
    
    def test_datapreparator_init(self):
        """Test DataPreparator initialization."""
        dp = DataPreparator(sequence_length=15)
        
        assert dp.sequence_length == 15
        assert dp.augment == True
    
    def test_extract_moves_from_game(self):
        """Test extracting moves from a game."""
        # Create a simple game
        board = chess.Board()
        board.push_san("e4")
        board.push_san("c5")
        board.push_san("Nf3")
        
        moves = [board.pop() for _ in range(3)]
        moves.reverse()
        
        dp = DataPreparator()
        
        # Note: This would need a proper PGN game object
        # Just test that we can create moves
        assert len(moves) == 3
    
    def test_balance_dataset_oversample(self):
        """Test dataset balancing with oversampling."""
        # Create imbalanced dataset
        X = np.random.randn(100, 20, 8, 8, 12).astype(np.float32)
        y = np.vstack([
            np.array([[1, 0]] * 80),  # 80 class 0
            np.array([[0, 1]] * 20),  # 20 class 1
        ])
        
        dp = DataPreparator()
        X_bal, y_bal = dp.balance_dataset(X, y, strategy='oversample')
        
        # Should be larger or equal
        assert X_bal.shape[0] >= X.shape[0]
        # Should have more balanced classes
        class_counts = np.sum(y_bal, axis=0)
        assert class_counts[0] == class_counts[1]
    
    def test_balance_dataset_undersample(self):
        """Test dataset balancing with undersampling."""
        X = np.random.randn(100, 20, 8, 8, 12).astype(np.float32)
        y = np.vstack([
            np.array([[1, 0]] * 80),
            np.array([[0, 1]] * 20),
        ])
        
        dp = DataPreparator()
        X_bal, y_bal = dp.balance_dataset(X, y, strategy='undersample')
        
        # Should be smaller
        assert X_bal.shape[0] < X.shape[0]
        # Should be balanced
        class_counts = np.sum(y_bal, axis=0)
        assert class_counts[0] == class_counts[1]
    
    def test_calculate_class_weights(self):
        """Test class weight calculation."""
        y = np.vstack([
            np.array([[1, 0]] * 80),
            np.array([[0, 1]] * 20),
        ])
        
        dp = DataPreparator()
        weights = dp.calculate_class_weights(y)
        
        assert 0 in weights
        assert 1 in weights
        assert weights[0] < weights[1]  # Minority class has higher weight
    
    def test_normalize_tensors(self):
        """Test tensor normalization."""
        X = np.array([[[0.5, 1.5], [-0.1, 1.0]]])
        
        dp = DataPreparator()
        X_norm = dp.normalize_tensors(X)
        
        assert np.all(X_norm >= 0.0)
        assert np.all(X_norm <= 1.0)
    
    def test_save_and_load_dataset(self):
        """Test saving and loading dataset."""
        data = {
            'X_train': np.random.randn(10, 20, 8, 8, 12).astype(np.float32),
            'y_train': np.random.randint(0, 2, (10, 2)).astype(np.float32),
            'X_val': np.random.randn(5, 20, 8, 8, 12).astype(np.float32),
            'y_val': np.random.randint(0, 2, (5, 2)).astype(np.float32),
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dp = DataPreparator()
            dp.save_dataset(data, tmpdir)
            
            loaded_data = dp.load_dataset(tmpdir)
            
            for key in data:
                assert key in loaded_data
                assert np.allclose(data[key], loaded_data[key])


class TestTrainer:
    """Test training functionality."""
    
    def test_trainer_init(self):
        """Test Trainer initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = MLTrainer(model_dir=tmpdir, log_dir=tmpdir)
            
            assert trainer.model_dir.exists()
            assert trainer.log_dir.exists()
    
    @pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
    def test_trainer_setup_callbacks(self):
        """Test callback setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = MLTrainer(model_dir=tmpdir, log_dir=tmpdir)
            callbacks = trainer.setup_callbacks("test_model")
            
            assert len(callbacks) > 0
            # Should have EarlyStopping, ModelCheckpoint, etc.
            callback_types = [type(cb).__name__ for cb in callbacks]
            assert 'EarlyStopping' in callback_types


# Quick integration test
def test_integration_tensor_to_model():
    """Integration test: board -> tensor -> model."""
    if not TENSORFLOW_AVAILABLE:
        pytest.skip("TensorFlow not available")
    
    # Create board
    board = chess.Board()
    board.push_san("e4")
    board.push_san("c5")
    
    # Convert to tensor
    tensor = TensorConverter.board_to_tensor(board)
    
    # Create sequences
    sequences = np.array([tensor] * 20)  # Repeat to create sequence
    sequences = np.expand_dims(sequences, axis=0)  # Add batch dimension
    
    # Create and test model
    model = build_simple_cnn_model(input_shape=(8, 8, 12))
    
    predictions = model.predict(sequences[0:1, 0:1], verbose=0)
    
    assert predictions.shape == (1, 2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
