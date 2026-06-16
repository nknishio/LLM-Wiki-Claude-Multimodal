"""llm-wiki: pure-Python helpers for the llm-wiki Claude skill.

Everything the multimodal-ingest path needs (doc->Markdown conversion,
embedded-image extraction, SHA-256 caption caching) lives here so the
skill calls one installed CLI instead of shelling out to markitdown,
poppler, or pandoc. All dependencies are pip wheels -> identical on
macOS, Windows, and Linux.
"""

__version__ = "2.2.0"
