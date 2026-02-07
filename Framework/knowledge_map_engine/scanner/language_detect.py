"""
Language detection by file extension and shebang lines.

This module maps file extensions to programming languages and detects
language from shebang lines for extensionless scripts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

# Extension -> language mapping (comprehensive but not framework-specific)
EXTENSION_MAP: dict[str, str] = {
    # Python
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    ".pxd": "python",
    # JavaScript / TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # Java / Kotlin / Scala
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    # C / C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".cc": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    # C#
    ".cs": "csharp",
    # Ruby
    ".rb": "ruby",
    ".rake": "ruby",
    ".gemspec": "ruby",
    # PHP
    ".php": "php",
    # Swift
    ".swift": "swift",
    # Objective-C
    ".m": "objc",
    ".mm": "objc",
    # Dart
    ".dart": "dart",
    # Elixir / Erlang
    ".ex": "elixir",
    ".exs": "elixir",
    ".erl": "erlang",
    # Haskell
    ".hs": "haskell",
    ".lhs": "haskell",
    # Lua
    ".lua": "lua",
    # Perl
    ".pl": "perl",
    ".pm": "perl",
    # R
    ".r": "r",
    ".R": "r",
    # Shell
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".fish": "shell",
    # PowerShell
    ".ps1": "powershell",
    ".psm1": "powershell",
    # SQL
    ".sql": "sql",
    # Markup / Config
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".xml": "xml",
    ".xsl": "xml",
    ".xslt": "xml",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "config",
    ".properties": "properties",
    # Protobuf / GraphQL / Thrift
    ".proto": "protobuf",
    ".graphql": "graphql",
    ".gql": "graphql",
    ".thrift": "thrift",
    # Documentation
    ".md": "markdown",
    ".rst": "rst",
    ".txt": "text",
    ".adoc": "asciidoc",
    # Build files
    ".gradle": "gradle",
    ".cmake": "cmake",
    ".make": "makefile",
    # Docker
    ".dockerfile": "dockerfile",
    # Terraform / HCL
    ".tf": "terraform",
    ".hcl": "hcl",
    # Nix
    ".nix": "nix",
    # Zig
    ".zig": "zig",
    # V
    ".v": "vlang",
    # Nim
    ".nim": "nim",
}

# Special filenames that indicate a language
FILENAME_MAP: dict[str, str] = {
    "Makefile": "makefile",
    "makefile": "makefile",
    "GNUmakefile": "makefile",
    "Dockerfile": "dockerfile",
    "Containerfile": "dockerfile",
    "Vagrantfile": "ruby",
    "Rakefile": "ruby",
    "Gemfile": "ruby",
    "Podfile": "ruby",
    "Fastfile": "ruby",
    "Justfile": "just",
    "Taskfile.yml": "yaml",
    "CMakeLists.txt": "cmake",
    "BUILD": "bazel",
    "BUILD.bazel": "bazel",
    "WORKSPACE": "bazel",
    "WORKSPACE.bazel": "bazel",
}

# Shebang -> language mapping
SHEBANG_MAP: dict[str, str] = {
    "python": "python",
    "python3": "python",
    "node": "javascript",
    "ruby": "ruby",
    "perl": "perl",
    "bash": "shell",
    "sh": "shell",
    "zsh": "shell",
    "fish": "shell",
    "php": "php",
    "lua": "lua",
    "Rscript": "r",
}


def detect_language(path: str, first_line: Optional[str] = None) -> str:
    """
    Detect programming language from file path and optional first line.

    Args:
        path: File path (can be relative or absolute).
        first_line: Optional first line of the file for shebang detection.

    Returns:
        Detected language string, or "unknown" if unrecognized.
    """
    p = Path(path)

    # Check exact filename match first
    if p.name in FILENAME_MAP:
        return FILENAME_MAP[p.name]

    # Check extension
    ext = p.suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    # Check shebang
    if first_line and first_line.startswith("#!"):
        return _detect_from_shebang(first_line)

    return "unknown"


def _detect_from_shebang(shebang: str) -> str:
    """Extract language from a shebang line."""
    # Handle both "#!/usr/bin/env python" and "#!/usr/bin/python"
    parts = shebang.lstrip("#!").strip().split()
    if not parts:
        return "unknown"

    # If using env, the language is the next argument
    if parts[0].endswith("/env") and len(parts) > 1:
        executable = parts[1]
    else:
        executable = parts[0].rsplit("/", 1)[-1]

    # Strip version numbers (python3.11 -> python3 -> python)
    for name, lang in SHEBANG_MAP.items():
        if executable.startswith(name):
            return lang

    return "unknown"
