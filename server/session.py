import secrets
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class Session:
    username: str
    expires_at: float


class SessionManager:
    def __init__(self, max_sessions_per_user: int = 3) -> None:
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        self._max_sessions_per_user = max_sessions_per_user

    def create_session(self, username: str, ttl_minutes: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + ttl_minutes * 60

        with self._lock:
            # Clean up expired sessions first
            self._cleanup_expired_sessions()

            # Enforce max sessions per user
            user_sessions = [
                (t, s) for t, s in self._sessions.items() if s.username == username
            ]

            if len(user_sessions) >= self._max_sessions_per_user:
                # Remove oldest session
                oldest_token = min(user_sessions, key=lambda x: x[1].expires_at)[0]
                del self._sessions[oldest_token]

            self._sessions[token] = Session(username=username, expires_at=expires_at)
        return token

    def _cleanup_expired_sessions(self) -> None:
        """Remove all expired sessions. Must be called with lock held."""
        now = time.time()
        expired = [token for token, session in self._sessions.items() if session.expires_at < now]
        for token in expired:
            del self._sessions[token]

    def get_session(self, token: Optional[str]) -> Optional[Session]:
        if not token:
            return None
        with self._lock:
            session = self._sessions.get(token)
            if not session:
                return None
            if session.expires_at < time.time():
                del self._sessions[token]
                return None
            return session

    def invalidate(self, token: Optional[str]) -> None:
        if not token:
            return
        with self._lock:
            self._sessions.pop(token, None)
