"""SHA-256 caption cache (package version, importable + used by the CLI).

Captions are keyed by the hash of the image BYTES (not its path), so the
same image -- a logo reused across 50 decks, or a re-ingested source -- is
only described once, by the agent, ever. The cache lives at
`<project>/.llm-wiki/image-caption-cache.json`.

The on-disk schema (caption / mimeType / model / capturedAt) is identical
to the standalone `scripts/caption_cache.py` and the TS
`image-caption-pipeline.ts` cache, so all three share one file with no
migration. This module never calls an LLM -- the agent does the captioning
between `get` and `put`.
"""
import datetime
import hashlib
import json
import os

CACHE_REL = ".llm-wiki/image-caption-cache.json"


def cache_path(project: str) -> str:
    return os.path.join(project, CACHE_REL)


def load(project: str) -> dict:
    path = cache_path(project)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        # Corrupt/truncated cache -- start fresh rather than wedge ingest.
        return {}


def save(project: str, cache: dict) -> None:
    path = cache_path(project)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)  # atomic; no half-written cache on crash


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get(project: str, image: str) -> str:
    """Return 'HIT\\t<caption>' or 'MISS\\t<sha256>'."""
    digest = sha256_file(image)
    entry = load(project).get(digest)
    if entry and entry.get("caption"):
        return "HIT\t" + entry["caption"].replace("\n", " ")
    return "MISS\t" + digest


def put(project: str, digest: str, model: str, mime: str, caption: str) -> str:
    cache = load(project)
    cache[digest] = {
        "caption": caption,
        "mimeType": mime,
        "model": model,
        "capturedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    save(project, cache)
    return "OK"
