"""
Generic symbol extractor using language-agnostic heuristics.

Uses regex-based patterns to extract function, class, and other symbol
definitions from source code. This is the baseline extractor - adapters
can provide more accurate, framework-aware extraction.

For Python, uses the `ast` module for accurate extraction.
For other languages, falls back to regex patterns.
"""

from __future__ import annotations

import ast
import logging
import re
from typing import Optional

from Framework.knowledge_map_engine.ir.models import (
    Evidence,
    Confidence,
    Symbol,
    SymbolKind,
)

logger = logging.getLogger(__name__)


def extract_symbols(
    path: str, content: str, language: str
) -> list[Symbol]:
    """
    Extract symbols from source code.

    Args:
        path: File path for evidence references.
        content: Source code content.
        language: Detected programming language.

    Returns:
        List of extracted Symbol IR objects.
    """
    if language == "python":
        return _extract_python_symbols(path, content)
    elif language in ("javascript", "typescript"):
        return _extract_js_ts_symbols(path, content, language)
    elif language == "go":
        return _extract_go_symbols(path, content)
    elif language in ("java", "kotlin", "csharp"):
        return _extract_jvm_style_symbols(path, content, language)
    elif language == "rust":
        return _extract_rust_symbols(path, content)
    elif language == "ruby":
        return _extract_ruby_symbols(path, content)
    else:
        return _extract_generic_symbols(path, content, language)


# ---------------------------------------------------------------------------
# Python (AST-based, high accuracy)
# ---------------------------------------------------------------------------

def _extract_python_symbols(path: str, content: str) -> list[Symbol]:
    """Extract symbols from Python using the ast module."""
    symbols: list[Symbol] = []
    try:
        tree = ast.parse(content, filename=path)
    except SyntaxError:
        logger.debug("Failed to parse Python file: %s", path)
        return _extract_generic_symbols(path, content, "python")

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            # Determine if it's a method (inside a class)
            parent = _find_parent_class(tree, node)
            kind = SymbolKind.METHOD if parent else SymbolKind.FUNCTION

            sig = _python_signature(node)
            doc = ast.get_docstring(node)

            symbols.append(Symbol(
                name=node.name,
                kind=kind,
                file_path=path,
                line_start=node.lineno,
                line_end=node.end_lineno,
                parent=parent,
                docstring=doc[:200] if doc else None,
                signature=sig,
                evidence=[Evidence(
                    path=path,
                    symbol=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    confidence=Confidence.HIGH,
                )],
            ))

        elif isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            bases = [_ast_name(b) for b in node.bases if _ast_name(b)]

            symbols.append(Symbol(
                name=node.name,
                kind=SymbolKind.CLASS,
                file_path=path,
                line_start=node.lineno,
                line_end=node.end_lineno,
                docstring=doc[:200] if doc else None,
                dependencies=bases,
                evidence=[Evidence(
                    path=path,
                    symbol=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    confidence=Confidence.HIGH,
                )],
            ))

    return symbols


def _find_parent_class(tree: ast.Module, target: ast.AST) -> Optional[str]:
    """Find the parent class name of a function node."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if child is target:
                    return node.name
    return None


def _python_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Build a simple signature string from a Python function AST node."""
    args = node.args
    params: list[str] = []

    all_args = args.posonlyargs + args.args + args.kwonlyargs
    for arg in all_args:
        name = arg.arg
        if arg.annotation:
            name += f": {_ast_name(arg.annotation) or '...'}"
        params.append(name)

    if args.vararg:
        params.append(f"*{args.vararg.arg}")
    if args.kwarg:
        params.append(f"**{args.kwarg.arg}")

    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    ret = ""
    if node.returns:
        ret_name = _ast_name(node.returns)
        if ret_name:
            ret = f" -> {ret_name}"

    return f"{prefix} {node.name}({', '.join(params)}){ret}"


