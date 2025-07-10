#!/usr/bin/env python3
"""Simple test to understand the command flow."""

import asyncio
from unittest.mock import patch, AsyncMock

# Test the actual scene_bot module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from examples.scene_bot import bot

async def test_command_flow():
    """Test command handling flow."""
    
    # Test cases
    test_cases = [
        ("/greeting", "Testing /greeting command"),
        ("/start", "Testing /start command"),
        ("/help", "Testing /help command"),
        ("hello", "Testing regular text"),
        ("/unknown", "Testing unknown command")
    ]
    
    for message_text, description in test_cases:
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
                "chatId": "1234567890@c.us",
                "sender": "1234567890@c.us",
                "senderName": "Test User"
            },
            "messageData": {
                "typeMessage": "textMessage",
                "textMessageData": {
                    "textMessage": message_text
                }
            }
        }
        
        print(f"\n=== {description} ===")
        
        # Mock the API client
        with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True}
            
            try:
                await bot.handle_update(update)
                
                # Check what was sent
                calls = mock_send.call_args_list
                print(f"Number of API calls made: {len(calls)}")
                for i, call in enumerate(calls):
                    args, kwargs = call
                    if 'message' in kwargs:
                        message = kwargs['message']
                        # Truncate long messages
                        if len(message) > 50:
                            message = message[:50] + "..."
                        print(f"Call {i+1}: {message}")
                    
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_command_flow())
