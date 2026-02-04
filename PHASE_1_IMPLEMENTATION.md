# Phase 1 Implementation Plan: ML Cheat Detection

## Overview
Phase 1 focuses on integrating CNN-LSTM models to enhance cheat detection accuracy from the current engine-correlation-only approach to a multi-modal detection system achieving 80%+ accuracy.

## Timeline: Q2 2026 (April - June)
- **Month 1** (April): Research & Architecture
- **Month 2** (May): Model Development & Training  
- **Month 3** (June): Integration & Testing

---

## Task Breakdown

### Week 1-2: Research & Architecture (April 1-14)

**1.1 Model Architecture Design**
- [ ] Review Lichess Irwin source code (TensorFlow reference)
- [ ] Review Kaladin CNN architecture
- [ ] Design custom CNN-LSTM for PV analysis
- [ ] Document layer specifications
- [ ] Create model_architecture.md

**Output**: `docs/ml_architecture.md`

**1.2 Dataset Planning**
- [ ] Research FICS dataset (open chess games)
- [ ] Research Lichess open dataset (AGPL)
- [ ] Plan labeling strategy (human vs. engine)
- [ ] Estimate data requirements (50k+ games)
- [ ] Create data_sourcing.md

**Output**: `docs/data_sourcing.md`

**1.3 Environment Setup**
- [ ] Update requirements.txt with TensorFlow, Keras
- [ ] Create `chess_analyzer/ml/` module structure
- [ ] Setup training environment
- [ ] Document GPU/CPU requirements
- [ ] Create setup_ml_environment.sh

**Output**: `requirements_ml.txt`, `setup_ml_environment.sh`

---

### Week 3-4: Initial Development (April 15-28)

**2.1 Board Tensorization Module**
- [ ] Create `chess_analyzer/ml/tensor_converter.py`
- [ ] Implement 12-channel 8x8 grid conversion
- [ ] Handle piece representations
- [ ] Handle move sequences (temporal dimension)
- [ ] Unit tests for conversion accuracy
- [ ] Benchmark conversion speed

```python
# Example: 12-channel representation
# Channels: WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK
def board_to_tensor(board):
    """Convert chess.Board to 12x8x8 tensor"""
    # Implementation
    pass
```

**Output**: `chess_analyzer/ml/tensor_converter.py` + tests

**2.2 Model Architecture Implementation**
- [ ] Create `chess_analyzer/ml/models.py`
- [ ] Implement CNN layers (feature extraction)
- [ ] Implement LSTM layers (sequence learning)
- [ ] Add dropout for regularization
- [ ] Add batch normalization
- [ ] Create model factory function

```python
def build_cnn_lstm_model(input_shape=(20, 8, 8, 12)):
    """Build CNN-LSTM architecture"""
    # Conv layers for board feature extraction
    # LSTM for move sequence patterns
    # Dense layer for binary classification
    pass
```

**Output**: `chess_analyzer/ml/models.py`

**2.3 Training Pipeline Setup**
- [ ] Create `chess_analyzer/ml/trainer.py`
- [ ] Implement data loader (PGN → tensors)
- [ ] Implement training loop
- [ ] Implement validation metrics
- [ ] Add checkpoint saving
- [ ] Add tensorboard logging

**Output**: `chess_analyzer/ml/trainer.py`

---

### Week 5-6: Data Collection & Preparation (May 1-12)

**3.1 Dataset Acquisition**
- [ ] Download FICS dataset (or subset)
- [ ] Download Lichess open games
- [ ] Verify AGPL compliance
- [ ] Store in `datasets/` directory
- [ ] Document source and license

**Estimated**: 10,000-50,000 games minimum

**3.2 Data Labeling**
- [ ] Identify human games (from established humans)
- [ ] Identify engine games (Stockfish evaluation)
- [ ] Create labeling script
- [ ] Generate labeled dataset CSV
- [ ] Verify label distribution (balanced classes)

