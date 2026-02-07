"""
File classifier for the Generic Scanner.

Classifies files as generated, test, config, documentation, etc.
using language-agnostic heuristics (path patterns, naming conventions).
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import NamedTuple


class FileClassification(NamedTuple):
    """Result of file classification."""
    is_generated: bool
    is_test: bool
    is_config: bool
    is_documentation: bool
    is_vendored: bool
    is_binary: bool


# Patterns for generated code detection
GENERATED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(^|/)generated/", re.IGNORECASE),
    re.compile(r"(^|/)gen/", re.IGNORECASE),
    re.compile(r"\.generated\.", re.IGNORECASE),
    re.compile(r"\.g\.(cs|dart)$", re.IGNORECASE),
    re.compile(r"\.pb\.(go|py|cc|h|js)$"),
    re.compile(r"_pb2\.py$"),
    re.compile(r"_pb2_grpc\.py$"),
    re.compile(r"\.min\.(js|css)$"),
    re.compile(r"(^|/)dist/"),
    re.compile(r"(^|/)build/output"),
    re.compile(r"(^|/)__pycache__/"),
    re.compile(r"\.pyc$"),
    re.compile(r"(^|/)node_modules/"),
    re.compile(r"package-lock\.json$"),
    re.compile(r"yarn\.lock$"),
    re.compile(r"pnpm-lock\.yaml$"),
    re.compile(r"uv\.lock$"),
    re.compile(r"poetry\.lock$"),
    re.compile(r"Pipfile\.lock$"),
    re.compile(r"Cargo\.lock$"),
    re.compile(r"Gemfile\.lock$"),
    re.compile(r"composer\.lock$"),
    re.compile(r"go\.sum$"),
]

# Patterns for test files
TEST_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(^|/)tests?/", re.IGNORECASE),
    re.compile(r"(^|/)__tests__/", re.IGNORECASE),
    re.compile(r"(^|/)spec/", re.IGNORECASE),
    re.compile(r"(^|/)specs/", re.IGNORECASE),
    re.compile(r"test_[^/]+\.(py|rb|js|ts|go|rs|java|kt|cs|swift)$", re.IGNORECASE),
    re.compile(r"[^/]+_test\.(py|rb|js|ts|go|rs|java|kt|cs|swift)$", re.IGNORECASE),
    re.compile(r"[^/]+\.test\.(js|ts|jsx|tsx|mjs)$", re.IGNORECASE),
    re.compile(r"[^/]+\.spec\.(js|ts|jsx|tsx|mjs|rb)$", re.IGNORECASE),
    re.compile(r"[^/]+Test\.(java|kt|cs|swift)$"),
    re.compile(r"[^/]+Tests\.(java|kt|cs|swift)$"),
    re.compile(r"(^|/)conftest\.py$"),
    re.compile(r"(^|/)fixtures/", re.IGNORECASE),
    re.compile(r"(^|/)testdata/", re.IGNORECASE),
    re.compile(r"(^|/)test[-_]?helpers?/", re.IGNORECASE),
]

# Patterns for config files
CONFIG_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(^|/)\.[^/]+rc$"),  # .eslintrc, .babelrc, etc.
    re.compile(r"(^|/)\.[^/]+rc\.(json|ya?ml|js|ts|cjs|mjs)$"),
    re.compile(r"(^|/)\.env(\..+)?$"),
    re.compile(r"(^|/)(tsconfig|jsconfig).*\.json$"),
    re.compile(r"(^|/)pyproject\.toml$"),
    re.compile(r"(^|/)setup\.(py|cfg)$"),
    re.compile(r"(^|/)package\.json$"),
    re.compile(r"(^|/)Cargo\.toml$"),
    re.compile(r"(^|/)go\.(mod|sum)$"),
    re.compile(r"(^|/)Gemfile$"),
    re.compile(r"(^|/)requirements.*\.txt$"),
    re.compile(r"(^|/)Pipfile$"),
    re.compile(r"(^|/)\.gitignore$"),
    re.compile(r"(^|/)\.dockerignore$"),
    re.compile(r"(^|/)docker-compose.*\.ya?ml$"),
    re.compile(r"(^|/)Makefile$"),
    re.compile(r"(^|/)webpack\.config\.(js|ts)$"),
    re.compile(r"(^|/)vite\.config\.(js|ts|mjs)$"),
    re.compile(r"(^|/)rollup\.config\.(js|ts|mjs)$"),
    re.compile(r"(^|/)next\.config\.(js|ts|mjs)$"),
    re.compile(r"(^|/)\.github/"),
    re.compile(r"(^|/)\.gitlab-ci"),
    re.compile(r"(^|/)Jenkinsfile$"),
    re.compile(r"(^|/)\.circleci/"),
    re.compile(r"(^|/)\.travis\.yml$"),
    re.compile(r"(^|/)tox\.ini$"),
    re.compile(r"(^|/)\.pre-commit-config\.ya?ml$"),
]

# Patterns for documentation
DOC_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(^|/)docs?/", re.IGNORECASE),
    re.compile(r"(^|/)documentation/", re.IGNORECASE),
    re.compile(r"(^|/)README", re.IGNORECASE),
    re.compile(r"(^|/)CHANGELOG", re.IGNORECASE),
    re.compile(r"(^|/)CONTRIBUTING", re.IGNORECASE),
    re.compile(r"(^|/)LICENSE", re.IGNORECASE),
    re.compile(r"(^|/)COPYING", re.IGNORECASE),
    re.compile(r"(^|/)AUTHORS", re.IGNORECASE),
    re.compile(r"\.(md|rst|adoc|txt)$", re.IGNORECASE),
]

# Patterns for vendored / third-party code
VENDORED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(^|/)vendor/"),
    re.compile(r"(^|/)vendored/"),
    re.compile(r"(^|/)third[_-]?party/", re.IGNORECASE),
    re.compile(r"(^|/)external/", re.IGNORECASE),
    re.compile(r"(^|/)node_modules/"),
    re.compile(r"(^|/)bower_components/"),
    re.compile(r"(^|/)\.bundle/"),
]

# Binary file extensions
BINARY_EXTENSIONS: set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".webp", ".avif", ".tiff", ".tif",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".a", ".o", ".lib",
    ".wasm", ".class", ".pyc", ".pyo",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac", ".ogg",
    ".sqlite", ".db", ".mdb",
}


def classify_file(path: str) -> FileClassification:
    """
    Classify a file based on its path using heuristic patterns.

    Args:
        path: File path (relative to repo root recommended).

    Returns:
        FileClassification with boolean flags for each category.
    """
    # Normalize to forward slashes
    normalized = path.replace("\\", "/")

    is_generated = any(p.search(normalized) for p in GENERATED_PATTERNS)
    is_test = any(p.search(normalized) for p in TEST_PATTERNS)
    is_config = any(p.search(normalized) for p in CONFIG_PATTERNS)
    is_documentation = any(p.search(normalized) for p in DOC_PATTERNS)
    is_vendored = any(p.search(normalized) for p in VENDORED_PATTERNS)

    ext = PurePosixPath(normalized).suffix.lower()
    is_binary = ext in BINARY_EXTENSIONS

    return FileClassification(
        is_generated=is_generated,
        is_test=is_test,
        is_config=is_config,
        is_documentation=is_documentation,
        is_vendored=is_vendored,
        is_binary=is_binary,
    )
