#!/usr/bin/env python3
"""Test the enhanced analyze_player with depth selection"""

import yaml

# Simulate user selecting options
config = yaml.safe_load(open('config.yaml'))

# Show what happens with different depth settings
print("\n" + "="*80)
print("ENHANCED ANALYZER - DEPTH AND TIME CONTROL SELECTION")
print("="*80)

print("\n[TIME CONTROL SELECTION]")
print("1. Rapid (10-25 min) - More strategical games")
print("2. Blitz (3-9 min) - Tactical games")
print("3. Bullet (1-2 min) - Fast reflexive play")
print("4. All time controls")

print("\n[DEPTH SELECTION]")
print("1. Standard (Depth 16) - 10-20s per game")
print("   Good for rapid analysis, fast results")
print("   RECOMMENDED for most users")
print()
print("2. Deep (Depth 20) - 30-60s per game") 
print("   Better accuracy, moderate time investment")
print("   Good for Super GMs like Hikaru")
print()
print("3. Very Deep (Depth 24) - 2-5 min per game")
print("   Very accurate, significant time investment")
print("   For serious forensic analysis")
print()
print("4. Maximum (Depth 28) - 5-15 min per game")
print("   Ultra precise, extreme accuracy")
print("   For detecting subtle assistance patterns")

print("\n" + "="*80)
print("[EXAMPLE SCENARIO]")
print("="*80)

print("\nAnalyzing Hikaru's recent rapid games with Deep analysis...")
print("Configuration: Rapid Games + Depth 20")
print()

# Show what would be updated
config['analysis']['engine_depth'] = 20

print("Updated Configuration:")
print(f"  Analysis Depth: {config.get('analysis', {}).get('engine_depth')} (was 16)")
print(f"  Time per move: ~1.0 seconds (Deep level)")
print()

print("Expected Results for Hikaru:")
print("  - Rapid games analyzed with higher depth")
print("  - Elo fetched from most recent games")
print("  - Accuracy should reflect Super GM level (75-85%+)")
print("  - Engine match will show exceptional move quality")
print()

print("Time Estimate:")
print("  - 50 rapid games * ~45 seconds per game")
print("  - Total: ~37-40 minutes")
print("  - Much more accurate than basic analysis")

print("\n" + "="*80)
print("[ADVANTAGES]")
print("="*80)
print()
print("Depth 16 (Default):")
print("  + Fast (perfect for initial screening)")
print("  + Good for most players")
print("  - May miss subtle engine assistance at elite levels")
print()
print("Depth 20+ (Enhanced):")
print("  + Better accuracy for Super GMs")
print("  + Catches more subtle assistance")
print("  + More reliable forensic analysis")
print("  - Takes longer per game")
print()
print("For Hikaru specifically:")
print("  RECOMMENDED: Depth 20 + Rapid games")
print("  Captures his super-human accuracy without excessive time")
print()

print("="*80)
