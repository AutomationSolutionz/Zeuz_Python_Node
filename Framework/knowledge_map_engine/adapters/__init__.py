"""
Adapter plugin system for the Knowledge Map Engine.

Adapters are optional plugins that add ecosystem-specific fact extraction.
They must implement the Adapter base class and register via the AdapterRegistry.

Adapters only output IR facts - never final documents.
"""

from Framework.knowledge_map_engine.adapters.base import Adapter, AdapterRegistry

__all__ = ["Adapter", "AdapterRegistry"]
