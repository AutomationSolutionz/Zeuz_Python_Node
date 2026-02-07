"""
React Web adapter - detects and extracts facts from React/Next.js applications.

Extracts component definitions, page routes (file-based and code-based),
API calls (fetch/axios), state management patterns, and UI event handlers.
"""

from Framework.knowledge_map_engine.adapters.react_web.adapter import ReactWebAdapter

__all__ = ["ReactWebAdapter"]
