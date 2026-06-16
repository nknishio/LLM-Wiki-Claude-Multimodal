# LLM-Wiki-Claude-Multimodal
PoC for LLM Wiki with implemented multimodal processing and image extraction/captioning, testing on Claude Code before integration to Hermes

The following are the changes and additions made to the Hermes agent's built-in LLM Wiki skill (reference: https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/research/research-llm-wiki)

1. **Cache helper** — .claude/skills/llm-wiki/scripts/caption_cache.py (smoke-tested: MISS → put → HIT, atomic writes). Keyed by SHA-256 of image bytes, with the exact on-disk schema (caption/mimeType/model/capturedAt) as the reference image-caption-pipeline.ts — so if you later add a scripted batch captioner (the Option B graft), it shares this file with no migration. get/put are split so the agent does the captioning in between, keeping the script provider-agnostic — no LLM call, no API key.

2. **Bundled `llm-wiki` CLI** — .claude/skills/llm-wiki/ now ships a pure-Python CLI (`pyproject.toml` + `src/llm_wiki/`, installed via `install.sh`/`install.ps1` → `uv tool install`). It replaces the previous external prerequisites (markitdown/poppler/pandoc/unzip) with pip wheels that install identically on macOS/Windows/Linux. Subcommands: `convert` (PDF/PPTX/DOCX/XLSX/CSV/HTML → Markdown via PyMuPDF/python-pptx/python-docx/pandas/markdownify), `extract-images` (PyMuPDF for PDFs, stdlib zipfile for Office, built-in sub-3 KB noise filter), `caption get/put` (wraps the SHA-256 cache), `hash`/`hash-text`/`slug`, and `doctor`. The standalone caption_cache.py (point 1) stays as a zero-dependency fallback. See .claude/skills/llm-wiki/README.md for the full reference.

3. **SKILL.md edits** (now v2.2.0):
- Activation list + architecture diagram — documents documents/images as sources, the raw/assets/<slug>/ media layout, and the .llm-wiki/ cache.
- Ingest ① now routes local PDF/PPTX/DOCX/XLSX/HTML/images into a new Multimodal Ingest procedure, then rejoins the normal flow.
- Multimodal Ingest subsection — the heart of it: install/probe the bundled `llm-wiki` CLI (`llm-wiki doctor`), then slugify → `llm-wiki convert` to MD → `llm-wiki extract-images` → cache-first caption (agent reads the image only on MISS, using the pinned factual prompt) → inject ![caption](path) so captions flow through search as ordinary text.
- SCHEMA.md raw frontmatter — added source_file/converted_from/media_dir.
- Lint ⑨a — media integrity (missing files, empty captions, orphaned media).
- Pitfalls — converted MD/images are immutable, cache-first, one bad image never aborts a batch.

### The flow it encodes

slugify → `llm-wiki convert` to MD (keep original binary) → `llm-wiki extract-images` to raw/assets/<slug>/ (tiny-noise filter built in) → per image: `llm-wiki caption get` → HIT reuse / MISS read+caption+`put` → inject captions → resume normal ingest


### Why this fits the Hermes goal

No second API key: the agent's own multimodal read does the captioning, inheriting whatever model Hermes runs — the CLI is provider-agnostic and never calls an LLM. It stays a single portable skill that drops into a Hermes agent exactly like llm-wiki already does. The conversion/extraction prerequisites are now bundled as a pure-Python CLI installed with one command (`uv`), so a fresh machine needs no manual markitdown/poppler/pandoc setup — while the shared cache format leaves the door open to bolt on scripted batch captioning later without rework.

### Note

The bundled CLI is the only thing to install per machine (`./install.sh` bootstraps `uv` and installs it in an isolated env; verify with `llm-wiki doctor`). The skill still degrades gracefully to the zero-dependency caption_cache.py if the CLI can't be installed.

