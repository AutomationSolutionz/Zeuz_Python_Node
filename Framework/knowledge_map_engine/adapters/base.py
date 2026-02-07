"""
Adapter base class and registry for the Knowledge Map Engine.

Every adapter must subclass `Adapter` and implement:
  - name: unique adapter identifier
  - detect(snapshot) -> float: return 0.0-1.0 confidence this adapter applies
  - extract(snapshot) -> RepoSnapshot: return new IR facts to merge
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional

from Framework.knowledge_map_engine.ir.models import RepoSnapshot

logger = logging.getLogger(__name__)


class Adapter(ABC):
    """
    Base class for all KME adapters.

    Adapters follow a two-phase protocol:
      1. detect() - probe the snapshot to determine if this adapter applies
      2. extract() - extract ecosystem-specific facts as IR objects

    Adapters must ONLY produce IR objects. They must NEVER produce final
    documentation or assume they are the only adapter running.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this adapter (e.g., 'python_web', 'react')."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what this adapter detects."""
        return ""

    @abstractmethod
    def detect(self, snapshot: RepoSnapshot) -> float:
        """
        Probe the repo snapshot and return confidence (0.0 to 1.0) that
        this adapter is relevant.

        Args:
            snapshot: The current repo snapshot with files and basic symbols.

        Returns:
            Confidence score from 0.0 (not applicable) to 1.0 (certain match).
            Adapters with score > 0.0 will be offered for extraction.
        """
        ...

    @abstractmethod
    def extract(self, snapshot: RepoSnapshot) -> RepoSnapshot:
        """
        Extract ecosystem-specific facts and return them as a new RepoSnapshot.

        The returned snapshot will be merged into the main snapshot by the core.
        Only include NEW facts discovered by this adapter.

        Args:
            snapshot: The current repo snapshot (read-only context).

        Returns:
            A new RepoSnapshot containing only the adapter's discovered facts.
        """
        ...

    def __repr__(self) -> str:
        return f"<Adapter:{self.name}>"


class AdapterRegistry:
    """
    Registry of available adapters.

    Adapters register themselves (or are registered at init time).
    The engine queries the registry to find applicable adapters for a repo.
    """

    def __init__(self) -> None:
        self._adapters: dict[str, Adapter] = {}

    def register(self, adapter: Adapter) -> None:
        """Register an adapter instance."""
        if adapter.name in self._adapters:
            logger.warning(
                "Adapter '%s' already registered, replacing", adapter.name
            )
        self._adapters[adapter.name] = adapter
        logger.debug("Registered adapter: %s", adapter.name)

    def unregister(self, name: str) -> None:
        """Remove an adapter by name."""
        self._adapters.pop(name, None)

    def get(self, name: str) -> Optional[Adapter]:
        """Get an adapter by name."""
        return self._adapters.get(name)

    def list_adapters(self) -> list[Adapter]:
        """Return all registered adapters."""
        return list(self._adapters.values())

    def detect_applicable(
        self, snapshot: RepoSnapshot, threshold: float = 0.1
    ) -> list[tuple[Adapter, float]]:
        """
        Run detection on all registered adapters and return those that apply.

        Args:
            snapshot: The repo snapshot to probe.
            threshold: Minimum confidence score to consider an adapter applicable.

        Returns:
            List of (adapter, confidence) tuples, sorted by confidence descending.
        """
        results: list[tuple[Adapter, float]] = []
        for adapter in self._adapters.values():
            try:
                score = adapter.detect(snapshot)
                if score >= threshold:
                    results.append((adapter, score))
                    logger.info(
                        "Adapter '%s' detected with confidence %.2f",
                        adapter.name,
                        score,
                    )
                else:
                    logger.debug(
                        "Adapter '%s' below threshold (%.2f < %.2f)",
                        adapter.name,
                        score,
                        threshold,
                    )
            except Exception:
                logger.exception(
                    "Adapter '%s' failed during detection", adapter.name
                )

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def __len__(self) -> int:
        return len(self._adapters)

    def __contains__(self, name: str) -> bool:
        return name in self._adapters
