"""
Chess Fairplay Analyzer - ML Module
Machine Learning models for cheat detection using CNN-LSTM architecture
"""

__version__ = "1.0.0"
__author__ = "Chess Fairplay Analyzer Team"

from .tensor_converter import TensorConverter
from .models import build_cnn_lstm_model, build_simple_cnn_model
from .trainer import MLTrainer
from .data_prep import DataPreparator

__all__ = [
    'TensorConverter',
    'build_cnn_lstm_model',
    'build_simple_cnn_model',
    'MLTrainer',
    'DataPreparator',
]
