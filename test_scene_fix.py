#!/usr/bin/env python3
"""Test the fixed scene_bot behavior."""

import asyncio
from unittest.mock import patch, AsyncMock

from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

async def test_fixed_behavior():
    """Test the fixed scene bot behavior."""
    
    # Create bot
    bot = WhatsAppBot({
        "idInstance": "test",
        "apiTokenInstance": "test"
    })
    
    # Create greeting scene
    greeting_scene = BaseScene("greeting")
    
    @greeting_scene.enter()
    async def greeting_enter(ctx):
        print("✓ Scene: Enter greeting scene")
        await ctx.reply("Hi! What's your name?")
    
    @greeting_scene.on("text")
    async def greeting_text(ctx):
        name = ctx.message.text
        print(f"✓ Scene: Got name '{name}'")
        ctx.session["user_name"] = name
        await ctx.reply(f"Nice to meet you, {name}!")
        await ctx.scene.leave_scene(ctx)
    
    @greeting_scene.leave()
    async def greeting_leave(ctx):
        print("✓ Scene: Leaving greeting scene")
        await ctx.reply("Thanks for telling me your name!")
    
    # Create stage
    stage = Stage([greeting_scene])
    
    # Setup middleware (fixed version)
    bot.use(session(store=bot.session_manager.store))
    bot.use(stage.middleware())
    
    # Add command handlers
    @bot.command("greeting")
    async def start_greeting(ctx):
        print("✓ Command: /greeting")
        await ctx.scene_manager.enter("greeting", ctx)
    
    @bot.start()
    async def start(ctx):
        print("✓ Command: /start")
        user_name = ctx.session.get("user_name", "there")
        await ctx.reply(f"Hello {user_name}! Use /greeting to start.")
    
    # Add the FIXED global handler
    @bot.on("message")
    async def global_handler(ctx):
        """Handle messages when not in a scene."""
        # Skip if it's a command
        if ctx.message and ctx.message.text and ctx.message.text.startswith("/"):
            return
        
        # Check if we're in an active scene
        if hasattr(ctx, "session") and "__scene" in ctx.session:
            # We're in a scene, so the scene should handle this message
            print("✓ Global: Message in scene, skipping global handler")
            return
        
        # Only handle non-command messages when not in a scene
        print("✓ Global: No scene active, sending fallback message")
        await ctx.reply("Send /start to begin, or /help for available commands.")
    
    # Test the flow
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        print("=== Test 1: Random text (should get fallback) ===")
        random_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {"idInstance": "test", "wid": "test@c.us", "typeInstance": "whatsapp"},
            "timestamp": 1234567890,
            "idMessage": "test1",
            "senderData": {"chatId": "1234567890@c.us", "sender": "1234567890@c.us", "senderName": "Test User"},
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "hello"}}
        }
        await bot.handle_update(random_update)
        
        print("\n=== Test 2: /greeting command ===")
        greeting_update = {
            **random_update,
            "idMessage": "test2",
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "/greeting"}}
        }
        await bot.handle_update(greeting_update)
        
        print("\n=== Test 3: Name in scene (should NOT get fallback) ===")
        name_update = {
            **random_update,
            "idMessage": "test3",
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "Alice"}}
        }
        await bot.handle_update(name_update)
        
        print("\n=== Test 4: Another random text after scene (should get fallback) ===")
        random_update2 = {
            **random_update,
            "idMessage": "test4",
            "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "another message"}}
        }
        await bot.handle_update(random_update2)

if __name__ == "__main__":
    asyncio.run(test_fixed_behavior())
