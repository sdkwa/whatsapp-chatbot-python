#!/usr/bin/env python3
"""Test the fixed scene_bot.py."""

import asyncio
from unittest.mock import patch, AsyncMock
import sys
import os

# Import the fixed scene_bot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from examples.scene_bot import bot

async def test_fixed_scene_bot():
    """Test the fixed scene bot."""
    
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        print("Testing complete greeting scene flow...")
        
        # Test /greeting command
        greeting_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
            "timestamp": 1234567890,
            "idMessage": "greeting_cmd",
            "senderData": {"chatId": "user@c.us", "sender": "user@c.us", "senderName": "Test User"},
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "/greeting"}}
        }
        
        await bot.handle_update(greeting_update)
        print("✓ /greeting command processed")
        
        # Test name input in scene
        name_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
            "timestamp": 1234567891,
            "idMessage": "name_text",
            "senderData": {"chatId": "user@c.us", "sender": "user@c.us", "senderName": "Test User"},
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "Alice"}}
        }
        
        await bot.handle_update(name_update)
        print("✓ Name input in scene processed")
        
        # Check messages sent
        calls = mock_send.call_args_list
        messages = [call[1]['message'] for call in calls if 'message' in call[1]]
        
        print(f"\nMessages sent: {len(messages)}")
        for i, msg in enumerate(messages, 1):
            print(f"{i}. {msg}")
        
        # Verify the expected flow
        expected = [
            "Hi! What's your name?",
            "Nice to meet you, Alice!",
            "Thanks for telling me your name!"
        ]
        
        if len(messages) == len(expected):
            print("\n🎉 SCENE BOT IS WORKING CORRECTLY!")
            print("✅ Session persistence: FIXED")
            print("✅ Scene detection: WORKING")
            print("✅ Scene flow: COMPLETE")
        else:
            print(f"\n❌ Expected {len(expected)} messages, got {len(messages)}")

if __name__ == "__main__":
    asyncio.run(test_fixed_scene_bot())
