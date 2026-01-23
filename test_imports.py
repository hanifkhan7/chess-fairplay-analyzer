#!/usr/bin/env python3
"""Test imports for visualization libraries."""

print("Testing imports...")

try:
    import pandas as pd
    print(f"✓ pandas {pd.__version__}")
except ImportError as e:
    print(f"✗ pandas: {e}")

try:
    import matplotlib.pyplot as plt
    print(f"✓ matplotlib {plt.matplotlib.__version__}")
except ImportError as e:
    print(f"✗ matplotlib: {e}")

try:
    import seaborn as sns
    print(f"✓ seaborn {sns.__version__}")
except ImportError as e:
    print(f"✗ seaborn: {e}")

try:
    import openpyxl
    print(f"✓ openpyxl {openpyxl.__version__}")
except ImportError as e:
    print(f"✗ openpyxl: {e}")

print("\nAll imports completed!")
