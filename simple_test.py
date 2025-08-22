#!/usr/bin/env python3
"""
Simple manual test for tool selection
"""

from tools.distance_matrix import run as distance_test
from tools.places_nearby import run as places_test
from tools.geocode import run as geocode_test
from tools.reverse_geocode import run as reverse_test

print("🔧 Testing tools directly (no LLM)")
print("=" * 40)

# Test 1: Distance Matrix
print("\n1️⃣ Testing distance_matrix:")
try:
    result = distance_test("Paris", "Lyon")
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Places Nearby  
print("\n2️⃣ Testing places_nearby:")
try:
    result = places_test("48.8566,2.3522", radius=1000, type="restaurant")
    print(f"✅ Success: Found {len(result)} places")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Geocoding
print("\n3️⃣ Testing geocode:")
try:
    result = geocode_test("5 Place Jules Massenet, Paris")
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Reverse Geocoding
print("\n4️⃣ Testing reverse_geocode:")
try:
    result = reverse_test("48.8566,2.3522")
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 40)
print("✨ Tool testing complete!")