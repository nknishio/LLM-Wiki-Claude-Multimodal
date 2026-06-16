# llm-wiki skill + CLI

The `llm-wiki` Claude skill plus a bundled **`llm-wiki` CLI** that handles
everything the multimodal-ingest path needs, in **pure Python** — every
dependency is a pip wheel, so it installs identically on macOS, Windows, and
Linux with no system binaries to chase down.

The CLI does three things for the skill:

- **doc → Markdown** for PDF / PPTX / DOCX / XLSX / CSV / HTML
- **embedded-image extraction** from PDFs and Office files (with a noise filter)
- **SHA-256 caption caching** that dedups vision work (the agent writes the captions)

---

## Install (per machine)

```bash
# macOS / Linux
./install.sh

# Windows (PowerShell)
.\install.ps1
```

Each installer:

1. Installs [`uv`](https://docs.astral.sh/uv/) if it isn't already present.
2. Runs `uv tool install --force <skill-dir>` — builds the package and puts the
   `llm-wiki` command on your PATH inside an **isolated environment** (it never
   touches the system/Anaconda Python).
3. Runs `llm-wiki doctor` to confirm all dependencies import.

Verify any time:

```bash
llm-wiki doctor      # checks every dependency imports; exit 0 = ready
llm-wiki --version
```

**Manual / no-installer route:**

```bash
uv tool install --force .   # from the skill folder, with uv available
pip install .               # or into an existing venv with plain pip
```

`python3` (>=3.9) is the only prerequisite the installer assumes; `uv`
provides/manages the rest.

---

## The ingest workflow

`SKILL.md`'s **Multimodal Ingest** procedure calls the CLI at each step. A
local document flows through like this:

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
slug=$(llm-wiki slug "Q3 Ops Review.pptx")   # -> q3-ops-review

# ① convert the document to Markdown (one command for any supported type)
llm-wiki convert "input.pptx" --out "$WIKI/raw/articles/$slug.md"

# ② extract embedded images (sub-3 KB noise is dropped automatically)
llm-wiki extract-images "input.pptx" --out-dir "$WIKI/raw/assets/$slug"

# ③ caption each image — cache first, then the agent looks
llm-wiki caption get "$WIKI" "raw/assets/$slug/img-1.png"
#   HIT\t<caption>  -> reuse it, don't re-describe
#   MISS\t<sha>     -> the AGENT reads the image, writes a caption, then stores it:
llm-wiki caption put "$WIKI" "<sha>" "<model-id>" "image/png" "the caption text"

# ④ frontmatter hashes for provenance + drift detection
llm-wiki hash "input.pptx"                              # hash of the original binary
cat "$WIKI/raw/articles/$slug.md" | llm-wiki hash-text  # body hash for frontmatter
```

The agent then injects the captions into the converted Markdown and proceeds
with normal ingest — the images are now searchable text *and* still visible
on disk. The caption cache means any given image is described exactly once,
ever, even across decks and re-ingests.

If the CLI can't be installed on a given machine, the skill falls back to the
zero-dependency `scripts/caption_cache.py` for caching and the agent reads
documents directly.

---

## CLI reference

`llm-wiki <subcommand>`:

| Command | What it does | Output |
|---|---|---|
| `convert <input> [--out FILE]` | Doc → Markdown. Dispatches on extension: PDF, PPTX, DOCX, XLSX, XLS, CSV, HTML, HTM. | Markdown to stdout, or written to `FILE` |
| `extract-images <input> --out-dir DIR [--min-bytes N]` | Pulls embedded images. PDF via PyMuPDF (filenames carry page number: `img-p<N>-<id>.png`); Office files via stdlib `zipfile`; standalone image is copied. Drops files under `N` bytes (default 3072) as noise. | One written path per line (stdout) |
| `caption get <project> <image>` | Look up a caption by the SHA-256 of the image bytes. | `HIT\t<caption>` or `MISS\t<sha256>` |
| `caption put <project> <sha> <model> <mime> <caption>` | Store a caption in the cache. | `OK` |
| `hash <file>` | SHA-256 of a file's bytes (e.g. the original binary for provenance). | hex digest |
| `hash-text` | SHA-256 of **stdin** — used for the frontmatter body hash. | hex digest |
| `slug <name>` | Slugify a filename (lowercase, hyphens). | slug |
| `doctor` | Verify every dependency imports; print version + supported extensions. | report; exit 0 = ready |

---

## What's in the package

```
.claude/skills/llm-wiki/
├── SKILL.md                     # the skill instructions Claude reads
├── pyproject.toml               # package metadata + pinned deps + console-script entry point
├── README.md                    # this file
├── install.sh                   # macOS / Linux installer (bootstraps uv)
├── install.ps1                  # Windows / PowerShell installer (bootstraps uv)
├── src/
│   └── llm_wiki/
│       ├── __init__.py          # version
│       ├── cli.py               # argparse entry point -> `llm-wiki` command
│       ├── convert.py           # doc -> Markdown (per-extension dispatch)
│       ├── images.py            # embedded-image extraction + noise filter
│       └── caption_cache.py     # SHA-256 caption cache (importable module)
└── scripts/
    └── caption_cache.py         # zero-dependency fallback (standalone)
```

### Dependencies (all pip wheels, no system binaries)

Declared in `pyproject.toml`:

| Package | Used for |
|---|---|
| `pymupdf` (imports as `fitz`) | PDF text extraction + embedded-image extraction |
| `python-pptx` | PPTX slide text + tables |
| `python-docx` | DOCX paragraphs (heading-level aware) + tables |
| `pandas` | XLSX / CSV → Markdown tables |
| `openpyxl` | pandas' xlsx read engine |
| `tabulate` | `DataFrame.to_markdown()` |
| `markdownify` | HTML → Markdown |

---

## Design notes

- **Caption cache is byte-keyed and format-compatible.** Captions are keyed by
  the SHA-256 of the image *bytes*, not its path, so the same image is described
  exactly once. The on-disk JSON (`<project>/.llm-wiki/image-caption-cache.json`)
  uses the schema `caption` / `mimeType` / `model` / `capturedAt`, shared with
  the standalone `scripts/caption_cache.py` — no migration. Writes are atomic
  (temp file + `os.replace`).
- **The agent does the captioning.** `caption get`/`put` are split so the agent
  reads the image with its own multimodal capability in between. The CLI never
  calls an LLM — it stays provider-agnostic.
- **Noise filter is built in.** `extract-images` drops sub-3 KB files (logos,
  bullet decorations). Override with `--min-bytes 0` to keep everything.
- **Zero-dependency fallback preserved.** `scripts/caption_cache.py` still works
  on a machine where the CLI can't be installed.

**Known limitation:** `convert.py`'s PPTX path uses `python-pptx` shape
iteration, which does **not** see SmartArt text (SmartArt lives in raw slide
XML, `ppt/slides/slideN.xml` `<a:t>` runs). For SmartArt-heavy decks, parse
that XML manually.

---

## Distribution

Two routes, depending on how you run the agent:

**Route A — Claude Code plugin + internal marketplace (recommended).** Host this
folder as a plugin in a company git repo, wrapped with a
`.claude-plugin/plugin.json` manifest pointing at `skills/llm-wiki/`. Machines
run `/plugin marketplace add <org>/<repo>` then `/plugin install llm-wiki`; the
plugin's setup step runs the installer. Updates ship by pushing to the repo.

> Not yet added: the `.claude-plugin/plugin.json` manifest and a `uv.lock`
> lockfile (so every machine resolves identical dependency versions). Add both
> before publishing to the marketplace.

**Route B — standalone.** Drop this folder into `~/.claude/skills/llm-wiki/` (or
wherever your agent discovers skills) and run the installer once. Update with
`git pull` + re-running the installer.

Either way, **the CLI is the only binary to install**, and `uv` reduces that to
one command on every OS.
