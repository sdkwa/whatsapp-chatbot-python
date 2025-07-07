#!/usr/bin/env python3
"""Simple hello bot example."""

import os

from sdkwa_whatsapp_chatbot import WhatsAppBot

# Create bot with configuration
bot = WhatsAppBot(
    {
        "idInstance": os.getenv("ID_INSTANCE", "your-instance-id"),
        "apiTokenInstance": os.getenv("API_TOKEN_INSTANCE", "your-api-token"),
        "apiUrl": "https://api.sdkwa.pro",  # Optional
    }
)


# Handle all messages
@bot.on("message")
async def hello_handler(ctx):
    """Reply with hello message to all incoming messages."""
    await ctx.reply("Hello from Python WhatsApp Bot! 👋")


# Handle /start command
@bot.start()
async def start_handler(ctx):
    """Handle /start command."""
    await ctx.reply("Welcome! Send me any message and I will say hello back.")


# Handle /help command
@bot.help()
async def help_handler(ctx):
    """Handle /help command."""
    help_text = """
🤖 *WhatsApp Bot Help*

Available commands:
• /start - Start the bot
• /help - Show this help message

Just send me any message and I'll reply with a greeting!
    """
    await ctx.reply(help_text)


if __name__ == "__main__":
    print("Starting WhatsApp Bot...")
    print("Press Ctrl+C to stop")

    try:
        # Launch bot (starts polling)
        bot.launch()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
