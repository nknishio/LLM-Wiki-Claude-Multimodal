# LLM-Wiki-Claude-Multimodal
PoC for LLM Wiki with implemented multimodal processing and image extraction/captioning, testing on Claude Code before integration to Hermes

The following are the changes and additions made to the Hermes agent's built-in LLM Wiki skill (reference: https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/research/research-llm-wiki)

1. **Cache helper** — .claude/skills/llm-wiki/scripts/caption_cache.py (smoke-tested: MISS → put → HIT, atomic writes). Keyed by SHA-256 of image bytes, with the exact on-disk schema (caption/mimeType/model/capturedAt) as the reference image-caption-pipeline.ts — so if you later add a scripted batch captioner (the Option B graft), it shares this file with no migration. get/put are split so the agent does the captioning in between, keeping the script provider-agnostic — no LLM call, no API key.

2. **SKILL.md edits** (now v2.2.0):
- Activation list + architecture diagram — documents documents/images as sources, the raw/assets/<slug>/ media layout, and the .llm-wiki/ cache.
- Ingest ① now routes local PDF/PPTX/DOCX/XLSX/HTML/images into a new Multimodal Ingest procedure, then rejoins the normal flow.
- Multimodal Ingest subsection — the heart of it: prereq probe table (markitdown primary, pandoc/pdftotext/pdfimages/unzip fallbacks), then slugify → convert-to-MD → extract images → cache-first caption (agent reads the image only on MISS, using the pinned factual prompt) → inject ![caption](path) so captions flow through search as ordinary text.
- SCHEMA.md raw frontmatter — added source_file/converted_from/media_dir.
- Lint ⑨a — media integrity (missing files, empty captions, orphaned media).
- Pitfalls — converted MD/images are immutable, cache-first, one bad image never aborts a batch.

### The flow it encodes

slugify → markitdown to MD (keep original binary) → pdfimages/unzip to raw/assets/<slug>/ → filter tiny noise → per image: cache get → HIT reuse / MISS read+caption+put → inject captions → resume normal ingest


### Why this fits the Hermes goal                                                 

Zero new runtime: pure skill prose + one stdlib-only Python helper, no app, no second API key (the agent's own multimodal read does captioning, inheriting whatever model Hermes runs). It stays a single portable skill that drops into a Hermes agent exactly like llm-wiki already does — while the shared cache format leaves the door open to bolt on scripted batch captioning later without rework.

### Two notes:
-  The markitdown/poppler tools are runtime prerequisites, not bundled — the skill probes and degrades gracefully, but the host needs them installed for non-MD ingest to work.
- The reference image-cadal-images.md is still untracked in the repo root. They served as the capability spec; want me to move them into a docs/ oe them), or leave thembe?

