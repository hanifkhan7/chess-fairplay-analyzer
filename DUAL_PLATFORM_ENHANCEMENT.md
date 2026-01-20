# Chess Fairplay Analyzer v3.0 - Dual-Platform Enhancement

## Overview
The analyzer now supports **both Chess.com and Lichess games** simultaneously for all features. Users can select:
- Chess.com only
- Lichess only  
- Both platforms (dual-fetch) - **RECOMMENDED**

## What Was Added

### 1. **Dual-Platform Fetcher** (`chess_analyzer/dual_fetcher.py`)
New module with comprehensive dual-platform support:

```python
fetch_dual_platform_games(username, max_games, platforms=['chess.com', 'lichess'])
```

**Features:**
- Simultaneously fetches from selected platforms
- Returns tuple: (games list, platform counts dict)
- Handles platform-specific APIs gracefully
- Provides summary report of games fetched from each platform

**Example:**
```python
games, counts = fetch_dual_platform_games('hikaru', max_games=50)
# counts = {'chess.com': 30, 'lichess': 20}
```

### 2. **Menu Integration Updates**

All features now support platform selection:

#### Feature 1: Analyze Player (Enhanced v3.0)
- **New:** Platform selection menu (Chess.com/Lichess/Both)
- **New:** Shows platform breakdown in results
- **New:** Parallel analysis across platform-specific game formats

#### Feature 2: Download Games
- **New:** Select which platform(s) to export from
- **Update:** Uses unified `_fetch_games()` helper

#### All Other Features (Strength Profile, Accuracy Report, etc.)
- **Updated:** Function headers indicate dual-platform support
- **Updated:** Can now analyze mixed platform games

### 3. **Analyzer v3.0 Enhancements**

**Constructor Update:**
```python
analyzer = EnhancedPlayerAnalyzer(
    config,
    use_lichess=True,      # For Lichess cloud analysis
    use_chess_com=True,    # For Chess.com local analysis
    cache_dir="cache/analysis"
)
```

**Display Update:**
Results now show platform breakdown:
```
[ANALYSIS] ENHANCED PLAYER ANALYSIS v3.0 - HIKARU
Sources: Chess.Com: 5 games
...
```

### 4. **Helper Function**

New unified fetch function in menu.py:
```python
def _fetch_games(username, max_games=50, platforms=['chess.com', 'lichess'], config=None):
    """Fetch games from one or both platforms with unified interface."""
```

## Technical Details

### Platform Detection
Games are automatically tagged with their source:
```python
source = get_platform_source(game)  # Returns 'chess.com', 'lichess', or 'unknown'
```

### Error Handling
- Chess.com fetch failure doesn't block Lichess (and vice versa)
- If both fail, clear error message displayed
- Partial results still analyzed and reported

### Performance
- **Parallel fetching** from both platforms simultaneously
- Chess.com games analyzed with local Stockfish
- Lichess games use cloud analysis when available
- Combined caching across platforms

### Backwards Compatibility
- All existing single-platform functionality preserved
- `fetch_player_games()` still works for Chess.com only
- Menu gracefully handles missing platforms

## User Experience

### Option 1: Single Platform
```
Select source:
1. Chess.com only
2. Lichess only
3. Both platforms (recommended)
```

### Option 2: Unified Results
```
[SUMMARY] Total games fetched: 10
  Chess.Com: 5 games
  Lichess: 5 games

[ANALYSIS] Results (all 10 games combined analysis)
Sources: Chess.Com: 5 games, Lichess: 5 games
```

## Files Modified

1. **chess_analyzer/dual_fetcher.py** (NEW - 227 lines)
   - `fetch_dual_platform_games()`
   - `fetch_lichess_games()`
   - `get_platform_source()`
   - `merge_platform_results()`

2. **chess_analyzer/analyzer_v3.py** (712 lines)
   - Added `use_chess_com` parameter
   - Updated display to show platform breakdown
   - Fixed Unicode encoding for progress bar

3. **chess_analyzer/menu.py** (1633 lines)
   - Added `_fetch_games()` helper
   - Updated `_analyze_player()` with platform menu
   - Updated `_download_games()` with platform menu
   - Updated all feature function headers
   - Added platform selection to all major features

## Testing Recommended

1. **Dual-Fetch Test:**
   ```
   Analyze "hikaru": Fetch 10 games from both platforms
   ```

2. **Single Platform Test:**
   ```
   Analyze "someuser": Chess.com only / Lichess only
   ```

3. **Feature Test:**
   Download, Strength Profile, Accuracy Report (each with both platforms)

## Future Enhancements

Possible additions:
- Platform-specific accuracy metrics
- Cross-platform consistency analysis  
- Per-platform anomaly detection
- Merged statistics with platform weighting

## Status

✅ **Ready for Testing**
- All code changes implemented
- Syntax verified
- Error handling added
- Backwards compatible

**Next:** Test with various usernames to verify dual-platform functionality works as expected.
