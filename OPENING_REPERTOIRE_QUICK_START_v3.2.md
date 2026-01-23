# Opening Repertoire Inspector v3.2 - Quick Start Guide

## What's New (v3.2 Enhancements)

### 🎯 Main Features
1. **ECO Codes** - Every opening now shows its ECO classification (C20, C80, etc.)
2. **Opening Tree** - Visual ASCII tree showing how you branch into different openings
3. **Better Graphs** - Enhanced visualizations with colors, dual-panel layouts, and statistics
4. **Opening Names** - Full opening classifications displayed throughout

## How to Use

### Step 1: Run the Program
```bash
python run_menu.py
```

### Step 2: Select Option 10
```
Chess FairPlay Analyzer
======================
1. Game Analysis
2. Player Statistics
...
10. Opening Repertoire Inspector ← SELECT THIS
...
```

### Step 3: Enter Your Details
```
Player Username: HD-MI6
Select Color (white/black/both): white
Filter Results (all/wins/losses/draws): all
Minimum Moves: 15
Max Games to Analyze: 25
```

### Step 4: View Results

#### You'll see:
1. **Summary Section** - Overall stats
   - Total games analyzed
   - Color distribution
   - Unique openings found
   - Average game length
   - Win/Loss/Draw percentages

2. **Top Openings Table** - With ECO codes
   ```
   1. Ruy Lopez [C80]        (25 games, 56.2% W)
   2. Italian Game [C23]     (18 games, 52.1% W)
   3. Sicilian Defense [B20] (16 games, 48.5% W)
   ...
   ```

3. **Opening Tree Visualization** - ASCII diagram
   ```
   └── 1.e4 [C20] Italian Game          ✓ 58%W 20%D 22%L (50x)
       ├── 1...e5 [C20] Italian Game   = 51%W 25%D 24%L (35x)
       │   ├── 2.Nf3 [C23] Italian      ✓ 56%W 28%D 16%L (25x)
       │   └── 2.Bc4 [C23] Italian      = 48%W 26%D 26%L (10x)
       └── 1...c5 [C20] Sicilian Decline ✗ 42%W 30%D 28%L (15x)
   ```

4. **Statistical Graphs** (5 types, 10 panels total)
   - Opening frequency with ECO codes
   - Win rates by opening (color-coded)
   - White vs Black comparison
   - Result distribution
   - Game length analysis

### Step 5: Export Results (Optional)
After viewing graphs, you can export data:
- **CSV Format** - For spreadsheet analysis
- **Excel Format** - With multiple sheets and statistics

## Reading the Opening Tree

### Symbols & Meaning
- `✓` = Strong opening (>55% win rate) - GREEN
- `=` = Balanced opening (45-55% win rate) - ORANGE  
- `✗` = Weak opening (<45% win rate) - RED

### Example: `├── 2.Nf3 [C23] Italian [✓ 56%W 28%D 16%L (25x)]`
- **2.Nf3** = Move number and notation
- **[C23]** = ECO code for this position
- **Italian** = Opening classification
- **✓** = Performance indicator (strong)
- **56%W** = Win percentage with this move
- **28%D** = Draw percentage  
- **16%L** = Loss percentage
- **(25x)** = Played 25 games from this position

## Understanding the Graphs

### Graph 1: Most Played Openings
- Shows your favorite openings
- ECO codes below each opening name
- Longer bars = more games played

### Graph 2: Win Rate by Opening
- Green bars = Openings where you perform well
- Red bars = Openings where you struggle
- 50% line = Break-even point

### Graph 3: White vs Black Comparison
- Left panel = Result distribution (stacked percentages)
- Right panel = Win rate differences
- Shows if you perform differently with each color

### Graph 4: Result Distribution
- Left = Pie chart overview
- Right = Actual game counts
- Helps identify win/loss/draw tendencies

### Graph 5: Game Length Analysis
- Left = Histogram of typical game lengths
- Right = Length comparison by result (wins vs losses)
- Shows if you tend to have shorter decisive games

## Color Coding

### Performance Indicators
- **Green** (#2ecc71) = Strong/Winning
- **Blue** (#3498db) = Slight advantage
- **Orange** (#f39c12) = Balanced/Medium
- **Red** (#e74c3c) = Weak/Losing

## Tips for Analysis

1. **Find Your Strengths** - Look for green-coded openings
2. **Identify Weaknesses** - Check red-coded variations
3. **Understand Patterns** - Tree shows how games branch
4. **Compare Colors** - See if you play better as white/black
5. **Optimize Depth** - Tree shows up to 15 moves of analysis

## ECO Code Quick Reference

| Code | Opening Family |
|------|-----------------|
| A00-A99 | Unusual Openings |
| B00-B99 | Semi-Open Games (1.e4 but not 1...e5) |
| C00-C99 | Open Games (1.e4 e5) |
| D00-D99 | Closed Games (1.d4) |
| E00-E99 | Semi-Closed Games |

## Data Export

All exported files include:
- Opening names and ECO codes
- Full move sequences
- Results and opponent ratings
- Dates of games
- Color-specific breakdowns

## Questions?

The Opening Repertoire Inspector is designed to:
- ✓ Show your opening patterns
- ✓ Identify successful variations
- ✓ Find areas for improvement
- ✓ Compare performance by color
- ✓ Provide detailed statistics

Have fun analyzing your openings! 🎯♟️
