#!/usr/bin/env python3
"""Test script to debug the command handling issue."""

import asyncio
from unittest.mock import patch, AsyncMock

from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

async def test_greeting_command():
    """Test the /greeting command specifically."""
    
    # Create bot exactly like scene_bot.py
    bot = WhatsAppBot({
        "idInstance": "test",
        "apiTokenInstance": "test"
    })
    
    # Create scenes
    greeting_scene = BaseScene("greeting")
    
    @greeting_scene.enter()
    async def greeting_enter(ctx):
        print("✓ Greeting scene entered!")
        await ctx.reply("Hi! What's your name?")
    
    @greeting_scene.on("text")
    async def greeting_text(ctx):
        name = ctx.message.text
        ctx.session["user_name"] = name
        await ctx.reply(f"Nice to meet you, {name}!")
        await ctx.scene.leave_scene(ctx)
    
    @greeting_scene.leave()
    async def greeting_leave(ctx):
        print("✓ Greeting scene left!")
        await ctx.reply("Thanks for telling me your name!")
    
    echo_scene = BaseScene("echo")
    
    # Create stage and register scenes
    stage = Stage([greeting_scene, echo_scene])
    
    # Setup middleware exactly like scene_bot.py
    bot.use(session())
    bot.use(stage.middleware())
    
    # Add command handlers exactly like scene_bot.py
    @bot.command("greeting")
    async def start_greeting(ctx):
        print("✓ /greeting command handler called!")
        await ctx.scene_manager.enter("greeting", ctx)
    
    @bot.start()
    async def start(ctx):
        print("✓ /start command handler called!")
        await ctx.reply("Start command received!")
    
    # Add global handler exactly like scene_bot.py
    @bot.on("message")
    async def global_handler(ctx):
        print(f"✗ Global handler called for: {ctx.message.text if ctx.message else 'None'}")
        # Skip if it's a command (commands have their own handlers)
        if ctx.message and ctx.message.text and ctx.message.text.startswith("/"):
            print("  -> Detected command, returning early")
            return
        
        # Only handle non-command messages when not in a scene
        if not hasattr(ctx, "scene") or not ctx.scene:
            print("  -> No scene, sending help message")
            await ctx.reply("Send /start to begin, or /help for available commands.")
    
    # Test the /greeting command
    greeting_update = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {
            "idInstance": "test",
            "wid": "test@c.us",
            "typeInstance": "whatsapp"
        },
        "timestamp": 1234567890,
        "idMessage": "test_greeting",
        "senderData": {
            "chatId": "1234567890@c.us",
            "sender": "1234567890@c.us",
            "senderName": "Test User"
        },
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "/greeting"
            }
        }
    }
    
    # Mock the API client
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        print("=== Testing /greeting command ===")
        try:
            await bot.handle_update(greeting_update)
            print("Update handled successfully")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_greeting_command())
