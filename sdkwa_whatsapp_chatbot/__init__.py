"""SDKWA WhatsApp Chatbot Library.

A Python chatbot library that provides a Telegraf-like interface for building
WhatsApp bots using the SDKWA WhatsApp API.
"""

from . import scenes
from .composer import Composer
from .context import Context
from .extra import Extra
from .markup import Markup
from .scenes import BaseScene, Stage
from .session import MemorySessionStore, session
from .whatsapp_bot import WhatsAppBot

__version__ = "1.0.0"
__all__ = [
    "WhatsAppBot",
    "Composer",
    "Context",
    "session",
    "MemorySessionStore",
    "Markup",
    "Extra",
    "scenes",
    "BaseScene",
    "Stage",
]
