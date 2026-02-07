"""
KME Core Engine - the main orchestrator.

Coordinates:
  1. Repository ingestion (via GenericScanner)
  2. Adapter detection and execution (via AdapterRegistry)
  3. Snapshot merging
  4. Knowledge graph construction
  5. Output artifact generation
  6. Delta refresh (incremental re-scan)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from Framework.knowledge_map_engine.adapters.base import Adapter, AdapterRegistry
from Framework.knowledge_map_engine.core.graph import KnowledgeGraph
from Framework.knowledge_map_engine.ir.models import RepoSnapshot
from Framework.knowledge_map_engine.scanner.generic_scanner import GenericScanner

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Result of a full KME scan."""
    snapshot: RepoSnapshot
    graph: KnowledgeGraph
    adapters_used: list[str]
    scan_duration_seconds: float
    metadata: dict[str, Any] = field(default_factory=dict)


class KnowledgeMapEngine:
    """
    The main KME engine.

    Usage:
        engine = KnowledgeMapEngine()
        engine.register_adapter(PythonWebAdapter())
        engine.register_adapter(ReactAdapter())
        result = engine.scan("/path/to/repo")
        engine.generate_artifacts(result, "/path/to/output")
    """

    def __init__(
        self,
        adapter_threshold: float = 0.1,
        max_file_size: int = 5 * 1024 * 1024,
        skip_binary: bool = True,
        skip_vendored: bool = True,
    ) -> None:
        self._registry = AdapterRegistry()
        self._scanner = GenericScanner(
            max_file_size=max_file_size,
            skip_binary=skip_binary,
            skip_vendored=skip_vendored,
        )
        self._adapter_threshold = adapter_threshold
        self._last_snapshot: Optional[RepoSnapshot] = None

    # ------------------------------------------------------------------
    # Adapter management
    # ------------------------------------------------------------------

    def register_adapter(self, adapter: Adapter) -> None:
        """Register an adapter plugin."""
        self._registry.register(adapter)

    def unregister_adapter(self, name: str) -> None:
        """Remove an adapter by name."""
        self._registry.unregister(name)

    def list_adapters(self) -> list[str]:
        """List names of all registered adapters."""
        return [a.name for a in self._registry.list_adapters()]

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def scan(self, repo_path: str) -> ScanResult:
        """
        Perform a full scan of the repository.

        Steps:
          1. Run the generic scanner (always-on, Layer A)
          2. Detect applicable adapters
          3. Run each applicable adapter to extract additional facts
          4. Merge adapter facts into the main snapshot
          5. Build the knowledge graph

        Args:
            repo_path: Path to the repository root.

        Returns:
            ScanResult with the complete snapshot and graph.
        """
        start_time = time.monotonic()

        # Phase 1: Generic scan
        logger.info("Phase 1: Running generic scanner on %s", repo_path)
        snapshot = self._scanner.scan(repo_path)

        # Phase 2: Detect adapters
        logger.info("Phase 2: Detecting applicable adapters")
        applicable = self._registry.detect_applicable(
            snapshot, threshold=self._adapter_threshold
        )
        adapters_used: list[str] = []

        # Phase 3: Run adapters
        for adapter, confidence in applicable:
            logger.info(
                "Phase 3: Running adapter '%s' (confidence: %.2f)",
                adapter.name,
                confidence,
            )
            try:
                adapter_snapshot = adapter.extract(snapshot)
                # Track provenance
                adapter_snapshot.record_provenance(
                    adapter.name, "interfaces", len(adapter_snapshot.interfaces)
                )
                adapter_snapshot.record_provenance(
                    adapter.name, "symbols", len(adapter_snapshot.symbols)
                )
                adapter_snapshot.record_provenance(
                    adapter.name, "data_touches", len(adapter_snapshot.data_touches)
                )

                # Merge into main snapshot
                snapshot.merge(adapter_snapshot)
                adapters_used.append(adapter.name)
                logger.info(
                    "Adapter '%s' contributed: %d interfaces, %d symbols, "
                    "%d data_touches",
                    adapter.name,
                    len(adapter_snapshot.interfaces),
                    len(adapter_snapshot.symbols),
                    len(adapter_snapshot.data_touches),
                )
            except Exception:
                logger.exception(
                    "Adapter '%s' failed during extraction", adapter.name
                )

        # Phase 4: Build knowledge graph
        logger.info("Phase 4: Building knowledge graph")
        graph = KnowledgeGraph()
        graph.build_from_snapshot(snapshot)

        duration = time.monotonic() - start_time
        self._last_snapshot = snapshot

        return ScanResult(
            snapshot=snapshot,
            graph=graph,
            adapters_used=adapters_used,
            scan_duration_seconds=duration,
            metadata={
                "repo_path": repo_path,
                "total_files": len(snapshot.files),
                "total_symbols": len(snapshot.symbols),
                "total_interfaces": len(snapshot.interfaces),
                "total_data_touches": len(snapshot.data_touches),
                "total_features": len(snapshot.features),
                "total_hazards": len(snapshot.hazards),
                "adapters_detected": [
                    (a.name, c) for a, c in applicable
                ],
                "adapters_used": adapters_used,
            },
        )

    def delta_scan(
        self, repo_path: str, changed_paths: list[str]
    ) -> ScanResult:
        """
        Perform an incremental re-scan for changed files only.

        This is more efficient than a full scan when only a few files changed.
        The previous snapshot is used as a base, and only the changed files
        are re-scanned and re-processed by adapters.

        Args:
            repo_path: Path to the repository root.
            changed_paths: List of file paths that changed (relative to root).

        Returns:
            Updated ScanResult.
        """
        if self._last_snapshot is None:
            logger.info("No previous snapshot, performing full scan")
            return self.scan(repo_path)

        start_time = time.monotonic()
        snapshot = self._last_snapshot

        root = Path(repo_path).resolve()

        # Remove old data for changed files
        changed_set = set(changed_paths)
        snapshot.files = [
            f for f in snapshot.files if f.path not in changed_set
        ]
        snapshot.symbols = [
            s for s in snapshot.symbols if s.file_path not in changed_set
        ]
        snapshot.interfaces = [
            i for i in snapshot.interfaces
            if not any(
                e.path in changed_set for e in i.evidence
            )
        ]
        snapshot.data_touches = [
            d for d in snapshot.data_touches
            if not any(
                e.path in changed_set for e in d.evidence
            )
        ]

        # Re-scan changed files
        delta_scanner = GenericScanner(
            max_file_size=self._scanner.max_file_size,
            skip_binary=self._scanner.skip_binary,
            skip_vendored=self._scanner.skip_vendored,
        )

        for rel_path in changed_paths:
            abs_path = root / rel_path
            if not abs_path.exists():
                continue  # File was deleted

            delta_snapshot = delta_scanner.scan(str(root))
            # Filter to only the changed files
            delta_snapshot.files = [
                f for f in delta_snapshot.files if f.path in changed_set
            ]
            delta_snapshot.symbols = [
                s for s in delta_snapshot.symbols if s.file_path in changed_set
            ]

            snapshot.merge(delta_snapshot)
            break  # Only need one scan of the root

        # Re-run adapters on the updated snapshot
        applicable = self._registry.detect_applicable(
            snapshot, threshold=self._adapter_threshold
        )
        adapters_used: list[str] = []

        for adapter, confidence in applicable:
            try:
                adapter_snapshot = adapter.extract(snapshot)
                snapshot.merge(adapter_snapshot)
                adapters_used.append(adapter.name)
            except Exception:
                logger.exception(
                    "Adapter '%s' failed during delta extraction", adapter.name
                )

        # Rebuild graph
        graph = KnowledgeGraph()
        graph.build_from_snapshot(snapshot)

        duration = time.monotonic() - start_time
        self._last_snapshot = snapshot

        return ScanResult(
            snapshot=snapshot,
            graph=graph,
            adapters_used=adapters_used,
            scan_duration_seconds=duration,
            metadata={"delta": True, "changed_paths": changed_paths},
        )

    # ------------------------------------------------------------------
    # Output generation
    # ------------------------------------------------------------------

    def generate_artifacts(
        self, result: ScanResult, output_dir: str
    ) -> list[str]:
        """
        Generate all output artifacts from a scan result.

        This is a convenience method that calls all output generators.
        Returns the list of generated file paths.

        Args:
            result: The ScanResult from a scan() or delta_scan() call.
            output_dir: Directory to write artifacts to.

        Returns:
            List of generated file paths.
        """
        from Framework.knowledge_map_engine.output.generators import (
            generate_all_artifacts,
        )

        return generate_all_artifacts(result, output_dir)
