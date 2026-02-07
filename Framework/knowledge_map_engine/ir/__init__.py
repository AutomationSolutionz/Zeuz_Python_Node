"""
Universal Intermediate Representation (IR) for the Knowledge Map Engine.

All core components and adapters produce these same IR shapes.
No framework-specific fields allowed at this layer.
"""

from Framework.knowledge_map_engine.ir.models import (
    Confidence,
    DataTouch,
    DataTouchKind,
    Evidence,
    Feature,
    File,
    Hazard,
    HazardKind,
    Interface,
    InterfaceKind,
    RepoSnapshot,
    Symbol,
    SymbolKind,
    Workflow,
)

__all__ = [
    "Confidence",
    "DataTouch",
    "DataTouchKind",
    "Evidence",
    "Feature",
    "File",
    "Hazard",
    "HazardKind",
    "Interface",
    "InterfaceKind",
    "RepoSnapshot",
    "Symbol",
    "SymbolKind",
    "Workflow",
]
