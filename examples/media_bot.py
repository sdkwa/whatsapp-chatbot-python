#!/usr/bin/env python3
"""Media bot example for handling files, photos, and media."""

import os

from sdkwa_whatsapp_chatbot import WhatsAppBot

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": os.getenv("ID_INSTANCE", "your-instance-id"),
        "apiTokenInstance": os.getenv("API_TOKEN_INSTANCE", "your-api-token"),
    }
)


# Handle photo messages
@bot.on("message")
async def handle_photos(ctx):
    """Handle photo messages."""
    if ctx.message and ctx.message.message_type == "imageMessage":
        await ctx.reply("📸 Nice photo! Let me send you one back...")

        # Send a sample photo
        sample_photo_url = "https://picsum.photos/400/300"
        await ctx.reply_with_photo(
            photo_url=sample_photo_url, caption="Here's a random photo for you! 🖼️"
        )


# Handle document messages
@bot.on("message")
async def handle_documents(ctx):
    """Handle document messages."""
    if ctx.message and ctx.message.message_type == "documentMessage":
        file_name = ctx.message.file_name or "Unknown file"
        await ctx.reply(f"📄 Received document: {file_name}")

        # You could process the document here
        # download_url = ctx.message.file_url
        # if download_url:
        #     # Download and process file
        #     pass


# Handle audio messages
@bot.on("message")
async def handle_audio(ctx):
    """Handle audio messages."""
    if ctx.message and ctx.message.message_type in ["audioMessage", "pttMessage"]:
        message_type = (
            "voice note" if ctx.message.message_type == "pttMessage" else "audio"
        )
        await ctx.reply(f"🎵 Received {message_type}! Thanks for sharing.")


# Handle video messages
@bot.on("message")
async def handle_video(ctx):
    """Handle video messages."""
    if ctx.message and ctx.message.message_type == "videoMessage":
        await ctx.reply("🎥 Cool video! I received it successfully.")


# Commands for sending different media types
@bot.command("photo")
async def send_photo(ctx):
    """Send a random photo."""
    photo_url = "https://picsum.photos/500/400"
    await ctx.reply_with_photo(photo_url=photo_url, caption="Here's a random photo! 📸")


@bot.command("location")
async def send_location(ctx):
    """Send a location."""
    # Example coordinates (New York City)
    latitude = 40.7128
    longitude = -74.0060

    await ctx.reply_with_location(
        latitude=latitude,
        longitude=longitude,
        name="New York City",
        address="New York, NY, USA",
    )


@bot.command("contact")
async def send_contact(ctx):
    """Send a contact."""
    await ctx.reply_with_contact(
        phone="+1234567890",
        first_name="John",
        last_name="Doe",
        company="Example Company",
    )


@bot.command("document")
async def send_document(ctx):
    """Send a sample document."""
    # Example: Send a PDF document
    doc_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    await ctx.reply_with_document(
        document_url=doc_url, caption="Here's a sample PDF document 📄"
    )


@bot.command("media")
async def media_menu(ctx):
    """Show media command menu."""
    menu_text = """
📱 *Media Bot Commands*

Send me any media and I'll respond:
• 📸 Photos - I'll send one back
• 📄 Documents - I'll acknowledge receipt
• 🎵 Audio/Voice - I'll confirm I received it
• 🎥 Videos - I'll let you know I got it

Or try these commands:
• /photo - Get a random photo
• /location - Get a location
• /contact - Get a sample contact
• /document - Get a sample document
• /gallery - See a photo gallery
    """
    await ctx.reply(menu_text)


@bot.command("gallery")
async def photo_gallery(ctx):
    """Send multiple photos."""
    photos = [
        ("https://picsum.photos/400/300?random=1", "Random photo 1 🌄"),
        ("https://picsum.photos/400/300?random=2", "Random photo 2 🏞️"),
        ("https://picsum.photos/400/300?random=3", "Random photo 3 🌊"),
    ]

    await ctx.reply("📸 Here's a photo gallery for you:")

    for photo_url, caption in photos:
        await ctx.reply_with_photo(photo_url=photo_url, caption=caption)


@bot.start()
async def start(ctx):
    """Handle /start command."""
    welcome_text = """
📱 *Welcome to Media Bot!*

I can handle all types of media files:

*Send me:*
• 📸 Photos (I'll send one back)
• 📄 Documents (I'll acknowledge them)
• 🎵 Audio files or voice notes
• 🎥 Videos

*Commands:*
• /media - Show media menu
• /photo - Get a random photo
• /location - Get a location
• /contact - Get a contact
• /document - Get a sample document
• /gallery - See photo gallery
• /help - Show help

Try sending me any media file to see how I handle it!
    """
    await ctx.reply(welcome_text)


@bot.help()
async def help_cmd(ctx):
    """Handle /help command."""
    help_text = """
📱 *Media Bot Help*

This bot demonstrates handling different media types.

*Media Handling:*
• Photos → I respond with a photo
• Documents → I acknowledge receipt
• Audio/Voice → I confirm I received it
• Videos → I let you know I got it

*Commands:*
• /start - Welcome message
• /media - Media command menu
• /photo - Random photo
• /location - Sample location
• /contact - Sample contact
• /document - Sample PDF
• /gallery - Multiple photos
• /help - This help

*Tips:*
• Send any media file to see how I handle it
• I can send photos, documents, locations, and contacts
• Try the gallery command for multiple photos
    """
    await ctx.reply(help_text)


# Handle any other message types
@bot.on("message")
async def handle_other_messages(ctx):
    """Handle other message types."""
    if ctx.message and ctx.message.message_type == "textMessage":
        # Already handled by other handlers or will be handled by default
        pass
    elif ctx.message and not ctx.message.message_type:
        await ctx.reply(
            "I received your message but couldn't identify the type. Send /help for available commands."
        )


if __name__ == "__main__":
    print("Starting Media Bot...")
    bot.launch()
