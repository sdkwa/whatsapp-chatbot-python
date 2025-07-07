#!/usr/bin/env python3
"""Quick test script to verify decorator functionality."""

import sys
import os
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the SDKWA module before importing our code
sys.modules['sdkwa'] = Mock()

from sdkwa_whatsapp_chatbot import WhatsAppBot, BaseScene

def test_bot_decorators():
    """Test bot decorator functionality."""
    print("Testing bot decorators...")
    
    # Mock SDKWA for testing
    with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA"):
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        bot = WhatsAppBot(config)
        
        # Test decorator usage
        @bot.on("text")
        def text_handler(ctx):
            print("Text handler called")
        
        @bot.command("start")
        def start_handler(ctx):
            print("Start handler called")
        
        print("✅ Bot decorators work correctly")

def test_scene_decorators():
    """Test scene decorator functionality."""
    print("Testing scene decorators...")
    
    scene = BaseScene("test_scene")
    
    @scene.enter()
    def enter_handler(ctx):
        print("Enter handler called")
    
    @scene.leave()
    def leave_handler(ctx):
        print("Leave handler called")
    
    print("✅ Scene decorators work correctly")

if __name__ == "__main__":
    try:
        test_bot_decorators()
        test_scene_decorators()
        print("\n🎉 All decorator tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
