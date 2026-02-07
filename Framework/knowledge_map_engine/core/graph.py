"""
Knowledge Graph - builds a feature-level dependency graph from the IR.

Nodes represent symbols, interfaces, data touches, and features.
Edges represent relationships: calls, implements, uses, touches.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from Framework.knowledge_map_engine.ir.models import RepoSnapshot

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """A node in the knowledge graph."""
    id: str
    kind: str  # "symbol", "interface", "data_touch", "feature", "file"
    label: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "metadata": self.metadata,
        }


@dataclass
class GraphEdge:
    """An edge in the knowledge graph."""
    source: str
    target: str
    kind: str  # "calls", "implements", "uses", "contains", "touches"
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
        }
        if self.weight != 1.0:
            d["weight"] = self.weight
        if self.metadata:
            d["metadata"] = self.metadata
        return d


class KnowledgeGraph:
    """
    Builds and manages a knowledge graph from a RepoSnapshot.

    The graph connects symbols to their files, interfaces to handler symbols,
    data touches to their performing symbols, and features to all of the above.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def build_from_snapshot(self, snapshot: RepoSnapshot) -> None:
        """
        Populate the graph from a RepoSnapshot.

        Creates nodes for files, symbols, interfaces, data touches, and features.
        Creates edges for containment and reference relationships.
        """
        self._add_file_nodes(snapshot)
        self._add_symbol_nodes(snapshot)
        self._add_interface_nodes(snapshot)
        self._add_data_touch_nodes(snapshot)
        self._add_feature_nodes(snapshot)

        logger.info(
            "Built knowledge graph: %d nodes, %d edges",
            len(self.nodes),
            len(self.edges),
        )

    def _add_file_nodes(self, snapshot: RepoSnapshot) -> None:
        """Add file nodes."""
        for f in snapshot.files:
            if f.is_generated:
                continue
            node_id = f"file:{f.path}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                kind="file",
                label=f.path,
                metadata={"language": f.language, "size": f.size_bytes},
            )

    def _add_symbol_nodes(self, snapshot: RepoSnapshot) -> None:
        """Add symbol nodes and link them to files."""
        for s in snapshot.symbols:
            node_id = f"symbol:{s.qualified_name}@{s.file_path}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                kind="symbol",
                label=s.qualified_name,
                metadata={
                    "symbol_kind": s.kind.value,
                    "line_start": s.line_start,
                },
            )

            # Edge: file contains symbol
            file_id = f"file:{s.file_path}"
            if file_id in self.nodes:
                self.edges.append(GraphEdge(
                    source=file_id,
                    target=node_id,
                    kind="contains",
                ))

            # Edges: symbol depends on other symbols
            for dep in s.dependencies:
                self.edges.append(GraphEdge(
                    source=node_id,
                    target=f"symbol:{dep}",
                    kind="depends_on",
                ))

    def _add_interface_nodes(self, snapshot: RepoSnapshot) -> None:
        """Add interface nodes and link to handler symbols."""
        for iface in snapshot.interfaces:
            node_id = f"interface:{iface.kind.value}:{iface.name}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                kind="interface",
                label=f"[{iface.kind.value}] {iface.name}",
                metadata={
                    "method": iface.method,
                    "path_pattern": iface.path_pattern,
                    "confidence": iface.confidence.value,
                },
            )

            # Edge: interface implemented by symbol
            if iface.handler_symbol:
                self.edges.append(GraphEdge(
                    source=node_id,
                    target=f"symbol:{iface.handler_symbol}",
                    kind="implemented_by",
                ))

    def _add_data_touch_nodes(self, snapshot: RepoSnapshot) -> None:
        """Add data touch nodes."""
        for dt in snapshot.data_touches:
            node_id = f"data_touch:{dt.kind.value}:{dt.name}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                kind="data_touch",
                label=f"[{dt.kind.value}] {dt.name}",
                metadata={
                    "target": dt.target,
                    "operation": dt.operation,
                    "confidence": dt.confidence.value,
                },
            )

            # Edge: symbol touches data
            if dt.symbol:
                self.edges.append(GraphEdge(
                    source=f"symbol:{dt.symbol}",
                    target=node_id,
                    kind="touches",
                ))

    def _add_feature_nodes(self, snapshot: RepoSnapshot) -> None:
        """Add feature nodes and link to symbols/interfaces/data_touches."""
        for feat in snapshot.features:
            node_id = f"feature:{feat.name}"
            self.nodes[node_id] = GraphNode(
                id=node_id,
                kind="feature",
                label=feat.name,
                metadata={
                    "description": feat.description,
                    "confidence": feat.confidence.value,
                },
            )

            for sym_name in feat.symbols:
                self.edges.append(GraphEdge(
                    source=node_id,
                    target=f"symbol:{sym_name}",
                    kind="uses",
                ))

            for iface_name in feat.interfaces:
                self.edges.append(GraphEdge(
                    source=node_id,
                    target=f"interface:{iface_name}",
                    kind="exposes",
                ))

            for dt_name in feat.data_touches:
                self.edges.append(GraphEdge(
                    source=node_id,
                    target=f"data_touch:{dt_name}",
                    kind="touches",
                ))

    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to a dictionary."""
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "summary": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "node_kinds": self._count_by_kind(),
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize graph to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def _count_by_kind(self) -> dict[str, int]:
        """Count nodes by kind."""
        counts: dict[str, int] = {}
        for node in self.nodes.values():
            counts[node.kind] = counts.get(node.kind, 0) + 1
        return counts

    def get_neighbors(self, node_id: str) -> list[tuple[str, str]]:
        """Get neighboring node IDs and edge kinds for a given node."""
        neighbors: list[tuple[str, str]] = []
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.append((edge.target, edge.kind))
            elif edge.target == node_id:
                neighbors.append((edge.source, edge.kind))
        return neighbors

    def get_subgraph(self, root_id: str, depth: int = 2) -> KnowledgeGraph:
        """Extract a subgraph rooted at a given node up to a certain depth."""
        visited: set[str] = set()
        frontier: set[str] = {root_id}
        sub = KnowledgeGraph()

        for _ in range(depth + 1):
            next_frontier: set[str] = set()
            for nid in frontier:
                if nid in visited:
                    continue
                visited.add(nid)
                if nid in self.nodes:
                    sub.nodes[nid] = self.nodes[nid]
                for neighbor_id, _ in self.get_neighbors(nid):
                    if neighbor_id not in visited:
                        next_frontier.add(neighbor_id)
            frontier = next_frontier

        for edge in self.edges:
            if edge.source in visited and edge.target in visited:
                sub.edges.append(edge)

        return sub
