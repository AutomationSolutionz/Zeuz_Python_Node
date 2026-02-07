"""
Universal IR models for the Knowledge Map Engine.

These dataclasses define the adapter-neutral intermediate representation.
All adapters and the core scanner produce instances of these types.
No framework-specific fields belong here.
"""

from __future__ import annotations

import hashlib
import enum
from dataclasses import dataclass, field
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Confidence(enum.Enum):
    """Confidence level for extracted facts."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SymbolKind(enum.Enum):
    """Kind of code symbol."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    COMPONENT = "component"
    MODULE = "module"
    CONFIG = "config"
    CONSTANT = "constant"
    VARIABLE = "variable"
    TYPE = "type"
    UNKNOWN = "unknown"


class InterfaceKind(enum.Enum):
    """Kind of interface / API surface."""
    HTTP = "http"
    GRPC = "grpc"
    CLI = "cli"
    UI = "ui"
    JOB = "job"
    LIB = "lib"
    WEBSOCKET = "websocket"
    EVENT = "event"
    IPC = "ipc"
    UNKNOWN = "unknown"


class DataTouchKind(enum.Enum):
    """Kind of external data interaction."""
    DATABASE = "database"
    FILE = "file"
    QUEUE = "queue"
    CACHE = "cache"
    NETWORK = "network"
    ENVIRONMENT = "environment"
    UNKNOWN = "unknown"


class HazardKind(enum.Enum):
    """Kind of mapping hazard / uncertainty."""
    DUPLICATE_DEFINITIONS = "duplicate_definitions"
    HUGE_FILE = "huge_file"
    GENERATED_CODE = "generated_code"
    UNCERTAIN_MAPPING = "uncertain_mapping"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    DEAD_CODE = "dead_code"
    MISSING_TESTS = "missing_tests"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

@dataclass
class Evidence:
    """A citation pointing to a specific location in source code."""
    path: str
    symbol: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    snippet: Optional[str] = None
    confidence: Confidence = Confidence.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"path": self.path}
        if self.symbol:
            d["symbol"] = self.symbol
        if self.line_start is not None:
            d["line_start"] = self.line_start
        if self.line_end is not None:
            d["line_end"] = self.line_end
        if self.snippet:
            d["snippet"] = self.snippet
        d["confidence"] = self.confidence.value
        return d


# ---------------------------------------------------------------------------
# File
# ---------------------------------------------------------------------------

