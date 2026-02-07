"""Tests for the adapter plugin system and example adapters."""

import os
import tempfile
import textwrap


from Framework.knowledge_map_engine.adapters.base import Adapter, AdapterRegistry
from Framework.knowledge_map_engine.adapters.python_web import PythonWebAdapter
from Framework.knowledge_map_engine.adapters.react_web import ReactWebAdapter
from Framework.knowledge_map_engine.ir.models import (
    InterfaceKind,
    RepoSnapshot,
    SymbolKind,
)
from Framework.knowledge_map_engine.scanner.generic_scanner import GenericScanner


# ---------------------------------------------------------------------------
# Adapter Registry Tests
# ---------------------------------------------------------------------------

class DummyAdapter(Adapter):
    """A minimal adapter for testing."""
    @property
    def name(self) -> str:
        return "dummy"

    def detect(self, snapshot: RepoSnapshot) -> float:
        return 0.5

    def extract(self, snapshot: RepoSnapshot) -> RepoSnapshot:
        return RepoSnapshot(root_path=snapshot.root_path)


class FailingAdapter(Adapter):
    """An adapter that raises during detection."""
    @property
    def name(self) -> str:
        return "failing"

    def detect(self, snapshot: RepoSnapshot) -> float:
        raise RuntimeError("Detection failed")

    def extract(self, snapshot: RepoSnapshot) -> RepoSnapshot:
        raise RuntimeError("Extraction failed")


class TestAdapterRegistry:
    def test_register_and_list(self):
        reg = AdapterRegistry()
        adapter = DummyAdapter()
        reg.register(adapter)
        assert len(reg) == 1
        assert "dummy" in reg
        assert reg.get("dummy") is adapter

    def test_unregister(self):
        reg = AdapterRegistry()
        reg.register(DummyAdapter())
        reg.unregister("dummy")
        assert len(reg) == 0
        assert "dummy" not in reg

    def test_detect_applicable(self):
        reg = AdapterRegistry()
        reg.register(DummyAdapter())
        snap = RepoSnapshot(root_path="/tmp")
        results = reg.detect_applicable(snap, threshold=0.1)
        assert len(results) == 1
        assert results[0][0].name == "dummy"
        assert results[0][1] == 0.5

    def test_detect_with_threshold_filtering(self):
        reg = AdapterRegistry()
        reg.register(DummyAdapter())  # returns 0.5
        snap = RepoSnapshot(root_path="/tmp")
        results = reg.detect_applicable(snap, threshold=0.8)
        assert len(results) == 0

    def test_failing_adapter_handled_gracefully(self):
        reg = AdapterRegistry()
        reg.register(FailingAdapter())
        snap = RepoSnapshot(root_path="/tmp")
        # Should not raise, just log the error
        results = reg.detect_applicable(snap)
        assert len(results) == 0

    def test_duplicate_registration_replaces(self):
        reg = AdapterRegistry()
        adapter1 = DummyAdapter()
        adapter2 = DummyAdapter()
        reg.register(adapter1)
        reg.register(adapter2)
        assert len(reg) == 1
        assert reg.get("dummy") is adapter2


# ---------------------------------------------------------------------------
# Python Web Adapter Tests
# ---------------------------------------------------------------------------

class TestPythonWebAdapter:
    def _make_repo_with_files(self, files: dict[str, str]) -> tuple[str, RepoSnapshot]:
        """Create a temp repo with files and scan it."""
        tmpdir = tempfile.mkdtemp()
        for rel_path, content in files.items():
            abs_path = os.path.join(tmpdir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w") as f:
                f.write(content)

        scanner = GenericScanner()
        snapshot = scanner.scan(tmpdir)
        return tmpdir, snapshot

    def test_detect_fastapi(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "main.py": textwrap.dedent("""\
                from fastapi import FastAPI
                app = FastAPI()

                @app.get("/users")
                def get_users():
                    return []
            """),
        })
        adapter = PythonWebAdapter()
        score = adapter.detect(snapshot)
        assert score > 0.0

    def test_detect_no_web_framework(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "utils.py": "def add(a, b): return a + b\n",
        })
        adapter = PythonWebAdapter()
        score = adapter.detect(snapshot)
        assert score == 0.0

    def test_extract_fastapi_routes(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "main.py": textwrap.dedent("""\
                from fastapi import FastAPI
                app = FastAPI()

                @app.get("/users")
                def get_users():
                    return []

                @app.post("/users")
                async def create_user(data: dict):
                    return data
            """),
        })
        adapter = PythonWebAdapter()
        result = adapter.extract(snapshot)

        http_interfaces = [
            i for i in result.interfaces if i.kind == InterfaceKind.HTTP
        ]
        assert len(http_interfaces) >= 2

        route_names = {i.name for i in http_interfaces}
        assert any("/users" in name for name in route_names)

    def test_extract_django_urls(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "urls.py": textwrap.dedent("""\
                from django.urls import path
                from . import views

                urlpatterns = [
                    path("api/users/", views.user_list),
                    path("api/users/<int:pk>/", views.user_detail),
                ]
            """),
        })
        adapter = PythonWebAdapter()
        result = adapter.extract(snapshot)

        http_interfaces = [
            i for i in result.interfaces if i.kind == InterfaceKind.HTTP
        ]
        assert len(http_interfaces) >= 2

    def test_extract_orm_models(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "models.py": textwrap.dedent("""\
                from django.db import models

                class User(models.Model):
                    name = models.CharField(max_length=100)
                    email = models.EmailField()

                class Post(models.Model):
                    title = models.CharField(max_length=200)
                    author = models.ForeignKey(User, on_delete=models.CASCADE)
            """),
        })
        adapter = PythonWebAdapter()
        result = adapter.extract(snapshot)

        model_symbols = [
            s for s in result.symbols if s.kind == SymbolKind.CLASS
        ]
        assert len(model_symbols) >= 2
        model_names = {s.name for s in model_symbols}
        assert "User" in model_names
        assert "Post" in model_names

        # Should also create data touches
        assert len(result.data_touches) >= 2

    def test_extract_app_entry_point(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "app.py": "from flask import Flask\napp = Flask(__name__)\n",
        })
        adapter = PythonWebAdapter()
        result = adapter.extract(snapshot)

        entry_points = [
            i for i in result.interfaces
            if i.metadata.get("role") == "app_entry"
        ]
        assert len(entry_points) >= 1
        assert entry_points[0].metadata["framework"] == "flask"

    def test_detect_returns_zero_for_non_python(self):
        """Adapter should return 0.0 for repos with no Python files."""
        tmpdir, snapshot = self._make_repo_with_files({
            "app.js": "function main() {}\n",
        })
        adapter = PythonWebAdapter()
        assert adapter.detect(snapshot) == 0.0


