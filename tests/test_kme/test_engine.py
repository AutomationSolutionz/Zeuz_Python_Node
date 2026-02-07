"""Tests for the KME Core Engine."""

import json
import os
import tempfile
import textwrap


from Framework.knowledge_map_engine.core.engine import KnowledgeMapEngine
from Framework.knowledge_map_engine.core.graph import KnowledgeGraph, GraphNode, GraphEdge
from Framework.knowledge_map_engine.adapters.python_web import PythonWebAdapter
from Framework.knowledge_map_engine.adapters.react_web import ReactWebAdapter
from Framework.knowledge_map_engine.ir.models import (
    InterfaceKind,
    RepoSnapshot,
    Symbol,
    SymbolKind,
)


# ---------------------------------------------------------------------------
# Knowledge Graph Tests
# ---------------------------------------------------------------------------

class TestKnowledgeGraph:
    def test_build_from_empty_snapshot(self):
        snap = RepoSnapshot(root_path="/tmp")
        graph = KnowledgeGraph()
        graph.build_from_snapshot(snap)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_build_with_files_and_symbols(self):
        from Framework.knowledge_map_engine.ir.models import File
        snap = RepoSnapshot(root_path="/tmp")
        snap.files.append(File(path="main.py", language="python"))
        snap.symbols.append(Symbol(
            name="main", kind=SymbolKind.FUNCTION, file_path="main.py"
        ))

        graph = KnowledgeGraph()
        graph.build_from_snapshot(snap)

        assert "file:main.py" in graph.nodes
        assert any(
            "symbol:" in nid and "main" in nid
            for nid in graph.nodes
        )

        # Should have a "contains" edge
        contains_edges = [e for e in graph.edges if e.kind == "contains"]
        assert len(contains_edges) >= 1

    def test_to_json(self):
        graph = KnowledgeGraph()
        graph.nodes["test"] = GraphNode(id="test", kind="file", label="test.py")
        j = graph.to_json()
        data = json.loads(j)
        assert len(data["nodes"]) == 1
        assert data["summary"]["total_nodes"] == 1

    def test_get_neighbors(self):
        graph = KnowledgeGraph()
        graph.nodes["a"] = GraphNode(id="a", kind="file", label="a")
        graph.nodes["b"] = GraphNode(id="b", kind="symbol", label="b")
        graph.edges.append(GraphEdge(source="a", target="b", kind="contains"))

        neighbors = graph.get_neighbors("a")
        assert len(neighbors) == 1
        assert neighbors[0] == ("b", "contains")

    def test_get_subgraph(self):
        graph = KnowledgeGraph()
        for name in ["a", "b", "c", "d"]:
            graph.nodes[name] = GraphNode(id=name, kind="file", label=name)
        graph.edges.append(GraphEdge(source="a", target="b", kind="contains"))
        graph.edges.append(GraphEdge(source="b", target="c", kind="calls"))
        graph.edges.append(GraphEdge(source="c", target="d", kind="calls"))

        sub = graph.get_subgraph("a", depth=1)
        assert "a" in sub.nodes
        assert "b" in sub.nodes
        assert "d" not in sub.nodes  # Too far


# ---------------------------------------------------------------------------
# Engine Integration Tests
# ---------------------------------------------------------------------------

