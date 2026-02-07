"""
Python Web adapter - detects and extracts facts from Python web frameworks.

Supports detection of Django, FastAPI, Flask, Starlette, Tornado, Sanic,
and other ASGI/WSGI frameworks. Extracts HTTP routes, middleware, ORM models,
and other web-specific patterns.

This adapter does NOT assume any specific framework - it probes for indicators
and extracts facts only when evidence is found.
"""

from Framework.knowledge_map_engine.adapters.python_web.adapter import PythonWebAdapter

__all__ = ["PythonWebAdapter"]
