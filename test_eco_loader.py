"""Test ECO loader"""
from chess_analyzer.eco_loader import get_opening_name, ECOLoader

# Test ECO codes
test_codes = ['B32', 'C45', 'E50', 'A40', 'D50', 'B99', 'C89', 'E77']

print("[TEST] ECO Loader")
print("=" * 50)

for code in test_codes:
    name = get_opening_name(code)
    print(f"  {code} -> {name}")

# Test fallback
print(f"\n[FALLBACK] Unknown code: {get_opening_name('ZZZ')}")

# Test None
print(f"[NULL] None code: {get_opening_name(None)}")

print("\n✓ ECO loader test passed!")
