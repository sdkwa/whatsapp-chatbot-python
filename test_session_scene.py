#!/usr/bin/env python3
"""Test session and scene handling."""

import asyncio
from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": "1101000001",
        "apiTokenInstance": "fake_token",
    }
)

# Create greeting scene
greeting_scene = BaseScene("greeting")

@greeting_scene.enter()
async def greeting_enter(ctx):
    """Enter greeting scene."""
    print(f"DEBUG: Entering greeting scene")
    print(f"DEBUG: Session: {ctx.session}")
    await ctx.reply("Hi! What's your name?")

@greeting_scene.on("text")
async def greeting_text(ctx):
    """Handle text in greeting scene."""
    name = ctx.message.text
    print(f"DEBUG: Got name: {name}")
    print(f"DEBUG: Session before: {ctx.session}")
    ctx.session["user_name"] = name
    print(f"DEBUG: Session after: {ctx.session}")
    await ctx.reply(f"Nice to meet you, {name}!")
    await ctx.scene.leave_scene(ctx)

@greeting_scene.leave()
async def greeting_leave(ctx):
    """Leave greeting scene."""
    print("DEBUG: Leaving greeting scene")
    print(f"DEBUG: Session: {ctx.session}")
    await ctx.reply("Thanks for telling me your name!")

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
    welcome_text = f"Hello {user_name}! Use /greeting to start."
    await ctx.reply(welcome_text)

async def test_scenario():
    """Test a complete scenario."""
    print("\n=== Testing /start command ===")
    
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
    
    await bot.handle_update(start_update)
    
    print("\n=== Testing /greeting command ===")
    
    # Mock update for /greeting
    greeting_update = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {
            "idInstance": 1101000001,
            "wid": "1234567890@c.us",
            "typeInstance": "whatsapp"
        },
        "timestamp": 1234567890,
        "idMessage": "test124",
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
    
    print("\n=== Testing name response ===")
    
    # Mock update for name response
    name_update = {
        "typeWebhook": "incomingMessageReceived",
        "instanceData": {
            "idInstance": 1101000001,
            "wid": "1234567890@c.us",
            "typeInstance": "whatsapp"
        },
        "timestamp": 1234567890,
        "idMessage": "test125",
        "senderData": {
            "chatId": "1234567890@c.us",
            "sender": "1234567890@c.us", 
            "senderName": "Test User"
        },
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "Alice"
            }
        }
    }
    
    await bot.handle_update(name_update)
    
    print("\n=== Testing /start again to check session persistence ===")
    
    await bot.handle_update(start_update)

if __name__ == "__main__":
    print("Starting session and scene test...")
    asyncio.run(test_scenario())
