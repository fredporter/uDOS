#!/usr/bin/env python3
"""
v1.2.1 Performance Validation System - DEMO

This demo shows:
1. Unified logging in action
2. Performance tracking
3. Success criteria validation
4. Log file outputs

Run: python dev/scripts/demo_v1_2_1.py
"""

import sys
import time
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.unified_logger import (
    get_unified_logger,
    log_system,
    log_performance,
    log_api,
    log_command
)
from core.services.performance_monitor import get_performance_monitor

# Initialize
logger = get_unified_logger()
monitor = get_performance_monitor()

print("=" * 60)
print("🎬 v1.2.1 Performance Validation System - DEMO")
print("=" * 60)
print()

# Demo 1: System Logging
print("📝 Demo 1: Unified Logging System")
print("-" * 60)
print("Logging to memory/logs/ with minimal format...")
print()

log_system("Demo session started")
log_command("GENERATE", ["DO"], "success", 0.123, offline=True)
print("✅ Logged: System message + Command execution")
print()

# Demo 2: Performance Tracking (Offline Query)
print("📊 Demo 2: Offline Query Tracking")
print("-" * 60)
print("Simulating offline query: 'How do I purify water?'")
print()

start = time.time()
time.sleep(0.15)  # Simulate 150ms query
duration = time.time() - start

monitor.track_query(
    query_type='DO',
    mode='offline',
    duration=duration,
    cost=0.0,
    confidence=96.7,
    success=True
)

log_performance('DO', duration, offline=True, confidence=96.7, method='knowledge_bank')
print(f"✅ Tracked: Offline query ({duration*1000:.0f}ms, $0.00, 96.7% confidence)")
print()

# Demo 3: Performance Tracking (Online Query)
print("📊 Demo 3: Online Query Tracking (Gemini)")
print("-" * 60)
print("Simulating Gemini fallback query...")
print()

start = time.time()
time.sleep(0.35)  # Simulate 350ms API call
duration = time.time() - start
cost = 0.00015  # ~$0.00015 per query

monitor.track_query(
    query_type='DO',
    mode='gemini',
    duration=duration,
    cost=cost,
    tokens=245,
    success=True
)

log_performance('DO', duration, offline=False, mode='gemini', cost=cost)
log_api('gemini', duration, cost, success=True, operation='DO')
print(f"✅ Tracked: Gemini query ({duration*1000:.0f}ms, ${cost:.5f}, 245 tokens)")
print()

# Demo 4: More Offline Queries (to hit 90%+ offline rate)
print("📊 Demo 4: Simulating More Queries (for 90%+ offline)")
print("-" * 60)

for i in range(8):
    duration = 0.120 + (i * 0.015)  # Vary response time
    monitor.track_query(
        query_type='DO',
        mode='offline',
        duration=duration,
        cost=0.0,
        confidence=92.0 + i,
        success=True
    )
    log_performance(f'DO_{i+1}', duration, offline=True, confidence=92.0 + i)
    print(f"  Query {i+1}: {duration*1000:.0f}ms, offline, {92.0 + i:.1f}% confidence")

print()
print("✅ Tracked: 8 more offline queries")
print()

# Demo 5: Session Statistics
print("📈 Demo 5: Session Statistics")
print("-" * 60)

stats = monitor.get_session_stats()
print(f"Total Queries:    {stats['total_queries']}")
print(f"Offline Queries:  {stats['offline_queries']} ({stats['offline_rate']*100:.1f}%)")
print(f"Online Queries:   {stats['online_queries']} ({(1-stats['offline_rate'])*100:.1f}%)")
print(f"Avg Duration:     {stats['avg_duration']*1000:.0f}ms")
print(f"Total Cost:       ${stats['total_cost']:.5f}")
print(f"Baseline Cost:    ${stats['baseline_cost']:.2f}")
print(f"Cost Savings:     ${stats['cost_savings']:.2f}")
print(f"Cost Reduction:   {stats['cost_reduction_pct']:.1f}%")
print()

# Demo 6: Success Criteria Validation
print("✅ Demo 6: Success Criteria Validation")
print("-" * 60)

validation = monitor.validate_success_criteria()
criteria = validation['criteria']
all_passed = validation['all_passed']

print(f"Overall Status: {'✅ ALL CRITERIA MET' if all_passed else '❌ SOME CRITERIA NOT MET'}")
print()

for name, details in criteria.items():
    icon = "✅" if details['passed'] else "❌"
    desc = details['description']

    if 'rate' in name:
        actual = f"{details['actual']*100:.1f}%"
        target = f"{details['target']*100:.0f}%"
    elif 'cost' in name:
        actual = f"{details['actual']:.1f}%"
        target = f"{details['target']:.0f}%"
    else:
        actual = f"{details['actual']*1000:.0f}ms"
        target = f"{details['target']*1000:.0f}ms"

    print(f"{icon} {desc}: {actual} (target: {target})")

print()

# Demo 7: Log Files
print("📁 Demo 7: Log Files Created")
print("-" * 60)

log_dir = Path(project_root) / "memory" / "logs"
log_files = sorted(log_dir.glob("*.log"))

for log_file in log_files:
    size = log_file.stat().st_size
    lines = len(log_file.read_text().strip().split('\n')) if size > 0 else 0
    print(f"  {log_file.name:20} {size:6} bytes, {lines:3} lines")

print()

# Demo 8: Sample Log Entries
print("📄 Demo 8: Sample Log Entries")
print("-" * 60)

print("\n📝 performance.log (last 3 entries):")
perf_log = log_dir / "performance.log"
if perf_log.exists():
    lines = perf_log.read_text().strip().split('\n')
    for line in lines[-3:]:
        print(f"  {line}")

print("\n📝 api.log (last 2 entries):")
api_log = log_dir / "api.log"
if api_log.exists():
    lines = api_log.read_text().strip().split('\n')
    for line in lines[-2:]:
        print(f"  {line}")

print()

# Summary
print("=" * 60)
print("🎉 DEMO COMPLETE")
print("=" * 60)
print()
print("✅ Unified Logging System: Operational")
print("✅ Performance Monitoring: Tracking all queries")
print("✅ Success Criteria: Validated automatically")
print("✅ Log Files: Created and populated")
print()
print(f"📊 Final Metrics:")
print(f"   Offline Rate:     {stats['offline_rate']*100:.1f}% ({'✅' if stats['offline_rate'] >= 0.90 else '❌'} target: ≥90%)")
print(f"   Cost Reduction:   {stats['cost_reduction_pct']:.1f}% ({'✅' if stats['cost_reduction_pct'] >= 99.0 else '❌'} target: ≥99%)")
print(f"   Avg Response:     {stats['avg_duration']*1000:.0f}ms ({'✅' if stats['avg_duration'] < 0.500 else '❌'} target: <500ms)")
print()
print("💡 Try in uDOS: GENERATE VALIDATE")
print()
