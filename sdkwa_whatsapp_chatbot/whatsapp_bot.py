"""Main WhatsApp Bot implementation."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union

from sdkwa import SDKWA

from .composer import Composer
from .context import Context
from .session import SessionManager

logger = logging.getLogger(__name__)


class WhatsAppBot(Composer):
    """WhatsApp Bot with Telegraf-like interface using SDKWA API."""

    def __init__(
        self,
        config: Union[Dict[str, Any], str],
        session_manager: Optional[SessionManager] = None,
        **kwargs,
    ):
        """
        Initialize WhatsApp Bot.

        Args:
            config: Bot configuration (dict or JSON string)
            session_manager: Session manager instance
            **kwargs: Additional options
        """
        super().__init__()

        # Parse configuration
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON configuration string")

        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary or JSON string")

        # Validate required configuration
        required_fields = ["idInstance", "apiTokenInstance"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required configuration field: {field}")

        self.config = config
        self.session_manager = session_manager or SessionManager()

        # Initialize SDKWA client
        self.api_client = SDKWA(
            id_instance=config["idInstance"],
            api_token_instance=config["apiTokenInstance"],
            api_host=config.get("apiUrl", "https://api.sdkwa.pro"),
        )

        # Bot state
        self.is_polling = False
        self.polling_task: Optional[asyncio.Task] = None
        self.error_handler: Optional[Callable] = None
        self.middleware_stack: List[Callable] = []

        # Default options
        self.options = {
            "polling_interval": kwargs.get("polling_interval", 1),
            "max_retries": kwargs.get("max_retries", 3),
            "retry_delay": kwargs.get("retry_delay", 5),
            **kwargs,
        }

        logger.info(f"WhatsApp Bot initialized for instance: {config['idInstance']}")

    def catch(self, handler: Callable[[Exception, Context], Any]) -> WhatsAppBot:
        """Set error handler."""
        self.error_handler = handler
        return self

    async def handle_update(self, update: Dict[str, Any]) -> None:
        """Handle incoming update."""
        try:
            # Create context
            ctx = Context(self, update, self.api_client)
                
            # Process through middleware and handlers
            if self.handler:
                if asyncio.iscoroutinefunction(self.handler):
                    await self.handler(ctx)
                else:
                    self.handler(ctx)

            # Save session if middleware provided one and we have a chat_id
            if hasattr(ctx, 'session') and hasattr(ctx, 'chat_id') and ctx.chat_id:
                session_key = ctx.chat_id or "default"
                await self.session_manager.set_session(session_key, ctx.session)

        except Exception as e:
            if self.error_handler:
                try:
                    if asyncio.iscoroutinefunction(self.error_handler):
                        await self.error_handler(e, ctx if "ctx" in locals() else None)
                    else:
                        self.error_handler(e, ctx if "ctx" in locals() else None)
                except Exception as handler_error:
                    logger.error(f"Error in error handler: {handler_error}")
            else:
                logger.error(f"Unhandled error: {e}")
                
            # Still try to save session even if there was an error
            if "ctx" in locals() and hasattr(ctx, 'session') and hasattr(ctx, 'chat_id') and ctx.chat_id:
                session_key = ctx.chat_id or "default"
                await self.session_manager.set_session(session_key, ctx.session)

    async def get_updates(self) -> List[Dict[str, Any]]:
        """Get updates from SDKWA API."""
        try:
            # Get notifications
            notification = self.api_client.receive_notification()

            if notification:
                # Delete notification after receiving
                receipt_id = notification.get("receiptId")
                if receipt_id:
                    self.api_client.delete_notification(receipt_id)

                return [notification.get("body", {})] 
            return []

        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    async def start_polling(self) -> None:
        """Start polling for updates."""
        if self.is_polling:
            logger.warning("Bot is already polling")
            return

        self.is_polling = True
        logger.info("Starting WhatsApp bot polling...")

        try:
            while self.is_polling:
                try:
                    # Get updates
                    updates = await self.get_updates()

                    # Process each update
                    for update in updates:
                        await self.handle_update(update)

                    # Wait before next poll
                    await asyncio.sleep(self.options["polling_interval"])

                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    await asyncio.sleep(self.options["retry_delay"])

        except asyncio.CancelledError:
            logger.info("Polling cancelled")
        except Exception as e:
            logger.error(f"Fatal error in polling: {e}")
        finally:
            self.is_polling = False
            logger.info("Polling stopped")

    def launch(self, **kwargs) -> None:
        """Launch the bot (start polling)."""
        if kwargs:
            self.options.update(kwargs)

        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error launching bot: {e}")

    async def launch_async(self, **kwargs) -> None:
        """Launch the bot asynchronously."""
        if kwargs:
            self.options.update(kwargs)

        self.polling_task = asyncio.create_task(self.start_polling())
        await self.polling_task

    def stop(self) -> None:
        """Stop the bot."""
        self.is_polling = False
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
        logger.info("Bot stop requested")

    async def send_message(self, chat_id: str, text: str, **kwargs) -> Dict[str, Any]:
        """Send a text message."""
        return self.api_client.send_message(chat_id=chat_id, message=text, **kwargs)

    async def send_photo(
        self, chat_id: str, photo_url: str, caption: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Send a photo."""
        return self.api_client.send_file_by_url(
            chat_id=chat_id,
            url_file=photo_url,
            file_name=kwargs.get("file_name", "photo.jpg"),
            caption=caption,
            **kwargs,
        )

    async def send_document(
        self, chat_id: str, document_url: str, caption: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Send a document."""
        return self.api_client.send_file_by_url(
            chat_id=chat_id,
            url_file=document_url,
            file_name=kwargs.get("file_name", "document"),
            caption=caption,
            **kwargs,
        )

    async def send_audio(
        self, chat_id: str, audio_url: str, caption: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Send an audio file."""
        return self.api_client.send_file_by_url(
            chat_id=chat_id,
            url_file=audio_url,
            file_name=kwargs.get("file_name", "audio.mp3"),
            caption=caption,
            **kwargs,
        )

    async def send_location(
        self,
        chat_id: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a location."""
        return self.api_client.send_location(
            chat_id=chat_id,
            latitude=latitude,
            longitude=longitude,
            name_location=name or "Location",
            address=address or "",
        )

    async def send_contact(
        self,
        chat_id: str,
        phone: str,
        first_name: str,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a contact."""
        contact_data = {"phoneContact": phone, "firstName": first_name}

        if last_name:
            contact_data["lastName"] = last_name
        if company:
            contact_data["company"] = company

        return self.api_client.send_contact(chat_id=chat_id, contact=contact_data)

    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        return self.api_client.get_state_instance()

    async def get_settings(self) -> Dict[str, Any]:
        """Get account settings."""
        return self.api_client.get_settings()

    async def set_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update account settings."""
        return self.api_client.set_settings(settings)

    def set_webhook_url(self, webhook_url: str) -> None:
        """Set webhook URL."""
        self.api_client.set_settings({"webhookUrl": webhook_url})

    def get_me(self) -> Dict[str, Any]:
        """Get bot information."""
        return {
            "id": self.config["idInstance"],
            "is_bot": True,
            "first_name": "WhatsApp Bot",
            "username": f"whatsapp_bot_{self.config['idInstance']}",
        }

    def webhook_callback(self, path: str = "/webhook") -> Callable:
        """Create webhook callback function for web frameworks."""

        async def callback(request_data: Dict[str, Any]) -> Dict[str, str]:
            await self.handle_update(request_data)
            return {"status": "ok"}

        return callback

    def flask_webhook(self, app, path: str = "/webhook") -> None:
        """Set up Flask webhook endpoint."""
        try:
            from flask import jsonify, request

            @app.route(path, methods=["POST"])
            def webhook():
                asyncio.create_task(self.handle_update(request.json))
                return jsonify({"status": "ok"})

        except ImportError:
            raise ImportError(
                "Flask is required for flask_webhook. Install with: pip install flask"
            )

    def fastapi_webhook(self, app, path: str = "/webhook") -> None:
        """Set up FastAPI webhook endpoint."""
        try:
            from fastapi import Request

            @app.post(path)
            async def webhook(request: Request):
                data = await request.json()
                await self.handle_update(data)
                return {"status": "ok"}

        except ImportError:
            raise ImportError(
                "FastAPI is required for fastapi_webhook. Install with: pip install fastapi"
            )


# Alias for backward compatibility
Telegraf = WhatsAppBot
