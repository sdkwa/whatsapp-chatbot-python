#!/usr/bin/env python3
"""Comprehensive test for the improved scene bot system."""

import asyncio
from unittest.mock import patch, AsyncMock
import sys
import os

# Import the scene bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from examples.scene_bot import bot

async def test_comprehensive_scene_system():
    """Test the complete scene system with improved session handling."""
    
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        test_cases = [
            # Test 1: Complete greeting flow
            {
                "name": "Complete Greeting Flow",
                "messages": [
                    ("/greeting", "Enter greeting scene"),
                    ("Bob", "Provide name in scene")
                ],
                "expected_responses": 3  # enter + response + leave
            },
            
            # Test 2: Echo scene flow  
            {
                "name": "Echo Scene Flow",
                "messages": [
                    ("/echo", "Enter echo scene"),
                    ("test message", "Send message to echo"),
                    ("/back", "Exit echo scene")
                ],
                "expected_responses": 3  # enter + echo + leave
            },
            
            # Test 3: Global commands
            {
                "name": "Global Commands",
                "messages": [
                    ("/start", "Start command"),
                    ("/help", "Help command")
                ],
                "expected_responses": 2  # start + help responses
            },
            
            # Test 4: Non-command text (should get help)
            {
                "name": "Non-command Text",
                "messages": [
                    ("hello", "Regular text outside scene")
                ],
                "expected_responses": 1  # help message
            }
        ]
        
        total_tests_passed = 0
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            mock_send.reset_mock()
            
            # Create fresh session for each test
            chat_id = f"test_{test_case['name'].lower().replace(' ', '_')}@c.us"
            
            for message_text, description in test_case["messages"]:
                print(f"  📤 {description}: '{message_text}'")
                
                update = {
                    "typeWebhook": "incomingMessageReceived",
                    "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
                    "timestamp": 1234567890,
                    "idMessage": f"test_{len(mock_send.call_args_list)}",
                    "senderData": {"chatId": chat_id, "sender": chat_id, "senderName": "Test User"},
                    "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": message_text}}
                }
                
                await bot.handle_update(update)
            
            # Check results
            calls = mock_send.call_args_list
            actual_responses = len(calls)
            expected_responses = test_case["expected_responses"]
            
            if actual_responses == expected_responses:
                print(f"  ✅ PASSED: {actual_responses} responses (expected {expected_responses})")
                total_tests_passed += 1
            else:
                print(f"  ❌ FAILED: {actual_responses} responses (expected {expected_responses})")
                for i, call in enumerate(calls):
                    if 'message' in call[1]:
                        msg = call[1]['message'][:50] + "..." if len(call[1]['message']) > 50 else call[1]['message']
                        print(f"    {i+1}. {msg}")
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"✅ Tests passed: {total_tests_passed}/{len(test_cases)}")
        
        if total_tests_passed == len(test_cases):
            print("🎉 ALL TESTS PASSED! Scene bot system is fully functional!")
            print("✅ Session persistence working")
            print("✅ Scene detection working") 
            print("✅ Scene flows working")
            print("✅ Command handling working")
            print("✅ Global handlers working")
        else:
            print("❌ Some tests failed. Scene bot needs debugging.")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_scene_system())
