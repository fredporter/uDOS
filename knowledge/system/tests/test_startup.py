#!/usr/bin/env python3
"""Quick startup test"""

import sys
import warnings
from pathlib import Path

# Add uDOS root to path (3 levels up from knowledge/system/tests/)
UDOS_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(UDOS_ROOT))

warnings.filterwarnings('ignore')

try:
    print("1. Testing imports...")
    from core.uDOS_main import initialize_system, main
    print("   ✓ Imports successful")

    print("\n2. Testing initialization...")
    components = initialize_system(is_script_mode=True)
    print(f"   ✓ Components: {list(components.keys())}")

    print("\n3. Starting interactive mode...")
    print("   Type 'help' to see commands, 'exit' to quit\n")
    main()

except KeyboardInterrupt:
    print("\n\nInterrupted by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
