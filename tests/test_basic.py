"""Test basic functionality of the WhatsApp Chatbot library."""

import json
from unittest.mock import AsyncMock, Mock, patch

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

        # Test text message update (SDKWA format)
        update = {
            "typeWebhook": "incomingMessageReceived",
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
            "typeWebhook": "incomingMessageReceived",
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

    @pytest.mark.asyncio
    async def test_session_middleware(self):
        """Test session middleware functionality."""
        from sdkwa_whatsapp_chatbot.session import session
        
        store = MemorySessionStore()
        middleware = session(store)
        
        # Mock context
        bot_mock = Mock()
        api_client_mock = Mock()
        
        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Hello"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }
        
        from sdkwa_whatsapp_chatbot.context import Context
        ctx = Context(bot_mock, update, api_client_mock)
        
        # Apply middleware
        await middleware(ctx)
        
        # Verify session was added to context
        assert hasattr(ctx, "session")
        assert isinstance(ctx.session, dict)
        
        # Modify session
        ctx.session["test_key"] = "test_value"
        
        # Manually save the session (simulate end of processing)
        session_key = ctx.chat_id or "default"
        await store.set(session_key, ctx.session)
        
        # Create another context with same chat_id and apply middleware
        ctx2 = Context(bot_mock, update, api_client_mock)
        await middleware(ctx2)
        
        # Session should have the saved data since it's the same chat_id
        assert ctx2.session == {"test_key": "test_value"}

    @pytest.mark.asyncio
    async def test_session_with_custom_key_generator(self):
        """Test session middleware with custom key generator."""
        from sdkwa_whatsapp_chatbot.session import session
        
        store = MemorySessionStore()
        
        def custom_key_generator(ctx):
            return f"custom_{ctx.chat_id}"
        
        middleware = session(store, custom_key_generator)
        
        # Mock context
        bot_mock = Mock()
        api_client_mock = Mock()
        
        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Hello"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }
        
        from sdkwa_whatsapp_chatbot.context import Context
        ctx = Context(bot_mock, update, api_client_mock)
        
        # Apply middleware
        await middleware(ctx)
        
        # Verify session was added
        assert hasattr(ctx, "session")
        
        # Add some data to session
        ctx.session["user"] = "test_user"
        
        # Save session manually to test the key generator
        await store.set("custom_1234567890@c.us", ctx.session)
        
        # Create new context and apply middleware
        ctx2 = Context(bot_mock, update, api_client_mock)
        await middleware(ctx2)
        
        # Should get the session data we saved
        assert ctx2.session.get("user") == "test_user"


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

    def test_stage_middleware(self):
        """Test stage middleware functionality."""
        from sdkwa_whatsapp_chatbot.scenes import BaseScene, Stage
        
        # Create a simple scene
        test_scene = BaseScene("test_scene")
        stage = Stage([test_scene])
        
        middleware = stage.middleware()
        
        # Mock context
        bot_mock = Mock()
        api_client_mock = Mock()
        
        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Hello"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }
        
        from sdkwa_whatsapp_chatbot.context import Context
        ctx = Context(bot_mock, update, api_client_mock)
        ctx.session = {}
        
        # Apply middleware - this should add scene_manager to context
        import asyncio
        asyncio.run(middleware(ctx))
        
        # Verify scene_manager was added
        assert hasattr(ctx, "scene_manager")
        assert ctx.scene_manager == stage


class TestMessageTypes:
    """Test different message types in SDKWA format."""

    def test_file_message_parsing(self):
        """Test file message parsing."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "fileMessage",
                "fileMessageData": {
                    "downloadUrl": "https://example.com/file.pdf",
                    "fileName": "document.pdf",
                    "caption": "Important document",
                },
            },
            "senderData": {
                "chatId": "1234567890@c.us",
                "senderName": "John Doe",
                "sender": "1234567890",
            },
            "timestamp": 1640995200,
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.message.file_url == "https://example.com/file.pdf"
        assert ctx.message.file_name == "document.pdf"
        assert ctx.message.caption == "Important document"
        assert ctx.message.message_type == "fileMessage"
        assert ctx.update_type == "message"

    def test_quoted_message_parsing(self):
        """Test quoted message parsing."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "This is a reply"},
                "quotedMessage": {
                    "idMessage": "quoted123",
                    "textMessage": "Original message",
                },
            },
            "senderData": {
                "chatId": "1234567890@c.us",
                "senderName": "John Doe",
                "sender": "1234567890",
            },
            "timestamp": 1640995200,
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.message.text == "This is a reply"
        assert ctx.message.quoted_message_id == "quoted123"
        assert ctx.update_type == "message"

    def test_callback_query_parsing(self):
        """Test callback query parsing."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "callbackQuery": {
                "id": "callback123",
                "data": "button_data",
                "chatId": "1234567890@c.us",
            }
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.callback_query.id == "callback123"
        assert ctx.callback_query.data == "button_data"
        assert ctx.update_type == "callback_query"
        assert ctx.chat_id == "1234567890@c.us"

    def test_status_update_parsing(self):
        """Test status update parsing."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "status": "online",
            "chatId": "1234567890@c.us",
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.status == "online"
        assert ctx.update_type == "status"
        assert ctx.chat_id == "1234567890@c.us"

    def test_unknown_update_type(self):
        """Test unknown update type."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "unknownField": "unknown_value"
        }

        ctx = Context(bot_mock, update, api_client_mock)

        assert ctx.update_type == "unknown"
        assert ctx.chat_id == ""

    def test_context_properties(self):
        """Test context properties."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Hello"},
            },
            "senderData": {
                "chatId": "1234567890@c.us",
                "senderName": "John Doe",
                "sender": "1234567890",
            },
            "timestamp": 1640995200,
        }

        ctx = Context(bot_mock, update, api_client_mock)

        # Test from_user property
        from_user = ctx.from_user
        assert from_user["id"] == "1234567890"
        assert from_user["name"] == "John Doe"
        assert from_user["phone"] == "1234567890"

        # Test chat property
        chat = ctx.chat
        assert chat["id"] == "1234567890@c.us"
        assert chat["type"] == "private"

        # Test group chat
        update["senderData"]["chatId"] = "group123@g.us"
        ctx = Context(bot_mock, update, api_client_mock)
        chat = ctx.chat
        assert chat["type"] == "group"


