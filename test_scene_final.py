#!/usr/bin/env python3
"""Test the scene bot functionality."""

import asyncio
from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

# Create bot with error handler that ignores API errors
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
        print(f"DEBUG: Ignoring API error (expected with fake credentials)")
    else:
        print(f"DEBUG: Unexpected error: {error}")

# Create greeting scene
greeting_scene = BaseScene("greeting")

@greeting_scene.enter()
async def greeting_enter(ctx):
    """Enter greeting scene."""
    print(f"DEBUG: Entering greeting scene")
    print(f"DEBUG: Session: {ctx.session}")
    print("Would send: Hi! What's your name?")

@greeting_scene.on("text")
async def greeting_text(ctx):
    """Handle text in greeting scene."""
    name = ctx.message.text
    print(f"DEBUG: Got name: {name}")
    print(f"DEBUG: Session before: {ctx.session}")
    ctx.session["user_name"] = name
    print(f"DEBUG: Session after: {ctx.session}")
    print(f"Would send: Nice to meet you, {name}!")
    await ctx.scene.leave_scene(ctx)

@greeting_scene.leave()
async def greeting_leave(ctx):
    """Leave greeting scene."""
    print("DEBUG: Leaving greeting scene")
    print(f"DEBUG: Session: {ctx.session}")
    print("Would send: Thanks for telling me your name!")

# Create stage and register scenes
stage = Stage([greeting_scene])

# Setup bot with session and stage middleware
bot.use(session(store=bot.session_manager.store))
bot.use(stage.middleware())

@bot.command("greeting")
async def start_greeting(ctx):
    """Start greeting scene."""
    print("DEBUG: Starting greeting command")
    print(f"DEBUG: Session: {ctx.session}")
    await ctx.scene_manager.enter("greeting", ctx)

@bot.start()
async def start(ctx):
    """Handle /start command."""
    print("DEBUG: Start command called")
    print(f"DEBUG: Session: {ctx.session}")
    user_name = ctx.session.get("user_name", "there")
    print(f"Would send: Hello {user_name}! Use /greeting to start.")

async def test_scenario():
    """Test the complete scenario."""
    
    # Mock updates
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
    
    greeting_update = {
        **start_update,
        "idMessage": "test124",
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "/greeting"
            }
        }
    }
    
    name_update = {
        **start_update,
        "idMessage": "test125",
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "Alice"
            }
        }
    }
    
    print("=== Testing /start command ===")
    await bot.handle_update(start_update)
    
    print("\n=== Testing /greeting command ===")
    await bot.handle_update(greeting_update)
    
    print("\n=== Testing name response (should trigger scene text handler) ===")
    await bot.handle_update(name_update)
    
    print("\n=== Testing /start again (should show remembered name) ===")
    await bot.handle_update(start_update)

if __name__ == "__main__":
    print("Starting scene bot test...")
    asyncio.run(test_scenario())
