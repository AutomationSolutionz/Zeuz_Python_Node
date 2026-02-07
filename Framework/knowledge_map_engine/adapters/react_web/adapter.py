"""
React Web Adapter implementation.

Detects React/Next.js/Remix/Gatsby applications and extracts:
- React component definitions (function and class components)
- Page routes (file-based routing for Next.js/Remix, react-router)
- API calls (fetch, axios, custom hooks)
- UI event handlers
- State management patterns (useState, useReducer, Redux, Zustand, etc.)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path, PurePosixPath
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

# React import indicators
REACT_INDICATORS = [
    "from 'react'",
    'from "react"',
    "from 'react-dom'",
    'from "react-dom"',
    "import React",
    "require('react')",
    'require("react")',
]

# Framework detection
NEXTJS_INDICATORS = [
    "next/router",
    "next/link",
    "next/image",
    "next/head",
    "next/app",
    "getServerSideProps",
    "getStaticProps",
    "getStaticPaths",
]

REMIX_INDICATORS = [
    "@remix-run",
    "from 'remix'",
    'from "remix"',
]

# Component patterns
FUNCTION_COMPONENT_RE = re.compile(
    r"^(?:export\s+)?(?:default\s+)?(?:const|function)\s+([A-Z]\w+)\s*"
    r"(?::\s*React\.FC|:\s*FC|=\s*(?:React\.)?(?:memo|forwardRef)\s*\(|[=(])",
    re.MULTILINE,
)

CLASS_COMPONENT_RE = re.compile(
    r"^(?:export\s+)?(?:default\s+)?class\s+([A-Z]\w+)\s+extends\s+"
    r"(?:React\.)?(?:Component|PureComponent)",
    re.MULTILINE,
)

# Hook usage patterns
USE_STATE_RE = re.compile(r"useState\s*[<(]")
USE_EFFECT_RE = re.compile(r"useEffect\s*\(")
USE_REDUCER_RE = re.compile(r"useReducer\s*\(")
CUSTOM_HOOK_RE = re.compile(
    r"^(?:export\s+)?(?:const|function)\s+(use[A-Z]\w+)\s*[=(]",
    re.MULTILINE,
)

# API call patterns
FETCH_RE = re.compile(
    r"(?:fetch|axios\.(?:get|post|put|patch|delete)|useSWR|useQuery)\s*\(\s*"
    r"[`'\"]([^`'\"]+)[`'\"]",
    re.MULTILINE,
)

# React Router route patterns
ROUTER_ROUTE_RE = re.compile(
    r'<Route\s+[^>]*path\s*=\s*[{"\']([^"\']+)["\'][^>]*>',
    re.MULTILINE,
)

# Event handler patterns
EVENT_HANDLER_RE = re.compile(
    r"(?:on[A-Z]\w+)\s*=\s*\{?\s*(?:(?:\(\w*\)\s*=>)|(\w+))",
)

# Next.js API route patterns (file-based)
NEXTJS_API_ROUTE_DIRS = {"pages/api", "app/api", "src/pages/api", "src/app/api"}
NEXTJS_PAGE_DIRS = {"pages", "app", "src/pages", "src/app"}


class ReactWebAdapter(Adapter):
    """
    Adapter for React-based web applications.

    Detects React, Next.js, Remix, and Gatsby applications,
    then extracts components, routes, API calls, and event handlers.
    """

    @property
    def name(self) -> str:
        return "react_web"

    @property
    def description(self) -> str:
        return (
            "Extracts React components, page routes, API calls, and event "
            "handlers from React/Next.js/Remix applications"
        )

    def detect(self, snapshot: RepoSnapshot) -> float:
        """Detect if this repo uses React."""
        js_ts_files = [
            f for f in snapshot.files
            if f.language in ("javascript", "typescript")
            and not f.is_generated
        ]
        if not js_ts_files:
            return 0.0

        root = Path(snapshot.root_path)
        react_hits = 0
        nextjs_hits = 0
        files_checked = 0

        for file_obj in js_ts_files[:200]:
            abs_path = root / file_obj.path
            try:
                content = abs_path.read_text(errors="ignore")
            except OSError:
                continue

            files_checked += 1

            for indicator in REACT_INDICATORS:
                if indicator in content:
                    react_hits += 1
                    break

            for indicator in NEXTJS_INDICATORS:
                if indicator in content:
                    nextjs_hits += 1
                    break

        if react_hits == 0:
            # Check for package.json React dependency
            package_json = root / "package.json"
            if package_json.exists():
                try:
                    pkg_content = package_json.read_text(errors="ignore")
                    if '"react"' in pkg_content:
                        return 0.4
                except OSError:
                    pass
            return 0.0

        total_hits = react_hits + nextjs_hits
        if total_hits >= 20:
            return 0.95
        elif total_hits >= 10:
            return 0.8
        elif total_hits >= 5:
            return 0.6
        else:
            return 0.3

    def extract(self, snapshot: RepoSnapshot) -> RepoSnapshot:
        """Extract React-specific facts."""
        result = RepoSnapshot(root_path=snapshot.root_path)
        root = Path(snapshot.root_path)

        js_ts_files = [
            f for f in snapshot.files
            if f.language in ("javascript", "typescript")
            and not f.is_generated
        ]

        # Detect if Next.js or Remix
        meta_framework = self._detect_meta_framework(root, js_ts_files)

        for file_obj in js_ts_files:
            abs_path = root / file_obj.path
            try:
                content = abs_path.read_text(errors="ignore")
            except OSError:
                continue

            # Extract components
            self._extract_components(file_obj.path, content, result)

            # Extract custom hooks
            self._extract_custom_hooks(file_obj.path, content, result)

            # Extract API calls
            self._extract_api_calls(file_obj.path, content, result)

            # Extract router-defined routes
            self._extract_router_routes(file_obj.path, content, result)

            # Extract UI event handlers
            self._extract_event_handlers(file_obj.path, content, result)

        # File-based routing (Next.js, Remix)
        if meta_framework in ("nextjs", "remix"):
            self._extract_file_based_routes(
                root, js_ts_files, meta_framework, result
            )

        return result

    def _detect_meta_framework(
        self, root: Path, files: list
    ) -> Optional[str]:
        """Detect if using Next.js, Remix, or plain React."""
        # Check package.json
        package_json = root / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text(errors="ignore")
                if '"next"' in content:
                    return "nextjs"
                if '"@remix-run' in content:
                    return "remix"
                if '"gatsby"' in content:
                    return "gatsby"
            except OSError:
                pass

        # Check for next.config.js/ts
        for cfg in ("next.config.js", "next.config.mjs", "next.config.ts"):
            if (root / cfg).exists():
                return "nextjs"

        return None

    def _extract_components(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract React component definitions."""
        for match in FUNCTION_COMPONENT_RE.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count("\n") + 1

            result.symbols.append(Symbol(
                name=name,
                kind=SymbolKind.COMPONENT,
                file_path=path,
                line_start=line_num,
                evidence=[Evidence(
                    path=path,
                    symbol=name,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
            ))

        for match in CLASS_COMPONENT_RE.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count("\n") + 1

            result.symbols.append(Symbol(
                name=name,
                kind=SymbolKind.COMPONENT,
                file_path=path,
                line_start=line_num,
                evidence=[Evidence(
                    path=path,
                    symbol=name,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
            ))

    def _extract_custom_hooks(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract custom React hook definitions."""
        for match in CUSTOM_HOOK_RE.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count("\n") + 1

            result.symbols.append(Symbol(
                name=name,
                kind=SymbolKind.FUNCTION,
                file_path=path,
                line_start=line_num,
                evidence=[Evidence(
                    path=path,
                    symbol=name,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
            ))

    def _extract_api_calls(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract API call patterns (fetch, axios, SWR, React Query)."""
        for match in FETCH_RE.finditer(content):
            url = match.group(1)
            line_num = content[:match.start()].count("\n") + 1

            result.data_touches.append(DataTouch(
                kind=DataTouchKind.NETWORK,
                name=f"api_call:{url[:80]}",
                target=url,
                operation="request",
                evidence=[Evidence(
                    path=path,
                    line_start=line_num,
                    confidence=Confidence.MEDIUM,
                )],
                confidence=Confidence.MEDIUM,
            ))

    def _extract_router_routes(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract routes defined via react-router <Route> components."""
        for match in ROUTER_ROUTE_RE.finditer(content):
            route_path = match.group(1)
            line_num = content[:match.start()].count("\n") + 1

            result.interfaces.append(Interface(
                kind=InterfaceKind.UI,
                name=f"page:{route_path}",
                path_pattern=route_path,
                evidence=[Evidence(
                    path=path,
                    line_start=line_num,
                    confidence=Confidence.HIGH,
                )],
                confidence=Confidence.HIGH,
                metadata={"routing": "react-router"},
            ))

    def _extract_event_handlers(
        self, path: str, content: str, result: RepoSnapshot
    ) -> None:
        """Extract UI event handlers (onClick, onChange, etc.)."""
        # Count event handlers per file rather than listing each one
        handler_matches = EVENT_HANDLER_RE.findall(content)
        if handler_matches:
            named_handlers = [h for h in handler_matches if h]
            if named_handlers:
                for handler in set(named_handlers):
                    result.interfaces.append(Interface(
                        kind=InterfaceKind.UI,
                        name=f"handler:{handler}",
                        handler_symbol=handler,
                        evidence=[Evidence(
                            path=path,
                            symbol=handler,
                            confidence=Confidence.LOW,
                        )],
                        confidence=Confidence.LOW,
                        metadata={"role": "event_handler"},
                    ))

    def _extract_file_based_routes(
        self,
        root: Path,
        files: list,
        meta_framework: str,
        result: RepoSnapshot,
    ) -> None:
        """Extract routes from file-based routing (Next.js, Remix)."""
        page_dirs = NEXTJS_PAGE_DIRS if meta_framework == "nextjs" else {"app/routes", "src/routes"}
        api_dirs = NEXTJS_API_ROUTE_DIRS

        for file_obj in files:
            rel_path = file_obj.path.replace("\\", "/")

            # API routes
            for api_dir in api_dirs:
                if rel_path.startswith(api_dir + "/"):
                    route = self._file_path_to_route(rel_path, api_dir)
                    if route:
                        result.interfaces.append(Interface(
                            kind=InterfaceKind.HTTP,
                            name=f"API {route}",
                            path_pattern=route,
                            evidence=[Evidence(
                                path=file_obj.path,
                                confidence=Confidence.HIGH,
                            )],
                            confidence=Confidence.HIGH,
                            metadata={
                                "framework": meta_framework,
                                "routing": "file-based",
                            },
                        ))
                    break

            # Page routes
            for page_dir in page_dirs:
                if rel_path.startswith(page_dir + "/"):
                    # Skip API routes, layout files, etc.
                    basename = PurePosixPath(rel_path).stem
                    if basename.startswith("_") or basename == "layout":
                        continue

                    route = self._file_path_to_route(rel_path, page_dir)
                    if route:
                        result.interfaces.append(Interface(
                            kind=InterfaceKind.UI,
                            name=f"page:{route}",
                            path_pattern=route,
                            evidence=[Evidence(
                                path=file_obj.path,
                                confidence=Confidence.HIGH,
                            )],
                            confidence=Confidence.HIGH,
                            metadata={
                                "framework": meta_framework,
                                "routing": "file-based",
                            },
                        ))
                    break

    @staticmethod
    def _file_path_to_route(file_path: str, base_dir: str) -> Optional[str]:
        """Convert a file path to a URL route (Next.js style)."""
        # Remove base dir prefix
        rel = file_path[len(base_dir):]

        # Remove file extension
        p = PurePosixPath(rel)
        stem = str(p.with_suffix(""))

        # Remove /index suffix
        if stem.endswith("/index"):
            stem = stem[:-6] or "/"

        # Convert [param] to :param
        stem = re.sub(r"\[\.\.\.(\w+)\]", r"*\1", stem)
        stem = re.sub(r"\[(\w+)\]", r":\1", stem)

        # Convert (group) folders to empty (Next.js route groups)
        stem = re.sub(r"/\([^)]+\)", "", stem)

        return stem or "/"
