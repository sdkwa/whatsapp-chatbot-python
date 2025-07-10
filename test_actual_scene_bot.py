#!/usr/bin/env python3
"""Simple test of the actual scene_bot.py functionality."""

import asyncio
from unittest.mock import patch, AsyncMock
import sys
import os

# Add the examples directory to path so we can import scene_bot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "examples"))

async def test_actual_scene_bot():
    """Test the actual scene_bot.py functionality."""
    
    # Import the actual scene_bot
    from scene_bot import bot
    
    # Mock the API client to avoid errors
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        print("=== Test 1: Random message (should get fallback) ===")
        random_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
            "timestamp": 1234567890,
            "idMessage": "test1",
            "senderData": {"chatId": "1234567890@c.us", "sender": "1234567890@c.us", "senderName": "Test User"},
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "hello"}}
        }
        await bot.handle_update(random_update)
        print(f"API called {mock_send.call_count} times")
        if mock_send.call_count > 0:
            print(f"Last message: {mock_send.call_args[1]['message']}")
        
        mock_send.reset_mock()
        
        print("\n=== Test 2: /greeting command ===")
        greeting_update = {
            **random_update,
            "idMessage": "test2",
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "/greeting"}}
        }
        await bot.handle_update(greeting_update)
        print(f"API called {mock_send.call_count} times")
        if mock_send.call_count > 0:
            print(f"Last message: {mock_send.call_args[1]['message']}")
        
        mock_send.reset_mock()
        
        print("\n=== Test 3: Name response in scene ===")
        name_update = {
            **random_update,
            "idMessage": "test3",
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "Alice"}}
        }
        await bot.handle_update(name_update)
        print(f"API called {mock_send.call_count} times")
        if mock_send.call_count > 0:
            print(f"Messages sent: {[call[1]['message'] for call in mock_send.call_args_list]}")

if __name__ == "__main__":
    asyncio.run(test_actual_scene_bot())
