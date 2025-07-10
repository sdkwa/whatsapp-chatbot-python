# Enhanced Message Parsing Features

The WhatsApp Bot framework includes robust message parsing capabilities in the `Context` class that handle all WhatsApp message types supported by the SDKWA API.

## Supported Message Types

### Text Messages
- `textMessage` - Simple text messages
- `extendedTextMessage` - Rich text messages with formatting
- `quotedMessage` - Messages that quote/reply to other messages

### Media Messages
- `imageMessage` - Image files with optional captions
- `videoMessage` - Video files with optional captions
- `audioMessage` - Audio files with optional captions
- `documentMessage` - Document files with optional captions
- `fileMessage` - Generic file uploads with optional captions

### Special Message Types
- `locationMessage` - Location coordinates with optional name/address
- `contactMessage` - Contact information (vCard format)

## Message Object Features

The `Message` class provides convenient methods to check message types:

```python
# Text message checks
message.is_text()      # Returns True for text, extended text, or quoted messages
message.is_quoted()    # Returns True for quoted messages only

# Media message checks
message.is_image()     # Image messages
message.is_video()     # Video messages
message.is_audio()     # Audio messages
message.is_document()  # Document messages
message.is_file()      # Generic file messages
message.is_media()     # Any media type (image, video, audio, document, file)

# Special message checks
message.is_location()  # Location messages
message.is_contact()   # Contact messages

# Location helper methods
message.get_latitude()  # Extract latitude from location messages
message.get_longitude() # Extract longitude from location messages
```

## Parsing Logic

### Text Extraction
- For `textMessage`: Extracts from `textMessageData.textMessage`
- For `quotedMessage` and `extendedTextMessage`: Extracts from `extendedTextMessageData.text`
- For media messages: Uses caption as text if no explicit text is present

### File Data Extraction
- File URL: `fileMessageData.downloadUrl`
- File name: `fileMessageData.fileName`
- Caption: `fileMessageData.caption`

### Location Data Extraction
- Coordinates and metadata from `locationMessageData`

### Contact Data Extraction
- Contact information from `contactMessageData`

### Quoted Message Handling
- Safely extracts quoted message ID even when the quoted message data is null or malformed
- Handles edge cases where the quoted message reference might be missing

## Example Usage

```python
@bot.on("message")
async def handle_message(ctx):
    if ctx.message.is_text():
        await ctx.reply(f"You said: {ctx.message.text}")
    
    elif ctx.message.is_image():
        await ctx.reply(f"Nice image! Caption: {ctx.message.caption}")
        # Download the image using ctx.message.file_url
    
    elif ctx.message.is_location():
        lat = ctx.message.get_latitude()
        lng = ctx.message.get_longitude()
        await ctx.reply(f"Location received: {lat}, {lng}")
    
    elif ctx.message.is_contact():
        contact_name = ctx.message.contact.get('displayName', 'Unknown')
        await ctx.reply(f"Contact received: {contact_name}")
```

## Robust Error Handling

The parsing logic includes safeguards for:
- Missing or null data fields
- Malformed message structures
- Edge cases like empty quoted message references
- Graceful fallbacks for unknown message types

All parsing is defensive and will not crash the bot even with unexpected input formats.
