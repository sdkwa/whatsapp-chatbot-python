#!/usr/bin/env python3
"""Scene bot example with conversation flows."""

import os

from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot, session

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": os.getenv("ID_INSTANCE", "your-instance-id"),
        "apiTokenInstance": os.getenv("API_TOKEN_INSTANCE", "your-api-token"),
    }
)

# Create greeting scene
greeting_scene = BaseScene("greeting")


@greeting_scene.enter()
async def greeting_enter(ctx):
    """Enter greeting scene."""
    await ctx.reply("Hi! What's your name?")


@greeting_scene.on("text")
async def greeting_text(ctx):
    """Handle text in greeting scene."""
    name = ctx.message.text
    ctx.session["user_name"] = name
    await ctx.reply(f"Nice to meet you, {name}!")

    # Leave scene
    await ctx.scene.leave_scene(ctx)


@greeting_scene.leave()
async def greeting_leave(ctx):
    """Leave greeting scene."""
    await ctx.reply("Thanks for telling me your name!")


# Create echo scene
echo_scene = BaseScene("echo")


@echo_scene.enter()
async def echo_enter(ctx):
    """Enter echo scene."""
    user_name = ctx.session.get("user_name", "friend")
    await ctx.reply(f"Echo mode activated, {user_name}! Send me messages to echo.")


@echo_scene.on("text")
async def echo_text(ctx):
    """Handle text in echo scene."""
    if ctx.message.text == "/back":
        await ctx.scene.leave_scene(ctx)
    else:
        await ctx.reply(f"Echo: {ctx.message.text}")


@echo_scene.command("back")
async def echo_back(ctx):
    """Handle back command in echo scene."""
    await ctx.scene.leave_scene(ctx)


@echo_scene.leave()
async def echo_leave(ctx):
    """Leave echo scene."""
    await ctx.reply("Exiting echo mode.")


# Create stage and register scenes
stage = Stage([greeting_scene, echo_scene])

# Setup bot with session and stage middleware
bot.use(session())
bot.use(stage.middleware())


# Global commands
@bot.command("greeting")
async def start_greeting(ctx):
    """Start greeting scene."""
    await ctx.scene_manager.enter("greeting", ctx)


@bot.command("echo")
async def start_echo(ctx):
    """Start echo scene."""
    await ctx.scene_manager.enter("echo", ctx)


@bot.start()
async def start(ctx):
    """Handle /start command."""
    user_name = ctx.session.get("user_name", "there")
    welcome_text = f"""
👋 Hello {user_name}!

Available commands:
• /greeting - Enter greeting scene
• /echo - Enter echo scene
• /help - Show help

Try entering a scene to see conversation flows in action!
    """
    await ctx.reply(welcome_text)


@bot.help()
async def help_cmd(ctx):
    """Handle /help command."""
    help_text = """
🎭 *Scene Bot Help*

This bot demonstrates conversation scenes (flows).

*Global Commands:*
• /start - Show welcome message
• /help - Show this help
• /greeting - Enter greeting scene
• /echo - Enter echo scene

*In Scenes:*
• Follow the prompts for each scene
• Use /back to exit echo scene
• Scenes maintain their own state

Scenes allow you to create step-by-step conversations!
    """
    await ctx.reply(help_text)


# Handle messages outside scenes
@bot.on("message")
async def global_handler(ctx):
    """Handle messages when not in a scene."""
    # Skip if it's a command (commands have their own handlers)
    if ctx.message and ctx.message.text and ctx.message.text.startswith("/"):
        return
    
    # Check if a scene already handled this message
    if hasattr(ctx, "_scene_handled") and ctx._scene_handled:
        return
    
    # Check if we're in an active scene
    if hasattr(ctx, "session") and "__scene" in ctx.session:
        # We're in a scene, so the scene should handle this message
        # Don't send the fallback message
        return
    # Only handle non-command messages when not in a scene
    await ctx.reply("Send /start to begin, or /help for available commands.")


if __name__ == "__main__":
    print("Starting Scene Bot...")
    bot.launch()
