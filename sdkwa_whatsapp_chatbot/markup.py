"""Markup module for creating inline keyboards and reply markups."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class InlineKeyboardButton:
    """Represents an inline keyboard button."""

    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"text": self.text}

        if self.callback_data:
            result["callback_data"] = self.callback_data
        elif self.url:
            result["url"] = self.url

        return result


@dataclass
class KeyboardButton:
    """Represents a keyboard button."""

    text: str
    request_contact: bool = False
    request_location: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"text": self.text}

        if self.request_contact:
            result["request_contact"] = True

        if self.request_location:
            result["request_location"] = True

        return result


@dataclass
class InlineKeyboard:
    """Represents an inline keyboard."""

    keyboard: List[List[InlineKeyboardButton]] = field(default_factory=list)

    def add_row(self, *buttons: InlineKeyboardButton) -> InlineKeyboard:
        """Add a row of buttons."""
        self.keyboard.append(list(buttons))
        return self

    def add_button(
        self, text: str, callback_data: Optional[str] = None, url: Optional[str] = None
    ) -> InlineKeyboard:
        """Add a button to the last row (or create new row if empty)."""
        button = InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

        if not self.keyboard:
            self.keyboard.append([])

        self.keyboard[-1].append(button)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row] for row in self.keyboard
            ]
        }


@dataclass
class ReplyKeyboard:
    """Represents a reply keyboard."""

    keyboard: List[List[KeyboardButton]] = field(default_factory=list)
    one_time_keyboard: bool = False
    resize_keyboard: bool = True
    selective: bool = False

    def add_row(self, *buttons: KeyboardButton) -> ReplyKeyboard:
        """Add a row of buttons."""
        self.keyboard.append(list(buttons))
        return self

    def add_button(
        self, text: str, request_contact: bool = False, request_location: bool = False
    ) -> ReplyKeyboard:
        """Add a button to the last row (or create new row if empty)."""
        button = KeyboardButton(
            text=text,
            request_contact=request_contact,
            request_location=request_location,
        )

        if not self.keyboard:
            self.keyboard.append([])

        self.keyboard[-1].append(button)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "keyboard": [[button.to_dict() for button in row] for row in self.keyboard],
            "one_time_keyboard": self.one_time_keyboard,
            "resize_keyboard": self.resize_keyboard,
            "selective": self.selective,
        }


class RemoveKeyboard:
    """Represents keyboard removal."""

    def __init__(self, selective: bool = False):
        """Initialize keyboard removal."""
        self.selective = selective

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"remove_keyboard": True, "selective": self.selective}


class ForceReply:
    """Represents force reply."""

    def __init__(self, selective: bool = False):
        """Initialize force reply."""
        self.selective = selective

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {"force_reply": True, "selective": self.selective}


class Markup:
    """Factory class for creating markups."""

    @staticmethod
    def inline_keyboard(
        keyboard: Optional[List[List[InlineKeyboardButton]]] = None,
    ) -> InlineKeyboard:
        """Create an inline keyboard."""
        if keyboard is None:
            return InlineKeyboard()
        return InlineKeyboard(keyboard=keyboard)

    @staticmethod
    def keyboard(
        keyboard: Optional[List[List[KeyboardButton]]] = None, **kwargs
    ) -> ReplyKeyboard:
        """Create a reply keyboard."""
        if keyboard is None:
            return ReplyKeyboard(**kwargs)
        return ReplyKeyboard(keyboard=keyboard, **kwargs)

    @staticmethod
    def remove_keyboard(selective: bool = False) -> RemoveKeyboard:
        """Create keyboard removal markup."""
        return RemoveKeyboard(selective=selective)

    @staticmethod
    def force_reply(selective: bool = False) -> ForceReply:
        """Create force reply markup."""
        return ForceReply(selective=selective)

    @staticmethod
    def button(
        text: str, callback_data: Optional[str] = None, url: Optional[str] = None
    ) -> InlineKeyboardButton:
        """Create an inline keyboard button."""
        return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

    @staticmethod
    def keyboard_button(
        text: str, request_contact: bool = False, request_location: bool = False
    ) -> KeyboardButton:
        """Create a keyboard button."""
        return KeyboardButton(
            text=text,
            request_contact=request_contact,
            request_location=request_location,
        )

    @staticmethod
    def url_button(text: str, url: str) -> InlineKeyboardButton:
        """Create a URL button."""
        return InlineKeyboardButton(text=text, url=url)

    @staticmethod
    def callback_button(text: str, callback_data: str) -> InlineKeyboardButton:
        """Create a callback button."""
        return InlineKeyboardButton(text=text, callback_data=callback_data)

    @staticmethod
    def contact_button(text: str) -> KeyboardButton:
        """Create a contact request button."""
        return KeyboardButton(text=text, request_contact=True)

    @staticmethod
    def location_button(text: str) -> KeyboardButton:
        """Create a location request button."""
        return KeyboardButton(text=text, request_location=True)

    @staticmethod
    def quick_reply(buttons: List[str], **kwargs) -> ReplyKeyboard:
        """Create a quick reply keyboard with text buttons."""
        keyboard = ReplyKeyboard(**kwargs)
        for button_text in buttons:
            keyboard.add_row(KeyboardButton(text=button_text))
        return keyboard

    @staticmethod
    def inline_menu(buttons: List[tuple], columns: int = 1) -> InlineKeyboard:
        """
        Create an inline menu with specified layout.

        Args:
            buttons: List of (text, callback_data) or (text, url) tuples
            columns: Number of columns for button layout
        """
        keyboard = InlineKeyboard()

        for i in range(0, len(buttons), columns):
            row_buttons = []
            for j in range(columns):
                if i + j < len(buttons):
                    button_data = buttons[i + j]
                    if len(button_data) == 2:
                        text, data = button_data
                        if data.startswith("http"):
                            row_buttons.append(
                                InlineKeyboardButton(text=text, url=data)
                            )
                        else:
                            row_buttons.append(
                                InlineKeyboardButton(text=text, callback_data=data)
                            )

            if row_buttons:
                keyboard.add_row(*row_buttons)

        return keyboard


# Convenience functions
def inline_keyboard() -> InlineKeyboard:
    """Create an empty inline keyboard."""
    return Markup.inline_keyboard()


def keyboard(**kwargs) -> ReplyKeyboard:
    """Create an empty reply keyboard."""
    return Markup.keyboard(**kwargs)


def button(text: str, callback_data: str) -> InlineKeyboardButton:
    """Create a callback button."""
    return Markup.callback_button(text, callback_data)


def url_button(text: str, url: str) -> InlineKeyboardButton:
    """Create a URL button."""
    return Markup.url_button(text, url)
