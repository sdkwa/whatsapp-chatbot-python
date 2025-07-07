"""Base scene implementation for conversation flows."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

from ..composer import Composer
from ..context import Context


class BaseScene(Composer):
    """Base scene class for managing conversation flows."""

    def __init__(self, scene_id: str):
        """Initialize scene with unique identifier."""
        super().__init__()
        self.scene_id = scene_id
        self.enter_handlers: List[Callable] = []
        self.leave_handlers: List[Callable] = []
        self._ttl: Optional[int] = None

    def enter(self, *handlers: Callable):
        """Register enter handlers."""
        if handlers:
            self.enter_handlers.extend(handlers)
            return self
        else:

            def decorator(handler: Callable):
                self.enter_handlers.append(handler)
                return handler

            return decorator

    def leave(self, *handlers: Callable):
        """Register leave handlers."""
        if handlers:
            self.leave_handlers.extend(handlers)
            return self
        else:

            def decorator(handler: Callable):
                self.leave_handlers.append(handler)
                return handler

            return decorator

    def ttl(self, seconds: int) -> BaseScene:
        """Set time-to-live for the scene."""
        self._ttl = seconds
        return self

    async def enter_scene(self, ctx: Context) -> None:
        """Execute enter handlers."""
        ctx.scene = self

        # Set scene state
        if not hasattr(ctx, "session"):
            ctx.session = {}

        ctx.session["__scene"] = {
            "id": self.scene_id,
            "state": {},
            "entered_at": asyncio.get_event_loop().time(),
        }

        # Execute enter handlers
        for handler in self.enter_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(ctx)
            else:
                handler(ctx)

    async def leave_scene(self, ctx: Context) -> None:
        """Execute leave handlers."""
        # Execute leave handlers
        for handler in self.leave_handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(ctx)
            else:
                handler(ctx)

        # Clear scene state
        if hasattr(ctx, "session") and "__scene" in ctx.session:
            del ctx.session["__scene"]

        ctx.scene = None

    async def reenter(self, ctx: Context) -> None:
        """Re-enter the scene."""
        await self.leave_scene(ctx)
        await self.enter_scene(ctx)

    def is_active(self, ctx: Context) -> bool:
        """Check if scene is currently active."""
        if not hasattr(ctx, "session") or "__scene" not in ctx.session:
            return False

        scene_data = ctx.session["__scene"]
        if scene_data["id"] != self.scene_id:
            return False

        # Check TTL
        if self._ttl is not None:
            current_time = asyncio.get_event_loop().time()
            entered_at = scene_data.get("entered_at", current_time)
            if current_time - entered_at > self._ttl:
                return False

        return True

    def get_state(self, ctx: Context) -> Dict[str, Any]:
        """Get scene state."""
        if (
            hasattr(ctx, "session")
            and "__scene" in ctx.session
            and ctx.session["__scene"]["id"] == self.scene_id
        ):
            return ctx.session["__scene"]["state"]
        return {}

    def set_state(self, ctx: Context, state: Dict[str, Any]) -> None:
        """Set scene state."""
        if not hasattr(ctx, "session"):
            ctx.session = {}

        if (
            "__scene" not in ctx.session
            or ctx.session["__scene"]["id"] != self.scene_id
        ):
            ctx.session["__scene"] = {
                "id": self.scene_id,
                "state": {},
                "entered_at": asyncio.get_event_loop().time(),
            }

        ctx.session["__scene"]["state"] = state

    def update_state(self, ctx: Context, updates: Dict[str, Any]) -> None:
        """Update scene state."""
        current_state = self.get_state(ctx)
        current_state.update(updates)
        self.set_state(ctx, current_state)


# Convenience functions for scene control
def enter(scene_id: str) -> Callable:
    """Create a handler to enter a scene."""

    async def enter_handler(ctx: Context) -> None:
        if hasattr(ctx, "scene_manager"):
            await ctx.scene_manager.enter(scene_id, ctx)

    return enter_handler


def leave() -> Callable:
    """Create a handler to leave current scene."""

    async def leave_handler(ctx: Context) -> None:
        if hasattr(ctx, "scene") and ctx.scene:
            await ctx.scene.leave_scene(ctx)

    return leave_handler


def reenter() -> Callable:
    """Create a handler to re-enter current scene."""

    async def reenter_handler(ctx: Context) -> None:
        if hasattr(ctx, "scene") and ctx.scene:
            await ctx.scene.reenter(ctx)

    return reenter_handler