class TestContextAsync:
    """Test async methods in Context class."""

    @pytest.mark.asyncio
    async def test_reply_method(self):
        """Test reply method."""
        bot_mock = Mock()
        api_client_mock = Mock()
        
        # Mock the async method properly using AsyncMock
        api_client_mock.send_message = AsyncMock(return_value={"messageId": "response123"})

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Hello"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }

        ctx = Context(bot_mock, update, api_client_mock)
        
        # Test reply
        result = await ctx.reply("Hello back!")
        
        assert result == {"messageId": "response123"}

    @pytest.mark.asyncio
    async def test_reply_with_photo(self):
        """Test reply_with_photo method."""
        bot_mock = Mock()
        api_client_mock = Mock()
        
        # Mock the async method properly using AsyncMock
        api_client_mock.send_file_by_url = AsyncMock(return_value={"messageId": "photo123"})

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Send photo"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }

        ctx = Context(bot_mock, update, api_client_mock)
        
        # Test reply with photo
        result = await ctx.reply_with_photo("https://example.com/photo.jpg", caption="Nice photo")
        
        assert result == {"messageId": "photo123"}

    @pytest.mark.asyncio
    async def test_reply_with_location(self):
        """Test reply_with_location method."""
        bot_mock = Mock()
        api_client_mock = Mock()
        
        # Mock the async method properly using AsyncMock
        api_client_mock.send_location = AsyncMock(return_value={"messageId": "location123"})

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Send location"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }

        ctx = Context(bot_mock, update, api_client_mock)
        
        # Test reply with location
        result = await ctx.reply_with_location(
            latitude=40.7128, longitude=-74.0060, name="New York", address="NY, USA"
        )
        
        assert result == {"messageId": "location123"}

    @pytest.mark.asyncio
    async def test_reply_with_contact(self):
        """Test reply_with_contact method."""
        bot_mock = Mock()
        api_client_mock = Mock()
        
        # Mock the async method properly using AsyncMock
        api_client_mock.send_contact = AsyncMock(return_value={"messageId": "contact123"})

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Send contact"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }

        ctx = Context(bot_mock, update, api_client_mock)
        
        # Test reply with contact
        result = await ctx.reply_with_contact(
            phone="1234567890",
            first_name="John",
            last_name="Doe",
            company="Acme Corp"
        )
        
        assert result == {"messageId": "contact123"}

    @pytest.mark.asyncio
    async def test_delete_message(self):
        """Test delete_message method."""
        bot_mock = Mock()
        api_client_mock = Mock()
        
        # Mock the async method properly using AsyncMock
        api_client_mock.delete_message = AsyncMock(return_value={"result": True})

        update = {
            "typeWebhook": "incomingMessageReceived",
            "messageData": {
                "idMessage": "msg123",
                "typeMessage": "textMessage",
                "textMessageData": {"textMessage": "Delete this"},
            },
            "senderData": {"chatId": "1234567890@c.us"},
        }

        ctx = Context(bot_mock, update, api_client_mock)
        
        # Test delete message
        result = await ctx.delete_message()
        
        assert result == {"result": True}

    @pytest.mark.asyncio
    async def test_reply_no_chat_id(self):
        """Test reply method without chat_id."""
        bot_mock = Mock()
        api_client_mock = Mock()

        update = {
            "unknownField": "unknown_value"
        }

        ctx = Context(bot_mock, update, api_client_mock)
        
        # Test reply without chat_id should raise ValueError
        with pytest.raises(ValueError, match="No chat_id available for reply"):
            await ctx.reply("Hello")


