"""Test basic functionality of the WhatsApp Chatbot library."""

import json
from unittest.mock import Mock, patch

import pytest

from sdkwa_whatsapp_chatbot import BaseScene, Context, Stage, WhatsAppBot
from sdkwa_whatsapp_chatbot.session import MemorySessionStore


class TestWhatsAppBot:
    """Test WhatsAppBot class."""

    def test_bot_creation_with_dict(self):
        """Test bot creation with dictionary config."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}

        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA"):
            bot = WhatsAppBot(config)
            assert bot.config == config

    def test_bot_creation_with_json_string(self):
        """Test bot creation with JSON string config."""
        config_dict = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        config_json = json.dumps(config_dict)

        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA"):
            bot = WhatsAppBot(config_json)
            assert bot.config == config_dict

    def test_bot_creation_invalid_config(self):
        """Test bot creation with invalid config."""
        with pytest.raises(ValueError, match="Missing required configuration field"):
            with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA"):
                WhatsAppBot({"idInstance": "test"})  # Missing apiTokenInstance

    def test_bot_event_handlers(self):
        """Test adding event handlers."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}

        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA"):
            bot = WhatsAppBot(config)

            # Test adding handlers
            @bot.on("text")
            def text_handler(ctx):
                pass

            @bot.command("start")
            def start_handler(ctx):
                pass

            assert bot.handler is not None


class TestContext:
    """Test Context class."""

    def test_context_creation(self):
        """Test context creation and message parsing."""
        bot_mock = Mock()
        api_client_mock = Mock()

        # Test text message update
        update = {
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Hello world"},
            },
            "senderData": {
                "chatId": "1234567890@c.us",
                "senderName": "John Doe",
                "sender": "1234567890",
            },
            "timestamp": 1640995200,
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.message.text == "Hello world"
        assert ctx.message.chat_id == "1234567890@c.us"
        assert ctx.message.sender_name == "John Doe"
        assert ctx.update_type == "message"

    def test_command_parsing(self):
        """Test command parsing."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "/start hello world"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.get_command() == "start"
        assert ctx.get_command_args() == ["hello", "world"]


class TestSession:
    """Test session functionality."""

    def test_memory_session_store(self):
        """Test memory session store."""
        store = MemorySessionStore()

        # Test async methods (run in sync for testing)
        import asyncio

        async def test_store():
            # Test set and get
            await store.set("test_key", {"count": 1})
            data = await store.get("test_key")
            assert data == {"count": 1}

            # Test delete
            await store.delete("test_key")
            data = await store.get("test_key")
            assert data == {}

        asyncio.run(test_store())


class TestScenes:
    """Test scene functionality."""

    def test_base_scene_creation(self):
        """Test BaseScene creation."""
        scene = BaseScene("test_scene")
        assert scene.scene_id == "test_scene"
        assert scene.enter_handlers == []
        assert scene.leave_handlers == []

    def test_scene_handlers(self):
        """Test adding scene handlers."""
        scene = BaseScene("test_scene")

        @scene.enter()
        def enter_handler(ctx):
            pass

        @scene.leave()
        def leave_handler(ctx):
            pass

        @scene.on("text")
        def text_handler(ctx):
            pass

        assert len(scene.enter_handlers) == 1
        assert len(scene.leave_handlers) == 1
        assert scene.handler is not None

    def test_stage_creation(self):
        """Test Stage creation."""
        scene1 = BaseScene("scene1")
        scene2 = BaseScene("scene2")

        stage = Stage([scene1, scene2])

        assert "scene1" in stage.scenes
        assert "scene2" in stage.scenes
        assert stage.get_scene("scene1") == scene1
