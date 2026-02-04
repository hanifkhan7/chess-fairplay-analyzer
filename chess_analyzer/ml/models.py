"""
Neural Network Models: CNN-LSTM architecture for cheat detection

This module defines the neural network architectures used for detecting chess cheating.
The models take board positions and move sequences as input and output a binary
classification (human or engine).
"""

import numpy as np
from typing import Optional, Tuple
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Sequential, Model
    from tensorflow.keras.regularizers import l2
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not installed. Install with: pip install tensorflow")


def build_cnn_lstm_model(input_shape: Tuple[int, int, int, int] = (20, 8, 8, 12),
                         num_classes: int = 2,
                         learning_rate: float = 0.001) -> Optional[Model]:
    """
    Build a CNN-LSTM model for chess game analysis.
    
    Architecture:
    - 3x Conv2D layers for spatial feature extraction from each board position
    - MaxPooling2D for dimensionality reduction
    - LSTM layers to capture temporal patterns in move sequences
    - Dropout for regularization
    - Dense layers for classification
    
    Args:
        input_shape: Tuple (sequence_length, board_height, board_width, channels)
                     Default: (20, 8, 8, 12) = 20 positions with 12-channel boards
        num_classes: Number of output classes (2 for binary: human vs engine)
        learning_rate: Adam optimizer learning rate
        
    Returns:
        keras.Model: Compiled CNN-LSTM model
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for model building")
    
    model = Sequential([
        # Input layer
        layers.Input(shape=input_shape),
        
        # TimeDistributed CNN for spatial feature extraction
        # Process each board position independently
        layers.TimeDistributed(
            Sequential([
                # Conv Block 1
                layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Conv Block 2
                layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Conv Block 3
                layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Flatten for LSTM input
                layers.Flatten(),
            ]),
            input_shape=input_shape
        ),
        
        # Temporal modeling with LSTM
        layers.LSTM(128, return_sequences=True, dropout=0.3),
        layers.BatchNormalization(),
        
        layers.LSTM(64, return_sequences=False, dropout=0.3),
        layers.BatchNormalization(),
        
        # Dense layers for classification
        layers.Dense(128, activation='relu', kernel_regularizer=l2(0.01)),
        layers.Dropout(0.4),
        layers.BatchNormalization(),
        
        layers.Dense(64, activation='relu', kernel_regularizer=l2(0.01)),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        layers.Dense(32, activation='relu', kernel_regularizer=l2(0.01)),
        layers.Dropout(0.2),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall(), 
                 keras.metrics.AUC(name='auc')]
    )
    
    return model


def build_simple_cnn_model(input_shape: Tuple[int, int, int] = (8, 8, 12),
                          num_classes: int = 2,
                          learning_rate: float = 0.001) -> Optional[Model]:
    """
    Build a simpler CNN model for single position classification (if LSTM is too heavy).
    
    Args:
        input_shape: Tuple (board_height, board_width, channels)
                     Default: (8, 8, 12)
        num_classes: Number of output classes (2 for binary classification)
        learning_rate: Adam optimizer learning rate
        
    Returns:
        keras.Model: Compiled CNN model
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for model building")
    
    model = Sequential([
        layers.Input(shape=input_shape),
        
        # Conv Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Conv Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Conv Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Global average pooling
        layers.GlobalAveragePooling2D(),
        
        # Dense layers
        layers.Dense(256, activation='relu', kernel_regularizer=l2(0.01)),
        layers.Dropout(0.4),
        layers.BatchNormalization(),
        
        layers.Dense(128, activation='relu', kernel_regularizer=l2(0.01)),
        layers.Dropout(0.3),
        layers.BatchNormalization(),
        
        layers.Dense(64, activation='relu', kernel_regularizer=l2(0.01)),
        layers.Dropout(0.2),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
    )
    
    return model


def build_lightweight_cnn_lstm_model(input_shape: Tuple[int, int, int, int] = (10, 8, 8, 12),
                                    num_classes: int = 2,
                                    learning_rate: float = 0.001) -> Optional[Model]:
    """
    Build a lightweight CNN-LSTM model for deployment on modest hardware.
    Optimized for inference speed with fewer parameters.
    
    Args:
        input_shape: Tuple (sequence_length, board_height, board_width, channels)
        num_classes: Number of output classes
        learning_rate: Adam optimizer learning rate
        
    Returns:
        keras.Model: Compiled lightweight model
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for model building")
    
    model = Sequential([
        layers.Input(shape=input_shape),
        
        # Lightweight TimeDistributed CNN
        layers.TimeDistributed(
            Sequential([
                layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.2),
                
                layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.2),
                
                layers.Flatten(),
            ]),
            input_shape=input_shape
        ),
        
        # Single LSTM layer
        layers.LSTM(64, return_sequences=False, dropout=0.2),
        
        # Dense layers
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy', keras.metrics.AUC()]
    )
    
    return model


def load_model(model_path: str) -> Optional[Model]:
    """
    Load a saved model from disk.
    
    Args:
        model_path: Path to saved model (.h5 file)
        
    Returns:
        keras.Model or None if loading fails
    """
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required")
    
    if not os.path.exists(model_path):
        print(f"Error: Model file not found: {model_path}")
        return None
    
    try:
        model = keras.models.load_model(model_path)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def save_model(model: Model, model_path: str) -> bool:
    """
    Save a model to disk.
    
    Args:
        model: keras.Model to save
        model_path: Path where to save the model (.h5 file)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        model.save(model_path)
        return True
    except Exception as e:
        print(f"Error saving model: {e}")
        return False


def model_summary(model: Model) -> str:
    """
    Get a detailed summary of the model architecture.
    
    Args:
        model: keras.Model
        
    Returns:
        str: Model summary as string
    """
    from io import StringIO
    import sys
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    model.summary()
    
    summary_str = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    return summary_str


if __name__ == "__main__":
    if TENSORFLOW_AVAILABLE:
        print("Building CNN-LSTM model...")
        model = build_cnn_lstm_model()
        print(model_summary(model))
    else:
        print("TensorFlow not available. Install with: pip install tensorflow")
