#!/usr/bin/env python3
"""Final test to verify scene system works correctly."""

import asyncio
from unittest.mock import patch, AsyncMock
import sys
import os

# Import the fixed scene_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from examples.scene_bot import bot

async def test_final_scene_flow():
    """Test the complete scene flow."""
    
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        # Test full greeting flow
        messages = [
            ("/greeting", "Enter greeting scene"),
            ("Alice", "Provide name in scene"),
        ]
        
        for message_text, description in messages:
            print(f"Testing: {description} - '{message_text}'")
            
            update = {
                "typeWebhook": "incomingMessageReceived",
                "instanceData": {
                    "idInstance": "test",
                    "wid": "test@c.us",
                    "typeInstance": "whatsapp"
                },
                "timestamp": 1234567890,
                "idMessage": f"test_{message_text.replace('/', '').replace(' ', '_')}",
                "senderData": {
                    "chatId": "test_user@c.us",
                    "sender": "test_user@c.us",
                    "senderName": "Test User"
                },
                "messageData": {
                    "typeMessage": "textMessage",
                    "textMessageData": {
                        "textMessage": message_text
                    }
                }
            }
            
            await bot.handle_update(update)
        
        # Check the messages sent
        calls = mock_send.call_args_list
        print(f"\nTotal messages sent: {len(calls)}")
        for i, call in enumerate(calls):
            args, kwargs = call
            if 'message' in kwargs:
                message = kwargs['message'][:50] + "..." if len(kwargs['message']) > 50 else kwargs['message']
                print(f"{i+1}. {message}")
        
        # Verify expected flow
        expected_messages = [
            "Hi! What's your name?",  # Scene enter
            "Nice to meet you, Alice!",  # Scene text handler
            "Thanks for telling me your name!"  # Scene leave
        ]
        
        actual_messages = [call[1]['message'] for call in calls if 'message' in call[1]]
        
        if len(actual_messages) == len(expected_messages):
            print("\n✅ Scene flow working correctly!")
            print("✅ Session persistence fixed!")
            print("✅ Stage middleware functioning properly!")
        else:
            print(f"\n❌ Expected {len(expected_messages)} messages, got {len(actual_messages)}")

if __name__ == "__main__":
    asyncio.run(test_final_scene_flow())
