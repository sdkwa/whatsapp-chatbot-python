# SDKWA WhatsApp Chatbot - Python SDK

[![PyPI version](https://badge.fury.io/py/sdkwa-whatsapp-chatbot.svg)](https://badge.fury.io/py/sdkwa-whatsapp-chatbot)
[![Python](https://img.shields.io/pypi/pyversions/sdkwa-whatsapp-chatbot.svg)](https://pypi.org/project/sdkwa-whatsapp-chatbot/)
[![CI](https://github.com/sdkwa/whatsapp-chatbot-python/workflows/CI/badge.svg)](https://github.com/sdkwa/whatsapp-chatbot-python/actions/workflows/ci.yml)
[![Publish to PyPI](https://github.com/sdkwa/whatsapp-chatbot-python/workflows/Publish%20to%20PyPI/badge.svg)](https://github.com/sdkwa/whatsapp-chatbot-python/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python chatbot library that provides a **Telegraf-like interface** for building WhatsApp bots using the SDKWA WhatsApp API. This library is inspired by the popular Telegraf framework for Telegram bots, bringing the same elegant API design to WhatsApp.

## Features

🚀 **Telegraf-Like API** - Familiar and intuitive interface for Telegram developers  
🤖 **Easy Bot Creation** - Simple `WhatsAppBot` class with clean configuration  
🎭 **Scenes & Wizards** - Create complex conversation flows and step-by-step interactions  
💾 **Session Management** - Built-in session storage with memory and file backends  
🔧 **Middleware Support** - Compose functionality with middleware pattern  
📱 **Media Handling** - Send and receive photos, documents, audio, video, locations, and contacts  
⌨️ **Command Handling** - Handle `/start`, `/help`, and custom commands  
🎯 **Event Filtering** - Listen for specific message types and patterns  
🌐 **Webhook Support** - Built-in webhook support for Flask and FastAPI  
🔒 **Type Safe** - Full type hints for better development experience  

## Installation

```bash
pip install sdkwa-whatsapp-chatbot
```

## Quick Start

### 1. Basic Bot

```python
import os
from sdkwa_whatsapp_chatbot import WhatsAppBot

# Create bot
bot = WhatsAppBot({
    'idInstance': os.getenv('ID_INSTANCE'),
    'apiTokenInstance': os.getenv('API_TOKEN_INSTANCE')
})

# Handle text messages
@bot.on('text')
async def handle_text(ctx):
    await ctx.reply(f"You said: {ctx.message.text}")

# Handle commands
@bot.start()
async def start_command(ctx):
    await ctx.reply('Welcome to my WhatsApp bot!')

@bot.command('hello')
async def hello_command(ctx):
    await ctx.reply('Hello there! 👋')

# Launch bot
bot.launch()
```

### 2. Bot with Sessions

```python
from sdkwa_whatsapp_chatbot import WhatsAppBot, session

bot = WhatsAppBot({
    'idInstance': os.getenv('ID_INSTANCE'),
    'apiTokenInstance': os.getenv('API_TOKEN_INSTANCE')
})

# Enable sessions
bot.use(session())

@bot.command('count')
async def count_command(ctx):
    # Access session data
    count = ctx.session.get('count', 0) + 1
    ctx.session['count'] = count
    await ctx.reply(f"You've used this command {count} times!")

bot.launch()
```

### 3. Bot with Scenes (Conversation Flows)

```python
from sdkwa_whatsapp_chatbot import WhatsAppBot, session, BaseScene, Stage

bot = WhatsAppBot({
    'idInstance': os.getenv('ID_INSTANCE'),
    'apiTokenInstance': os.getenv('API_TOKEN_INSTANCE')
})

# Create a greeting scene
greeting_scene = BaseScene('greeting')

@greeting_scene.enter()
async def enter_greeting(ctx):
    await ctx.reply("What's your name?")

@greeting_scene.on('text')
async def handle_name(ctx):
    name = ctx.message.text
    ctx.session['name'] = name
    await ctx.reply(f"Nice to meet you, {name}!")
    await ctx.scene.leave_scene(ctx)

# Create stage and register scene
stage = Stage([greeting_scene])

# Use middleware
bot.use(session())
bot.use(stage.middleware())

# Command to enter scene
@bot.command('greet')
async def start_greeting(ctx):
    await ctx.scene_manager.enter('greeting', ctx)

bot.launch()
```

### 4. Wizard Scene (Step-by-Step)

```python
from sdkwa_whatsapp_chatbot import WhatsAppBot, session, Stage
from sdkwa_whatsapp_chatbot.scenes import WizardScene

bot = WhatsAppBot({
    'idInstance': os.getenv('ID_INSTANCE'),
    'apiTokenInstance': os.getenv('API_TOKEN_INSTANCE')
})

# Create registration wizard
wizard = WizardScene('registration')

@wizard.step
async def ask_name(ctx):
    await ctx.reply("Step 1: What's your name?")

@wizard.step
async def ask_age(ctx):
    name = ctx.message.text
    await ctx.wizard.next({'name': name})
    await ctx.reply("Step 2: How old are you?")

@wizard.step
async def finish(ctx):
    age = ctx.message.text
    await ctx.wizard.next({'age': age})
    
    # Get all collected data
    data = ctx.wizard.get_all_data()
    name = data.get(0, {}).get('name')
    age = data.get(1, {}).get('age')
    
    await ctx.reply(f"Registration complete!\nName: {name}\nAge: {age}")
    await ctx.wizard.complete()

# Setup
stage = Stage([wizard])
bot.use(session())
bot.use(stage.middleware())

@bot.command('register')
async def start_wizard(ctx):
    await ctx.scene_manager.enter('registration', ctx)

bot.launch()
```

## API Reference

### Bot Creation

```python
from sdkwa_whatsapp_chatbot import WhatsAppBot

# Configuration options
config = {
    'idInstance': 'your-instance-id',
    'apiTokenInstance': 'your-api-token',
    'apiUrl': 'https://api.sdkwa.pro'  # Optional
}

bot = WhatsAppBot(config)
```

### Event Handlers

```python
# Listen for specific update types
@bot.on('message')        # All messages
@bot.on('text')          # Text messages only
@bot.on(['text', 'photo']) # Multiple types

# Listen for text patterns
@bot.hears('hello')      # Exact match
@bot.hears(r'hello.*')   # Regex pattern

# Listen for commands
@bot.command('start')    # /start command
@bot.start()            # Alias for /start
@bot.help()             # Alias for /help
```

### Context Methods

```python
async def handler(ctx):
    # Send messages
    await ctx.reply('Hello!')
    await ctx.reply_with_photo('https://example.com/photo.jpg', caption='Photo')
    await ctx.reply_with_document('https://example.com/doc.pdf')
    await ctx.reply_with_location(40.7128, -74.0060, 'New York')
    await ctx.reply_with_contact('+1234567890', 'John', 'Doe')
    
    # Message info
    text = ctx.message.text
    chat_id = ctx.chat_id
    sender = ctx.from_user
    
    # Command helpers
    command = ctx.get_command()      # Get command name
    args = ctx.get_command_args()    # Get command arguments
    
    # Session access
    ctx.session['key'] = 'value'
    value = ctx.session.get('key')
```

### Session Management

```python
from sdkwa_whatsapp_chatbot import session, MemorySessionStore, FileSessionStore

# Use memory store (default)
bot.use(session())

# Use file store
bot.use(session(store=FileSessionStore('sessions.json')))

# Custom session key
def custom_key(ctx):
    return f"{ctx.chat_id}:{ctx.from_user.get('id', 'anonymous')}"

bot.use(session(key_generator=custom_key))
```

### Scene Management

```python
from sdkwa_whatsapp_chatbot import BaseScene, Stage

# Create scene
scene = BaseScene('my_scene')

@scene.enter()
async def on_enter(ctx):
    await ctx.reply("Entered scene!")

@scene.leave()
async def on_leave(ctx):
    await ctx.reply("Left scene!")

@scene.on('text')
async def handle_text(ctx):
    await ctx.reply("In scene: " + ctx.message.text)

# Scene state management
@scene.on('text')
async def save_data(ctx):
    scene.update_state(ctx, {'user_input': ctx.message.text})
    state = scene.get_state(ctx)

# Create stage
stage = Stage([scene])
bot.use(stage.middleware())

# Scene navigation
@bot.command('enter')
async def enter_scene(ctx):
    await ctx.scene_manager.enter('my_scene', ctx)
```

### Wizard Scenes

```python
from sdkwa_whatsapp_chatbot.scenes import WizardScene

wizard = WizardScene('my_wizard')

@wizard.step
async def step1(ctx):
    await ctx.reply("Step 1: Enter your name")

@wizard.step
async def step2(ctx):
    name = ctx.message.text
    await ctx.wizard.next({'name': name})
    await ctx.reply("Step 2: Enter your age")

@wizard.step
async def step3(ctx):
    age = ctx.message.text
    await ctx.wizard.next({'age': age})
    
    # Get all data
    all_data = ctx.wizard.get_all_data()
    await ctx.reply(f"Done! Name: {all_data[0]['name']}, Age: {all_data[1]['age']}")
    await ctx.wizard.complete()

# Wizard navigation
async def handler(ctx):
    await ctx.wizard.next()           # Next step
    await ctx.wizard.previous()       # Previous step
    await ctx.wizard.jump_to(2)       # Jump to step
    progress = ctx.wizard.progress    # Get progress info
```

### Media Handling

```python
# Send media
await ctx.reply_with_photo(
    photo_url='https://example.com/photo.jpg',
    caption='A nice photo'
)

await ctx.reply_with_document(
    document_url='https://example.com/doc.pdf',
    caption='Important document'
)

# Handle received media
@bot.on('message')
async def handle_media(ctx):
    if ctx.message.message_type == 'imageMessage':
        await ctx.reply("Received a photo!")
        # Download URL: ctx.message.file_url
        
    elif ctx.message.message_type == 'documentMessage':
        await ctx.reply(f"Received document: {ctx.message.file_name}")
```

### Webhook Support

```python
# Flask webhook
from flask import Flask
app = Flask(__name__)
bot.flask_webhook(app, '/webhook')

# FastAPI webhook
from fastapi import FastAPI
app = FastAPI()
bot.fastapi_webhook(app, '/webhook')

# Custom webhook
callback = bot.webhook_callback()
# Use callback in your web framework
```

### Error Handling

```python
@bot.catch
async def error_handler(error, ctx):
    print(f"Error: {error}")
    if ctx:
        await ctx.reply("Sorry, something went wrong!")
```

## Examples

The `examples/` directory contains several complete examples:

- [`hello_bot.py`](examples/hello_bot.py) - Simple hello bot
- [`echo_bot.py`](examples/echo_bot.py) - Echo messages and files
- [`scene_bot.py`](examples/scene_bot.py) - Conversation scenes
- [`wizard_bot.py`](examples/wizard_bot.py) - Step-by-step wizards
- [`media_bot.py`](examples/media_bot.py) - Media file handling

## Configuration

### Environment Variables

```bash
export ID_INSTANCE="your_instance_id"
export API_TOKEN_INSTANCE="your_api_token"
```

### Configuration Object

```python
config = {
    'idInstance': 'your-instance-id',
    'apiTokenInstance': 'your-api-token',
    'apiUrl': 'https://api.sdkwa.pro',  # Optional
    
    # Bot options
    'polling_interval': 1,    # Seconds between polls
    'max_retries': 3,        # Max retry attempts
    'retry_delay': 5         # Delay between retries
}

bot = WhatsAppBot(config)
```

## Getting SDKWA Credentials

1. Sign up at [SDKWA](https://sdkwa.pro)
2. Create a new WhatsApp instance
3. Get your `idInstance` and `apiTokenInstance` from the dashboard
4. Use these credentials in your bot configuration

## Comparison with JavaScript Version

This Python library provides the same functionality as the JavaScript `@sdkwa/whatsapp-chatbot` package:

| Feature | JavaScript | Python | Status |
|---------|------------|--------|--------|
| Basic Bot | ✅ | ✅ | Complete |
| Commands | ✅ | ✅ | Complete |
| Scenes | ✅ | ✅ | Complete |
| Sessions | ✅ | ✅ | Complete |
| Middleware | ✅ | ✅ | Complete |
| Media Files | ✅ | ✅ | Complete |
| Webhooks | ✅ | ✅ | Complete |
| Error Handling | ✅ | ✅ | Complete |

## Requirements

- Python 3.8+
- `sdkwa-whatsapp-api-client` >= 1.0.0
- `typing-extensions` >= 4.0.0
- `pydantic` >= 2.0.0

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/sdkwa/whatsapp-chatbot-python.git
cd whatsapp-chatbot-python

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black sdkwa_whatsapp_chatbot/
isort sdkwa_whatsapp_chatbot/

# Type checking
mypy sdkwa_whatsapp_chatbot/
```

## Development Setup

### Using Make (Recommended)

```bash
# Install development dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Build package
make build

# Clean build artifacts
make clean
```

### Manual Setup

```bash
# Clone repository
git clone https://github.com/sdkwa/whatsapp-chatbot-python.git
cd whatsapp-chatbot-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Set up pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy sdkwa_whatsapp_chatbot
```

### Publishing

For maintainers, see [PUBLISHING.md](PUBLISHING.md) for detailed instructions on publishing to PyPI.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://docs.sdkwa.pro)
- 💬 [Telegram Support](https://t.me/sdkwa_support)
- 🌐 [Official Website](https://sdkwa.pro)
- 🐛 [Report Issues](https://github.com/sdkwa/whatsapp-chatbot-python/issues)

## Changelog

### v1.0.0
- Initial release
- Telegraf-like API for WhatsApp bots
- Scene and wizard support
- Session management
- Media handling
- Webhook support
- Complete examples and documentation
