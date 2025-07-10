"""Wizard scene implementation for step-by-step conversations."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

from ..context import Context
from .base import BaseScene


class WizardScene(BaseScene):
    """Wizard scene for step-by-step conversation flows."""

    def __init__(self, scene_id: str):
        """Initialize wizard scene."""
        super().__init__(scene_id)
        self.steps: List[Callable] = []
        self.current_step = 0
        
        # Add default message handler for wizard flow
        self.on("message", self._handle_wizard_message)

    def step(self, handler: Callable = None):
        """Add a step to the wizard."""
        if handler is not None:
            self.steps.append(handler)
            return self
        else:

            def decorator(handler: Callable):
                self.steps.append(handler)
                return handler

            return decorator

    def add_step(self, handler: Callable) -> WizardScene:
        """Add a step to the wizard (alias for step)."""
        return self.step(handler)

    async def enter_scene(self, ctx: Context) -> None:
        """Enter the wizard scene."""
        await super().enter_scene(ctx)

        # Initialize wizard state
        wizard_state = {"current_step": 0, "step_data": {}, "completed_steps": []}

        scene_state = self.get_state(ctx)
        scene_state["wizard"] = wizard_state
        self.set_state(ctx, scene_state)

        # Execute first step
        await self.execute_current_step(ctx)

    async def _handle_wizard_message(self, ctx: Context) -> None:
        """Handle incoming messages in wizard flow."""
        # Skip commands - they should be handled by the main bot
        if hasattr(ctx.message, 'text') and ctx.message.text and ctx.message.text.startswith('/'):
            return
            
        wizard_state = self.get_wizard_state(ctx)
        current_step_index = wizard_state.get("current_step", 0)
        
        # Advance to the next step and execute it
        # This is because user input is a response to the current step
        next_step_index = current_step_index + 1
        
        if next_step_index < len(self.steps):
            # Advance to next step
            wizard_state["current_step"] = next_step_index
            
            # Update state
            scene_state = self.get_state(ctx)
            scene_state["wizard"] = wizard_state
            self.set_state(ctx, scene_state)
            
            # Execute the next step
            await self.execute_current_step(ctx)

    async def execute_current_step(self, ctx: Context) -> None:
        """Execute the current step."""
        wizard_state = self.get_wizard_state(ctx)
        step_index = wizard_state["current_step"]

        if step_index < len(self.steps):
            step_handler = self.steps[step_index]

            # Add wizard navigation methods to context
            ctx.wizard = WizardContext(self, ctx)

            if asyncio.iscoroutinefunction(step_handler):
                await step_handler(ctx)
            else:
                step_handler(ctx)

    async def next_step(
        self, ctx: Context, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Move to next step."""
        wizard_state = self.get_wizard_state(ctx)
        current_step = wizard_state["current_step"]

        # Save current step data
        if data:
            wizard_state["step_data"][current_step] = data

        # Mark step as completed
        if current_step not in wizard_state["completed_steps"]:
            wizard_state["completed_steps"].append(current_step)

        # Move to next step
        wizard_state["current_step"] = current_step + 1

        # Update state
        scene_state = self.get_state(ctx)
        scene_state["wizard"] = wizard_state
        self.set_state(ctx, scene_state)

        # Execute next step if available
        if wizard_state["current_step"] < len(self.steps):
            await self.execute_current_step(ctx)
            return True
        else:
            # Wizard completed
            await self.complete_wizard(ctx)
            return False

    async def previous_step(self, ctx: Context) -> bool:
        """Move to previous step."""
        wizard_state = self.get_wizard_state(ctx)
        current_step = wizard_state["current_step"]

        if current_step > 0:
            wizard_state["current_step"] = current_step - 1

            # Update state
            scene_state = self.get_state(ctx)
            scene_state["wizard"] = wizard_state
            self.set_state(ctx, scene_state)

            # Execute previous step
            await self.execute_current_step(ctx)
            return True

        return False

    async def jump_to_step(self, ctx: Context, step_index: int) -> bool:
        """Jump to specific step."""
        if 0 <= step_index < len(self.steps):
            wizard_state = self.get_wizard_state(ctx)
            wizard_state["current_step"] = step_index

            # Update state
            scene_state = self.get_state(ctx)
            scene_state["wizard"] = wizard_state
            self.set_state(ctx, scene_state)

            # Execute target step
            await self.execute_current_step(ctx)
            return True

        return False

    async def complete_wizard(self, ctx: Context) -> None:
        """Complete the wizard."""
        wizard_state = self.get_wizard_state(ctx)

        # Mark wizard as completed
        wizard_state["completed"] = True

        # Update state
        scene_state = self.get_state(ctx)
        scene_state["wizard"] = wizard_state
        self.set_state(ctx, scene_state)

        # Leave scene
        await self.leave_scene(ctx)

    def get_wizard_state(self, ctx: Context) -> Dict[str, Any]:
        """Get wizard state."""
        scene_state = self.get_state(ctx)
        return scene_state.get("wizard", {})

    def get_step_data(
        self, ctx: Context, step_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get data from a specific step."""
        wizard_state = self.get_wizard_state(ctx)
        step_data = wizard_state.get("step_data", {})

        if step_index is not None:
            return step_data.get(step_index, {})

        return step_data

    def get_current_step_index(self, ctx: Context) -> int:
        """Get current step index."""
        wizard_state = self.get_wizard_state(ctx)
        return wizard_state.get("current_step", 0)

    def is_completed(self, ctx: Context) -> bool:
        """Check if wizard is completed."""
        wizard_state = self.get_wizard_state(ctx)
        return wizard_state.get("completed", False)

    def get_progress(self, ctx: Context) -> Dict[str, Any]:
        """Get wizard progress information."""
        wizard_state = self.get_wizard_state(ctx)
        current_step = wizard_state.get("current_step", 0)
        total_steps = len(self.steps)
        completed_steps = len(wizard_state.get("completed_steps", []))

        return {
            "current_step": current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": (
                (completed_steps / total_steps * 100) if total_steps > 0 else 0
            ),
            "is_completed": self.is_completed(ctx),
        }


class WizardContext:
    """Wizard context for step navigation."""

    def __init__(self, wizard: WizardScene, ctx: Context):
        """Initialize wizard context."""
        self.wizard = wizard
        self.ctx = ctx

    async def next(self, data: Optional[Dict[str, Any]] = None) -> bool:
        """Move to next step."""
        return await self.wizard.next_step(self.ctx, data)

    async def previous(self) -> bool:
        """Move to previous step."""
        return await self.wizard.previous_step(self.ctx)

    async def jump_to(self, step_index: int) -> bool:
        """Jump to specific step."""
        return await self.wizard.jump_to_step(self.ctx, step_index)

    async def complete(self) -> None:
        """Complete the wizard."""
        await self.wizard.complete_wizard(self.ctx)

    @property
    def current_step(self) -> int:
        """Get current step index."""
        return self.wizard.get_current_step_index(self.ctx)

    @property
    def progress(self) -> Dict[str, Any]:
        """Get progress information."""
        return self.wizard.get_progress(self.ctx)

    def get_step_data(self, step_index: Optional[int] = None) -> Dict[str, Any]:
        """Get step data."""
        return self.wizard.get_step_data(self.ctx, step_index)

    def get_all_data(self) -> Dict[str, Any]:
        """Get all step data."""
        return self.wizard.get_step_data(self.ctx)

    @property
    def is_completed(self) -> bool:
        """Check if wizard is completed."""
        return self.wizard.is_completed(self.ctx)
