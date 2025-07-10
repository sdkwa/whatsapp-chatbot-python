"""Session module for maintaining user state across conversations."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, Optional

from .context import Context


class SessionStore(ABC):
    """Abstract base class for session storage."""

    @abstractmethod
    async def get(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get session data by key."""
        pass

    @abstractmethod
    async def set(self, session_key: str, session_data: Dict[str, Any]) -> None:
        """Set session data by key."""
        pass

    @abstractmethod
    async def delete(self, session_key: str) -> None:
        """Delete session data by key."""
        pass


class MemorySessionStore(SessionStore):
    """In-memory session store implementation."""

    def __init__(self):
        """Initialize memory store."""
        self._sessions: Dict[str, Dict[str, Any]] = {}

    async def get(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get session data by key."""
        return self._sessions.get(session_key, {})

    async def set(self, session_key: str, session_data: Dict[str, Any]) -> None:
        """Set session data by key."""
        self._sessions[session_key] = session_data

    async def delete(self, session_key: str) -> None:
        """Delete session data by key."""
        self._sessions.pop(session_key, None)


class FileSessionStore(SessionStore):
    """File-based session store implementation."""

    def __init__(self, file_path: str = "sessions.json"):
        """Initialize file store."""
        self.file_path = file_path
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load sessions from file."""
        try:
            import json

            with open(self.file_path, "r") as f:
                self._sessions = json.load(f)
        except FileNotFoundError:
            self._sessions = {}
        except Exception:
            self._sessions = {}

    def _save_sessions(self) -> None:
        """Save sessions to file."""
        try:
            import json

            with open(self.file_path, "w") as f:
                json.dump(self._sessions, f, indent=2)
        except Exception:
            pass

    async def get(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get session data by key."""
        return self._sessions.get(session_key, {})

    async def set(self, session_key: str, session_data: Dict[str, Any]) -> None:
        """Set session data by key."""
        self._sessions[session_key] = session_data
        self._save_sessions()

    async def delete(self, session_key: str) -> None:
        """Delete session data by key."""
        self._sessions.pop(session_key, None)
        self._save_sessions()


def session(
    store: Optional[SessionStore] = None,
    key_generator: Optional[Callable[[Context], str]] = None,
) -> Callable[[Context], Awaitable[Any]]:
    """
    Create session middleware.

    Args:
        store: Session store implementation (defaults to MemorySessionStore)
        key_generator: Function to generate session key from context

    Returns:
        Session middleware function
    """
    if store is None:
        store = MemorySessionStore()

    if key_generator is None:

        def default_key_generator(ctx: Context) -> str:
            # Use chat_id as session key by default
            return ctx.chat_id or "default"

        key_generator = default_key_generator

    async def session_middleware(ctx: Context, next_handler: Optional[Callable] = None) -> Any:
        """Session middleware implementation."""
        session_key = key_generator(ctx)

        # Load session data
        session_data = await store.get(session_key) or {}
        ctx.session = session_data

        try:
            # If next_handler is provided, call it (for compatibility with other middleware patterns)
            result = None
            if next_handler:
                if asyncio.iscoroutinefunction(next_handler):
                    result = await next_handler(ctx)
                else:
                    result = next_handler(ctx)
            
            return result
        finally:
            # Always save session data back to store after processing
            if hasattr(ctx, 'session'):
                await store.set(session_key, ctx.session)

    return session_middleware


class SessionManager:
    """Manager for handling sessions."""

    def __init__(self, store: Optional[SessionStore] = None):
        """Initialize session manager."""
        self.store = store or MemorySessionStore()

    async def get_session(self, session_key: str) -> Dict[str, Any]:
        """Get session data."""
        return await self.store.get(session_key) or {}

    async def set_session(self, session_key: str, session_data: Dict[str, Any]) -> None:
        """Set session data."""
        await self.store.set(session_key, session_data)

    async def delete_session(self, session_key: str) -> None:
        """Delete session data."""
        await self.store.delete(session_key)

    async def clear_all_sessions(self) -> None:
        """Clear all sessions."""
        if isinstance(self.store, MemorySessionStore):
            self.store._sessions.clear()
        elif isinstance(self.store, FileSessionStore):
            self.store._sessions.clear()
            self.store._save_sessions()

    def middleware(
        self, key_generator: Optional[Callable[[Context], str]] = None
    ) -> Callable:
        """Get session middleware."""
        return session(self.store, key_generator)
