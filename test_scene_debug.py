#!/usr/bin/env python3
"""Test scene_bot with debug output."""

import asyncio
from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": "1101000001",
        "apiTokenInstance": "fake_token",
    }
)

# Add error handler to suppress API errors
@bot.catch
async def error_handler(error, ctx):
    if "401 Client Error" in str(error):
        pass  # Ignore API errors

# Create greeting scene
greeting_scene = BaseScene("greeting")

@greeting_scene.enter()
async def greeting_enter(ctx):
    print(f"DEBUG: Scene enter called")

@greeting_scene.on("text")
async def greeting_text(ctx):
    name = ctx.message.text
    print(f"DEBUG: Scene text handler called with: {name}")
    ctx.session["user_name"] = name
    await ctx.scene.leave_scene(ctx)

@greeting_scene.leave()
async def greeting_leave(ctx):
    print("DEBUG: Scene leave called")

# Create stage and register scenes
stage = Stage([greeting_scene])

# Setup bot with session and stage middleware
bot.use(session(store=bot.session_manager.store))
bot.use(stage.middleware())

@bot.command("greeting")
async def start_greeting(ctx):
    print("DEBUG: Greeting command called")
    await ctx.scene_manager.enter("greeting", ctx)

async def test():
    """Test the scene bot."""
    
    # Mock updates
    greeting_update = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {"idInstance": 1101000001, "wid": "1234567890@c.us", "typeInstance": "whatsapp"},
        "timestamp": 1234567890,
        "idMessage": "test124",
        "senderData": {"chatId": "1234567890@c.us", "sender": "1234567890@c.us", "senderName": "Test User"},
        "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "/greeting"}}
    }
    
    name_update = {
        **greeting_update,
        "idMessage": "test125",
        "messageData": {"typeMessage": "textMessage", "textMessageData": {"textMessage": "Alice"}}
    }
    
    print("=== 1. Testing /greeting command ===")
    await bot.handle_update(greeting_update)
    
    print("\n=== 2. Testing name response ===")
    await bot.handle_update(name_update)

if __name__ == "__main__":
    asyncio.run(test())
