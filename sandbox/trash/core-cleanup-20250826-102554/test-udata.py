#!/usr/bin/env python3
"""
Test script to demonstrate uDATA parsing capabilities
"""

import sys
import os
sys.path.append('/Users/agentdigital/uDOS/uCORE/json')

# Import directly since we're in the same directory
exec(open('udata-converter.py').read())

def test_universal_reader():
    print("🧪 Testing Universal Reader")
    print("=" * 40)

    # Test reading uDATA format
    print("\n📖 Reading uDATA format:")
    udata_records = uDATAParser.read_universal('test-sample.udata')
    print(f"   Found {len(udata_records)} records from uDATA file")

    # Test reading JSON format
    print("\n📖 Reading JSON format:")
    json_records = uDATAParser.read_universal('test-sample.json')
    print(f"   Found {len(json_records)} records from JSON file")

    # Show first record from each
    if udata_records:
        print(f"\n📋 First uDATA record: {udata_records[0]}")

    if json_records:
        print(f"\n📋 First JSON record: {json_records[0]}")

    # Test statistics
    print(f"\n📊 uDATA Statistics:")
    stats = uDATAParser.get_stats(udata_records)
    for key, value in stats.items():
        if isinstance(value, list) and len(value) > 5:
            print(f"   {key}: {len(value)} items")
        else:
            print(f"   {key}: {value}")

if __name__ == "__main__":
    test_universal_reader()
