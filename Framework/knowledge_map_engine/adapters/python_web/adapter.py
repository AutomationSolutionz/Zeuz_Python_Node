"""
Python Web Adapter implementation.

Detects Python web frameworks and extracts:
- HTTP route definitions (Django urlpatterns, FastAPI decorators, Flask routes)
- Middleware chains
- ORM model definitions
- Database migrations
- WSGI/ASGI application entry points
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from Framework.knowledge_map_engine.adapters.base import Adapter
from Framework.knowledge_map_engine.ir.models import (
    Confidence,
    DataTouch,
    DataTouchKind,
    Evidence,
    Interface,
    InterfaceKind,
    RepoSnapshot,
    Symbol,
    SymbolKind,
)

logger = logging.getLogger(__name__)

# Framework detection indicators (import patterns)
FRAMEWORK_INDICATORS: dict[str, list[str]] = {
    "django": ["django", "from django"],
    "fastapi": ["fastapi", "from fastapi"],
    "flask": ["flask", "from flask"],
    "starlette": ["starlette", "from starlette"],
    "tornado": ["tornado.web", "from tornado"],
    "sanic": ["sanic", "from sanic"],
    "aiohttp": ["aiohttp.web", "from aiohttp"],
    "bottle": ["bottle", "from bottle"],
    "falcon": ["falcon", "from falcon"],
    "pyramid": ["pyramid", "from pyramid"],
    "cherrypy": ["cherrypy", "from cherrypy"],
    "litestar": ["litestar", "from litestar"],
}

# Route decorator patterns (framework-specific)
ROUTE_DECORATOR_RE = re.compile(
    r'@\w+\.(route|get|post|put|patch|delete|head|options|api_view|action)\s*\(\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)

# FastAPI/Starlette style: @app.get("/path")
FASTAPI_ROUTE_RE = re.compile(
    r'@\w+\.(get|post|put|patch|delete|head|options|websocket)\s*\(\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)

# Django URL patterns: path("route/", view_func)
DJANGO_PATH_RE = re.compile(
    r'(?:path|re_path|url)\s*\(\s*["\']([^"\']*)["\']'
    r'(?:\s*,\s*(\w+(?:\.\w+)*))?',
    re.MULTILINE,
)

# ORM model classes
ORM_MODEL_RE = re.compile(
    r"class\s+(\w+)\s*\(\s*(?:models\.Model|db\.Model|Base|DeclarativeBase|SQLModel)\s*\)",
    re.MULTILINE,
)

# SQLAlchemy table definitions
SQLA_TABLE_RE = re.compile(
    r'__tablename__\s*=\s*["\'](\w+)["\']',
    re.MULTILINE,
)


class PythonWebAdapter(Adapter):
    """
    Adapter for Python web frameworks.

    Detects Django, FastAPI, Flask, and other Python web frameworks,
    then extracts HTTP routes, middleware, ORM models, and entry points.
    """

    @property
    def name(self) -> str:
        return "python_web"

    @property
    def description(self) -> str:
        return (
            "Extracts HTTP routes, ORM models, and middleware from "
            "Python web frameworks (Django, FastAPI, Flask, etc.)"
        )

    def detect(self, snapshot: RepoSnapshot) -> float:
        """
        Detect if this repo uses a Python web framework.

        Returns confidence based on number of matching indicators found.
        """
        python_files = [
            f for f in snapshot.files
            if f.language == "python" and not f.is_generated
        ]
        if not python_files:
            return 0.0

        root = Path(snapshot.root_path)
        framework_hits: dict[str, int] = {}
        files_checked = 0

        for file_obj in python_files[:200]:  # Cap to avoid scanning huge repos
            abs_path = root / file_obj.path
            try:
                content = abs_path.read_text(errors="ignore")
            except OSError:
                continue

            files_checked += 1
            content_lower = content.lower()

            for framework, indicators in FRAMEWORK_INDICATORS.items():
                for indicator in indicators:
                    if indicator in content_lower:
                        framework_hits[framework] = (
                            framework_hits.get(framework, 0) + 1
                        )

        if not framework_hits:
            return 0.0

        # Confidence based on how many files reference web frameworks
        max_hits = max(framework_hits.values())
        if max_hits >= 10:
            return 0.95
        elif max_hits >= 5:
            return 0.8
        elif max_hits >= 2:
            return 0.6
        else:
            return 0.3

    def extract(self, snapshot: RepoSnapshot) -> RepoSnapshot:
        """
        Extract web-specific facts from Python files.

        Returns a new RepoSnapshot with discovered interfaces, data touches,
        and additional symbols.
        """
        result = RepoSnapshot(root_path=snapshot.root_path)
        root = Path(snapshot.root_path)

        python_files = [
            f for f in snapshot.files
            if f.language == "python" and not f.is_generated
        ]

        for file_obj in python_files:
            abs_path = root / file_obj.path
            try:
                content = abs_path.read_text(errors="ignore")
            except OSError:
                continue

            # Extract routes
            self._extract_routes(file_obj.path, content, result)

            # Extract ORM models
            self._extract_orm_models(file_obj.path, content, result)

            # Extract WSGI/ASGI entry points
            self._extract_app_entry_points(file_obj.path, content, result)

            # Extract middleware
            self._extract_middleware(file_obj.path, content, result)

        return result

    def _extract_routes(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract HTTP route definitions."""
        # Decorator-based routes (Flask, FastAPI, Sanic, etc.)
        for match in FASTAPI_ROUTE_RE.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            line_num = content[:match.start()].count("\n") + 1

            # Find the function defined after the decorator
            handler = self._find_handler_after_line(content, line_num)

            result.interfaces.append(Interface(
                kind=InterfaceKind.HTTP,
                name=f"{method} {route_path}",
                handler_symbol=handler,
                method=method,
                path_pattern=route_path,
                evidence=[Evidence(
                    path=path,
                    symbol=handler,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
                confidence=Confidence.HIGH,
            ))

        # Django URL patterns
        for match in DJANGO_PATH_RE.finditer(content):
            route_path = match.group(1)
            handler = match.group(2) if match.group(2) else None
            line_num = content[:match.start()].count("\n") + 1

            result.interfaces.append(Interface(
                kind=InterfaceKind.HTTP,
                name=f"URL {route_path}",
                handler_symbol=handler,
                path_pattern=route_path,
                evidence=[Evidence(
                    path=path,
                    symbol=handler,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
                confidence=Confidence.HIGH,
                metadata={"framework": "django"},
            ))

    def _extract_orm_models(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract ORM model definitions and their table names."""
        for match in ORM_MODEL_RE.finditer(content):
            model_name = match.group(1)
            line_num = content[:match.start()].count("\n") + 1

            result.symbols.append(Symbol(
                name=model_name,
                kind=SymbolKind.CLASS,
                file_path=path,
                line_start=line_num,
                evidence=[Evidence(
                    path=path,
                    symbol=model_name,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
            ))

            # Look for table name
            table_match = SQLA_TABLE_RE.search(content)
            table_name = (
                table_match.group(1) if table_match
                else model_name.lower() + "s"  # Convention guess
            )

            result.data_touches.append(DataTouch(
                kind=DataTouchKind.DATABASE,
                name=f"model:{model_name}",
                symbol=model_name,
                target=table_name,
                operation="read/write",
                evidence=[Evidence(
                    path=path,
                    symbol=model_name,
                    line_start=line_num,
                    confidence=Confidence.MEDIUM,
                )],
                confidence=Confidence.MEDIUM,
            ))

    def _extract_app_entry_points(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract WSGI/ASGI application definitions."""
        # FastAPI() / Flask(__name__) / Sanic(__name__) etc.
        app_patterns = [
            (r"(\w+)\s*=\s*FastAPI\s*\(", "FastAPI"),
            (r"(\w+)\s*=\s*Flask\s*\(", "Flask"),
            (r"(\w+)\s*=\s*Sanic\s*\(", "Sanic"),
            (r"(\w+)\s*=\s*Starlette\s*\(", "Starlette"),
            (r"(\w+)\s*=\s*Litestar\s*\(", "Litestar"),
            (r"(\w+)\s*=\s*Falcon\s*\(", "Falcon"),
        ]

        for pattern, framework in app_patterns:
            match = re.search(pattern, content)
            if match:
                var_name = match.group(1)
                line_num = content[:match.start()].count("\n") + 1

                result.interfaces.append(Interface(
                    kind=InterfaceKind.HTTP,
                    name=f"{framework} app ({var_name})",
                    handler_symbol=var_name,
                    evidence=[Evidence(
                        path=path,
                        symbol=var_name,
                        line_start=line_num,
                        confidence=Confidence.HIGH,
                    )],
                    confidence=Confidence.HIGH,
                    metadata={"framework": framework.lower(), "role": "app_entry"},
                ))

    def _extract_middleware(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract middleware registrations."""
        middleware_patterns = [
            r"\.add_middleware\s*\(\s*(\w+)",
            r"MIDDLEWARE\s*=\s*\[",  # Django
            r"@\w+\.middleware",
        ]

        for pattern in middleware_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                name = match.group(1) if match.lastindex else "middleware"

                result.interfaces.append(Interface(
                    kind=InterfaceKind.HTTP,
                    name=f"middleware:{name}",
                    evidence=[Evidence(
                        path=path,
                        line_start=line_num,
                        confidence=Confidence.MEDIUM,
                    )],
                    confidence=Confidence.MEDIUM,
                    metadata={"role": "middleware"},
                ))

    @staticmethod
    def _find_handler_after_line(content: str, decorator_line: int) -> Optional[str]:
        """Find the function name defined after a decorator line."""
        lines = content.split("\n")
        for i in range(decorator_line, min(decorator_line + 5, len(lines))):
            line = lines[i].strip()
            match = re.match(r"(?:async\s+)?def\s+(\w+)\s*\(", line)
            if match:
                return match.group(1)
        return None
