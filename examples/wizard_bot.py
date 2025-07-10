#!/usr/bin/env python3
"""Wizard scene example for step-by-step conversations."""

import os

from sdkwa_whatsapp_chatbot import Stage, WhatsAppBot, session
from sdkwa_whatsapp_chatbot.scenes import WizardScene

# Create bot
bot = WhatsAppBot(
    {
        "idInstance": os.getenv("ID_INSTANCE", "your-instance-id"),
        "apiTokenInstance": os.getenv("API_TOKEN_INSTANCE", "your-api-token"),
    }
)

# Create registration wizard
registration_wizard = WizardScene("registration")


@registration_wizard.step
async def ask_name(ctx):
    """Step 1: Ask for name."""
    await ctx.reply(
        "Welcome to the registration wizard! 📝\n\nStep 1/4: What's your name?"
    )


@registration_wizard.step
async def ask_age(ctx):
    """Step 2: Ask for age."""
    name = ctx.message.text
    # Save name to step 0 data
    wizard_state = ctx.wizard.wizard.get_wizard_state(ctx)
    wizard_state["step_data"][0] = {"name": name}
    ctx.wizard.wizard.set_state(ctx, {"wizard": wizard_state})
    
    await ctx.reply(f"Nice to meet you, {name}!\n\nStep 2/4: How old are you?")


@registration_wizard.step
async def ask_email(ctx):
    """Step 3: Ask for email."""
    try:
        age = int(ctx.message.text)
        # Save age to step 1 data
        wizard_state = ctx.wizard.wizard.get_wizard_state(ctx)
        wizard_state["step_data"][1] = {"age": age}
        ctx.wizard.wizard.set_state(ctx, {"wizard": wizard_state})
        
        await ctx.reply(f"Great!\n\nStep 3/4: What's your email address?")
    except ValueError:
        await ctx.reply("Please enter a valid age (number):")


@registration_wizard.step
async def ask_phone(ctx):
    """Step 4: Ask for phone."""
    email = ctx.message.text
    if "@" in email:
        # Save email to step 2 data
        wizard_state = ctx.wizard.wizard.get_wizard_state(ctx)
        wizard_state["step_data"][2] = {"email": email}
        ctx.wizard.wizard.set_state(ctx, {"wizard": wizard_state})
        
        await ctx.reply("Perfect!\n\nStep 4/4: What's your phone number?")
    else:
        await ctx.reply("Please enter a valid email address:")


@registration_wizard.step
async def complete_registration(ctx):
    """Step 5: Complete registration."""
    phone = ctx.message.text
    # Save phone to step 3 data
    wizard_state = ctx.wizard.wizard.get_wizard_state(ctx)
    wizard_state["step_data"][3] = {"phone": phone}
    ctx.wizard.wizard.set_state(ctx, {"wizard": wizard_state})

    # Get all collected data
    all_data = ctx.wizard.get_all_data()

    # Create summary
    summary = f"""
✅ *Registration Complete!*

Here's your information:
• Name: {all_data.get(0, {}).get('name', 'N/A')}
• Age: {all_data.get(1, {}).get('age', 'N/A')}
• Email: {all_data.get(2, {}).get('email', 'N/A')}
• Phone: {all_data.get(3, {}).get('phone', 'N/A')}

Thank you for registering! 🎉
    """

    await ctx.reply(summary)
    await ctx.wizard.complete()


# Create survey wizard
survey_wizard = WizardScene("survey")


@survey_wizard.step
async def survey_intro(ctx):
    """Survey introduction."""
    await ctx.reply(
        "📊 Quick Survey\n\nStep 1/3: How would you rate our service? (1-5)"
    )


@survey_wizard.step
async def survey_feedback(ctx):
    """Get feedback."""
    try:
        rating = int(ctx.message.text)
        if 1 <= rating <= 5:
            await ctx.wizard.next({"rating": rating})
            await ctx.reply(
                "Step 2/3: What did you like most? (Optional, send 'skip' to skip)"
            )
        else:
            await ctx.reply("Please enter a rating between 1 and 5:")
    except ValueError:
        await ctx.reply("Please enter a number between 1 and 5:")


@survey_wizard.step
async def survey_suggestions(ctx):
    """Get suggestions."""
    feedback = ctx.message.text if ctx.message.text.lower() != "skip" else None
    await ctx.wizard.next({"feedback": feedback})
    await ctx.reply(
        "Step 3/3: Any suggestions for improvement? (Optional, send 'skip' to skip)"
    )


@survey_wizard.step
async def survey_complete(ctx):
    """Complete survey."""
    suggestions = ctx.message.text if ctx.message.text.lower() != "skip" else None
    await ctx.wizard.next({"suggestions": suggestions})

    # Get all data
    all_data = ctx.wizard.get_all_data()
    rating = all_data.get(0, {}).get("rating", 0)
    feedback = all_data.get(1, {}).get("feedback")
    suggestions = all_data.get(2, {}).get("suggestions")

    response = f"""
📊 *Survey Complete!*

Rating: {'⭐' * rating} ({rating}/5)
"""

    if feedback:
        response += f"\nWhat you liked: {feedback}"

    if suggestions:
        response += f"\nSuggestions: {suggestions}"

    response += "\n\nThank you for your feedback! 🙏"

    await ctx.reply(response)
    await ctx.wizard.complete()


# Create stage
stage = Stage([registration_wizard, survey_wizard])

# Setup middleware
bot.use(session())
bot.use(stage.middleware())


# Commands
@bot.command("register")
async def start_registration(ctx):
    """Start registration wizard."""
    await ctx.scene_manager.enter("registration", ctx)


@bot.command("survey")
async def start_survey(ctx):
    """Start survey wizard."""
    await ctx.scene_manager.enter("survey", ctx)


@bot.start()
async def start(ctx):
    """Handle /start command."""
    welcome_text = """
🧙‍♂️ *Wizard Bot Example*

This bot demonstrates step-by-step wizards!

Available commands:
• /register - Start registration wizard (4 steps)
• /survey - Start quick survey (3 steps)
• /help - Show help

Try starting a wizard to see how it guides you through multiple steps!
    """
    await ctx.reply(welcome_text)


@bot.help()
async def help_cmd(ctx):
    """Handle /help command."""
    help_text = """
🧙‍♂️ *Wizard Bot Help*

This bot demonstrates wizard scenes for step-by-step conversations.

*Commands:*
• /start - Welcome message
• /register - Registration wizard (4 steps)
• /survey - Quick survey (3 steps)
• /help - This help message

*How Wizards Work:*
• Each wizard has multiple steps
• Follow the prompts for each step
• Your data is collected step by step
• Get a summary when complete

*Tips:*
• Answer each question as prompted
• Invalid inputs will ask you to retry
• Each step builds on the previous one
    """
    await ctx.reply(help_text)


# Show progress in wizards (removed the general message handler that was causing duplication)


if __name__ == "__main__":
    print("Starting Wizard Bot...")
    bot.launch()
