"""Composer module for building middleware and handlers."""

from __future__ import annotations

import asyncio
import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Pattern, Union

from .context import Context

Handler = Callable[[Context], Any]
Middleware = Callable[[Context, Callable], Any]
FilterPredicate = Callable[[Context], bool]


class Composer:
    """Base class for composing middleware and handlers."""

    def __init__(self, *handlers: Handler):
        """Initialize composer with handlers."""
        self.handler = self.compose(*handlers) if handlers else None

    def use(self, *middlewares: Union[Handler, Middleware]) -> Composer:
        """Add middleware to the composer."""
        if self.handler:
            self.handler = self.compose(self.handler, *middlewares)
        else:
            self.handler = self.compose(*middlewares)
        return self

    def on(self, update_types: Union[str, List[str]], *handlers: Handler):
        """Listen for specific update types."""
        if handlers:
            # If handlers are provided, add them and return self
            return self.use(self.mount(update_types, *handlers))
        else:
            # If no handlers, return a decorator
            def decorator(handler: Handler):
                self.use(self.mount(update_types, handler))
                return handler

            return decorator

    def hears(
        self,
        triggers: Union[str, Pattern, List[Union[str, Pattern]]],
        *handlers: Handler,
    ):
        """Listen for text messages matching patterns."""
        if handlers:
            return self.use(self.hears_middleware(triggers, *handlers))
        else:

            def decorator(handler: Handler):
                self.use(self.hears_middleware(triggers, handler))
                return handler

            return decorator

    def command(self, commands: Union[str, List[str]], *handlers: Handler):
        """Listen for specific commands."""
        if handlers:
            return self.use(self.command_middleware(commands, *handlers))
        else:

            def decorator(handler: Handler):
                self.use(self.command_middleware(commands, handler))
                return handler

            return decorator

    def action(self, triggers: Union[str, List[str]], *handlers: Handler):
        """Listen for callback query actions."""
        if handlers:
            return self.use(self.action_middleware(triggers, *handlers))
        else:

            def decorator(handler: Handler):
                self.use(self.action_middleware(triggers, handler))
                return handler

            return decorator

    def start(self, *handlers: Handler):
        """Listen for /start command."""
        if handlers:
            return self.command("start", *handlers)
        else:

            def decorator(handler: Handler):
                self.command("start", handler)
                return handler

            return decorator

    def help(self, *handlers: Handler):
        """Listen for /help command."""
        if handlers:
            return self.command("help", *handlers)
        else:

            def decorator(handler: Handler):
                self.command("help", handler)
                return handler

            return decorator

    def filter(self, predicate: FilterPredicate) -> Composer:
        """Filter updates based on predicate."""
        return self.use(self.filter_middleware(predicate))

    def drop(self, predicate: FilterPredicate) -> Composer:
        """Drop updates based on predicate."""
        return self.use(self.drop_middleware(predicate))
        """Drop updates based on predicate."""
        return self.filter(lambda ctx: not predicate(ctx))

    @staticmethod
    def compose(*handlers: Handler) -> Optional[Handler]:
        """Compose multiple handlers into one."""
        if not handlers:
            return None

        if len(handlers) == 1:
            return handlers[0]

        async def composed_handler(ctx: Context) -> Any:
            for handler in handlers:
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(ctx)
                    else:
                        handler(ctx)

        return composed_handler

    @staticmethod
    def mount(update_types: Union[str, List[str]], *handlers: Handler) -> Handler:
        """Mount handlers for specific update types."""
        if isinstance(update_types, str):
            update_types = [update_types]

        composed = Composer.compose(*handlers)
        if not composed:
            return lambda ctx: None

        async def mounted_handler(ctx: Context) -> Any:
            if hasattr(ctx, "update_type") and ctx.update_type in update_types:
                if asyncio.iscoroutinefunction(composed):
                    await composed(ctx)
                else:
                    composed(ctx)
            elif "message" in update_types and hasattr(ctx, "message") and ctx.message:
                if asyncio.iscoroutinefunction(composed):
                    await composed(ctx)
                else:
                    composed(ctx)
            elif (
                "text" in update_types
                and hasattr(ctx, "message")
                and ctx.message
                and hasattr(ctx.message, "text")
            ):
                if asyncio.iscoroutinefunction(composed):
                    await composed(ctx)
                else:
                    composed(ctx)

        return mounted_handler

    @staticmethod
    def hears_middleware(
        triggers: Union[str, Pattern, List[Union[str, Pattern]]], *handlers: Handler
    ) -> Handler:
        """Create middleware for hearing text patterns."""
        if not isinstance(triggers, list):
            triggers = [triggers]

        compiled_patterns = []
        for trigger in triggers:
            if isinstance(trigger, str):
                compiled_patterns.append(re.compile(trigger, re.IGNORECASE))
            elif isinstance(trigger, Pattern):
                compiled_patterns.append(trigger)

        composed = Composer.compose(*handlers)
        if not composed:
            return lambda ctx: None

        async def hears_handler(ctx: Context) -> Any:
            if (
                hasattr(ctx, "message")
                and ctx.message
                and hasattr(ctx.message, "text")
                and ctx.message.text
            ):
                for pattern in compiled_patterns:
                    match = pattern.search(ctx.message.text)
                    if match:
                        ctx.match = match
                        if asyncio.iscoroutinefunction(composed):
                            await composed(ctx)
                        else:
                            composed(ctx)
                        break

        return hears_handler

    @staticmethod
    def command_middleware(
        commands: Union[str, List[str]], *handlers: Handler
    ) -> Handler:
        """Create middleware for command handling."""
        if isinstance(commands, str):
            commands = [commands]

        composed = Composer.compose(*handlers)
        if not composed:
            return lambda ctx: None

        async def command_handler(ctx: Context) -> Any:
            if (
                hasattr(ctx, "message")
                and ctx.message
                and hasattr(ctx.message, "text")
                and ctx.message.text
                and ctx.message.text.startswith("/")
            ):

                command_text = ctx.message.text[1:].split()[0].lower()
                if command_text in [cmd.lower() for cmd in commands]:
                    if asyncio.iscoroutinefunction(composed):
                        await composed(ctx)
                    else:
                        composed(ctx)

        return command_handler

    @staticmethod
    def action_middleware(
        triggers: Union[str, List[str]], *handlers: Handler
    ) -> Handler:
        """Create middleware for callback actions."""
        if isinstance(triggers, str):
            triggers = [triggers]

        composed = Composer.compose(*handlers)
        if not composed:
            return lambda ctx: None

        async def action_handler(ctx: Context) -> Any:
            if hasattr(ctx, "callback_query") and ctx.callback_query:
                action_data = getattr(ctx.callback_query, "data", "")
                if action_data in triggers:
                    if asyncio.iscoroutinefunction(composed):
                        await composed(ctx)
                    else:
                        composed(ctx)

        return action_handler

    @staticmethod
    def filter_middleware(predicate: FilterPredicate) -> Handler:
        """Create filter middleware."""

        async def filter_handler(ctx: Context) -> Any:
            if predicate(ctx):
                # Continue to next middleware
                pass

        return filter_handler
