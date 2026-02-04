# ML Module Quick Start Guide

## Installation

Install ML dependencies:

```bash
pip install -r requirements_ml.txt
```

This installs:
- TensorFlow/Keras for neural networks
- scikit-learn for data processing
- Jupyter for interactive notebooks
- All other required packages

## Quick Start: Training a Model

### 1. Prepare Your Data

You need PGN files with labeled games:
- **Human games**: Regular chess games played by humans
- **Engine games**: Games played by chess engines like Stockfish

Place PGN files in a directory:
```
data/
  ├── human_games.pgn
  └── engine_games.pgn
```

### 2. Create Training Script

```python
import os
from chess_analyzer.ml import DataPreparator, build_cnn_lstm_model
from chess_analyzer.ml.trainer import MLTrainer

# Setup directories
os.makedirs("models", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("datasets", exist_ok=True)

# Prepare data
print("Preparing dataset...")
preparator = DataPreparator(sequence_length=20, augment=True)

data = preparator.prepare_dataset(
    pgn_file="data/",  # Directory with PGN files
    max_games=1000,    # Limit for testing
    test_size=0.1,
    val_size=0.1
)

# Save prepared dataset
preparator.save_dataset(data, "datasets/chess_detector")

# Balance dataset if needed
print("Balancing dataset...")
X_train, y_train = preparator.balance_dataset(
    data['X_train'], 
    data['y_train'], 
    strategy='oversample'
)

# Build model
print("Building model...")
model = build_cnn_lstm_model(
    input_shape=(20, 8, 8, 12),
    num_classes=2,
    learning_rate=0.001
)

model.summary()

# Train model
print("Training model...")
trainer = MLTrainer(model_dir="models", log_dir="logs")

history = trainer.train(
    model=model,
    train_data=(X_train, y_train),
    val_data=(data['X_val'], data['y_val']),
    model_name="chess_detector_v1",
    epochs=50,
    batch_size=32,
    class_weight=preparator.calculate_class_weights(y_train)
)

# Evaluate
print("Evaluating on test set...")
eval_results = trainer.evaluate(model, (data['X_test'], data['y_test']))
print(f"Test Accuracy: {eval_results['test_accuracy']:.3f}")
print(f"Test AUC: {eval_results['test_auc']:.3f}")

# Save metadata
trainer.save_metadata("chess_detector_v1")

# Plot history
trainer.plot_training_history("chess_detector_v1", save_path="logs/training_history.png")
```

### 3. Run Training

```bash
python train_ml_model.py
```

This will:
1. Load and parse PGN files
2. Convert games to tensor sequences
3. Split into train/val/test
4. Build CNN-LSTM model
5. Train with early stopping and checkpointing
6. Evaluate on test set
7. Save best model to `models/chess_detector_v1_best.h5`

## Using the Trained Model

### Load and Analyze a Game

```python
from chess_analyzer.ml_detector import MLCheatDetector
import chess

# Load detector
detector = MLCheatDetector(
    model_path="models/chess_detector_v1_best.h5",
    threshold=0.7
)

# Create a game
board = chess.Board()
moves = [
    chess.Move.from_uci("e2e4"),
    chess.Move.from_uci("c7c5"),
    chess.Move.from_uci("g1f3"),
    # ... more moves ...
]

# Analyze
result = detector.analyze_game(moves)

# Check result
if result.get('is_cheating'):
    print("🚩 Likely cheating detected!")
    print(f"Engine similarity: {result['mean_engine_probability']:.1%}")
else:
    print("✓ Likely legitimate play")

# Get explanation
explanation = detector.explain_prediction(result)
print(explanation)
```

### Analyze Multiple Games

```python
# Prepare games
games_data = [
    {'moves': moves1},
    {'moves': moves2},
    {'moves': moves3},
]

# Analyze all
results = detector.analyze_games(games_data)

# Save results
detector.save_results(results, "analysis_results.json")
```

### Generate Report

```python
from chess_analyzer.ml_detector import MLDetectionReport

# Create report
html_report = MLDetectionReport.create_report(
    detector=detector,
    analysis_results=results,
    player_name="Username"
)

# Save
with open("report.html", "w") as f:
    f.write(html_report)
```

## Understanding the Model Architecture

The CNN-LSTM model has three main components:

### 1. Temporal Convolutional Layers (TimeDistributed)