**Output**: `datasets/labeled_games.csv`

**3.3 Data Preprocessing**
- [ ] Create `chess_analyzer/ml/data_prep.py`
- [ ] Convert PGN to tensors
- [ ] Handle variable game lengths
- [ ] Normalize/standardize data
- [ ] Split train/val/test (80/10/10)
- [ ] Create data augmentation (position flipping, etc.)

**Output**: Training dataset files

---

### Week 7-8: Model Training (May 13-26)

**4.1 Initial Training Run**
- [ ] Train on small subset (1,000 games)
- [ ] Validate training process
- [ ] Check for NaN/gradient issues
- [ ] Benchmark training time
- [ ] Document hyperparameters

**4.2 Full Model Training**
- [ ] Train on full dataset
- [ ] Monitor loss curves
- [ ] Monitor accuracy metrics
- [ ] Early stopping implementation
- [ ] Save best model checkpoints
- [ ] Track training metrics with TensorBoard

**Target Metrics**:
- Validation accuracy: 80%+
- Precision: 85%+
- Recall: 75%+
- AUC-ROC: 0.88+

**Output**: `models/cnn_lstm_detector_v1.h5`

**4.3 Cross-Validation**
- [ ] Implement k-fold cross-validation
- [ ] Test on hold-out test set
- [ ] Generate confusion matrix
- [ ] Calculate false positive rate (<5%)
- [ ] Generate ROC curves

---

### Week 9-10: Integration (June 2-16)

**5.1 Create ML Detector Module**
- [ ] Create `chess_analyzer/ml_detector.py`
- [ ] Implement detection interface
- [ ] Add model loading/caching
- [ ] Add confidence score calculation
- [ ] Add explanations for predictions

```python
class MLCheatDetector:
    def __init__(self, model_path):
        self.model = load_model(model_path)
    
    def detect_cheating(self, games, confidence_threshold=0.7):
        """Detect cheating with confidence scores"""
        # Process games
        # Return predictions with scores
        pass
    
    def explain_prediction(self, game, prediction):
        """Provide explanation for flag"""
        # Which moves were suspicious?
        # What patterns matched?
        pass
```

**Output**: `chess_analyzer/ml_detector.py`

**5.2 Menu Integration**
- [ ] Add Feature 17 to menu.py
- [ ] Add ML detection to Feature 1 (Player Analysis)
- [ ] Modify Feature 5 (Accuracy Report) to include ML scores
- [ ] Add confidence percentage display
- [ ] Add option to use ML-only or combined detection

```python
# Feature 17: ML Cheat Detection
def _ml_cheat_detection():
    """Analyze games using ML model"""
    # Get player
    # Get games
    # Run ML detector
    # Display results with confidence
    pass
```

**Output**: Menu updates, Feature 17

**5.3 Report Generation**
- [ ] Create `chess_analyzer/ml_report_generator.py`
- [ ] Add ML scores to HTML reports
- [ ] Add confidence visualizations
- [ ] Add explanation sections
- [ ] Compare ML vs. traditional detection

**Output**: Enhanced report templates

---

### Week 11-12: Testing & Documentation (June 17-30)

**6.1 Unit Tests**
- [ ] Test tensorization accuracy
- [ ] Test model inference
- [ ] Test edge cases (incomplete games, etc.)
- [ ] Test performance benchmarks

```python
def test_tensor_conversion():
    """Verify board_to_tensor correctness"""
    # Test known positions
    # Check tensor shape
    # Check piece counts
    pass

def test_model_inference():
    """Verify model predictions"""
    # Test on known human game
    # Test on known engine game
    # Check output format
    pass
```

**Output**: `tests/test_ml_detector.py` (80%+ coverage)

**6.2 Integration Tests**
- [ ] Test end-to-end detection flow
- [ ] Test menu navigation
- [ ] Test report generation
- [ ] Test with real player data

