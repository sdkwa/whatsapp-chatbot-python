#!/usr/bin/env python3
"""Wizard bot example with step-by-step user registration."""

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
async def step_name(ctx):
    """Step 1: Ask for name."""
    await ctx.reply("🚀 *Registration Wizard - Step 1/4*\n\nWhat's your full name?")


@registration_wizard.step
async def step_age(ctx):
    """Step 2: Ask for age."""
    name = ctx.message.text
    await ctx.wizard.next({"name": name})
    await ctx.reply(f"👋 Nice to meet you, {name}!\n\n*Step 2/4*\n\nHow old are you?")


@registration_wizard.step
async def step_email(ctx):
    """Step 3: Ask for email."""
    age_text = ctx.message.text

    # Validate age
    try:
        age = int(age_text)
        if age < 1 or age > 120:
            await ctx.reply("Please enter a valid age (1-120):")
            return  # Stay on same step
    except ValueError:
        await ctx.reply("Please enter a valid number for your age:")
        return  # Stay on same step

    await ctx.wizard.next({"age": age})
    await ctx.reply("📧 *Step 3/4*\n\nWhat's your email address?")


@registration_wizard.step
async def step_finish(ctx):
    """Final step: Complete registration."""
    email = ctx.message.text

    # Basic email validation
    if "@" not in email or "." not in email:
        await ctx.reply("Please enter a valid email address:")
        return  # Stay on same step

    await ctx.wizard.next({"email": email})

    # Get all collected data
    all_data = ctx.wizard.get_all_data()

    # Extract data from each step
    name = all_data.get(0, {}).get("name", "Unknown")
    age = all_data.get(1, {}).get("age", "Unknown")
    email = all_data.get(2, {}).get("email", "Unknown")

    # Save to session for later use
    ctx.session["user_profile"] = {
        "name": name,
        "age": age,
        "email": email,
        "registered_at": ctx.update.get("timestamp"),
    }

    # Show completion message
    completion_text = f"""
✅ *Registration Complete!*

Your profile:
👤 **Name:** {name}
🎂 **Age:** {age}
📧 **Email:** {email}

Welcome to our service! You can now use all features.

Use /profile to view your profile anytime.
    """

    await ctx.reply(completion_text)
    await ctx.wizard.complete()


# Create stage and register wizard
stage = Stage([registration_wizard])

# Setup middleware
bot.use(session())
bot.use(stage.middleware())


# Commands
@bot.command("register")
async def start_registration(ctx):
    """Start registration wizard."""
    if "user_profile" in ctx.session:
        await ctx.reply("You're already registered! Use /profile to view your details.")
    else:
        await ctx.scene_manager.enter("registration", ctx)


@bot.command("profile")
async def show_profile(ctx):
    """Show user profile."""
    profile = ctx.session.get("user_profile")
    if not profile:
        await ctx.reply(
            "You haven't registered yet! Use /register to create your profile."
        )
        return

    profile_text = f"""
👤 *Your Profile*

**Name:** {profile['name']}
**Age:** {profile['age']}
**Email:** {profile['email']}

Use /register to update your profile.
    """

    await ctx.reply(profile_text)


@bot.start()
async def start(ctx):
    """Handle /start command."""
    welcome_text = """
🎭 *Welcome to Wizard Bot!*

This bot demonstrates step-by-step wizards:

**Available Commands:**
• 📝 /register - User registration wizard
• 👤 /profile - View your profile
• ❓ /help - Show help

Try /register to see a step-by-step wizard in action!
    """

    await ctx.reply(welcome_text)


@bot.help()
async def help_cmd(ctx):
    """Handle /help command."""
    help_text = """
🎭 *Wizard Bot Help*

This bot demonstrates conversation wizards - step-by-step flows.

**Commands:**
• /register - Complete registration (4 steps)
• /profile - View your registration data
• /help - This help message

**Features:**
• ✅ Step validation and error handling
• 💾 Data collection and storage
• 🔄 Session persistence

Try /register to see a complete wizard in action!
    """

    await ctx.reply(help_text)


if __name__ == "__main__":
    print("Starting Wizard Bot...")
    bot.launch()