Processes each board position independently to extract spatial features:
- Conv2D (32 filters)
- Conv2D (32 filters)
- MaxPooling (spatial reduction)
- Conv2D (64 filters)
- Conv2D (64 filters)
- MaxPooling
- Conv2D (128 filters)
- MaxPooling
- Flatten

### 2. Temporal LSTM Layers

Captures patterns across move sequences:
- LSTM (128 units, 30% dropout)
- LSTM (64 units, 30% dropout)

### 3. Classification Head

Dense layers with dropout and batch normalization:
- Dense (128 units, ReLU)
- Dense (64 units, ReLU)
- Dense (32 units, ReLU)
- Dense (2 units, Softmax) → [P(human), P(engine)]

## Tensor Representation

Each board position is converted to a 12×8×8 tensor:

**Channels:**
- 0-5: White pieces (Pawn, Knight, Bishop, Rook, Queen, King)
- 6-11: Black pieces (Pawn, Knight, Bishop, Rook, Queen, King)

**Values:** Binary (1.0 if piece present, 0.0 otherwise)

## Input/Output

- **Input**: Sequence of 20 consecutive board positions (from 20 moves)
- **Output**: Binary classification
  - Class 0: Human play (confidence 0-1)
  - Class 1: Engine play (confidence 0-1)

## Training Tips

### Data Collection
- Use games from Chess.com API (400+ rating)
- Use Lichess API (1800+ rating for human games)
- Use Stockfish 14+ for engine games

### Hyperparameters
- Sequence length: 20 (captures ~40 moves of context)
- Batch size: 32 (balance between speed and memory)
- Learning rate: 0.001 (Adam optimizer)
- Dropout: 0.2-0.4 (prevent overfitting)

### Best Practices
1. Balance human/engine games in training set
2. Use data augmentation (board flipping)
3. Monitor validation loss for early stopping
4. Save best checkpoint (highest validation accuracy)
5. Evaluate on separate test set
6. Cross-validate with k-fold

## Expected Performance

Target metrics:
- **Accuracy**: 80%+
- **Precision**: 85%+ (minimize false positives)
- **Recall**: 75%+ (catch cheaters)
- **AUC**: 0.88+
- **False Positive Rate**: <5% (important!)

## Troubleshooting

### Model not training (loss stuck at high value)
- Check data normalization (should be 0-1)
- Verify label encoding (one-hot with 2 classes)
- Reduce learning rate
- Check for NaN values in data

### Model overfitting (high train, low val accuracy)
- Increase dropout rates
- Add L2 regularization
- Use data augmentation
- Train for fewer epochs

### Inference too slow
- Use lightweight model: `build_lightweight_cnn_lstm_model()`
- Reduce sequence length (10-15 instead of 20)
- Batch predictions together
- Use GPU (install tensorflow-gpu)

### Out of memory during training
- Reduce batch size (16 → 8)
- Reduce sequence length
- Use gradient accumulation
- Train on subset of data first

## Integration with Main Analyzer

The ML detector integrates with the main Chess Fairplay Analyzer:

```python
from chess_analyzer.enhanced_analyzer import EnhancedAnalyzer
from chess_analyzer.ml_detector import MLCheatDetector

analyzer = EnhancedAnalyzer(config)
ml_detector = MLCheatDetector("models/chess_detector_v1_best.h5")

# Analyze player
results = analyzer.analyze_player("johndoe")

# Add ML detection
for result in results:
    if 'moves' in result:
        ml_result = ml_detector.analyze_game(result['moves'])
        result['ml_detection'] = ml_result
```

## References

- **TensorFlow Documentation**: https://www.tensorflow.org/
- **Keras API**: https://keras.io/
- **Chess Engine Analysis**: https://en.wikipedia.org/wiki/Chess_engine
- **Lichess Irwin**: https://github.com/lichess-org/irwin
- **Kaladin**: https://github.com/ianreah/chess-stat-tracker

## Next Steps

1. Collect labeled game data
2. Prepare dataset using DataPreparator
3. Train model with MLTrainer
4. Evaluate on test set
5. Integrate into Feature 17 (ML Cheat Detection)
6. Gather user feedback and retrain
7. Deploy to production

**Questions?** See PHASE_1_IMPLEMENTATION.md for detailed roadmap.
