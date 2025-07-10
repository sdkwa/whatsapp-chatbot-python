#!/usr/bin/env python3
"""Test to demonstrate the session persistence issue."""

import asyncio
from unittest.mock import patch, AsyncMock

from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

async def test_session_issue():
    """Test showing the session persistence problem."""
    
    # Create bot
    bot = WhatsAppBot({
        "idInstance": "test",
        "apiTokenInstance": "test"
    })
    
    # Create a simple scene
    test_scene = BaseScene("test")
    
    @test_scene.enter()
    async def enter_handler(ctx):
        print("✓ Scene entered!")
        ctx.session["scene_data"] = "test_value"
        await ctx.reply("Scene entered")
    
    @test_scene.on("text")
    async def text_handler(ctx):
        print(f"✓ Scene text handler - session data: {ctx.session}")
        await ctx.reply("Scene got text")
    
    # Create stage
    stage = Stage([test_scene])
    
    # Setup middleware - FIXED way (using bot's session store)
    bot.use(session(store=bot.session_manager.store))
    bot.use(stage.middleware())
    
    @bot.command("test")
    async def test_command(ctx):
        print(f"Command handler - session before: {ctx.session}")
        await ctx.scene_manager.enter("test", ctx)
        print(f"Command handler - session after: {ctx.session}")
    
    # Test with mock
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        print("=== Testing /test command ===")
        command_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
            "timestamp": 1234567890,
            "idMessage": "test_cmd",
            "senderData": {"chatId": "user@c.us", "sender": "user@c.us", "senderName": "Test User"},
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "/test"}}
        }
        
        await bot.handle_update(command_update)
        
        print("\n=== Testing text message in scene ===")
        text_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
            "timestamp": 1234567891,
            "idMessage": "test_text",
            "senderData": {"chatId": "user@c.us", "sender": "user@c.us", "senderName": "Test User"},
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "hello"}}
        }
        
        await bot.handle_update(text_update)

if __name__ == "__main__":
    asyncio.run(test_session_issue())
