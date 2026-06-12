#!/usr/bin/env python3
"""SHA-256 caption cache for the llm-wiki multimodal ingest path.

Captions are keyed by the hash of the image BYTES (not its path), so
the same image — a logo reused across 50 decks, or a re-ingested
source — is only described once, by the agent, ever. The cache lives
at `<project>/.llm-wiki/image-caption-cache.json`.

The on-disk schema (caption / mimeType / model / capturedAt) is
deliberately identical to the TS `image-caption-pipeline.ts` cache, so
a future scripted/batch captioner can share this exact file with no
migration.

Usage:
  caption_cache.py get <project_path> <image_path>
      -> "HIT\\t<caption>"   cache hit — reuse this caption, skip the VLM
      -> "MISS\\t<sha256>"   no entry — caption the image, then `put` it
  caption_cache.py put <project_path> <sha256> <model> <mime> <caption>
      -> "OK"

`get` and `put` are split so the agent can do the actual captioning in
between (look at the image with its own multimodal read), keeping this
script provider-agnostic — it never calls an LLM itself.
"""
import datetime
import hashlib
import json
import os
import sys

CACHE_REL = ".llm-wiki/image-caption-cache.json"


def _cache_path(project: str) -> str:
    return os.path.join(project, CACHE_REL)


def _load(project: str) -> dict:
    path = _cache_path(project)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        # Corrupt/truncated cache — start fresh rather than wedge the
        # whole ingest. A re-caption is cheaper than a stuck pipeline.
        return {}


def _save(project: str, cache: dict) -> None:
    path = _cache_path(project)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)  # atomic; no half-written cache on crash


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list) -> int:
    if len(argv) < 2:
        print("usage: caption_cache.py get|put ...", file=sys.stderr)
        return 2

    cmd = argv[1]

    if cmd == "get":
        if len(argv) != 4:
            print("usage: caption_cache.py get <project> <image>", file=sys.stderr)
            return 2
        project, image = argv[2], argv[3]
        digest = _sha256_file(image)
        entry = _load(project).get(digest)
        if entry and entry.get("caption"):
            sys.stdout.write("HIT\t" + entry["caption"].replace("\n", " "))
        else:
            sys.stdout.write("MISS\t" + digest)
        return 0

    if cmd == "put":
        if len(argv) != 7:
            print(
                "usage: caption_cache.py put <project> <sha256> <model> <mime> <caption>",
                file=sys.stderr,
            )
            return 2
        project, digest, model, mime, caption = argv[2:7]
        cache = _load(project)
        cache[digest] = {
            "caption": caption,
            "mimeType": mime,
            "model": model,
            "capturedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        _save(project, cache)
        sys.stdout.write("OK")
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
