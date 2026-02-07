"""
Output artifact generators for the Knowledge Map Engine.

Generates the standard KME output artifacts:
- SYSTEM_OVERVIEW.md
- FEATURE_CATALOG.md
- INTERFACE_CATALOG.json
- DATA_TOUCH_MAP.json
- WORKFLOW_BOOK.md
- KNOWN_HAZARDS.md
- feature_graph.json
- claude_context_pack.md
- claude_context_pack_index.json
"""

from Framework.knowledge_map_engine.output.generators import generate_all_artifacts

__all__ = ["generate_all_artifacts"]
