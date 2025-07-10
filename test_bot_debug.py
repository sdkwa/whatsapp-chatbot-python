#!/usr/bin/env python3
"""Debug test for scene bot."""

import os
import asyncio

from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": os.getenv("ID_INSTANCE", "1101000001"),
        "apiTokenInstance": os.getenv("API_TOKEN_INSTANCE", "bdc849951cd130f830e0a45094fffbf8cc2eaabbf6be97f9"),
    }
)

# Create greeting scene
greeting_scene = BaseScene("greeting")

@greeting_scene.enter()
async def greeting_enter(ctx):
    """Enter greeting scene."""
    print(f"DEBUG: Entering greeting scene for {ctx.message.from_user}")
    await ctx.reply("Hi! What's your name?")

@greeting_scene.on("text")
async def greeting_text(ctx):
    """Handle text in greeting scene."""
    name = ctx.message.text
    print(f"DEBUG: Got name: {name}")
    ctx.session["user_name"] = name
    await ctx.reply(f"Nice to meet you, {name}!")
    await ctx.scene.leave_scene(ctx)

@greeting_scene.leave()
async def greeting_leave(ctx):
    """Leave greeting scene."""
    print("DEBUG: Leaving greeting scene")
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
    await ctx.scene_manager.enter("greeting", ctx)

@bot.start()
async def start(ctx):
    """Handle /start command."""
    print("DEBUG: Start command called")
    user_name = ctx.session.get("user_name", "there")
    welcome_text = f"Hello {user_name}! Use /greeting to start."
    await ctx.reply(welcome_text)

async def test_manual():
    """Test the bot manually without connecting to WhatsApp."""
    print("Testing bot initialization...")
    
    # Check if session manager is working
    print(f"Session manager: {bot.session_manager}")
    print(f"Session store: {bot.session_manager.store}")
    
    # Check middleware
    print(f"Middleware count: {len(bot.middleware_stack)}")
    for i, mw in enumerate(bot.middleware_stack):
        print(f"Middleware {i}: {mw}")
    
    # Check stage
    print(f"Stage scenes: {stage.scenes}")
    
    print("Bot setup looks good!")

if __name__ == "__main__":
    print("Starting debug test...")
    asyncio.run(test_manual())
