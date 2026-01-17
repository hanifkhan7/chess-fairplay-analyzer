#!/usr/bin/env python3
"""Test dataclass to dict conversion"""
from dataclasses import asdict, dataclass

@dataclass
class TestData:
    name: str
    value: int

# Test conversion
test = TestData("test", 123)
print(f"Original: {test}")
converted = asdict(test)
print(f"Converted: {converted}")
print(f"Type: {type(converted)}")
print(f"Can call .get(): {converted.get('name')}")
print("✓ Conversion works!")
