#!/usr/bin/env python3
"""Test session persistence with debug output."""

import asyncio
from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": "1101000001", 
        "apiTokenInstance": "fake_token",
    }
)

# Setup bot with session middleware
session_middleware = session(store=bot.session_manager.store)
bot.use(session_middleware)

@bot.start()
async def start(ctx):
    """Handle /start command."""
    print("DEBUG: Start command called")
    print(f"DEBUG: Session: {ctx.session}")
    print(f"DEBUG: chat_id: {ctx.chat_id}")
    ctx.session["test_key"] = "test_value"
    print(f"DEBUG: Session after setting: {ctx.session}")
    await ctx.reply("Hello!")

async def test_session_persistence():
    """Test session persistence."""
    
    # Mock update for /start
    start_update = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {
            "idInstance": 1101000001,
            "wid": "1234567890@c.us",
            "typeInstance": "whatsapp"
        },
        "timestamp": 1234567890,
        "idMessage": "test123",
        "senderData": {
            "chatId": "1234567890@c.us",
            "sender": "1234567890@c.us",
            "senderName": "Test User"
        },
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "/start"
            }
        }
    }
    
    print("=== First /start call ===")
    await bot.handle_update(start_update)
    
    # Check what's in the session store directly
    print(f"\nDirect store check: {await bot.session_manager.store.get('1234567890@c.us')}")
    
    print("\n=== Second /start call ===")
    await bot.handle_update(start_update)

if __name__ == "__main__":
    asyncio.run(test_session_persistence())
