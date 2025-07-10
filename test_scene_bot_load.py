#!/usr/bin/env python3
"""Quick test to verify scene_bot.py loads without errors."""

try:
    # Import scene_bot to test it loads
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "examples"))
    
    print("Testing scene_bot.py import...")
    exec(open("examples/scene_bot.py").read().replace("bot.launch()", "print('Bot would launch successfully')"))
    print("✅ scene_bot.py loads and initializes correctly!")
    
except Exception as e:
    print(f"❌ Error in scene_bot.py: {e}")
    import traceback
    traceback.print_exc()
