"""
Generic Scanner - the always-on Layer A scanner.

Ingests a repository (directory or git checkout), detects languages,
classifies files, extracts symbols, and identifies hazards.
Works on any codebase regardless of framework or language.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from Framework.knowledge_map_engine.ir.models import (
    Confidence,
    DataTouch,
    DataTouchKind,
    Evidence,
    File,
    Hazard,
    HazardKind,
    RepoSnapshot,
)
from Framework.knowledge_map_engine.scanner.file_classifier import classify_file
from Framework.knowledge_map_engine.scanner.language_detect import detect_language
from Framework.knowledge_map_engine.scanner.symbol_extractor import extract_symbols

logger = logging.getLogger(__name__)

# Max file size to attempt reading (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Huge file threshold for hazard reporting (100 KB source, 500 KB config)
HUGE_SOURCE_THRESHOLD = 100 * 1024
HUGE_CONFIG_THRESHOLD = 500 * 1024

# Directories to always skip during scanning
SKIP_DIRS: set[str] = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".tox", ".nox",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".next", ".nuxt", ".output",
    "dist", "build", "out",
    ".venv", "venv", "env",
    ".eggs", "*.egg-info",
    "target",  # Rust/Java build output
    "Pods",  # iOS CocoaPods
}


class GenericScanner:
    """
    Universal code scanner that works on any repository.

    This is Layer A of the KME. It provides:
    - File enumeration and classification
    - Language detection
    - Symbol extraction (functions, classes, etc.)
    - Basic data touch detection (imports/requires)
    - Hazard identification (huge files, generated code, duplicates)
    """

    def __init__(
        self,
        max_file_size: int = MAX_FILE_SIZE,
        skip_binary: bool = True,
        skip_vendored: bool = True,
        skip_generated: bool = False,
    ) -> None:
        self.max_file_size = max_file_size
        self.skip_binary = skip_binary
        self.skip_vendored = skip_vendored
        self.skip_generated = skip_generated

    def scan(self, repo_path: str) -> RepoSnapshot:
        """
        Scan a repository directory and produce a RepoSnapshot.

        Args:
            repo_path: Absolute or relative path to the repository root.

        Returns:
            RepoSnapshot populated with files, symbols, and hazards.
        """
        root = Path(repo_path).resolve()
        if not root.is_dir():
            raise ValueError(f"Repository path is not a directory: {root}")

        snapshot = RepoSnapshot(root_path=str(root))

        logger.info("Starting generic scan of %s", root)

        # Phase 1: Enumerate and classify files
        self._enumerate_files(root, snapshot)
        logger.info("Found %d files", len(snapshot.files))

        # Phase 2: Extract symbols from source files
        self._extract_all_symbols(root, snapshot)
        logger.info("Extracted %d symbols", len(snapshot.symbols))

        # Phase 3: Detect basic data touches
        self._detect_data_touches(root, snapshot)
        logger.info("Found %d data touches", len(snapshot.data_touches))

        # Phase 4: Identify hazards
        self._identify_hazards(snapshot)
        logger.info("Identified %d hazards", len(snapshot.hazards))

        # Phase 5: Compute metadata
        snapshot.metadata["languages"] = self._language_summary(snapshot)
        snapshot.metadata["total_files"] = len(snapshot.files)
        snapshot.metadata["total_symbols"] = len(snapshot.symbols)
        snapshot.metadata["scanner"] = "generic"

        snapshot.record_provenance("generic_scanner", "files", len(snapshot.files))
        snapshot.record_provenance("generic_scanner", "symbols", len(snapshot.symbols))

        return snapshot

    # ------------------------------------------------------------------
    # Phase 1: File enumeration
    # ------------------------------------------------------------------

    def _enumerate_files(self, root: Path, snapshot: RepoSnapshot) -> None:
        """Walk the repository tree and classify each file."""
        for dirpath, dirnames, filenames in os.walk(root):
            # Filter out skip dirs in-place to prevent descending
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS and not d.startswith(".")
            ]

            for fname in filenames:
                abs_path = Path(dirpath) / fname
                rel_path = str(abs_path.relative_to(root))

                try:
                    stat = abs_path.stat()
                except OSError:
                    continue

                classification = classify_file(rel_path)

                if self.skip_binary and classification.is_binary:
                    continue
                if self.skip_vendored and classification.is_vendored:
                    continue
                if self.skip_generated and classification.is_generated:
                    continue

                # Detect language
                first_line = None
                if stat.st_size > 0 and stat.st_size <= self.max_file_size:
                    try:
                        with open(abs_path, "r", errors="ignore") as f:
                            first_line = f.readline()
                    except OSError:
                        pass

                language = detect_language(rel_path, first_line)

                file_obj = File(
                    path=rel_path,
                    language=language,
                    size_bytes=stat.st_size,
                    is_generated=classification.is_generated,
                    is_test=classification.is_test,
                    is_config=classification.is_config,
                    is_documentation=classification.is_documentation,
                )

                snapshot.files.append(file_obj)

    # ------------------------------------------------------------------
    # Phase 2: Symbol extraction
    # ------------------------------------------------------------------

    def _extract_all_symbols(
        self, root: Path, snapshot: RepoSnapshot
    ) -> None:
        """Extract symbols from all source files."""
        source_languages = {
            "python", "javascript", "typescript", "go", "rust",
            "java", "kotlin", "csharp", "ruby", "swift", "dart",
            "elixir", "haskell", "lua", "perl", "php", "scala",
            "cpp", "c", "objc",
        }

        for file_obj in snapshot.files:
            if file_obj.language not in source_languages:
                continue
            if file_obj.is_generated and self.skip_generated:
                continue
            if file_obj.size_bytes > self.max_file_size:
                continue

            abs_path = root / file_obj.path
            try:
                content = abs_path.read_text(errors="ignore")
            except OSError:
                logger.debug("Could not read file: %s", file_obj.path)
                continue

            symbols = extract_symbols(file_obj.path, content, file_obj.language)
            snapshot.symbols.extend(symbols)

    # ------------------------------------------------------------------
    # Phase 3: Data touch detection
    # ------------------------------------------------------------------

    def _detect_data_touches(
        self, root: Path, snapshot: RepoSnapshot
    ) -> None:
        """Detect basic data interactions from import patterns and common APIs."""
        db_indicators = {
            "sqlite", "psycopg", "mysql", "pymongo", "sqlalchemy",
            "django.db", "sequelize", "typeorm", "prisma", "knex",
            "mongoose", "pg", "database/sql", "gorm", "diesel",
            "activerecord", "ecto", "sqlx",
        }
        cache_indicators = {
            "redis", "memcached", "cache", "lru_cache",
        }
        queue_indicators = {
            "celery", "rq", "bull", "rabbitmq", "amqp", "kafka",
            "sqs", "pubsub", "nats",
        }
        network_indicators = {
            "requests", "httpx", "aiohttp", "urllib", "fetch",
            "axios", "http.client", "net/http", "reqwest",
        }

        for file_obj in snapshot.files:
            if file_obj.language == "unknown" or file_obj.is_generated:
                continue
            if file_obj.size_bytes > self.max_file_size:
                continue

            abs_path = root / file_obj.path
            try:
                content = abs_path.read_text(errors="ignore")
            except OSError:
                continue

            content_lower = content.lower()

            for indicator in db_indicators:
                if indicator in content_lower:
                    snapshot.data_touches.append(DataTouch(
                        kind=DataTouchKind.DATABASE,
                        name=f"db:{indicator}",
                        target=indicator,
                        evidence=[Evidence(
                            path=file_obj.path,
                            confidence=Confidence.LOW,
                        )],
                        confidence=Confidence.LOW,
                    ))
                    break  # One per file

            for indicator in cache_indicators:
                if indicator in content_lower:
                    snapshot.data_touches.append(DataTouch(
                        kind=DataTouchKind.CACHE,
                        name=f"cache:{indicator}",
                        target=indicator,
                        evidence=[Evidence(
                            path=file_obj.path,
                            confidence=Confidence.LOW,
                        )],
                        confidence=Confidence.LOW,
                    ))
                    break

            for indicator in queue_indicators:
                if indicator in content_lower:
                    snapshot.data_touches.append(DataTouch(
                        kind=DataTouchKind.QUEUE,
                        name=f"queue:{indicator}",
                        target=indicator,
                        evidence=[Evidence(
                            path=file_obj.path,
                            confidence=Confidence.LOW,
                        )],
                        confidence=Confidence.LOW,
                    ))
                    break

            for indicator in network_indicators:
                if indicator in content_lower:
                    snapshot.data_touches.append(DataTouch(
                        kind=DataTouchKind.NETWORK,
                        name=f"network:{indicator}",
                        target=indicator,
                        evidence=[Evidence(
                            path=file_obj.path,
                            confidence=Confidence.LOW,
                        )],
                        confidence=Confidence.LOW,
                    ))
                    break

    # ------------------------------------------------------------------
    # Phase 4: Hazard identification
    # ------------------------------------------------------------------

    def _identify_hazards(self, snapshot: RepoSnapshot) -> None:
        """Identify mapping hazards and sources of uncertainty."""
        # Huge files
        for f in snapshot.files:
            threshold = (
                HUGE_CONFIG_THRESHOLD if f.is_config else HUGE_SOURCE_THRESHOLD
            )
            if f.size_bytes > threshold and not f.is_generated:
                snapshot.hazards.append(Hazard(
                    kind=HazardKind.HUGE_FILE,
                    description=f"File {f.path} is {f.size_bytes:,} bytes",
                    severity="medium",
                    affected_paths=[f.path],
                    evidence=[Evidence(path=f.path, confidence=Confidence.HIGH)],
                ))

        # Generated code that was still scanned
        generated_files = [f.path for f in snapshot.files if f.is_generated]
        if generated_files:
            snapshot.hazards.append(Hazard(
                kind=HazardKind.GENERATED_CODE,
                description=f"{len(generated_files)} generated/lock files detected",
                severity="low",
                affected_paths=generated_files[:20],  # Cap at 20
            ))

        # Duplicate symbol definitions
        symbol_names: dict[str, list[str]] = {}
        for s in snapshot.symbols:
            key = s.name
            symbol_names.setdefault(key, []).append(s.file_path)

        for name, paths in symbol_names.items():
            unique_paths = list(set(paths))
            if len(unique_paths) > 2:
                snapshot.hazards.append(Hazard(
                    kind=HazardKind.DUPLICATE_DEFINITIONS,
                    description=(
                        f"Symbol '{name}' defined in {len(unique_paths)} files"
                    ),
                    severity="medium",
                    affected_paths=unique_paths[:10],
                    affected_symbols=[name],
                ))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _language_summary(snapshot: RepoSnapshot) -> dict[str, int]:
        """Count files per language."""
        counts: dict[str, int] = {}
        for f in snapshot.files:
            counts[f.language] = counts.get(f.language, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
