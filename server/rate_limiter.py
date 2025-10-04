"""Rate limiting for login attempts."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class LoginAttempt:
    count: int
    first_attempt: float
    locked_until: float = 0.0


class RateLimiter:
    """Simple rate limiter for login attempts."""

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,
        lockout_seconds: int = 300,
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            max_attempts: Maximum failed attempts allowed in window
            window_seconds: Time window for counting attempts (seconds)
            lockout_seconds: How long to lock out after max attempts exceeded
        """
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._lockout_seconds = lockout_seconds
        self._attempts: Dict[str, LoginAttempt] = {}
        self._lock = threading.RLock()

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if login attempt is allowed for the given identifier.

        Args:
            identifier: IP address or username

        Returns:
            True if attempt is allowed, False if rate limited
        """
        now = time.time()

        with self._lock:
            self._cleanup_old_entries(now)

            if identifier not in self._attempts:
                return True

            attempt = self._attempts[identifier]

            # Check if still locked out
            if attempt.locked_until > now:
                return False

            # Check if window has passed
            if now - attempt.first_attempt > self._window_seconds:
                # Reset the attempt
                del self._attempts[identifier]
                return True

            # Check if under limit
            return attempt.count < self._max_attempts

    def record_failed_attempt(self, identifier: str) -> None:
        """
        Record a failed login attempt.

        Args:
            identifier: IP address or username
        """
        now = time.time()

        with self._lock:
            if identifier not in self._attempts:
                self._attempts[identifier] = LoginAttempt(
                    count=1, first_attempt=now, locked_until=0.0
                )
            else:
                attempt = self._attempts[identifier]

                # If window has passed, reset
                if now - attempt.first_attempt > self._window_seconds:
                    self._attempts[identifier] = LoginAttempt(
                        count=1, first_attempt=now, locked_until=0.0
                    )
                else:
                    attempt.count += 1

                    # If exceeded max attempts, lock out
                    if attempt.count >= self._max_attempts:
                        attempt.locked_until = now + self._lockout_seconds

    def record_successful_attempt(self, identifier: str) -> None:
        """
        Clear failed attempts for identifier after successful login.

        Args:
            identifier: IP address or username
        """
        with self._lock:
            if identifier in self._attempts:
                del self._attempts[identifier]

    def _cleanup_old_entries(self, now: float) -> None:
        """Remove expired entries. Must be called with lock held."""
        expired = []
        for identifier, attempt in self._attempts.items():
            # Remove if lockout expired and window passed
            if (
                attempt.locked_until < now
                and now - attempt.first_attempt > self._window_seconds
            ):
                expired.append(identifier)

        for identifier in expired:
            del self._attempts[identifier]

    def get_remaining_lockout(self, identifier: str) -> int:
        """
        Get remaining lockout time in seconds.

        Returns:
            Seconds remaining, or 0 if not locked out
        """
        now = time.time()
        with self._lock:
            if identifier not in self._attempts:
                return 0

            attempt = self._attempts[identifier]
            if attempt.locked_until <= now:
                return 0

            return int(attempt.locked_until - now)
