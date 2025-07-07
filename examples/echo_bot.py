#!/usr/bin/env python3
"""Echo bot example."""

import os

from sdkwa_whatsapp_chatbot import WhatsAppBot

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": os.getenv("ID_INSTANCE", "your-instance-id"),
        "apiTokenInstance": os.getenv("API_TOKEN_INSTANCE", "your-api-token"),
    }
)


# Echo text messages
@bot.on("text")
async def echo_text(ctx):
    """Echo back text messages."""
    if ctx.message and ctx.message.text:
        await ctx.reply(f"You said: {ctx.message.text}")


# Handle commands
@bot.command("echo")
async def echo_command(ctx):
    """Handle /echo command with arguments."""
    args = ctx.get_command_args()
    if args:
        text = " ".join(args)
        await ctx.reply(f"Echo: {text}")
    else:
        await ctx.reply("Usage: /echo <message>")


@bot.start()
async def start(ctx):
    """Handle /start command."""
    await ctx.reply("Echo bot started! Send me any message and I'll echo it back.")


@bot.help()
async def help_cmd(ctx):
    """Handle /help command."""
    help_text = """
🔄 *Echo Bot Help*

Commands:
• /start - Start the bot
• /help - Show this help
• /echo <message> - Echo a specific message

Or just send any text message and I'll echo it back!
    """
    await ctx.reply(help_text)


# Handle file messages
@bot.on("message")
async def handle_files(ctx):
    """Handle file messages."""
    if (
        ctx.message
        and ctx.message.message_type
        and ctx.message.message_type != "textMessage"
    ):

        file_type = ctx.message.message_type
        caption = ctx.message.caption or "No caption"

        await ctx.reply(f"Received {file_type}!\nCaption: {caption}")


if __name__ == "__main__":
    print("Starting Echo Bot...")
    bot.launch()