def _ast_name(node: ast.AST) -> Optional[str]:
    """Get a simple name string from various AST node types."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        value = _ast_name(node.value)
        if value:
            return f"{value}.{node.attr}"
        return node.attr
    elif isinstance(node, ast.Constant):
        return repr(node.value)
    elif isinstance(node, ast.Subscript):
        base = _ast_name(node.value)
        return f"{base}[...]" if base else None
    return None


# ---------------------------------------------------------------------------
# JavaScript / TypeScript (regex-based)
# ---------------------------------------------------------------------------

_JS_FUNCTION_RE = re.compile(
    r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
    re.MULTILINE,
)
_JS_ARROW_RE = re.compile(
    r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(?",
    re.MULTILINE,
)
_JS_CLASS_RE = re.compile(
    r"^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+)",
    re.MULTILINE,
)
_JS_INTERFACE_RE = re.compile(
    r"^(?:export\s+)?(?:interface|type)\s+(\w+)",
    re.MULTILINE,
)


def _extract_js_ts_symbols(
    path: str, content: str, language: str
) -> list[Symbol]:
    """Extract symbols from JavaScript/TypeScript using regex."""
    symbols: list[Symbol] = []

    for match in _JS_FUNCTION_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.FUNCTION,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path,
                symbol=match.group(1),
                line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _JS_CLASS_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.CLASS,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path,
                symbol=match.group(1),
                line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _JS_INTERFACE_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.TYPE,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path,
                symbol=match.group(1),
                line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    return symbols


# ---------------------------------------------------------------------------
# Go (regex-based)
# ---------------------------------------------------------------------------

_GO_FUNC_RE = re.compile(
    r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(",
    re.MULTILINE,
)
_GO_TYPE_RE = re.compile(
    r"^type\s+(\w+)\s+(struct|interface)",
    re.MULTILINE,
)


def _extract_go_symbols(path: str, content: str) -> list[Symbol]:
    """Extract symbols from Go using regex."""
    symbols: list[Symbol] = []

    for match in _GO_FUNC_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.FUNCTION,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _GO_TYPE_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        kind = SymbolKind.CLASS if match.group(2) == "struct" else SymbolKind.TYPE
        symbols.append(Symbol(
            name=match.group(1),
            kind=kind,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    return symbols


# ---------------------------------------------------------------------------
# JVM-style (Java, Kotlin, C#) (regex-based)
# ---------------------------------------------------------------------------

_JVM_CLASS_RE = re.compile(
    r"^(?:\w+\s+)*(?:class|interface|enum|record|object)\s+(\w+)",
    re.MULTILINE,
)
_JVM_METHOD_RE = re.compile(
    r"^\s+(?:(?:public|private|protected|internal|static|override|abstract|suspend|fun|async)\s+)*"
    r"(?:\w+(?:<[^>]+>)?(?:\[\])?\s+)?(\w+)\s*\(",
    re.MULTILINE,
)


def _extract_jvm_style_symbols(
    path: str, content: str, language: str
) -> list[Symbol]:
    """Extract symbols from Java/Kotlin/C# using regex."""
    symbols: list[Symbol] = []

    for match in _JVM_CLASS_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.CLASS,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _JVM_METHOD_RE.finditer(content):
        name = match.group(1)
        # Skip common false positives
        if name in ("if", "for", "while", "switch", "catch", "return", "new", "throw"):
            continue
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=name,
            kind=SymbolKind.METHOD,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=name, line_start=line_num,
                confidence=Confidence.LOW,
            )],
        ))

    return symbols


# ---------------------------------------------------------------------------
# Rust (regex-based)
# ---------------------------------------------------------------------------

_RUST_FN_RE = re.compile(
    r"^(?:pub(?:\(crate\))?\s+)?(?:async\s+)?fn\s+(\w+)",
    re.MULTILINE,
)
_RUST_STRUCT_RE = re.compile(
    r"^(?:pub(?:\(crate\))?\s+)?(?:struct|enum|trait)\s+(\w+)",
    re.MULTILINE,
)
_RUST_IMPL_RE = re.compile(
    r"^impl(?:<[^>]+>)?\s+(\w+)",
    re.MULTILINE,
)


def _extract_rust_symbols(path: str, content: str) -> list[Symbol]:
    """Extract symbols from Rust using regex."""
    symbols: list[Symbol] = []

    for match in _RUST_FN_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.FUNCTION,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _RUST_STRUCT_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.CLASS,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    return symbols


# ---------------------------------------------------------------------------
# Ruby (regex-based)
# ---------------------------------------------------------------------------

_RUBY_CLASS_RE = re.compile(r"^(?:\s*)class\s+(\w+)", re.MULTILINE)
_RUBY_MODULE_RE = re.compile(r"^(?:\s*)module\s+(\w+)", re.MULTILINE)
_RUBY_DEF_RE = re.compile(r"^(?:\s*)def\s+(self\.)?(\w+[?!=]?)", re.MULTILINE)


def _extract_ruby_symbols(path: str, content: str) -> list[Symbol]:
    """Extract symbols from Ruby using regex."""
    symbols: list[Symbol] = []

    for match in _RUBY_CLASS_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.CLASS,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _RUBY_MODULE_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.MODULE,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    for match in _RUBY_DEF_RE.finditer(content):
        name = match.group(2)
        line_num = content[:match.start()].count("\n") + 1
        kind = SymbolKind.METHOD if match.group(1) else SymbolKind.FUNCTION
        symbols.append(Symbol(
            name=name,
            kind=kind,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=name, line_start=line_num,
                confidence=Confidence.MEDIUM,
            )],
        ))

    return symbols


# ---------------------------------------------------------------------------
# Generic fallback (very low confidence)
# ---------------------------------------------------------------------------

_GENERIC_FUNC_RE = re.compile(
    r"^\s*(?:(?:export|public|private|protected|static|async|def|fn|func|function|sub|proc)\s+)+"
    r"(\w+)\s*\(",
    re.MULTILINE,
)
_GENERIC_CLASS_RE = re.compile(
    r"^\s*(?:(?:export|public|private|abstract)\s+)*"
    r"(?:class|struct|interface|trait|enum|type|object|record)\s+(\w+)",
    re.MULTILINE,
)


def _extract_generic_symbols(
    path: str, content: str, language: str
) -> list[Symbol]:
    """Fallback symbol extraction using generic regex patterns."""
    symbols: list[Symbol] = []

    for match in _GENERIC_CLASS_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.CLASS,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.LOW,
            )],
        ))

    for match in _GENERIC_FUNC_RE.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        symbols.append(Symbol(
            name=match.group(1),
            kind=SymbolKind.FUNCTION,
            file_path=path,
            line_start=line_num,
            evidence=[Evidence(
                path=path, symbol=match.group(1), line_start=line_num,
                confidence=Confidence.LOW,
            )],
        ))

    return symbols
