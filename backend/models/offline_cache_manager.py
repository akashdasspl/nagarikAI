"""
Offline Cache Manager for graceful degradation under low bandwidth and offline conditions.
Validates: Requirements 21.1, 21.2, 21.5, 21.6
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List


@dataclass
class OfflineCacheManifest:
    """Current state of the local model cache."""
    model_version: str
    checksum: str           # SHA-256 hex of model_version string (demo)
    last_sync_timestamp: datetime
    is_stale: bool
    connectivity_mode: str  # 'Online' | 'Lite_Mode' | 'Offline'


@dataclass
class SyncResult:
    """Result of a deferred-data synchronisation attempt."""
    success: bool
    synced_at: datetime
    deferred_calls_uploaded: int
    models_updated: bool
    error_message: str      # empty string on success


@dataclass
class _DeferredCall:
    endpoint: str
    payload: Dict[str, Any]


class OfflineCacheManager:
    """
    Manages local model cache, connectivity mode detection, deferred API calls,
    and staleness-based confidence penalties for offline/low-bandwidth operation.
    """

    def __init__(self) -> None:
        self.last_sync_timestamp: datetime = datetime.utcnow()
        self.model_version: str = "1.0.0"
        self._deferred_calls: List[_DeferredCall] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_cache_manifest(self, bandwidth_kbps: float = 100) -> OfflineCacheManifest:
        """
        Return the current cache manifest including model version, checksum,
        last sync timestamp, staleness flag, and connectivity mode.
        """
        return OfflineCacheManifest(
            model_version=self.model_version,
            checksum=self._compute_checksum(self.model_version),
            last_sync_timestamp=self.last_sync_timestamp,
            is_stale=self.is_cache_stale(),
            connectivity_mode=self.get_connectivity_mode(bandwidth_kbps),
        )

    def is_cache_stale(self, max_age_hours: float = 72) -> bool:
        """
        Return True if last_sync_timestamp is older than max_age_hours.

        Req 21.6: cached model > 72 hours old → staleness warning + confidence penalty.
        """
        age = datetime.utcnow() - self.last_sync_timestamp
        return age > timedelta(hours=max_age_hours)

    def get_connectivity_mode(self, bandwidth_kbps: float) -> str:
        """
        Determine operating mode from current bandwidth.

        - 'Offline'   : bandwidth == 0
        - 'Lite_Mode' : 0 < bandwidth < 50 kbps  (Req 21.2)
        - 'Online'    : bandwidth >= 50 kbps
        """
        if bandwidth_kbps == 0:
            return "Offline"
        if bandwidth_kbps < 50:
            return "Lite_Mode"
        return "Online"

    def sync_deferred_data(self) -> SyncResult:
        """
        Simulate uploading deferred API calls and downloading fresh model/pattern data.

        Clears the deferred call queue, updates last_sync_timestamp, and bumps
        the model version to signal a fresh sync.  Completes within 60 seconds
        (simulated instantly for MVP).

        Req 21.5: exit Lite_Mode and sync deferred data within 60 seconds.
        """
        uploaded_count = len(self._deferred_calls)
        self._deferred_calls.clear()

        # Simulate downloading a fresh model version
        self.last_sync_timestamp = datetime.utcnow()
        self.model_version = self._next_model_version(self.model_version)

        return SyncResult(
            success=True,
            synced_at=self.last_sync_timestamp,
            deferred_calls_uploaded=uploaded_count,
            models_updated=True,
            error_message="",
        )

    def apply_staleness_penalty(self, raw_confidence: float) -> float:
        """
        If the cache is stale, subtract 0.10 from raw_confidence.
        Always clamp the result to [0.0, 1.0].

        Req 21.6: reduce confidence by 10 percentage points when stale.
        """
        confidence = raw_confidence
        if self.is_cache_stale():
            confidence = raw_confidence - 0.10
        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, confidence))

    def add_deferred_call(self, endpoint: str, payload: Dict[str, Any]) -> None:
        """
        Queue a non-critical API call for later upload when connectivity improves.

        Req 21.2: defer non-critical API calls in Lite_Mode.
        """
        self._deferred_calls.append(_DeferredCall(endpoint=endpoint, payload=payload))

    def get_deferred_calls(self) -> List[Dict[str, Any]]:
        """Return the current list of deferred calls as plain dicts."""
        return [{"endpoint": c.endpoint, "payload": c.payload} for c in self._deferred_calls]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_checksum(model_version: str) -> str:
        """Return SHA-256 hex digest of the model version string."""
        return hashlib.sha256(model_version.encode()).hexdigest()

    @staticmethod
    def _next_model_version(current: str) -> str:
        """Increment the patch component of a semver string."""
        parts = current.split(".")
        try:
            parts[-1] = str(int(parts[-1]) + 1)
        except (ValueError, IndexError):
            parts = ["1", "0", "1"]
        return ".".join(parts)
