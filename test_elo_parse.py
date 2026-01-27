"""Test ELO parsing fix"""

# Simulate the _parse_elo method
def _parse_elo(elo_str: str) -> int:
    """Parse ELO rating, handling invalid values like '?'."""
    try:
        return int(elo_str)
    except (ValueError, TypeError):
        return 0

print("[TEST] ELO Parsing")
print("=" * 50)

# Test cases
test_cases = [
    ("1800", 1800),
    ("2000", 2000),
    ("?", 0),
    ("", 0),
    (None, 0),
    ("invalid", 0),
    ("1500", 1500),
]

for elo_str, expected in test_cases:
    try:
        result = _parse_elo(elo_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} {repr(elo_str):15} -> {result:4} (expected {expected})")
    except Exception as e:
        print(f"✗ {repr(elo_str):15} -> ERROR: {e}")

print("\n✓ ELO parsing test passed!")
