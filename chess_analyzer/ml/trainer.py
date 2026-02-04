"""
ML Trainer: Training pipeline for chess cheat detection models

This module handles:
- Data loading and preprocessing
- Model training with validation
- Checkpoint management
- Metrics tracking and logging
- Early stopping and learning rate scheduling
"""

import os
import json
import numpy as np
from datetime import datetime
from typing import Tuple, Optional, Dict, List
from pathlib import Path

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.callbacks import (
        EarlyStopping, ModelCheckpoint, ReduceLROnPlateau,
        TensorBoard, CSVLogger
    )
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class MLTrainer:
    """Handle model training, validation, and checkpoint management."""
    
    def __init__(self, model_dir: str = "models", log_dir: str = "logs"):
        """
        Initialize trainer.
        
        Args:
            model_dir: Directory to save trained models
            log_dir: Directory for TensorBoard logs and CSV logs
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for training")
        
        self.model_dir = Path(model_dir)
        self.log_dir = Path(log_dir)
        
        # Create directories if they don't exist
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.history = None
        self.training_metadata = {}
    
    def setup_callbacks(self, model_name: str, patience: int = 10,
                       reduce_lr_patience: int = 5) -> List:
        """
        Setup training callbacks for monitoring and checkpointing.
        
        Args:
            model_name: Name for checkpoint files
            patience: Early stopping patience (epochs)
            reduce_lr_patience: Learning rate reduction patience
            
        Returns:
            List of Keras callbacks
        """
        callbacks = []
        
        # Early stopping
        callbacks.append(EarlyStopping(
            monitor='val_loss',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        ))
        
        # Model checkpoint (save best model)
        checkpoint_path = self.model_dir / f"{model_name}_best.h5"
        callbacks.append(ModelCheckpoint(
            str(checkpoint_path),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ))
        
        # Reduce learning rate on plateau
        callbacks.append(ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=reduce_lr_patience,
            min_lr=1e-6,
            verbose=1
        ))
        
        # TensorBoard logging
        tb_log_dir = self.log_dir / f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        callbacks.append(TensorBoard(
            log_dir=str(tb_log_dir),
            histogram_freq=1,
            update_freq='epoch'
        ))
        
        # CSV logging
        csv_log_path = self.log_dir / f"{model_name}_training.csv"
        callbacks.append(CSVLogger(
            str(csv_log_path),
            append=True
        ))
        
        return callbacks
    
    def train(self, 
              model: keras.Model,
              train_data: Tuple[np.ndarray, np.ndarray],
              val_data: Tuple[np.ndarray, np.ndarray],
              model_name: str = "chess_detector",
              epochs: int = 50,
              batch_size: int = 32,
              validation_split: Optional[float] = None,
              class_weight: Optional[Dict] = None) -> keras.callbacks.History:
        """
        Train a model on the provided data.
        
        Args:
            model: Compiled keras.Model
            train_data: Tuple of (X_train, y_train)
            val_data: Tuple of (X_val, y_val)
            model_name: Name for saving checkpoints
            epochs: Maximum number of epochs
            batch_size: Training batch size
            validation_split: If provided, use this split instead of val_data
            class_weight: Class weights for imbalanced data
            
        Returns:
            keras.callbacks.History: Training history
        """
        self.model = model
        
        # Setup callbacks
        callbacks = self.setup_callbacks(model_name)
        
        # Prepare training data
        X_train, y_train = train_data
        X_val, y_val = val_data
        
        print(f"\n{'='*60}")
        print(f"Training {model_name}")
        print(f"{'='*60}")
        print(f"Train set size: {X_train.shape[0]} samples")
        print(f"Validation set size: {X_val.shape[0]} samples")
        print(f"Input shape: {X_train.shape[1:]}")
        print(f"Output classes: {y_train.shape[1]}")
        print(f"{'='*60}\n")
        
        # Train model
        self.history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            class_weight=class_weight,
            verbose=1
        )
        
        # Store metadata
        self.training_metadata = {
            'model_name': model_name,
            'train_samples': int(X_train.shape[0]),
            'val_samples': int(X_val.shape[0]),
            'epochs_trained': len(self.history.history['loss']),
            'batch_size': batch_size,
            'input_shape': X_train.shape[1:],
            'final_train_loss': float(self.history.history['loss'][-1]),
            'final_val_loss': float(self.history.history['val_loss'][-1]),
            'final_train_accuracy': float(self.history.history['accuracy'][-1]),
            'final_val_accuracy': float(self.history.history['val_accuracy'][-1]),
            'best_val_accuracy': float(max(self.history.history['val_accuracy'])),
            'training_date': datetime.now().isoformat(),
        }
        
        return self.history
    
    def evaluate(self, model: keras.Model,
                test_data: Tuple[np.ndarray, np.ndarray]) -> Dict:
        """
        Evaluate model on test data.
        
        Args:
            model: Trained keras.Model
            test_data: Tuple of (X_test, y_test)
            
        Returns:
            Dict with evaluation metrics
        """
        X_test, y_test = test_data
        
        # Evaluate
        results = model.evaluate(X_test, y_test, verbose=0)
        
        # Get predictions
        predictions = model.predict(X_test, verbose=0)
        
        metrics = {
            'test_loss': float(results[0]),
            'test_accuracy': float(results[1]),
            'test_precision': float(results[2]) if len(results) > 2 else None,
            'test_recall': float(results[3]) if len(results) > 3 else None,
            'test_auc': float(results[4]) if len(results) > 4 else None,
            'predictions': predictions.tolist(),
            'true_labels': y_test.tolist(),
        }
        
        return metrics
    
    def save_metadata(self, model_name: str):
        """Save training metadata to JSON."""
        metadata_path = self.log_dir / f"{model_name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.training_metadata, f, indent=2)
        print(f"Metadata saved to {metadata_path}")
    
    def plot_training_history(self, model_name: str, save_path: Optional[str] = None):
        """
        Plot training history (requires matplotlib).
        
        Args:
            model_name: Name for title
            save_path: Path to save figure
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available. Install with: pip install matplotlib")
            return
        
        if self.history is None:
            print("No training history available")
            return
        
        history = self.history.history
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss
        axes[0].plot(history['loss'], label='Train Loss')
        axes[0].plot(history['val_loss'], label='Val Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title(f'{model_name} - Loss')
        axes[0].legend()
        axes[0].grid(True)
        
        # Accuracy
        axes[1].plot(history['accuracy'], label='Train Accuracy')
        axes[1].plot(history['val_accuracy'], label='Val Accuracy')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy')
        axes[1].set_title(f'{model_name} - Accuracy')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            print(f"Training history plot saved to {save_path}")
        else:
            plt.show()
    
    def load_best_model(self, model_name: str) -> Optional[keras.Model]:
        """
        Load the best checkpoint for a given model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Loaded model or None if not found
        """
        checkpoint_path = self.model_dir / f"{model_name}_best.h5"
        
        if not checkpoint_path.exists():
            print(f"Model not found: {checkpoint_path}")
            return None
        
        try:
            model = keras.models.load_model(str(checkpoint_path))
            print(f"Loaded model from {checkpoint_path}")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None


def train_with_early_stopping(model: keras.Model,
                             X_train: np.ndarray,
                             y_train: np.ndarray,
                             X_val: np.ndarray,
                             y_val: np.ndarray,
                             epochs: int = 50,
                             batch_size: int = 32,
                             patience: int = 10) -> keras.callbacks.History:
    """
    Quick training function with early stopping.
    
    Args:
        model: Compiled keras.Model
        X_train, y_train: Training data
        X_val, y_val: Validation data
        epochs: Max epochs
        batch_size: Batch size
        patience: Early stopping patience
        
    Returns:
        Training history
    """
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=patience,
        restore_best_weights=True
    )
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stop],
        verbose=1
    )
    
    return history
