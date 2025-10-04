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
    def __init__(self) -> None:
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()

    def create_session(self, username: str, ttl_minutes: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + ttl_minutes * 60
        with self._lock:
            self._sessions[token] = Session(username=username, expires_at=expires_at)
        return token

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
