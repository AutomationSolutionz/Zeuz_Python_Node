"""
Generic Scanner - the always-on universal code scanner.

This scanner works on any repository regardless of language or framework.
It provides baseline file classification, language detection, symbol extraction,
and hazard detection using language-agnostic heuristics.
"""

from Framework.knowledge_map_engine.scanner.generic_scanner import GenericScanner
from Framework.knowledge_map_engine.scanner.language_detect import detect_language
from Framework.knowledge_map_engine.scanner.file_classifier import classify_file
from Framework.knowledge_map_engine.scanner.symbol_extractor import extract_symbols

__all__ = [
    "GenericScanner",
    "classify_file",
    "detect_language",
    "extract_symbols",
]
