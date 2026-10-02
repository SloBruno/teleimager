"""Thread-safe, in-memory per-camera stream telemetry."""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional


class CameraTelemetry:
    """Count successful capture/publication and errors without capture-loop I/O."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._capture_seq = 0
        self._publish_seq = 0
        self._capture_errors = 0
        self._publish_errors = 0
        self._last_capture_at: Optional[float] = None
        self._last_publish_at: Optional[float] = None

    def capture_ok(self) -> None:
        with self._lock:
            self._capture_seq += 1
            self._last_capture_at = self._clock()

    def publish_ok(self) -> None:
        with self._lock:
            self._publish_seq += 1
            self._last_publish_at = self._clock()

    def capture_error(self) -> None:
        with self._lock:
            self._capture_errors += 1

    def publish_error(self) -> None:
        with self._lock:
            self._publish_errors += 1

    def snapshot(self) -> dict[str, Optional[float] | int]:
        now = self._clock()
        with self._lock:
            return {
                "capture_seq": self._capture_seq,
                "publish_seq": self._publish_seq,
                "capture_errors": self._capture_errors,
                "publish_errors": self._publish_errors,
                "capture_age_s": None if self._last_capture_at is None else now - self._last_capture_at,
                "publish_age_s": None if self._last_publish_at is None else now - self._last_publish_at,
            }