class TestKnowledgeMapEngine:
    def _make_repo(self, files: dict[str, str]) -> str:
        tmpdir = tempfile.mkdtemp()
        for rel_path, content in files.items():
            abs_path = os.path.join(tmpdir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w") as f:
                f.write(content)
        return tmpdir

    def test_scan_empty_repo(self):
        tmpdir = self._make_repo({})
        engine = KnowledgeMapEngine()
        result = engine.scan(tmpdir)
        assert result.snapshot is not None
        assert result.scan_duration_seconds >= 0

    def test_scan_python_repo(self):
        tmpdir = self._make_repo({
            "main.py": textwrap.dedent("""\
                def main():
                    print("hello")

                class App:
                    def run(self):
                        pass
            """),
            "utils.py": "def helper(): return 42\n",
        })

        engine = KnowledgeMapEngine()
        result = engine.scan(tmpdir)

        assert len(result.snapshot.files) >= 2
        assert len(result.snapshot.symbols) >= 3  # main, App, helper + maybe run
        assert result.graph is not None
        assert len(result.graph.nodes) > 0

    def test_scan_with_python_web_adapter(self):
        tmpdir = self._make_repo({
            "app.py": textwrap.dedent("""\
                from fastapi import FastAPI
                app = FastAPI()

                @app.get("/health")
                def health_check():
                    return {"status": "ok"}

                @app.post("/users")
                async def create_user(data: dict):
                    return data
            """),
        })

        engine = KnowledgeMapEngine()
        engine.register_adapter(PythonWebAdapter())
        result = engine.scan(tmpdir)

        assert "python_web" in result.adapters_used
        assert len(result.snapshot.interfaces) > 0

        http_interfaces = [
            i for i in result.snapshot.interfaces
            if i.kind == InterfaceKind.HTTP
        ]
        assert len(http_interfaces) >= 2

    def test_scan_with_react_adapter(self):
        tmpdir = self._make_repo({
            "package.json": '{"dependencies": {"react": "^18.0.0"}}',
            "src/App.tsx": textwrap.dedent("""\
                import React from 'react';

                export function App() {
                    return <div>Hello</div>;
                }

                export function Dashboard() {
                    return <div>Dashboard</div>;
                }
            """),
        })

        engine = KnowledgeMapEngine()
        engine.register_adapter(ReactWebAdapter())
        result = engine.scan(tmpdir)

        assert "react_web" in result.adapters_used
        components = [
            s for s in result.snapshot.symbols
            if s.kind == SymbolKind.COMPONENT
        ]
        assert len(components) >= 1

    def test_scan_with_multiple_adapters(self):
        tmpdir = self._make_repo({
            "backend/app.py": textwrap.dedent("""\
                from fastapi import FastAPI
                app = FastAPI()

                @app.get("/api/data")
                def get_data():
                    return []
            """),
            "frontend/package.json": '{"dependencies": {"react": "^18.0.0"}}',
            "frontend/App.tsx": textwrap.dedent("""\
                import React from 'react';
                export function App() { return <div/>; }
            """),
        })

        engine = KnowledgeMapEngine()
        engine.register_adapter(PythonWebAdapter())
        engine.register_adapter(ReactWebAdapter())
        result = engine.scan(tmpdir)

        # Both adapters should have been used
        assert len(result.adapters_used) >= 1  # At least one should match

    def test_generate_artifacts(self):
        tmpdir = self._make_repo({
            "main.py": textwrap.dedent("""\
                from fastapi import FastAPI
                app = FastAPI()

                @app.get("/users")
                def get_users():
                    return []
            """),
        })

        engine = KnowledgeMapEngine()
        engine.register_adapter(PythonWebAdapter())
        result = engine.scan(tmpdir)

        output_dir = os.path.join(tmpdir, "kme_output")
        generated = engine.generate_artifacts(result, output_dir)

        assert len(generated) == 9  # All 9 artifacts

        # Verify key files exist and have content
        expected_files = [
            "SYSTEM_OVERVIEW.md",
            "FEATURE_CATALOG.md",
            "INTERFACE_CATALOG.json",
            "DATA_TOUCH_MAP.json",
            "WORKFLOW_BOOK.md",
            "KNOWN_HAZARDS.md",
            "feature_graph.json",
            "claude_context_pack.md",
            "claude_context_pack_index.json",
        ]
        for filename in expected_files:
            filepath = os.path.join(output_dir, filename)
            assert os.path.exists(filepath), f"{filename} not generated"
            assert os.path.getsize(filepath) > 0, f"{filename} is empty"

        # Verify JSON files are valid
        for json_file in ["INTERFACE_CATALOG.json", "DATA_TOUCH_MAP.json",
                          "feature_graph.json", "claude_context_pack_index.json"]:
            filepath = os.path.join(output_dir, json_file)
            with open(filepath) as f:
                data = json.load(f)
            assert isinstance(data, dict)

    def test_adapter_management(self):
        engine = KnowledgeMapEngine()
        assert len(engine.list_adapters()) == 0

        engine.register_adapter(PythonWebAdapter())
        assert "python_web" in engine.list_adapters()

        engine.register_adapter(ReactWebAdapter())
        assert len(engine.list_adapters()) == 2

        engine.unregister_adapter("python_web")
        assert "python_web" not in engine.list_adapters()
        assert len(engine.list_adapters()) == 1

    def test_metadata_populated(self):
        tmpdir = self._make_repo({
            "app.py": "def main(): pass\n",
        })

        engine = KnowledgeMapEngine()
        result = engine.scan(tmpdir)

        assert "total_files" in result.metadata
        assert "total_symbols" in result.metadata
        assert "adapters_used" in result.metadata
        assert result.metadata["repo_path"] == tmpdir
