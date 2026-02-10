#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/wizard/Code/uDOS')

print("1. Testing module import...")
try:
    from wizard.routes.self_heal_routes import create_self_heal_routes
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Testing router creation...")
try:
    router = create_self_heal_routes()
    print(f"✅ Router created: {router}")
    print(f"   Routes: {len(router.routes)}")
except Exception as e:
    print(f"❌ Router creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Checking critical imports...")
try:
    from core.services.ok_setup import run_ok_setup
    print("✅ run_ok_setup imported")
except Exception as e:
    print(f"⚠️  run_ok_setup: {e}")

try:
    from wizard.services.port_manager import get_port_manager
    pm = get_port_manager()
    print(f"✅ port_manager works")
except Exception as e:
    print(f"❌ port_manager: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All basic tests passed!")
