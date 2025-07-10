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
    
    # Additional fields for different message types
    location: Optional[Dict[str, Any]] = None
    contact: Optional[Dict[str, Any]] = None
    file_data: Optional[Dict[str, Any]] = None

    # Convenience methods for checking message types
    def is_text(self) -> bool:
        """Check if message is a text message."""
        return self.message_type in ["textMessage", "extendedTextMessage"] and bool(self.text)
    
    def is_quoted(self) -> bool:
        """Check if message is a quoted message."""
        return self.message_type == "quotedMessage"
    
    def is_image(self) -> bool:
        """Check if message is an image."""
        return self.message_type == "imageMessage"
    
    def is_video(self) -> bool:
        """Check if message is a video."""
        return self.message_type == "videoMessage"
    
    def is_audio(self) -> bool:
        """Check if message is an audio message."""
        return self.message_type == "audioMessage"
    
    def is_document(self) -> bool:
        """Check if message is a document."""
        return self.message_type == "documentMessage"
    
    def is_location(self) -> bool:
        """Check if message is a location."""
        return self.message_type == "locationMessage"
    
    def is_contact(self) -> bool:
        """Check if message is a contact."""
        return self.message_type == "contactMessage"
    
    def is_media(self) -> bool:
        """Check if message contains media (image, video, audio, document, or generic file)."""
        return self.message_type in ["imageMessage", "videoMessage", "audioMessage", "documentMessage", "fileMessage"]
    
    def is_file(self) -> bool:
        """Check if message is a generic file message."""
        return self.message_type == "fileMessage"
    
    def get_latitude(self) -> Optional[float]:
        """Get latitude from location message."""
        if self.location:
            return self.location.get("latitude")
        return None
    
    def get_longitude(self) -> Optional[float]:
        """Get longitude from location message."""
        if self.location:
            return self.location.get("longitude")
        return None


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
        if "messageData" in self.update and self.update.get("typeWebhook") == "incomingMessageReceived":
            message_data = self.update["messageData"]
            sender_data = self.update.get("senderData", {})
            message_type = message_data.get("typeMessage", "")

            # Parse text based on message type (following JavaScript example)
            text = None
            caption = None
            
            # Text messages
            if message_type == "textMessage":
                text = message_data.get("textMessageData", {}).get("textMessage")
            elif message_type == "quotedMessage":
                text = message_data.get("extendedTextMessageData", {}).get("text")
            elif message_type == "extendedTextMessage":
                text = message_data.get("extendedTextMessageData", {}).get("text")

            # Parse file data based on message type
            file_data = {}
            file_url = None
            file_name = None
            
            # Media messages (image, video, audio, document)
            if message_type in ["imageMessage", "audioMessage", "documentMessage", "videoMessage", "fileMessage"]:
                file_data = message_data.get("fileMessageData", {})
                file_url = file_data.get("downloadUrl")
                file_name = file_data.get("fileName")
                caption = file_data.get("caption")
                
                # For media messages, if there's no explicit text, use caption as text
                if not text and caption:
                    text = caption
            
            # Parse location data
            location_data = None
            if message_type == "locationMessage":
                location_data = message_data.get("locationMessageData", {})
            
            # Parse contact data
            contact_data = None
            if message_type == "contactMessage":
                contact_data = message_data.get("contactMessageData", {})

            # Handle quoted message data more robustly
            quoted_message_id = None
            quoted_message = message_data.get("quotedMessage")
            if quoted_message and isinstance(quoted_message, dict):
                quoted_message_id = quoted_message.get("idMessage")

            self.message = Message(
                message_id=message_data.get("idMessage", ""),
                chat_id=sender_data.get("chatId", ""),
                text=text,
                timestamp=self.update.get("timestamp"),
                sender_name=sender_data.get("senderName"),
                sender_phone=sender_data.get("sender"),
                message_type=message_type,
                file_url=file_url,
                file_name=file_name,
                caption=caption,
                quoted_message_id=quoted_message_id,
                raw_data=message_data,
                location=location_data,
                contact=contact_data,
                file_data=file_data if file_data else None,
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
