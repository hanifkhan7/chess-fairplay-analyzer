"""
Sample ML Training Script for Chess Fairplay Analyzer

This script demonstrates how to:
1. Prepare chess game data from PGN files
2. Build a CNN-LSTM model
3. Train on labeled human/engine games
4. Evaluate and save the model

Run with: python train_ml_model_sample.py

Note: This requires TensorFlow and sufficient game data.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")

# Check if ML dependencies are installed
try:
    import tensorflow as tf
    import numpy as np
    print(f"✓ TensorFlow {tf.__version__} installed")
except ImportError as e:
    print(f"✗ TensorFlow not found. Install with:")
    print(f"  pip install -r requirements_ml.txt")
    sys.exit(1)

# Import ML modules
try:
    from chess_analyzer.ml import (
        DataPreparator, 
        build_cnn_lstm_model,
        build_lightweight_cnn_lstm_model
    )
    from chess_analyzer.ml.trainer import MLTrainer
    print("✓ ML modules imported successfully")
except ImportError as e:
    print(f"✗ Error importing ML modules: {e}")
    sys.exit(1)


def setup_directories():
    """Create necessary directories."""
    directories = ['models', 'logs', 'datasets', 'data']
    for d in directories:
        os.makedirs(d, exist_ok=True)
    print(f"✓ Created directories: {', '.join(directories)}")


def create_sample_data():
    """
    Create sample synthetic training data for demonstration.
    
    In production, you would:
    - Download real games from Chess.com API
    - Download real games from Lichess API  
    - Label them as human or engine
    """
    print("\n" + "="*60)
    print("CREATING SAMPLE DATA")
    print("="*60)
    
    np.random.seed(42)
    
    # Create synthetic data for demonstration
    # Real training would use actual PGN games
    num_human_samples = 100
    num_engine_samples = 100
    
    # Human games: more variance (lower probability of engine moves)
    X_human = np.random.rand(num_human_samples, 20, 8, 8, 12).astype(np.float32)
    y_human = np.tile([1, 0], (num_human_samples, 1)).astype(np.float32)  # Class 0: human
    
    # Engine games: more consistent (higher probability of engine moves)
    X_engine = np.random.rand(num_engine_samples, 20, 8, 8, 12).astype(np.float32)
    y_engine = np.tile([0, 1], (num_engine_samples, 1)).astype(np.float32)  # Class 1: engine
    
    # Combine and shuffle
    X = np.vstack([X_human, X_engine])
    y = np.vstack([y_human, y_engine])
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    print(f"✓ Created {num_human_samples} human game samples")
    print(f"✓ Created {num_engine_samples} engine game samples")
    print(f"✓ Total: {len(X)} samples")
    print(f"  Shape: {X.shape}")
    print(f"  Labels: {np.sum(y, axis=0)}")
    
    return X, y


def split_data(X, y, train_ratio=0.8, val_ratio=0.1):
    """Split data into train/val/test."""
    from sklearn.model_selection import train_test_split
    
    # First split: train vs temp (val + test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(1 - train_ratio), random_state=42
    )
    
    # Second split: val vs test
    val_ratio_adjusted = val_ratio / (1 - train_ratio)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    return {
        'X_train': X_train,
        'y_train': y_train,
        'X_val': X_val,
        'y_val': y_val,
        'X_test': X_test,
        'y_test': y_test,
    }


def train_model():
    """Main training function."""
    
    print("\n" + "="*60)
    print("CHESS FAIRPLAY ANALYZER - ML MODEL TRAINING")
    print("="*60)
    
    # Setup
    setup_directories()
    
    # Create sample data
    print("\n" + "="*60)
    print("DATA PREPARATION")
    print("="*60)
    
    X, y = create_sample_data()
    data = split_data(X, y)
    
    print(f"\nDataset split:")
    print(f"  Train: {data['X_train'].shape[0]} samples")
    print(f"  Val:   {data['X_val'].shape[0]} samples")
    print(f"  Test:  {data['X_test'].shape[0]} samples")
    
    # Build model
    print("\n" + "="*60)
    print("MODEL ARCHITECTURE")
    print("="*60)
    
    model_choice = input("\nSelect model (1=CNN-LSTM [default], 2=Lightweight): ").strip()
    
    if model_choice == "2":
        print("Building lightweight CNN-LSTM model...")
        model = build_lightweight_cnn_lstm_model(
            input_shape=(20, 8, 8, 12),
            num_classes=2,
            learning_rate=0.001
        )
    else:
        print("Building full CNN-LSTM model...")
        model = build_cnn_lstm_model(
            input_shape=(20, 8, 8, 12),
            num_classes=2,
            learning_rate=0.001
        )
    
    # Print model architecture
    print("\nModel Summary:")
    model.summary()
    
    print(f"\nTotal Parameters: {model.count_params():,}")
    
    # Calculate class weights
    print("\n" + "="*60)
    print("TRAINING CONFIGURATION")
    print("="*60)
    
    preparator = DataPreparator()
    class_weights = preparator.calculate_class_weights(data['y_train'])
    
    print(f"\nClass weights: {class_weights}")
    print(f"  (Minority class gets higher weight for balancing)")
    
    # Train model
    print("\n" + "="*60)
    print("TRAINING")
    print("="*60)
    
    trainer = MLTrainer(model_dir="models", log_dir="logs")
    
    print("\nStarting training...")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        history = trainer.train(
            model=model,
            train_data=(data['X_train'], data['y_train']),
            val_data=(data['X_val'], data['y_val']),
            model_name="chess_detector_sample",
            epochs=20,  # Limited for demonstration
            batch_size=16,
            class_weight=class_weights
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        return
    
    # Evaluate
    print("\n" + "="*60)
    print("EVALUATION")
    print("="*60)
    
    print("\nEvaluating on test set...")
    eval_results = trainer.evaluate(model, (data['X_test'], data['y_test']))
    
    print(f"\nTest Results:")
    print(f"  Loss:      {eval_results['test_loss']:.4f}")
    print(f"  Accuracy:  {eval_results['test_accuracy']:.3%}")
    if eval_results['test_precision']:
        print(f"  Precision: {eval_results['test_precision']:.3%}")
    if eval_results['test_recall']:
        print(f"  Recall:    {eval_results['test_recall']:.3%}")
    if eval_results['test_auc']:
        print(f"  AUC:       {eval_results['test_auc']:.3f}")
    
    # Save metadata
    trainer.save_metadata("chess_detector_sample")
    
    # Plot training history
    print("\nGenerating training history plot...")
    trainer.plot_training_history(
        "chess_detector_sample",
        save_path="logs/training_history_sample.png"
    )
    
    # Save results
    print("\n" + "="*60)
    print("RESULTS SAVED")
    print("="*60)
    
    print("\nFiles saved:")
    print("  ✓ models/chess_detector_sample_best.h5")
    print("  ✓ logs/chess_detector_sample_training.csv")
    print("  ✓ logs/chess_detector_sample_metadata.json")
    print("  ✓ logs/training_history_sample.png")
    
    # Next steps
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    
    print("\n1. Test the model with:")
    print("   python -c \"from chess_analyzer.ml_detector import MLCheatDetector\"")
    print("   python -c \"detector = MLCheatDetector('models/chess_detector_sample_best.h5')\"")
    
    print("\n2. For production training:")
    print("   - Use real PGN files (download from Chess.com, Lichess)")
    print("   - Prepare larger dataset (10,000+ games)")
    print("   - Tune hyperparameters")
    print("   - Use multiple models and ensemble")
    print("   - Evaluate on diverse players")
    
    print("\n3. Integration:")
    print("   - Feature 17: ML Cheat Detection")
    print("   - Add to Feature 1 (Player Analysis)")
    print("   - Include in reports")
    
    print("\n" + "="*60)
    print("Training complete! 🎉")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        train_model()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
