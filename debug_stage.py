#!/usr/bin/env python3
"""Debug stage middleware issue."""

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
    else:
        print(f"DEBUG: Unexpected error: {error}")

# Create greeting scene
greeting_scene = BaseScene("greeting")

@greeting_scene.enter()
async def greeting_enter(ctx):
    """Enter greeting scene."""
    print(f"DEBUG: Entering greeting scene")
    print(f"DEBUG: Session after enter: {ctx.session}")

@greeting_scene.on("text")
async def greeting_text(ctx):
    """Handle text in greeting scene."""
    name = ctx.message.text
    print(f"DEBUG: Got name in scene: {name}")
    ctx.session["user_name"] = name
    await ctx.scene.leave_scene(ctx)

@greeting_scene.leave()
async def greeting_leave(ctx):
    """Leave greeting scene."""
    print("DEBUG: Leaving greeting scene")

# Create stage with debug
stage = Stage([greeting_scene])

# Add custom stage middleware with debug
async def debug_stage_middleware(ctx, next_handler=None):
    print(f"DEBUG: Stage middleware called")
    print(f"DEBUG: Session at start: {ctx.session}")
    
    # Add scene manager to context
    ctx.scene_manager = stage

    # Get current scene
    current_scene = stage.get_current_scene(ctx)
    print(f"DEBUG: Current scene: {current_scene}")
    
    if current_scene:
        print(f"DEBUG: Scene ID: {current_scene.scene_id}")
        ctx.scene = current_scene

        # Process update through scene handlers
        if current_scene.handler:
            print(f"DEBUG: Calling scene handler")
            if asyncio.iscoroutinefunction(current_scene.handler):
                scene_result = await current_scene.handler(ctx)
            else:
                scene_result = current_scene.handler(ctx)
            print(f"DEBUG: Scene handler result: {scene_result}")
            return scene_result
    else:
        print(f"DEBUG: No current scene, calling next handler")

    # If next_handler is provided and scene didn't handle it, call it
    if next_handler:
        if asyncio.iscoroutinefunction(next_handler):
            return await next_handler(ctx)
        else:
            return next_handler(ctx)

# Setup bot with session and custom debug stage middleware
bot.use(session(store=bot.session_manager.store))
bot.use(debug_stage_middleware)

@bot.command("greeting")
async def start_greeting(ctx):
    """Start greeting scene."""
    print("DEBUG: Starting greeting command")
    print(f"DEBUG: Session: {ctx.session}")
    await ctx.scene_manager.enter("greeting", ctx)
    print(f"DEBUG: Session after enter: {ctx.session}")

@bot.start()
async def start(ctx):
    """Handle /start command."""
    print("DEBUG: Start command called")
    user_name = ctx.session.get("user_name", "there")
    print(f"Would send: Hello {user_name}! Use /greeting to start.")

async def test_scene_detection():
    """Test scene detection logic."""
    
    # Mock updates
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
    
    name_update = {
        **greeting_update,
        "idMessage": "test125",
        "messageData": {
            "typeMessage": "textMessage",
            "textMessageData": {
                "textMessage": "Alice"
            }
        }
    }
    
    print("=== Testing /greeting command ===")
    await bot.handle_update(greeting_update)
    
    print("\n=== Testing name response (should be handled by scene) ===")
    await bot.handle_update(name_update)

if __name__ == "__main__":
    print("Starting stage middleware debug...")
    asyncio.run(test_scene_detection())