class TestBotUpdates:
    """Test bot update handling."""

    def test_get_updates(self):
        """Test get_updates method."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            # Mock receive_notification
            mock_client.receive_notification.return_value = {
                "receiptId": "receipt123",
                "body": {
                    "typeWebhook": "incomingMessageReceived",
                    "messageData": {
                        "idMessage": "msg123",
                        "typeMessage": "textMessage",
                        "textMessageData": {"textMessage": "Hello"},
                    },
                    "senderData": {"chatId": "1234567890@c.us"},
                }
            }
            
            bot = WhatsAppBot(config)
            
            # Test get_updates
            import asyncio
            updates = asyncio.run(bot.get_updates())
            
            assert len(updates) == 1
            assert updates[0]["typeWebhook"] == "incomingMessageReceived"
            
            # Verify delete_notification was called
            mock_client.delete_notification.assert_called_once_with("receipt123")

    def test_get_updates_no_notification(self):
        """Test get_updates with no notification."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            # Mock receive_notification returning None
            mock_client.receive_notification.return_value = None
            
            bot = WhatsAppBot(config)
            
            # Test get_updates
            import asyncio
            updates = asyncio.run(bot.get_updates())
            
            assert len(updates) == 0

    def test_get_updates_exception(self):
        """Test get_updates with exception."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            # Mock receive_notification raising an exception
            mock_client.receive_notification.side_effect = Exception("API Error")
            
            bot = WhatsAppBot(config)
            
            # Test get_updates
            import asyncio
            updates = asyncio.run(bot.get_updates())
            
            assert len(updates) == 0  # Should return empty list on exception


class TestIntegration:
    """Integration tests for the WhatsApp bot."""

    @pytest.mark.asyncio
    async def test_bot_handle_update_message(self):
        """Test bot handling a message update."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Add a simple text handler
            handled = False
            
            @bot.on("text")
            async def handle_text(ctx):
                nonlocal handled
                handled = True
                assert ctx.message.text == "Hello bot"
                assert ctx.message.chat_id == "1234567890@c.us"
                assert ctx.message.sender_name == "John Doe"
            
            # Create a test update
            update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg123",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "Hello bot"},
                },
                "senderData": {
                    "chatId": "1234567890@c.us",
                    "senderName": "John Doe",
                    "sender": "1234567890",
                },
                "timestamp": 1640995200,
            }
            
            # Handle the update
            await bot.handle_update(update)
            
            # Verify the handler was called
            assert handled

    @pytest.mark.asyncio
    async def test_bot_handle_update_command(self):
        """Test bot handling a command update."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Add a command handler
            handled = False
            
            @bot.command("start")
            async def handle_start(ctx):
                nonlocal handled
                handled = True
                assert ctx.get_command() == "start"
                assert ctx.get_command_args() == ["hello", "world"]
            
            # Create a test update
            update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg123",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "/start hello world"},
                },
                "senderData": {
                    "chatId": "1234567890@c.us",
                    "senderName": "John Doe",
                    "sender": "1234567890",
                },
                "timestamp": 1640995200,
            }
            
            # Handle the update
            await bot.handle_update(update)
            
            # Verify the handler was called
            assert handled

    @pytest.mark.asyncio
    async def test_bot_handle_update_with_session(self):
        """Test bot handling update with session."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Add session middleware with bot's store
            from sdkwa_whatsapp_chatbot.session import session
            bot.use(session(store=bot.session_manager.store))
            
            # Add a handler that uses session
            @bot.on("text")
            async def handle_text(ctx):
                ctx.session["counter"] = ctx.session.get("counter", 0) + 1
                assert ctx.session["counter"] > 0
            
            # Create a test update
            update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg123",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "Hello"},
                },
                "senderData": {
                    "chatId": "1234567890@c.us",
                    "senderName": "John Doe",
                    "sender": "1234567890",
                },
                "timestamp": 1640995200,
            }
            
            # Handle the update twice
            await bot.handle_update(update)
            await bot.handle_update(update)
            
            # Verify session persistence
            session_data = await bot.session_manager.get_session("1234567890@c.us")
            assert session_data["counter"] == 2

    def test_bot_error_handling(self):
        """Test bot error handling."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Add an error handler
            error_handled = False
            
            @bot.catch
            async def handle_error(error, ctx):
                nonlocal error_handled
                error_handled = True
                assert isinstance(error, ValueError)
                assert "test error" in str(error)
            
            # Add a handler that raises an error
            @bot.on("text")
            async def handle_text(ctx):
                raise ValueError("test error")
            
            # Create a test update
            update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg123",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "Hello"},
                },
                "senderData": {"chatId": "1234567890@c.us"},
            }
            
            # Handle the update
            import asyncio
            asyncio.run(bot.handle_update(update))
            
            # Verify error was handled
            assert error_handled


class TestWebhookFunctionality:
    """Test webhook-related functionality."""

    def test_set_webhook_url(self):
        """Test setting webhook URL."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Test setting webhook URL
            bot.set_webhook_url("https://example.com/webhook")
            
            # Verify set_settings was called with correct parameters
            mock_client.set_settings.assert_called_once_with({"webhookUrl": "https://example.com/webhook"})

    def test_webhook_callback(self):
        """Test webhook callback function."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Get webhook callback
            callback = bot.webhook_callback()
            
            # Test callback function
            test_data = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg123",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "Hello"},
                },
                "senderData": {"chatId": "1234567890@c.us"},
            }
            
            import asyncio
            result = asyncio.run(callback(test_data))
            
            assert result == {"status": "ok"}

    def test_flask_webhook_setup(self):
        """Test Flask webhook setup."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Test Flask webhook setup with Flask available
            mock_app = Mock()
            mock_app.route = Mock(return_value=lambda x: x)  # Mock decorator
            
            # This should not raise an error since Flask is available
            bot.flask_webhook(mock_app)
            
            # Verify the route was configured
            mock_app.route.assert_called_once_with("/webhook", methods=["POST"])

    def test_fastapi_webhook_setup(self):
        """Test FastAPI webhook setup."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Test FastAPI webhook setup with FastAPI available
            mock_app = Mock()
            mock_app.post = Mock(return_value=lambda x: x)  # Mock decorator
            
            # This should not raise an error since FastAPI is available
            bot.fastapi_webhook(mock_app)
            
            # Verify the route was configured
            mock_app.post.assert_called_once_with("/webhook")


class TestBotMethods:
    """Test additional bot methods."""

    def test_get_me(self):
        """Test get_me method."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Test get_me
            result = bot.get_me()
            
            expected = {
                "id": "test_instance",
                "is_bot": True,
                "first_name": "WhatsApp Bot",
                "username": "whatsapp_bot_test_instance",
            }
            
            assert result == expected

    @pytest.mark.asyncio
    async def test_bot_send_methods(self):
        """Test bot send methods."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            # Mock async methods
            mock_client.send_message.return_value = {"messageId": "msg123"}
            mock_client.send_file_by_url.return_value = {"messageId": "file123"}
            mock_client.send_location.return_value = {"messageId": "location123"}
            mock_client.send_contact.return_value = {"messageId": "contact123"}
            
            bot = WhatsAppBot(config)
            
            # Test send_message
            result = await bot.send_message("1234567890@c.us", "Hello")
            assert result == {"messageId": "msg123"}
            
            # Test send_photo
            result = await bot.send_photo("1234567890@c.us", "https://example.com/photo.jpg")
            assert result == {"messageId": "file123"}
            
            # Test send_location
            result = await bot.send_location("1234567890@c.us", 40.7128, -74.0060)
            assert result == {"messageId": "location123"}
            
            # Test send_contact
            result = await bot.send_contact("1234567890@c.us", "1234567890", "John")
            assert result == {"messageId": "contact123"}

    @pytest.mark.asyncio
    async def test_bot_account_methods(self):
        """Test bot account methods."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            # Mock methods
            mock_client.get_state_instance.return_value = {"stateInstance": "authorized"}
            mock_client.get_settings.return_value = {"webhookUrl": "https://example.com"}
            mock_client.set_settings.return_value = {"result": True}
            
            bot = WhatsAppBot(config)
            
            # Test get_account_info
            result = await bot.get_account_info()
            assert result == {"stateInstance": "authorized"}
            
            # Test get_settings
            result = await bot.get_settings()
            assert result == {"webhookUrl": "https://example.com"}
            
            # Test set_settings
            result = await bot.set_settings({"webhookUrl": "https://new.example.com"})
            assert result == {"result": True}


