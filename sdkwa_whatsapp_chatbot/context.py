"""Context module for WhatsApp bot interactions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from .scenes.base import BaseScene
    from .whatsapp_bot import WhatsAppBot


@dataclass
class Message:
    """Represents a WhatsApp message."""

    message_id: str
    chat_id: str
    text: Optional[str] = None
    timestamp: Optional[int] = None
    sender_name: Optional[str] = None
    sender_phone: Optional[str] = None
    message_type: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    caption: Optional[str] = None
    quoted_message_id: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CallbackQuery:
    """Represents a callback query."""

    id: str
    data: str
    message: Optional[Message] = None


class Context:
    """Context object for WhatsApp bot interactions."""

    def __init__(self, bot: WhatsAppBot, update: Dict[str, Any], api_client: Any):
        """Initialize context with bot, update data, and API client."""
        self.bot = bot
        self.update = update
        self.api_client = api_client
        self.state: Dict[str, Any] = {}
        self.session: Dict[str, Any] = {}
        self.scene: Optional[BaseScene] = None
        self.match: Optional[re.Match] = None

        # Parse update data
        self._parse_update()

    def _parse_update(self) -> None:
        """Parse update data into context properties."""
        # Handle incoming message
        if "messageData" in self.update:
            message_data = self.update["messageData"]
            sender_data = self.update.get("senderData", {})

            self.message = Message(
                message_id=message_data.get("idMessage", ""),
                chat_id=sender_data.get("chatId", ""),
                text=message_data.get("textMessageData", {}).get("textMessage"),
                timestamp=self.update.get("timestamp"),
                sender_name=sender_data.get("senderName"),
                sender_phone=sender_data.get("sender"),
                message_type=message_data.get("typeMessage"),
                file_url=message_data.get("fileMessageData", {}).get("downloadUrl"),
                file_name=message_data.get("fileMessageData", {}).get("fileName"),
                caption=message_data.get("fileMessageData", {}).get("caption"),
                quoted_message_id=message_data.get("quotedMessage", {}).get(
                    "idMessage"
                ),
                raw_data=message_data,
            )

            self.update_type = "message"
            self.chat_id = self.message.chat_id

        # Handle callback query (for inline keyboards)
        elif "callbackQuery" in self.update:
            callback_data = self.update["callbackQuery"]
            self.callback_query = CallbackQuery(
                id=callback_data.get("id", ""),
                data=callback_data.get("data", ""),
                message=None,  # TODO: Parse message if available
            )
            self.update_type = "callback_query"
            self.chat_id = callback_data.get("chatId", "")

        # Handle status update
        elif "status" in self.update:
            self.update_type = "status"
            self.status = self.update["status"]
            self.chat_id = self.update.get("chatId", "")

        else:
            self.update_type = "unknown"
            self.chat_id = ""

    @property
    def from_user(self) -> Optional[Dict[str, Any]]:
        """Get sender information."""
        if hasattr(self, "message") and self.message:
            return {
                "id": self.message.sender_phone,
                "name": self.message.sender_name,
                "phone": self.message.sender_phone,
            }
        return None

    @property
    def chat(self) -> Optional[Dict[str, Any]]:
        """Get chat information."""
        if self.chat_id:
            return {
                "id": self.chat_id,
                "type": "private" if "@c.us" in self.chat_id else "group",
            }
        return None

    async def reply(self, text: str, **kwargs) -> Dict[str, Any]:
        """Reply to the current message."""
        if not self.chat_id:
            raise ValueError("No chat_id available for reply")

        return await self.api_client.send_message(
            chat_id=self.chat_id, message=text, **kwargs
        )

    async def reply_with_photo(
        self, photo_url: str, caption: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Reply with a photo."""
        if not self.chat_id:
            raise ValueError("No chat_id available for reply")

        return await self.api_client.send_file_by_url(
            chat_id=self.chat_id,
            url_file=photo_url,
            file_name=kwargs.get("file_name", "photo.jpg"),
            caption=caption,
            **kwargs,
        )

    async def reply_with_document(
        self, document_url: str, caption: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Reply with a document."""
        if not self.chat_id:
            raise ValueError("No chat_id available for reply")

        return await self.api_client.send_file_by_url(
            chat_id=self.chat_id,
            url_file=document_url,
            file_name=kwargs.get("file_name", "document"),
            caption=caption,
            **kwargs,
        )

    async def reply_with_audio(
        self, audio_url: str, caption: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Reply with an audio file."""
        if not self.chat_id:
            raise ValueError("No chat_id available for reply")

        return await self.api_client.send_file_by_url(
            chat_id=self.chat_id,
            url_file=audio_url,
            file_name=kwargs.get("file_name", "audio.mp3"),
            caption=caption,
            **kwargs,
        )

    async def reply_with_location(
        self,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reply with a location."""
        if not self.chat_id:
            raise ValueError("No chat_id available for reply")

        return await self.api_client.send_location(
            chat_id=self.chat_id,
            latitude=latitude,
            longitude=longitude,
            name_location=name or "Location",
            address=address or "",
        )

    async def reply_with_contact(
        self,
        phone: str,
        first_name: str,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reply with a contact."""
        if not self.chat_id:
            raise ValueError("No chat_id available for reply")

        contact_data = {"phoneContact": phone, "firstName": first_name}

        if last_name:
            contact_data["lastName"] = last_name
        if company:
            contact_data["company"] = company

        return await self.api_client.send_contact(
            chat_id=self.chat_id, contact=contact_data
        )

    async def answer_callback_query(
        self, text: Optional[str] = None, show_alert: bool = False
    ) -> Dict[str, Any]:
        """Answer a callback query."""
        if not hasattr(self, "callback_query"):
            raise ValueError("No callback query to answer")

        # Note: This might need to be implemented based on SDKWA API capabilities
        return {"ok": True}

    async def edit_message_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Edit message text."""
        # Note: This might need to be implemented based on SDKWA API capabilities
        return {"ok": True}

    async def delete_message(self, message_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a message."""
        if not self.chat_id:
            raise ValueError("No chat_id available")

        msg_id = message_id or (
            self.message.message_id
            if hasattr(self, "message") and self.message
            else None
        )
        if not msg_id:
            raise ValueError("No message_id available")

        return await self.api_client.delete_message(
            chat_id=self.chat_id, id_message=msg_id
        )

    async def forward_message(
        self, to_chat_id: str, message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Forward a message."""
        msg_id = message_id or (
            self.message.message_id
            if hasattr(self, "message") and self.message
            else None
        )
        if not msg_id:
            raise ValueError("No message_id available")

        # Note: This might need to be implemented based on SDKWA API capabilities
        return {"ok": True}

    def get_command_args(self) -> List[str]:
        """Get command arguments."""
        if (
            hasattr(self, "message")
            and self.message
            and self.message.text
            and self.message.text.startswith("/")
        ):
            parts = self.message.text.split()[1:]
            return parts
        return []

    def get_command(self) -> Optional[str]:
        """Get the command name."""
        if (
            hasattr(self, "message")
            and self.message
            and self.message.text
            and self.message.text.startswith("/")
        ):
            command = self.message.text[1:].split()[0].lower()
            return command
        return None
