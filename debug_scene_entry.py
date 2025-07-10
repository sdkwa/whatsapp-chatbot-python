#!/usr/bin/env python3
"""Test to debug the current_scene issue."""

import asyncio
from unittest.mock import patch, AsyncMock

from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

async def test_scene_entry():
    """Test scene entry flow."""
    
    # Create bot
    bot = WhatsAppBot({
        "idInstance": "test",
        "apiTokenInstance": "test"
    })
    
    # Create greeting scene with debug output
    greeting_scene = BaseScene("greeting")
    
    @greeting_scene.enter()
    async def greeting_enter(ctx):
        print("✓ Greeting scene enter handler called!")
        await ctx.reply("Hi! What's your name?")
    
    @greeting_scene.on("text")
    async def greeting_text(ctx):
        print(f"✓ Greeting scene text handler called with: {ctx.message.text}")
        name = ctx.message.text
        ctx.session["user_name"] = name
        await ctx.reply(f"Nice to meet you, {name}!")
        await ctx.scene.leave_scene(ctx)
    
    @greeting_scene.leave()
    async def greeting_leave(ctx):
        print("✓ Greeting scene leave handler called!")
        await ctx.reply("Thanks for telling me your name!")
    
    # Create stage
    stage = Stage([greeting_scene])
    
    # Setup middleware - use bot's session manager store
    bot.use(session(store=bot.session_manager.store))
    bot.use(stage.middleware())
    
    # Add command handler
    @bot.command("greeting")
    async def start_greeting(ctx):
        print("✓ /greeting command handler called!")
        print(f"  Chat ID: {ctx.chat_id}")
        print(f"  Session before enter: {ctx.session}")
        print(f"  Scene manager: {hasattr(ctx, 'scene_manager')}")
        result = await ctx.scene_manager.enter("greeting", ctx)
        print(f"  Enter result: {result}")
        print(f"  Session after enter: {ctx.session}")
        print(f"  Context scene: {getattr(ctx, 'scene', 'No scene attr')}")
    
    # Add global handler like in scene_bot.py
    @bot.on("message")
    async def global_handler(ctx):
        """Handle messages when not in a scene."""
        print(f"DEBUG: Global handler called for message: {ctx.message.text}")
        print(f"DEBUG: Has _scene_handled: {hasattr(ctx, '_scene_handled')}")
        print(f"DEBUG: _scene_handled value: {getattr(ctx, '_scene_handled', 'Not set')}")
        print(f"DEBUG: Session: {ctx.session}")
        
        # Skip if it's a command (commands have their own handlers)
        if ctx.message and ctx.message.text and ctx.message.text.startswith("/"):
            print("DEBUG: Skipping command")
            return
        
        # Check if a scene already handled this message
        if hasattr(ctx, "_scene_handled") and ctx._scene_handled:
            print("DEBUG: Scene handled message, skipping global handler")
            return
        
        # Check if we're in an active scene
        if hasattr(ctx, "session") and "__scene" in ctx.session:
            # We're in a scene, so the scene should handle this message
            # Don't send the fallback message
            print("DEBUG: In active scene, skipping global handler")
            return
        
        # Only handle non-command messages when not in a scene
        print("DEBUG: Sending fallback message")
        await ctx.reply("Send /start to begin, or /help for available commands.")
    
    # Test the flow
    with patch.object(bot.api_client, 'send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"success": True}
        
        print("=== Testing /greeting command ===")
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
        
        await bot.handle_update(greeting_update)
        
        print("\n=== Testing text message in scene ===")
        text_update = {
            "typeWebhook": "incomingMessageReceived",
            "instanceData": {
                "idInstance": "test",
                "wid": "test@c.us",
                "typeInstance": "whatsapp"
            },
            "timestamp": 1234567891,
            "idMessage": "test_text",
            "senderData": {
                "chatId": "1234567890@c.us",
                "sender": "1234567890@c.us",
                "senderName": "Test User"
            },
            "messageData": {
                "typeMessage": "textMessage",
                "textMessageData": {
                    "textMessage": "John"
                }
            }
        }
        
        await bot.handle_update(text_update)

if __name__ == "__main__":
    asyncio.run(test_scene_entry())
