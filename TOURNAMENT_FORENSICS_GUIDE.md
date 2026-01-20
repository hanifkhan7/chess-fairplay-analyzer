#!/usr/bin/env python3
"""
Tournament Forensics Feature - Usage Examples & Tutorial
"""

print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                 TOURNAMENT FORENSICS ANALYSIS FEATURE                      ║
║              Detect Suspicious Activity in Tournament Results              ║
╚═══════════════════════════════════════════════════════════════════════════╝

OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This feature analyzes tournament results to detect suspicious patterns:

✓ ELO Probability Violations
  - Detects when weaker players beat much stronger opponents
  - Calculates statistical improbability
  - Example: 1600 ELO player wins tournament vs 2000+ ELO players

✓ Anomaly Detection
  - Unusually high win rates (>90%)
  - Unexpected tournament victories
  - Performance inconsistencies

✓ Statistical Analysis
  - Expected vs actual win rates
  - ELO rating analysis
  - Performance patterns

SUPPORTED PLATFORMS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ LICHESS (Recommended - Free API Access)
   - Full tournament data available
   - Real-time analysis
   - No authentication required

❌ CHESS.COM (Requires Paid API Access)
   - Tournament API requires premium subscription
   - Consider alternatives below

ALTERNATIVE FOR CHESS.COM TOURNAMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Since Chess.com's tournament API is behind a paywall, use these approaches:

1. ANALYZE TOURNAMENT PARTICIPANTS' GAMES
   - Get list of top finishers from Chess.com tournament
   - Use "Analyze Player" feature to check each top player
   - Look for anomalies in their historical games
   - Use "Multi-Player Comparison" to compare top performers

2. USE LICHESS TOURNAMENTS
   - Search lichess.org/tournament for similar tournaments
   - Analyze Lichess tournaments instead
   - Example: "Chess Puzzle Tournament" or "Arena Tournaments"

3. MANUAL TOURNAMENT CREATION
   - Export tournament results from Chess.com
   - Provide player names and ratings
   - System can analyze individual player games

HOW TO USE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTION 1: Analyze a Lichess Tournament
──────────────────────────────────────

1. Go to https://lichess.org/tournament
2. Find a concluded tournament
3. Copy the tournament ID from the URL
   Example: https://lichess.org/tournament/5N8Ny9oK → ID is "5N8Ny9oK"
4. In Chess Detective menu, select "Tournament Forensics"
5. Enter the tournament ID or full URL
6. System will analyze standings and flag anomalies

OPTION 2: Analyze Chess.com Tournament (Alternative Method)
────────────────────────────────────────────────────────────

1. Visit Chess.com tournament page
2. Note the top 10 finishers
3. In Chess Detective menu, select "Multi-Player Comparison"
4. Enter the top finisher usernames
5. System will compare their ELOs, accuracy, and performance patterns
6. Look for statistical anomalies

WHAT TO LOOK FOR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When analyzing tournament results:

🚩 HIGH SEVERITY FLAGS:
   • Much weaker player (200+ ELO gap) wins tournament
   • Win rate >95% against stronger opposition
   • Probability of result <1%

⚠️  MEDIUM SEVERITY FLAGS:
   • Win rate >90% against average opposition
   • 100+ ELO weaker player finishes top 3
   • Unusual score improvements vs historical

✓ NORMAL RESULTS:
   • Favorites win as expected
   • Ratings align with results
   • Win rates match ELO expectations

EXAMPLE ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tournament: "Blitz Battle Arena"
Average ELO: 1800

Finishers:
  1. Player A: 1600 ELO - 15/15 wins (100% win rate)
     🚩 FLAG: 200 ELO weaker than average, beat much stronger players
     Probability: <0.1%

  2. Player B: 2100 ELO - 14/15 wins (93% win rate)
     ✓ Normal: Expected to win, slight overperformance

  3. Player C: 1900 ELO - 13/15 wins (87% win rate)
     ✓ Normal: Near expected performance

Result: Player A's victory is statistically suspicious.

NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If anomalies are detected:

1. Use "Analyze Player" → Check flagged player's individual games
2. Look for: Engine-like moves, perfect accuracy, unusual time management
3. Use "Multi-Player Comparison" → Compare flagged player with others
4. Review game-by-game analysis for pattern recognition
5. Check "Account Metrics" → Rapid ELO swings, inconsistent performance

═══════════════════════════════════════════════════════════════════════════════

QUICK START:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open Chess Detective Menu
2. Select: 11. Tournament Forensics
3. Enter Lichess tournament URL or ID
4. Review the flagged anomalies
5. Click on each anomaly to see detailed analysis
6. Use other features to dive deeper into suspicious players

═══════════════════════════════════════════════════════════════════════════════
""")