**6.3 Documentation**
- [ ] Create `docs/ml_detector_usage.md`
- [ ] Document model architecture
- [ ] Document training procedure (if needed for fine-tuning)
- [ ] Add examples
- [ ] Add FAQ

**6.4 Performance Benchmarking**
- [ ] Benchmark inference time per game
- [ ] Benchmark memory usage
- [ ] Test on various hardware
- [ ] Document system requirements

**Output**: `docs/performance_benchmark.md`

---

## Deliverables Checklist

**Code**:
- [ ] `chess_analyzer/ml/__init__.py`
- [ ] `chess_analyzer/ml/tensor_converter.py` (+ tests)
- [ ] `chess_analyzer/ml/models.py` (+ tests)
- [ ] `chess_analyzer/ml/trainer.py`
- [ ] `chess_analyzer/ml/data_prep.py`
- [ ] `chess_analyzer/ml_detector.py` (+ tests)
- [ ] `chess_analyzer/ml_report_generator.py`
- [ ] Updated `chess_analyzer/menu.py` (Feature 17)
- [ ] `requirements_ml.txt`

**Documentation**:
- [ ] `docs/ml_architecture.md`
- [ ] `docs/data_sourcing.md`
- [ ] `docs/ml_detector_usage.md`
- [ ] `docs/performance_benchmark.md`
- [ ] `TRAINING_GUIDE.md` (for community model updates)

**Models & Data**:
- [ ] Trained model: `models/cnn_lstm_detector_v1.h5`
- [ ] Training logs: `logs/training_*.log`
- [ ] Evaluation metrics: `reports/ml_evaluation.json`

**Tests**:
- [ ] Unit tests: `tests/test_ml_detector.py`
- [ ] Integration tests: `tests/test_integration_ml.py`
- [ ] Coverage: 80%+

---

## Success Criteria

**Detection Accuracy**:
- ✅ Achieves 80%+ accuracy on hold-out test set
- ✅ False positive rate < 5%
- ✅ Precision >= 85%
- ✅ Recall >= 75%

**Integration**:
- ✅ Seamlessly integrated with existing features
- ✅ No breaking changes to CLI
- ✅ Optional (works without GPU)
- ✅ Clear confidence scores in output

**Performance**:
- ✅ Inference time: <100ms per game
- ✅ Memory footprint: <500MB
- ✅ Works on CPU (with acceptable speed)

**Documentation**:
- ✅ Complete usage guide
- ✅ Model architecture documented
- ✅ Training procedure repeatable
- ✅ Community can fine-tune models

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Data imbalance | Poor accuracy | Use class weights, data augmentation |
| Overfitting | Poor generalization | Dropout, regularization, cross-validation |
| GPU requirements | Limited adoption | Ensure CPU inference works, optimize model |
| Dataset licensing | Legal issues | Use only open AGPL datasets |
| False positives | User trust | Confidence thresholds, conservative flagging |
| Model staleness | Accuracy degradation | Plan for retraining quarterly |

---

## Budget Estimate
- **Development Time**: 100 hours (~2.5 months, 1 developer)
- **GPU Cloud Cost** (optional): $200-500 (Google Colab Pro alternative)
- **Data Storage**: ~10GB (manageable on standard hardware)

---

## Next Steps After Phase 1

1. **Community Feedback** (2 weeks)
   - Release as beta feature
   - Gather user feedback
   - Collect real-world data

2. **Model Refinement** (1 month)
   - Retrain with user feedback
   - Improve on edge cases
   - Achieve 85%+ accuracy

3. **Phase 2 Transition** (1 month)
   - Begin web UI development
   - Integrate ML into web dashboard
   - Plan API endpoints

---

**Document Created**: January 30, 2026  
**Phase 1 Start Date**: April 1, 2026  
**Phase 1 Target Completion**: June 30, 2026  
**Version**: 1.0
