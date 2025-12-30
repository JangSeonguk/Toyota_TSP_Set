"""
Session Manager Module
Manages browser session state for add_request mode
"""

import threading
from typing import Optional

import logger


class SessionState:
    """Thread-safe session state management for add_request mode"""

    def __init__(self):
        self._lock = threading.Lock()
        self._vin: Optional[str] = None
        self._is_active: bool = False
        logger.log_info("SessionState initialized")

    def start_session(self, vin: str) -> None:
        """
        Start a new add_request session

        Args:
            vin: VIN to store for subsequent requests
        """
        with self._lock:
            self._vin = vin
            self._is_active = True
            logger.log_info(f"Session started: VIN={vin}")

    def get_stored_vin(self) -> Optional[str]:
        """
        Get the stored VIN from current session

        Returns:
            Stored VIN or None if no active session
        """
        with self._lock:
            return self._vin

    def is_active(self) -> bool:
        """
        Check if session is currently active

        Returns:
            True if session is active, False otherwise
        """
        with self._lock:
            return self._is_active

    def close_session(self) -> None:
        """Close current session and clear stored data"""
        with self._lock:
            if self._is_active:
                logger.log_info(f"Session closed: VIN={self._vin}")
            self._vin = None
            self._is_active = False

    def reset(self) -> None:
        """Reset session state (alias for close_session)"""
        self.close_session()


# Global session state instance
_session_state: Optional[SessionState] = None
_session_lock = threading.Lock()


def get_session() -> SessionState:
    """
    Get or create the global session state instance

    Returns:
        SessionState instance
    """
    global _session_state
    with _session_lock:
        if _session_state is None:
            _session_state = SessionState()
        return _session_state


def start_session(vin: str) -> None:
    """
    Start a new add_request session

    Args:
        vin: VIN to store
    """
    get_session().start_session(vin)


def get_stored_vin() -> Optional[str]:
    """
    Get the stored VIN from current session

    Returns:
        Stored VIN or None
    """
    return get_session().get_stored_vin()


def is_session_active() -> bool:
    """
    Check if session is currently active

    Returns:
        True if active
    """
    return get_session().is_active()


def close_session() -> None:
    """Close current session"""
    get_session().close_session()
