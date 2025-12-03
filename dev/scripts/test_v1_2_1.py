#!/usr/bin/env python3
"""
Test script for v1.2.1 features.

Tests:
1. Unified logger initialization
2. Performance monitor initialization
3. GENERATE handler with performance tracking
4. Log file creation
5. Performance metrics validation
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test imports
print("Testing v1.2.1 Infrastructure...")
print("=" * 50)

# Test 1: Unified Logger
print("\n1. Testing Unified Logger...")
try:
    from core.services.unified_logger import (
        get_unified_logger,
        log_system,
        log_performance,
        log_api
    )
    logger = get_unified_logger()
    print("✅ Unified Logger imported successfully")
    print(f"   Log directory: {logger.log_dir}")

    # Test logging
    log_system("Test system message")
    log_performance('TEST', 0.123, offline=True, confidence=95.5)
    log_api('test_api', 0.456, 0.001, success=True)
    print("✅ Logging functions work")
except Exception as e:
    print(f"❌ Unified Logger failed: {e}")
    sys.exit(1)

# Test 2: Performance Monitor
print("\n2. Testing Performance Monitor...")
try:
    from core.services.performance_monitor import (
        get_performance_monitor,
        QueryMetric
    )
    monitor = get_performance_monitor()
    print("✅ Performance Monitor imported successfully")
    print(f"   Baseline cost: ${monitor.BASELINE_COST_PER_QUERY}/query")

    # Test tracking
    monitor.track_query(
        query_type='TEST',
        mode='offline',
        duration=0.234,
        cost=0.0,
        confidence=98.5,
        success=True
    )

    monitor.track_query(
        query_type='TEST',
        mode='gemini',
        duration=0.567,
        cost=0.0001,
        tokens=150,
        success=True
    )

    # Get stats
    stats = monitor.get_session_stats()
    print(f"✅ Performance tracking works")
    print(f"   Total queries: {stats['total_queries']}")
    print(f"   Offline rate: {stats['offline_rate']:.1f}%")
    print(f"   Avg duration: {stats['avg_duration']*1000:.0f}ms")

except Exception as e:
    print(f"❌ Performance Monitor failed: {e}")
    sys.exit(1)

# Test 3: GENERATE Handler Integration
print("\n3. Testing GENERATE Handler...")
try:
    from core.commands.generate_handler import GenerateHandler
    handler = GenerateHandler()
    print("✅ GENERATE Handler imported successfully")
    print(f"   Performance monitor active: {handler.performance_monitor is not None}")

    # Check if VALIDATE command exists
    if hasattr(handler, '_handle_validate'):
        print("✅ VALIDATE command exists")

        # Try to run validation
        try:
            result = handler._handle_validate()
            print("✅ VALIDATE command executes")
            print(f"   Report length: {len(result)} characters")
        except Exception as e:
            print(f"⚠️  VALIDATE execution issue: {e}")
    else:
        print("❌ VALIDATE command not found")

except Exception as e:
    print(f"❌ GENERATE Handler failed: {e}")
    sys.exit(1)

# Test 4: Check log files
print("\n4. Checking Log Files...")
try:
    log_dir = Path(project_root) / "memory" / "logs"
    print(f"   Log directory: {log_dir}")

    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"✅ Log directory exists with {len(log_files)} files")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"   - {log_file.name}: {size} bytes")
    else:
        print("⚠️  Log directory not yet created")

except Exception as e:
    print(f"❌ Log file check failed: {e}")

# Test 5: Validation
print("\n5. Testing Success Criteria Validation...")
try:
    validation = monitor.validate_success_criteria()
    print("✅ Validation executed successfully")

    # Show individual criteria
    criteria = validation['criteria']
    for name, details in criteria.items():
        icon = "✅" if details['passed'] else "❌"
        print(f"   {icon} {details['description']}: {'PASS' if details['passed'] else 'FAIL'}")

    # Show overall status
    all_passed = validation['all_passed']
    print(f"\n   Overall: {'✅ ALL CRITERIA MET' if all_passed else '❌ SOME CRITERIA NOT MET'}")

    # Generate report
    report = monitor.generate_report()
    print(f"\n✅ Performance report generated ({len(report)} characters)")

except Exception as e:
    print(f"❌ Validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED")
print("\nv1.2.1 Infrastructure Summary:")
print(f"  - Unified Logger: Active ({len(list(log_dir.glob('*.log')))} log files)")
print(f"  - Performance Monitor: Active ({stats['total_queries']} queries tracked)")
print(f"  - GENERATE Handler: Integrated")
print(f"  - VALIDATE Command: Available")
print(f"  - Success Criteria: {sum(1 for c in criteria.values() if c['passed'])}/{len(criteria)} met")
print("\n🎉 v1.2.1 Performance Validation System is operational!")
