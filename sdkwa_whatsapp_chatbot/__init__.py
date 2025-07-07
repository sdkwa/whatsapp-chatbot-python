"""SDKWA WhatsApp Chatbot Library.

A Python chatbot library that provides a Telegraf-like interface for building
WhatsApp bots using the SDKWA WhatsApp API.
"""

from .whatsapp_bot import WhatsAppBot
from .composer import Composer
from .context import Context
from .session import session, MemorySessionStore
from .markup import Markup
from .extra import Extra
from . import scenes
from .scenes import BaseScene, Stage

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
