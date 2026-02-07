"""
Knowledge Map Engine (KME) - Framework-Agnostic Code Analysis

A two-layer architecture:
  Layer A (Core): Universal concepts - files, symbols, interfaces, data touches
  Layer B (Adapters): Optional plugins that extract ecosystem-specific facts

The core never assumes any framework, language, or runtime. Adapters add
extra fact extraction per ecosystem but only output IR objects - never final docs.
"""

__version__ = "0.1.0"
