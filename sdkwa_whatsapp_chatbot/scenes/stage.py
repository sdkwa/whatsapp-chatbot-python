"""Stage implementation for managing scenes."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

from ..context import Context
from .base import BaseScene


class Stage:
    """Stage for managing multiple scenes."""

    def __init__(self, scenes: List[BaseScene], default_scene: Optional[str] = None):
        """Initialize stage with scenes."""
        self.scenes: Dict[str, BaseScene] = {scene.scene_id: scene for scene in scenes}
        self.default_scene = default_scene

    def register(self, scene: BaseScene) -> Stage:
        """Register a new scene."""
        self.scenes[scene.scene_id] = scene
        return self

    def unregister(self, scene_id: str) -> Stage:
        """Unregister a scene."""
        self.scenes.pop(scene_id, None)
        return self

    def get_scene(self, scene_id: str) -> Optional[BaseScene]:
        """Get scene by ID."""
        return self.scenes.get(scene_id)

    async def enter(self, scene_id: str, ctx: Context) -> bool:
        """Enter a scene."""
        scene = self.get_scene(scene_id)
        if not scene:
            return False

        # Leave current scene if any
        if hasattr(ctx, "scene") and ctx.scene:
            await ctx.scene.leave_scene(ctx)

        # Enter new scene
        await scene.enter_scene(ctx)
        return True

    async def leave(self, ctx: Context) -> bool:
        """Leave current scene."""
        if hasattr(ctx, "scene") and ctx.scene:
            await ctx.scene.leave_scene(ctx)
            return True
        return False

    async def reenter(self, ctx: Context) -> bool:
        """Re-enter current scene."""
        if hasattr(ctx, "scene") and ctx.scene:
            await ctx.scene.reenter(ctx)
            return True
        return False

    def get_current_scene(self, ctx: Context) -> Optional[BaseScene]:
        """Get current active scene."""
        if not hasattr(ctx, "session") or "__scene" not in ctx.session:
            return None

        scene_id = ctx.session["__scene"]["id"]
        scene = self.get_scene(scene_id)

        if scene and scene.is_active(ctx):
            return scene

        return None

    def middleware(self) -> Callable:
        """Create middleware for scene handling."""

        async def stage_middleware(ctx: Context, next_handler: Optional[Callable] = None) -> Any:
            # Add scene manager to context
            ctx.scene_manager = self

            # Get current scene
            current_scene = self.get_current_scene(ctx)
            if current_scene:
                ctx.scene = current_scene

                # Process update through scene handlers
                if current_scene.handler:
                    # Mark that a scene is handling this message
                    ctx._scene_handled = True
                    
                    if asyncio.iscoroutinefunction(current_scene.handler):
                        scene_result = await current_scene.handler(ctx)
                    else:
                        scene_result = current_scene.handler(ctx)

                    # Scene handled the update - don't call next_handler
                    return scene_result

            # If next_handler is provided and scene didn't handle it, call it
            if next_handler:
                if asyncio.iscoroutinefunction(next_handler):
                    return await next_handler(ctx)
                else:
                    return next_handler(ctx)

            # Scene manager middleware doesn't block other handlers

        return stage_middleware

    def scene_middleware(self, scene_id: str) -> Callable:
        """Create middleware that only activates for a specific scene."""

        async def scene_specific_middleware(ctx: Context) -> Any:
            current_scene = self.get_current_scene(ctx)
            if current_scene and current_scene.scene_id == scene_id:
                # This middleware only runs for the specific scene
                pass

        return scene_specific_middleware

    def reset_scene(self, ctx: Context) -> None:
        """Reset scene state."""
        if hasattr(ctx, "session") and "__scene" in ctx.session:
            del ctx.session["__scene"]

        if hasattr(ctx, "scene"):
            ctx.scene = None

    def list_scenes(self) -> List[str]:
        """List all registered scene IDs."""
        return list(self.scenes.keys())

    def scene_exists(self, scene_id: str) -> bool:
        """Check if scene exists."""
        return scene_id in self.scenes

    def enter_default(self, ctx: Context) -> bool:
        """Enter default scene if set."""
        if self.default_scene:
            return asyncio.create_task(self.enter(self.default_scene, ctx))
        return False


class SceneContext:
    """Scene context helper for managing scene state."""

    def __init__(self, ctx: Context, stage: Stage):
        """Initialize scene context."""
        self.ctx = ctx
        self.stage = stage

    async def enter(self, scene_id: str) -> bool:
        """Enter a scene."""
        return await self.stage.enter(scene_id, self.ctx)

    async def leave(self) -> bool:
        """Leave current scene."""
        return await self.stage.leave(self.ctx)

    async def reenter(self) -> bool:
        """Re-enter current scene."""
        return await self.stage.reenter(self.ctx)

    @property
    def current(self) -> Optional[BaseScene]:
        """Get current scene."""
        return self.stage.get_current_scene(self.ctx)

    @property
    def state(self) -> Dict[str, Any]:
        """Get current scene state."""
        current_scene = self.current
        if current_scene:
            return current_scene.get_state(self.ctx)
        return {}

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update current scene state."""
        current_scene = self.current
        if current_scene:
            current_scene.update_state(self.ctx, updates)

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set current scene state."""
        current_scene = self.current
        if current_scene:
            current_scene.set_state(self.ctx, state)
