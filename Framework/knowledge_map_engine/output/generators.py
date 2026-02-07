"""
Output artifact generators.

Each function generates one output artifact from a ScanResult.
All generators are pure functions: ScanResult in, file content out.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from Framework.knowledge_map_engine.ir.models import Confidence

if TYPE_CHECKING:
    from Framework.knowledge_map_engine.core.engine import ScanResult

logger = logging.getLogger(__name__)


def generate_all_artifacts(result: ScanResult, output_dir: str) -> list[str]:
    """
    Generate all output artifacts and write them to output_dir.

    Returns list of generated file paths.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []

    generators = [
        ("SYSTEM_OVERVIEW.md", generate_system_overview),
        ("FEATURE_CATALOG.md", generate_feature_catalog),
        ("INTERFACE_CATALOG.json", generate_interface_catalog),
        ("DATA_TOUCH_MAP.json", generate_data_touch_map),
        ("WORKFLOW_BOOK.md", generate_workflow_book),
        ("KNOWN_HAZARDS.md", generate_known_hazards),
        ("feature_graph.json", generate_feature_graph),
        ("claude_context_pack.md", generate_claude_context_pack),
        ("claude_context_pack_index.json", generate_claude_context_pack_index),
    ]

    for filename, generator in generators:
        try:
            content = generator(result)
            filepath = out / filename
            filepath.write_text(content, encoding="utf-8")
            generated.append(str(filepath))
            logger.info("Generated: %s", filepath)
        except Exception:
            logger.exception("Failed to generate %s", filename)

    return generated


# ---------------------------------------------------------------------------
# SYSTEM_OVERVIEW.md
# ---------------------------------------------------------------------------

