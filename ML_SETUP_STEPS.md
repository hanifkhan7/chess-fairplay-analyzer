# ML Setup Checklist - Do This Now

## 🟢 STEP 1: Install ML Dependencies (5 minutes)
```bash
cd c:\Users\zaibi\chess-fairplay-analyzer
pip install -r requirements_ml.txt
```
**Expected output**: TensorFlow, scikit-learn, etc. installed
**✓ Mark done when complete**

---

## 🟢 STEP 2: Test Installation with Sample Data (5 minutes)
```bash
python train_ml_model_sample.py
```
**What happens**:
- Creates fake training data
- Trains model for 20 epochs
- Shows accuracy metrics
- Saves model to: `models/chess_detector_sample_best.h5`

**✓ Mark done when you see "Training complete! 🎉"**

---

## 🟡 STEP 3: Download Real Training Data (30 minutes)

You need PGN files with real games. Choose ONE method:

### Method A: Quick (Recommended for First Time)
1. Go to: https://lichess.org/api/explorer/master
2. Download 50 games as PGN
3. Save to: `data/human_games.pgn`

Then download engine games:
1. Go to: https://www.chess.com/news/view/public-data-api
2. Download chess.com games
3. Save to: `data/engine_games.pgn`

### Method B: Automated (Advanced)
Use this Python script:
```python
import requests
import os

os.makedirs("data", exist_ok=True)

# Download from Lichess
url = "https://lichess.org/api/games/user/GothamChess?max=100&format=pgn"
r = requests.get(url, headers={"Accept": "text/plain"})
with open("data/human_games.pgn", "w") as f:
    f.write(r.text)
```

**✓ Verify**: You have files in `data/` folder

---

## 🟡 STEP 4: Create Training Script (5 minutes)

Create file: `train_ml_real_model.py`

Copy the script from **ML_SETUP_GUIDE.md** → "Create Training Script" section

Save it to your project root

**✓ Verify**: File exists at `c:\Users\zaibi\chess-fairplay-analyzer\train_ml_real_model.py`

---

## 🔴 STEP 5: Train the Model (1-2 hours)

```bash
python train_ml_real_model.py
```

**What happens**:
- Loads PGN files (5-10 min)
- Converts to tensors (5-10 min)
- Trains CNN-LSTM model (20-40 min depending on data)
- Saves best model to: `models/chess_detector_real_best.h5`
- Shows final accuracy

**Expected accuracy**: 75-85%

**✓ Watch for**:
- "Training complete" message
- Model accuracy printed
- File saved in models/

---

## 🟢 STEP 6: Test Your Trained Model (2 minutes)

```bash
python run_menu.py
```

Then:
1. Select **Feature 17: ML Cheat Detection**
2. Enter a player username
3. It will analyze their games with YOUR trained model
4. Shows: cheating probability for each game

**✓ You're done when** you see analysis results!

---

## 📊 Progress Tracker

```
☐ Step 1: Install ML dependencies
☐ Step 2: Test with sample data  
☐ Step 3: Download real games
☐ Step 4: Create training script
☐ Step 5: Train real model
☐ Step 6: Test in Feature 17
```

---

## ⏱️ Time Estimate

| Step | Time | Status |
|------|------|--------|
| 1. Install deps | 5 min | Quick ✓ |
| 2. Sample test | 5 min | Quick ✓ |
| 3. Download data | 30 min | Medium |
| 4. Create script | 5 min | Quick ✓ |
| 5. Train model | 1-2 hrs | Long ⏳ |
| 6. Test in menu | 2 min | Quick ✓ |
| **TOTAL** | **~2-3 hours** | - |

---

## 🆘 Quick Help

**Q: Where do I put PGN files?**
A: Create folder `data/` in project root. Put `.pgn` files there.

**Q: How do I download PGN files?**
A: 
- Lichess: https://lichess.org → Export games
- Chess.com: https://www.chess.com → Player profile → Download games

**Q: Training too slow?**
A: 
- Use fewer games in script: `max_games=1000`
- Reduce batch_size: 32 → 16
- Use GPU version of TensorFlow

**Q: Model accuracy is low?**
A:
- Use more games (50,000+ for good accuracy)
- Use balanced dataset (equal human + engine)
- Train for more epochs

**Q: Where is the trained model saved?**
A: `models/chess_detector_real_best.h5`

---

## 📖 Full Documentation

- **Complete Guide**: `ML_SETUP_GUIDE.md`
- **Quick Start**: `docs/ML_QUICK_START.md`  
- **Implementation Plan**: `PHASE_1_IMPLEMENTATION.md`
- **Sample Script**: `train_ml_model_sample.py`

---

## ✅ Current Status

- ✓ ML module created
- ✓ Feature 17 integrated into menu
- ✓ All code ready
- ✓ Documentation complete
- ⏳ **WAITING**: You to follow these steps!

**Start now with Step 1!** 👇

```bash
pip install -r requirements_ml.txt
```