@dataclass
class File:
    """A single file in the repository."""
    path: str
    language: str = "unknown"
    size_bytes: int = 0
    hash: str = ""
    is_generated: bool = False
    is_test: bool = False
    is_config: bool = False
    is_documentation: bool = False

    def compute_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of file content."""
        self.hash = hashlib.sha256(content).hexdigest()
        return self.hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "language": self.language,
            "size_bytes": self.size_bytes,
            "hash": self.hash,
            "is_generated": self.is_generated,
            "is_test": self.is_test,
            "is_config": self.is_config,
            "is_documentation": self.is_documentation,
        }


# ---------------------------------------------------------------------------
# Symbol
# ---------------------------------------------------------------------------

@dataclass
class Symbol:
    """A code symbol (function, class, component, etc.)."""
    name: str
    kind: SymbolKind
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    parent: Optional[str] = None  # parent symbol name (e.g. class for method)
    docstring: Optional[str] = None
    signature: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    @property
    def qualified_name(self) -> str:
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "kind": self.kind.value,
            "file_path": self.file_path,
            "qualified_name": self.qualified_name,
        }
        if self.line_start is not None:
            d["line_start"] = self.line_start
        if self.line_end is not None:
            d["line_end"] = self.line_end
        if self.parent:
            d["parent"] = self.parent
        if self.docstring:
            d["docstring"] = self.docstring
        if self.signature:
            d["signature"] = self.signature
        if self.dependencies:
            d["dependencies"] = self.dependencies
        if self.evidence:
            d["evidence"] = [e.to_dict() for e in self.evidence]
        return d


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------

@dataclass
class Interface:
    """
    An interface / API surface exposed by the codebase.

    This is the universal replacement for framework-specific "Endpoint" thinking.
    An interface can be an HTTP route, gRPC method, CLI command, UI action,
    background job entrypoint, or public library API.
    """
    kind: InterfaceKind
    name: str
    handler_symbol: Optional[str] = None
    method: Optional[str] = None  # HTTP method, gRPC method type, etc.
    path_pattern: Optional[str] = None  # route pattern, CLI subcommand, etc.
    parameters: list[dict[str, Any]] = field(default_factory=list)
    response_schema: Optional[dict[str, Any]] = None
    evidence: list[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "kind": self.kind.value,
            "name": self.name,
            "confidence": self.confidence.value,
        }
        if self.handler_symbol:
            d["handler_symbol"] = self.handler_symbol
        if self.method:
            d["method"] = self.method
        if self.path_pattern:
            d["path_pattern"] = self.path_pattern
        if self.parameters:
            d["parameters"] = self.parameters
        if self.response_schema:
            d["response_schema"] = self.response_schema
        if self.evidence:
            d["evidence"] = [e.to_dict() for e in self.evidence]
        if self.metadata:
            d["metadata"] = self.metadata
        return d


# ---------------------------------------------------------------------------
# DataTouch
# ---------------------------------------------------------------------------

@dataclass
class DataTouch:
    """An interaction with external data (db, file, queue, cache, network)."""
    kind: DataTouchKind
    name: str
    symbol: Optional[str] = None  # the symbol performing the touch
    target: Optional[str] = None  # table name, file path, queue name, URL, etc.
    operation: Optional[str] = None  # read, write, delete, etc.
    evidence: list[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "kind": self.kind.value,
            "name": self.name,
            "confidence": self.confidence.value,
        }
        if self.symbol:
            d["symbol"] = self.symbol
        if self.target:
            d["target"] = self.target
        if self.operation:
            d["operation"] = self.operation
        if self.evidence:
            d["evidence"] = [e.to_dict() for e in self.evidence]
        return d


# ---------------------------------------------------------------------------
# Feature
# ---------------------------------------------------------------------------

@dataclass
class Feature:
    """A human-level concept / feature of the system."""
    name: str
    description: str = ""
    symbols: list[str] = field(default_factory=list)  # qualified symbol names
    interfaces: list[str] = field(default_factory=list)  # interface names
    data_touches: list[str] = field(default_factory=list)  # data touch names
    evidence: list[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "confidence": self.confidence.value,
        }
        if self.symbols:
            d["symbols"] = self.symbols
        if self.interfaces:
            d["interfaces"] = self.interfaces
        if self.data_touches:
            d["data_touches"] = self.data_touches
        if self.evidence:
            d["evidence"] = [e.to_dict() for e in self.evidence]
        return d


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

@dataclass
class Workflow:
    """A sequence of features forming a user-facing workflow."""
    name: str
    description: str = ""
    steps: list[str] = field(default_factory=list)  # feature names in order
    entry_interface: Optional[str] = None
    evidence: list[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "confidence": self.confidence.value,
        }
        if self.steps:
            d["steps"] = self.steps
        if self.entry_interface:
            d["entry_interface"] = self.entry_interface
        if self.evidence:
            d["evidence"] = [e.to_dict() for e in self.evidence]
        return d


# ---------------------------------------------------------------------------
# Hazard
# ---------------------------------------------------------------------------

@dataclass
class Hazard:
    """A mapping hazard or source of uncertainty."""
    kind: HazardKind
    description: str
    severity: str = "medium"  # low, medium, high
    affected_paths: list[str] = field(default_factory=list)
    affected_symbols: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "kind": self.kind.value,
            "description": self.description,
            "severity": self.severity,
        }
        if self.affected_paths:
            d["affected_paths"] = self.affected_paths
        if self.affected_symbols:
            d["affected_symbols"] = self.affected_symbols
        if self.evidence:
            d["evidence"] = [e.to_dict() for e in self.evidence]
        return d


# ---------------------------------------------------------------------------
# RepoSnapshot
# ---------------------------------------------------------------------------

@dataclass
class RepoSnapshot:
    """
    Complete snapshot of a repository analysis.

    This is the top-level container holding all extracted IR objects.
    Both the core scanner and adapters contribute to this snapshot.
    """
    root_path: str
    files: list[File] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)
    data_touches: list[DataTouch] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)
    hazards: list[Hazard] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Adapter provenance: tracks which adapter contributed which facts
    _provenance: dict[str, list[str]] = field(default_factory=dict)

    def record_provenance(self, adapter_name: str, fact_type: str, count: int) -> None:
        """Record that an adapter contributed facts."""
        key = f"{adapter_name}:{fact_type}"
        if key not in self._provenance:
            self._provenance[key] = []
        self._provenance[key].append(f"count={count}")

    @property
    def file_index(self) -> dict[str, File]:
        """Index files by path for quick lookup."""
        return {f.path: f for f in self.files}

    @property
    def symbol_index(self) -> dict[str, Symbol]:
        """Index symbols by qualified name for quick lookup."""
        return {s.qualified_name: s for s in self.symbols}

    def merge(self, other: RepoSnapshot) -> None:
        """Merge another snapshot's facts into this one (used by adapters).

        For symbols, adapter-provided facts with more specific kinds
        (e.g., COMPONENT vs FUNCTION) upgrade existing generic symbols.
        """
        existing_paths = {f.path for f in self.files}
        for f in other.files:
            if f.path not in existing_paths:
                self.files.append(f)

        # Build index for upgrade-merge of symbols
        symbol_idx: dict[str, int] = {}
        for i, s in enumerate(self.symbols):
            symbol_idx[s.qualified_name] = i

        # More specific kinds that should upgrade generic ones
        _specific_kinds = {
            SymbolKind.COMPONENT, SymbolKind.MODULE, SymbolKind.CONFIG,
        }

        for s in other.symbols:
            if s.qualified_name in symbol_idx:
                # Upgrade if the new symbol has a more specific kind
                idx = symbol_idx[s.qualified_name]
                existing = self.symbols[idx]
                if (
                    s.kind in _specific_kinds
                    and existing.kind not in _specific_kinds
                ):
                    self.symbols[idx] = s
            else:
                symbol_idx[s.qualified_name] = len(self.symbols)
                self.symbols.append(s)

        self.interfaces.extend(other.interfaces)
        self.data_touches.extend(other.data_touches)
        self.features.extend(other.features)
        self.workflows.extend(other.workflows)
        self.hazards.extend(other.hazards)

        for k, v in other._provenance.items():
            self._provenance.setdefault(k, []).extend(v)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_path": self.root_path,
            "files": [f.to_dict() for f in self.files],
            "symbols": [s.to_dict() for s in self.symbols],
            "interfaces": [i.to_dict() for i in self.interfaces],
            "data_touches": [d.to_dict() for d in self.data_touches],
            "features": [f.to_dict() for f in self.features],
            "workflows": [w.to_dict() for w in self.workflows],
            "hazards": [h.to_dict() for h in self.hazards],
            "metadata": self.metadata,
            "provenance": self._provenance,
        }