def generate_system_overview(result: ScanResult) -> str:
    """Generate a high-level system overview document."""
    snap = result.snapshot
    meta = result.metadata

    languages = snap.metadata.get("languages", {})
    top_languages = list(languages.items())[:10]

    lines = [
        "# System Overview",
        "",
        f"**Repository**: `{snap.root_path}`",
        f"**Total Files**: {meta.get('total_files', len(snap.files))}",
        f"**Total Symbols**: {meta.get('total_symbols', len(snap.symbols))}",
        f"**Total Interfaces**: {meta.get('total_interfaces', len(snap.interfaces))}",
        f"**Scan Duration**: {result.scan_duration_seconds:.2f}s",
        f"**Adapters Used**: {', '.join(result.adapters_used) or 'none (generic only)'}",
        "",
        "## Languages",
        "",
        "| Language | Files |",
        "|----------|-------|",
    ]
    for lang, count in top_languages:
        lines.append(f"| {lang} | {count} |")

    lines.extend([
        "",
        "## File Categories",
        "",
        f"- **Source files**: {sum(1 for f in snap.files if not f.is_test and not f.is_config and not f.is_documentation and not f.is_generated)}",
        f"- **Test files**: {sum(1 for f in snap.files if f.is_test)}",
        f"- **Config files**: {sum(1 for f in snap.files if f.is_config)}",
        f"- **Documentation**: {sum(1 for f in snap.files if f.is_documentation)}",
        f"- **Generated/Lock**: {sum(1 for f in snap.files if f.is_generated)}",
    ])

    if snap.interfaces:
        lines.extend([
            "",
            "## Interface Summary",
            "",
        ])
        kinds: dict[str, int] = {}
        for iface in snap.interfaces:
            kinds[iface.kind.value] = kinds.get(iface.kind.value, 0) + 1
        for kind, count in sorted(kinds.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{kind}**: {count} interfaces")

    if snap.hazards:
        lines.extend([
            "",
            f"## Hazards ({len(snap.hazards)} detected)",
            "",
        ])
        for hazard in snap.hazards[:5]:
            lines.append(f"- [{hazard.severity.upper()}] {hazard.description}")
        if len(snap.hazards) > 5:
            lines.append(f"- ... and {len(snap.hazards) - 5} more (see KNOWN_HAZARDS.md)")

    lines.extend([
        "",
        "## Confidence Note",
        "",
        "Facts are labeled **High**, **Medium**, or **Low** confidence.",
        "High confidence = supported by extracted facts + evidence.",
        "Medium/Low = heuristic or pattern-based detection, may need verification.",
    ])

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# FEATURE_CATALOG.md
# ---------------------------------------------------------------------------

def generate_feature_catalog(result: ScanResult) -> str:
    """Generate the feature catalog document."""
    snap = result.snapshot
    lines = [
        "# Feature Catalog",
        "",
    ]

    if not snap.features:
        lines.extend([
            "No features were extracted by the current scan.",
            "",
            "Features are typically populated by LLM-based atom generation",
            "or by adapters that can infer feature boundaries from code structure.",
            "",
            "## Symbols by File (as proxy)",
            "",
        ])
        # Group symbols by file as a feature proxy
        by_file: dict[str, list] = {}
        for sym in snap.symbols:
            by_file.setdefault(sym.file_path, []).append(sym)

        for fpath, syms in sorted(by_file.items()):
            if len(syms) > 1:
                lines.append(f"### `{fpath}`")
                for s in syms[:20]:
                    lines.append(f"- `{s.qualified_name}` ({s.kind.value})")
                if len(syms) > 20:
                    lines.append(f"- ... +{len(syms) - 20} more")
                lines.append("")
    else:
        for feat in snap.features:
            conf = feat.confidence.value
            lines.append(f"## {feat.name} [{conf}]")
            lines.append("")
            if feat.description:
                lines.append(feat.description)
                lines.append("")
            if feat.symbols:
                lines.append("**Symbols:**")
                for sym in feat.symbols:
                    lines.append(f"- `{sym}`")
                lines.append("")
            if feat.interfaces:
                lines.append("**Interfaces:**")
                for iface in feat.interfaces:
                    lines.append(f"- `{iface}`")
                lines.append("")
            if feat.evidence:
                lines.append("**Evidence:**")
                for ev in feat.evidence:
                    loc = ev.path
                    if ev.line_start:
                        loc += f":{ev.line_start}"
                    lines.append(f"- `{loc}`")
                lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# INTERFACE_CATALOG.json
# ---------------------------------------------------------------------------

def generate_interface_catalog(result: ScanResult) -> str:
    """Generate the interface catalog as JSON."""
    catalog = {
        "version": "1.0",
        "description": "All detected interfaces (HTTP, gRPC, CLI, UI, job, lib, etc.)",
        "total": len(result.snapshot.interfaces),
        "interfaces": [i.to_dict() for i in result.snapshot.interfaces],
    }
    return json.dumps(catalog, indent=2) + "\n"


# ---------------------------------------------------------------------------
# DATA_TOUCH_MAP.json
# ---------------------------------------------------------------------------

def generate_data_touch_map(result: ScanResult) -> str:
    """Generate the data touch map as JSON."""
    touch_map = {
        "version": "1.0",
        "description": "All detected external data interactions (db, file, queue, cache, network)",
        "total": len(result.snapshot.data_touches),
        "data_touches": [d.to_dict() for d in result.snapshot.data_touches],
    }
    return json.dumps(touch_map, indent=2) + "\n"


# ---------------------------------------------------------------------------
# WORKFLOW_BOOK.md
# ---------------------------------------------------------------------------

def generate_workflow_book(result: ScanResult) -> str:
    """Generate the workflow book document."""
    snap = result.snapshot
    lines = [
        "# Workflow Book",
        "",
    ]

    if not snap.workflows:
        lines.extend([
            "No workflows were extracted by the current scan.",
            "",
            "Workflows are typically populated by LLM-based analysis",
            "that traces user-facing flows through the codebase.",
            "",
        ])

        # Provide interface-based flow hints
        if snap.interfaces:
            lines.extend([
                "## Detected Entry Points (workflow hints)",
                "",
            ])
            for iface in snap.interfaces[:20]:
                conf = iface.confidence.value
                handler = iface.handler_symbol or "unknown"
                lines.append(
                    f"- [{iface.kind.value}] **{iface.name}** "
                    f"-> `{handler}` [{conf}]"
                )
            if len(snap.interfaces) > 20:
                lines.append(
                    f"- ... +{len(snap.interfaces) - 20} more "
                    "(see INTERFACE_CATALOG.json)"
                )
    else:
        for wf in snap.workflows:
            conf = wf.confidence.value
            lines.append(f"## {wf.name} [{conf}]")
            lines.append("")
            if wf.description:
                lines.append(wf.description)
                lines.append("")
            if wf.entry_interface:
                lines.append(f"**Entry**: `{wf.entry_interface}`")
                lines.append("")
            if wf.steps:
                lines.append("**Steps:**")
                for i, step in enumerate(wf.steps, 1):
                    lines.append(f"{i}. {step}")
                lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# KNOWN_HAZARDS.md
# ---------------------------------------------------------------------------

def generate_known_hazards(result: ScanResult) -> str:
    """Generate the known hazards document."""
    snap = result.snapshot
    lines = [
        "# Known Hazards",
        "",
        "Hazards are sources of mapping uncertainty or code quality concerns",
        "identified during the scan.",
        "",
    ]

    if not snap.hazards:
        lines.append("No hazards detected.")
    else:
        # Group by kind
        by_kind: dict[str, list] = {}
        for h in snap.hazards:
            by_kind.setdefault(h.kind.value, []).append(h)

        for kind, hazards in sorted(by_kind.items()):
            lines.append(f"## {kind.replace('_', ' ').title()} ({len(hazards)})")
            lines.append("")
            for h in hazards:
                lines.append(f"- **[{h.severity.upper()}]** {h.description}")
                if h.affected_paths:
                    for p in h.affected_paths[:5]:
                        lines.append(f"  - `{p}`")
                    if len(h.affected_paths) > 5:
                        lines.append(f"  - ... +{len(h.affected_paths) - 5} more")
            lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# feature_graph.json
# ---------------------------------------------------------------------------

def generate_feature_graph(result: ScanResult) -> str:
    """Generate the feature graph as JSON."""
    return result.graph.to_json(indent=2) + "\n"


# ---------------------------------------------------------------------------
# claude_context_pack.md
# ---------------------------------------------------------------------------

def generate_claude_context_pack(result: ScanResult) -> str:
    """
    Generate a Claude-optimized context pack.

    This is a single markdown document designed to be dropped into a Claude
    conversation as system context. It contains the most important facts
    about the codebase in a format optimized for LLM consumption.
    """
    snap = result.snapshot
    lines = [
        "# Claude Context Pack",
        "",
        "This document contains extracted facts about the codebase.",
        "Use it as context for code-related questions and tasks.",
        "",
        "## Repository Summary",
        "",
        f"- **Root**: `{snap.root_path}`",
        f"- **Files**: {len(snap.files)}",
        f"- **Symbols**: {len(snap.symbols)}",
        f"- **Interfaces**: {len(snap.interfaces)}",
        f"- **Data Touches**: {len(snap.data_touches)}",
        f"- **Hazards**: {len(snap.hazards)}",
        "",
    ]

    # Top languages
    languages = snap.metadata.get("languages", {})
    if languages:
        lines.append("## Languages")
        lines.append("")
        for lang, count in list(languages.items())[:8]:
            lines.append(f"- {lang}: {count} files")
        lines.append("")

    # Key interfaces (high confidence only)
    high_conf_interfaces = [
        i for i in snap.interfaces if i.confidence == Confidence.HIGH
    ]
    if high_conf_interfaces:
        lines.append(f"## Key Interfaces ({len(high_conf_interfaces)} high-confidence)")
        lines.append("")
        for iface in high_conf_interfaces[:30]:
            handler = f" -> `{iface.handler_symbol}`" if iface.handler_symbol else ""
            lines.append(f"- [{iface.kind.value}] **{iface.name}**{handler}")
        if len(high_conf_interfaces) > 30:
            lines.append(f"- ... +{len(high_conf_interfaces) - 30} more")
        lines.append("")

    # Key symbols (classes and top-level functions only, limited)
    key_symbols = [
        s for s in snap.symbols
        if s.kind.value in ("class", "component", "module")
    ]
    if key_symbols:
        lines.append(f"## Key Symbols ({len(key_symbols)} classes/components)")
        lines.append("")
        for sym in key_symbols[:40]:
            loc = f"{sym.file_path}"
            if sym.line_start:
                loc += f":{sym.line_start}"
            doc = f" - {sym.docstring[:80]}..." if sym.docstring and len(sym.docstring) > 80 else (f" - {sym.docstring}" if sym.docstring else "")
            lines.append(f"- `{sym.qualified_name}` at `{loc}`{doc}")
        if len(key_symbols) > 40:
            lines.append(f"- ... +{len(key_symbols) - 40} more")
        lines.append("")

    # Hazards
    if snap.hazards:
        lines.append(f"## Hazards ({len(snap.hazards)})")
        lines.append("")
        for h in snap.hazards[:10]:
            lines.append(f"- [{h.severity}] {h.description}")
        lines.append("")

    # Provenance
    if snap._provenance:
        lines.append("## Provenance")
        lines.append("")
        for key, values in snap._provenance.items():
            lines.append(f"- {key}: {', '.join(values)}")
        lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# claude_context_pack_index.json
# ---------------------------------------------------------------------------

def generate_claude_context_pack_index(result: ScanResult) -> str:
    """
    Generate an index for the Claude context pack.

    This JSON file maps features/interfaces to their source locations,
    enabling targeted context retrieval.
    """
    snap = result.snapshot

    index: dict[str, Any] = {
        "version": "1.0",
        "repo_root": snap.root_path,
        "files": len(snap.files),
        "symbols": {},
        "interfaces": {},
        "data_touches": {},
    }

    # Index symbols by file
    by_file: dict[str, list[str]] = {}
    for sym in snap.symbols:
        by_file.setdefault(sym.file_path, []).append(sym.qualified_name)
    index["symbols_by_file"] = by_file

    # Index interfaces
    for i, iface in enumerate(snap.interfaces):
        key = f"{iface.kind.value}:{iface.name}"
        index["interfaces"][key] = {
            "handler": iface.handler_symbol,
            "path_pattern": iface.path_pattern,
            "evidence": [e.path for e in iface.evidence],
            "confidence": iface.confidence.value,
        }

    # Index data touches
    for dt in snap.data_touches:
        key = f"{dt.kind.value}:{dt.name}"
        index["data_touches"][key] = {
            "target": dt.target,
            "operation": dt.operation,
            "evidence": [e.path for e in dt.evidence],
            "confidence": dt.confidence.value,
        }

    return json.dumps(index, indent=2) + "\n"