class TestComprehensive:
    """Comprehensive end-to-end tests."""

    @pytest.mark.asyncio
    async def test_full_message_flow(self):
        """Test complete message flow from SDKWA format to context handling."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Track what was handled
            handled_messages = []
            
            @bot.on("message")
            async def handle_message(ctx):
                if ctx.message.message_type == "textMessage" and ctx.message.text:
                    handled_messages.append({
                        "text": ctx.message.text,
                        "chat_id": ctx.message.chat_id,
                        "sender": ctx.message.sender_name,
                        "message_type": ctx.message.message_type,
                        "timestamp": ctx.message.timestamp
                    })
                elif ctx.message.message_type == "fileMessage":
                    handled_messages.append({
                        "file_url": ctx.message.file_url,
                        "file_name": ctx.message.file_name,
                        "caption": ctx.message.caption,
                        "chat_id": ctx.message.chat_id
                    })
            
            # Test different message types
            text_update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg1",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "Hello World!"},
                },
                "senderData": {
                    "chatId": "1234567890@c.us",
                    "senderName": "Alice",
                    "sender": "1234567890",
                },
                "timestamp": 1640995200,
            }
            
            file_update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "msg2",
                    "typeMessage": "fileMessage",
                    "fileMessageData": {
                        "downloadUrl": "https://example.com/doc.pdf",
                        "fileName": "document.pdf",
                        "caption": "Important file",
                    },
                },
                "senderData": {
                    "chatId": "1234567890@c.us",
                    "senderName": "Bob",
                    "sender": "1234567890",
                },
                "timestamp": 1640995300,
            }
            
            # Process the updates
            await bot.handle_update(text_update)
            await bot.handle_update(file_update)
            
            # Verify the messages were handled correctly
            assert len(handled_messages) == 2
            
            # Check text message
            text_msg = handled_messages[0]
            assert text_msg["text"] == "Hello World!"
            assert text_msg["chat_id"] == "1234567890@c.us"
            assert text_msg["sender"] == "Alice"
            assert text_msg["message_type"] == "textMessage"
            assert text_msg["timestamp"] == 1640995200
            
            # Check file message
            file_msg = handled_messages[1]
            assert file_msg["file_url"] == "https://example.com/doc.pdf"
            assert file_msg["file_name"] == "document.pdf"
            assert file_msg["caption"] == "Important file"
            assert file_msg["chat_id"] == "1234567890@c.us"

    @pytest.mark.asyncio
    async def test_command_handling_with_context(self):
        """Test command handling with full context."""
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client with reply capability
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            # Use AsyncMock for the async method
            mock_client.send_message = AsyncMock(side_effect=lambda **kwargs: {"messageId": f"response_{kwargs['chat_id']}"})
            
            bot = WhatsAppBot(config)
            
            # Track responses
            responses = []
            
            @bot.command("help")
            async def help_command(ctx):
                result = await ctx.reply("Here are the available commands...")
                responses.append(result)
            
            @bot.command("echo")
            async def echo_command(ctx):
                args = ctx.get_command_args()
                result = await ctx.reply(f"You said: {' '.join(args)}")
                responses.append(result)
            
            # Test help command
            help_update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "cmd1",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "/help"},
                },
                "senderData": {"chatId": "1234567890@c.us"},
            }
            
            # Test echo command with args
            echo_update = {
                "typeWebhook": "incomingMessageReceived",
                "messageData": {
                    "idMessage": "cmd2",
                    "typeMessage": "textMessage",
                    "textMessageData": {"textMessage": "/echo hello world"},
                },
                "senderData": {"chatId": "9876543210@c.us"},
            }
            
            # Process the commands
            await bot.handle_update(help_update)
            await bot.handle_update(echo_update)
            
            # Verify responses
            assert len(responses) == 2
            assert responses[0]["messageId"] == "response_1234567890@c.us"
            assert responses[1]["messageId"] == "response_9876543210@c.us"

    def test_sdkwa_format_compatibility(self):
        """Test that our context correctly parses SDKWA format."""
        bot_mock = Mock()
        api_client_mock = Mock()
        
        # Test various SDKWA message formats
        test_cases = [
            # Text message
            {
                "update": {
                    "typeWebhook": "incomingMessageReceived",
                    "messageData": {
                        "idMessage": "msg1",
                        "typeMessage": "textMessage",
                        "textMessageData": {"textMessage": "Test message"},
                    },
                    "senderData": {
                        "chatId": "1234567890@c.us",
                        "senderName": "Test User",
                        "sender": "1234567890",
                    },
                    "timestamp": 1640995200,
                },
                "expected_type": "message",
                "expected_text": "Test message",
                "expected_chat_id": "1234567890@c.us",
            },
            # File message
            {
                "update": {
                    "typeWebhook": "incomingMessageReceived",
                    "messageData": {
                        "idMessage": "msg2",
                        "typeMessage": "fileMessage",
                        "fileMessageData": {
                            "downloadUrl": "https://example.com/file.jpg",
                            "fileName": "photo.jpg",
                            "caption": "Nice photo",
                        },
                    },
                    "senderData": {"chatId": "1234567890@c.us"},
                },
                "expected_type": "message",
                "expected_file_url": "https://example.com/file.jpg",
                "expected_file_name": "photo.jpg",
                "expected_caption": "Nice photo",
            },
            # Status update
            {
                "update": {
                    "status": "typing",
                    "chatId": "1234567890@c.us",
                },
                "expected_type": "status",
                "expected_status": "typing",
            },
            # Unknown update
            {
                "update": {"unknown": "data"},
                "expected_type": "unknown",
                "expected_chat_id": "",
            },
        ]
        
        for case in test_cases:
            ctx = Context(bot_mock, case["update"], api_client_mock)
            
            # Check update type
            assert ctx.update_type == case["expected_type"]
            
            # Check specific fields based on update type
            if "expected_text" in case:
                assert ctx.message.text == case["expected_text"]
            if "expected_chat_id" in case:
                assert ctx.chat_id == case["expected_chat_id"]
            if "expected_file_url" in case:
                assert ctx.message.file_url == case["expected_file_url"]
            if "expected_file_name" in case:
                assert ctx.message.file_name == case["expected_file_name"]
            if "expected_caption" in case:
                assert ctx.message.caption == case["expected_caption"]
            if "expected_status" in case:
                assert ctx.status == case["expected_status"]


class TestSceneBotIntegration:
    """Integration test for scene bot functionality."""

    @pytest.mark.asyncio
    async def test_scene_bot_middleware_integration(self):
        """Test that scene bot middleware works correctly."""
        from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot
        from sdkwa_whatsapp_chatbot.session import session
        
        # Create bot with test config
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            # Mock the SDKWA client
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Mock the reply method to avoid API calls
            with patch("sdkwa_whatsapp_chatbot.context.Context.reply", new_callable=AsyncMock):
                # Create a test scene
                greeting_scene = BaseScene("greeting")
                
                @greeting_scene.enter()
                async def greeting_enter(ctx):
                    ctx.session["scene_entered"] = True
                    await ctx.reply("Hi! What's your name?")
                
                @greeting_scene.on("text")
                async def greeting_text(ctx):
                    name = ctx.message.text
                    ctx.session["user_name"] = name
                    await ctx.reply(f"Nice to meet you, {name}!")
                    await ctx.scene.leave_scene(ctx)
                
                @greeting_scene.leave()
                async def greeting_leave(ctx):
                    ctx.session["scene_left"] = True
                    await ctx.reply("Thanks for telling me your name!")
                
                # Create stage and setup middleware
                stage = Stage([greeting_scene])
                bot.use(session(store=bot.session_manager.store))
                bot.use(stage.middleware())
                
                # Add command to enter scene
                @bot.command("greeting")
                async def start_greeting(ctx):
                    await ctx.scene_manager.enter("greeting", ctx)
                
                # Test updates
                command_update = {
                    "typeWebhook": "incomingMessageReceived",
                    "messageData": {
                        "idMessage": "cmd1",
                        "typeMessage": "textMessage",
                        "textMessageData": {"textMessage": "/greeting"},
                    },
                    "senderData": {"chatId": "1234567890@c.us"},
                }
                
                text_update = {
                    "typeWebhook": "incomingMessageReceived",
                    "messageData": {
                        "idMessage": "msg1",
                        "typeMessage": "textMessage",
                        "textMessageData": {"textMessage": "John"},
                    },
                    "senderData": {"chatId": "1234567890@c.us"},
                }
                
                # Handle the command to enter scene
                await bot.handle_update(command_update)
                
                # Verify scene was entered
                session_data = await bot.session_manager.get_session("1234567890@c.us")
                assert session_data.get("scene_entered") is True
                assert "__scene" in session_data
                assert session_data["__scene"]["id"] == "greeting"
                
                # Handle text message in scene
                await bot.handle_update(text_update)
                
                # Verify scene processing
                session_data = await bot.session_manager.get_session("1234567890@c.us")
                assert session_data.get("user_name") == "John"
                assert session_data.get("scene_left") is True
                assert "__scene" not in session_data  # Scene should be left

    @pytest.mark.asyncio
    async def test_scene_bot_session_persistence(self):
        """Test that session data persists across multiple updates."""
        from sdkwa_whatsapp_chatbot import BaseScene, Stage, WhatsAppBot
        from sdkwa_whatsapp_chatbot.session import session
        
        config = {"idInstance": "test_instance", "apiTokenInstance": "test_token"}
        
        with patch("sdkwa_whatsapp_chatbot.whatsapp_bot.SDKWA") as mock_sdkwa:
            mock_client = Mock()
            mock_sdkwa.return_value = mock_client
            
            bot = WhatsAppBot(config)
            
            # Setup middleware
            bot.use(session(store=bot.session_manager.store))
            
            # Track session updates
            session_updates = []
            
            @bot.on("text")
            async def track_session(ctx):
                counter = ctx.session.get("counter", 0) + 1
                ctx.session["counter"] = counter
                session_updates.append(counter)
            
            # Create test updates
            updates = []
            for i in range(3):
                updates.append({
                    "typeWebhook": "incomingMessageReceived",
                    "messageData": {
                        "idMessage": f"msg{i}",
                        "typeMessage": "textMessage",
                        "textMessageData": {"textMessage": f"Message {i}"},
                    },
                    "senderData": {"chatId": "1234567890@c.us"},
                })
            
            # Process updates
            for update in updates:
                await bot.handle_update(update)
            
            # Verify session persistence
            assert session_updates == [1, 2, 3]
            
            # Verify final session state
            session_data = await bot.session_manager.get_session("1234567890@c.us")
            assert session_data["counter"] == 3