# ---------------------------------------------------------------------------
# React Web Adapter Tests
# ---------------------------------------------------------------------------

class TestReactWebAdapter:
    def _make_repo_with_files(self, files: dict[str, str]) -> tuple[str, RepoSnapshot]:
        tmpdir = tempfile.mkdtemp()
        for rel_path, content in files.items():
            abs_path = os.path.join(tmpdir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w") as f:
                f.write(content)

        scanner = GenericScanner()
        snapshot = scanner.scan(tmpdir)
        return tmpdir, snapshot

    def test_detect_react(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "App.jsx": textwrap.dedent("""\
                import React from 'react';

                export default function App() {
                    return <div>Hello</div>;
                }
            """),
        })
        adapter = ReactWebAdapter()
        score = adapter.detect(snapshot)
        assert score > 0.0

    def test_detect_react_via_package_json(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "package.json": '{"dependencies": {"react": "^18.0.0"}}',
            "src/index.js": "// entry point\n",
        })
        adapter = ReactWebAdapter()
        score = adapter.detect(snapshot)
        assert score > 0.0

    def test_detect_no_react(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "server.py": "def main(): pass\n",
        })
        adapter = ReactWebAdapter()
        assert adapter.detect(snapshot) == 0.0

    def test_extract_components(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "UserProfile.tsx": textwrap.dedent("""\
                import React from 'react';

                export function UserProfile({ user }) {
                    return <div>{user.name}</div>;
                }

                export const UserAvatar = ({ src }) => {
                    return <img src={src} />;
                }
            """),
        })
        adapter = ReactWebAdapter()
        result = adapter.extract(snapshot)

        components = [
            s for s in result.symbols if s.kind == SymbolKind.COMPONENT
        ]
        assert len(components) >= 1
        comp_names = {s.name for s in components}
        assert "UserProfile" in comp_names

    def test_extract_custom_hooks(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "hooks.ts": textwrap.dedent("""\
                import { useState, useEffect } from 'react';

                export function useAuth() {
                    const [user, setUser] = useState(null);
                    return { user };
                }

                export const useFetch = (url) => {
                    return fetch(url);
                };
            """),
        })
        adapter = ReactWebAdapter()
        result = adapter.extract(snapshot)

        hooks = [
            s for s in result.symbols
            if s.name.startswith("use") and s.kind == SymbolKind.FUNCTION
        ]
        assert len(hooks) >= 1
        hook_names = {s.name for s in hooks}
        assert "useAuth" in hook_names

    def test_extract_api_calls(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "api.ts": textwrap.dedent("""\
                const data = await fetch('/api/users');
                const posts = await axios.get('/api/posts');
            """),
        })
        adapter = ReactWebAdapter()
        result = adapter.extract(snapshot)

        api_touches = [
            dt for dt in result.data_touches
            if dt.kind.value == "network"
        ]
        assert len(api_touches) >= 2

    def test_extract_nextjs_file_routes(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "package.json": '{"dependencies": {"next": "^14.0.0", "react": "^18.0.0"}}',
            "pages/index.tsx": "export default function Home() { return <div/>; }\n",
            "pages/about.tsx": "export default function About() { return <div/>; }\n",
            "pages/api/users.ts": "export default function handler(req, res) {}\n",
            "pages/posts/[id].tsx": "export default function Post() { return <div/>; }\n",
        })
        adapter = ReactWebAdapter()
        result = adapter.extract(snapshot)

        ui_routes = [
            i for i in result.interfaces if i.kind == InterfaceKind.UI
        ]
        http_routes = [
            i for i in result.interfaces if i.kind == InterfaceKind.HTTP
        ]

        # Should detect pages and API routes
        assert len(ui_routes) >= 2
        assert len(http_routes) >= 1

    def test_extract_router_routes(self):
        tmpdir, snapshot = self._make_repo_with_files({
            "App.tsx": textwrap.dedent("""\
                import React from 'react';
                import { Route } from 'react-router-dom';

                export function App() {
                    return (
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/settings" element={<Settings />} />
                    );
                }
            """),
        })
        adapter = ReactWebAdapter()
        result = adapter.extract(snapshot)

        ui_routes = [
            i for i in result.interfaces
            if i.kind == InterfaceKind.UI and i.metadata.get("routing") == "react-router"
        ]
        assert len(ui_routes) >= 2
