"""Tests for the Universal IR models."""

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


class TestEvidence:
    def test_basic_creation(self):
        ev = Evidence(path="src/main.py", symbol="main", line_start=10)
        assert ev.path == "src/main.py"
        assert ev.symbol == "main"
        assert ev.line_start == 10
        assert ev.confidence == Confidence.MEDIUM

    def test_to_dict_minimal(self):
        ev = Evidence(path="file.py")
        d = ev.to_dict()
        assert d["path"] == "file.py"
        assert "symbol" not in d
        assert d["confidence"] == "medium"

    def test_to_dict_full(self):
        ev = Evidence(
            path="src/app.py",
            symbol="handler",
            line_start=5,
            line_end=20,
            snippet="def handler():",
            confidence=Confidence.HIGH,
        )
        d = ev.to_dict()
        assert d["path"] == "src/app.py"
        assert d["symbol"] == "handler"
        assert d["line_start"] == 5
        assert d["line_end"] == 20
        assert d["snippet"] == "def handler():"
        assert d["confidence"] == "high"


class TestFile:
    def test_basic_creation(self):
        f = File(path="src/main.py", language="python", size_bytes=1024)
        assert f.path == "src/main.py"
        assert f.language == "python"
        assert f.is_generated is False

    def test_compute_hash(self):
        f = File(path="test.py")
        h = f.compute_hash(b"hello world")
        assert len(h) == 64  # SHA-256 hex digest
        assert f.hash == h

    def test_to_dict(self):
        f = File(path="x.py", language="python", size_bytes=100, is_test=True)
        d = f.to_dict()
        assert d["path"] == "x.py"
        assert d["is_test"] is True


class TestSymbol:
    def test_qualified_name_no_parent(self):
        s = Symbol(name="foo", kind=SymbolKind.FUNCTION, file_path="a.py")
        assert s.qualified_name == "foo"

    def test_qualified_name_with_parent(self):
        s = Symbol(
            name="bar", kind=SymbolKind.METHOD,
            file_path="a.py", parent="MyClass"
        )
        assert s.qualified_name == "MyClass.bar"

    def test_to_dict(self):
        s = Symbol(
            name="MyClass",
            kind=SymbolKind.CLASS,
            file_path="src/models.py",
            line_start=10,
            docstring="A model class",
            dependencies=["Base"],
        )
        d = s.to_dict()
        assert d["name"] == "MyClass"
        assert d["kind"] == "class"
        assert d["dependencies"] == ["Base"]


class TestInterface:
    def test_http_interface(self):
        iface = Interface(
            kind=InterfaceKind.HTTP,
            name="GET /users",
            handler_symbol="get_users",
            method="GET",
            path_pattern="/users",
            confidence=Confidence.HIGH,
        )
        d = iface.to_dict()
        assert d["kind"] == "http"
        assert d["method"] == "GET"
        assert d["confidence"] == "high"

    def test_ui_interface(self):
        iface = Interface(
            kind=InterfaceKind.UI,
            name="onClick:submit",
            handler_symbol="handleSubmit",
        )
        assert iface.kind == InterfaceKind.UI

    def test_all_interface_kinds(self):
        """Verify all interface kinds are valid (not just HTTP)."""
        kinds = [
            InterfaceKind.HTTP, InterfaceKind.GRPC, InterfaceKind.CLI,
            InterfaceKind.UI, InterfaceKind.JOB, InterfaceKind.LIB,
            InterfaceKind.WEBSOCKET, InterfaceKind.EVENT, InterfaceKind.IPC,
        ]
        for kind in kinds:
            iface = Interface(kind=kind, name=f"test_{kind.value}")
            assert iface.kind == kind


class TestDataTouch:
    def test_database_touch(self):
        dt = DataTouch(
            kind=DataTouchKind.DATABASE,
            name="users_table",
            target="users",
            operation="read",
        )
        d = dt.to_dict()
        assert d["kind"] == "database"
        assert d["target"] == "users"


class TestRepoSnapshot:
    def test_empty_snapshot(self):
        snap = RepoSnapshot(root_path="/tmp/repo")
        assert snap.root_path == "/tmp/repo"
        assert len(snap.files) == 0
        assert len(snap.symbols) == 0

    def test_file_index(self):
        snap = RepoSnapshot(root_path="/tmp/repo")
        snap.files.append(File(path="a.py", language="python"))
        snap.files.append(File(path="b.js", language="javascript"))
        idx = snap.file_index
        assert "a.py" in idx
        assert idx["b.js"].language == "javascript"

    def test_symbol_index(self):
        snap = RepoSnapshot(root_path="/tmp/repo")
        snap.symbols.append(
            Symbol(name="foo", kind=SymbolKind.FUNCTION, file_path="a.py")
        )
        idx = snap.symbol_index
        assert "foo" in idx

    def test_merge(self):
        snap1 = RepoSnapshot(root_path="/tmp/repo")
        snap1.files.append(File(path="a.py", language="python"))
        snap1.symbols.append(
            Symbol(name="foo", kind=SymbolKind.FUNCTION, file_path="a.py")
        )

        snap2 = RepoSnapshot(root_path="/tmp/repo")
        snap2.files.append(File(path="b.py", language="python"))
        snap2.files.append(File(path="a.py", language="python"))  # Duplicate
        snap2.interfaces.append(
            Interface(kind=InterfaceKind.HTTP, name="GET /api")
        )

        snap1.merge(snap2)
        assert len(snap1.files) == 2  # Duplicate not added
        assert len(snap1.interfaces) == 1

    def test_provenance(self):
        snap = RepoSnapshot(root_path="/tmp/repo")
        snap.record_provenance("python_web", "interfaces", 5)
        assert "python_web:interfaces" in snap._provenance

    def test_to_dict(self):
        snap = RepoSnapshot(root_path="/tmp/repo")
        snap.files.append(File(path="a.py", language="python"))
        d = snap.to_dict()
        assert d["root_path"] == "/tmp/repo"
        assert len(d["files"]) == 1


class TestFeature:
    def test_to_dict(self):
        feat = Feature(
            name="User Auth",
            description="Handles user authentication",
            symbols=["login", "logout"],
            confidence=Confidence.HIGH,
        )
        d = feat.to_dict()
        assert d["name"] == "User Auth"
        assert d["confidence"] == "high"
        assert len(d["symbols"]) == 2


class TestWorkflow:
    def test_to_dict(self):
        wf = Workflow(
            name="Login Flow",
            steps=["visit_login", "enter_credentials", "submit"],
        )
        d = wf.to_dict()
        assert d["name"] == "Login Flow"
        assert len(d["steps"]) == 3


class TestHazard:
    def test_to_dict(self):
        h = Hazard(
            kind=HazardKind.HUGE_FILE,
            description="File is 500KB",
            severity="high",
            affected_paths=["big_file.py"],
        )
        d = h.to_dict()
        assert d["kind"] == "huge_file"
        assert d["severity"] == "high"
