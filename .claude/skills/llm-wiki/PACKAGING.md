# llm-wiki CLI — build & integration guide

This document describes the `llm-wiki` CLI that backs the multimodal-ingest
path of the **llm-wiki** Claude skill, why it exists, what it contains, and
how to install and distribute it across an organization.

---

## 1. Why this exists

The skill's original `SKILL.md` shelled out to system tools for converting
documents and extracting images during ingest:

| Capability | Original tool | Problem |
|---|---|---|
| Any doc → Markdown | `markitdown` (pip) | Needs Python 3.10+; on Anaconda 3.9 pip only resolves an ancient `0.0.1a1` with no CLI. Large, fragile dependency tree. |
| Text/images from PDF | `poppler` (`pdftotext`, `pdfimages`, `pdftoppm`) | System binary; `brew install poppler` fails on this machine (Cellar ownership). Per-OS install divergence. |
| docx/odt/html fallback | `pandoc` | System binary; another per-OS install. |
| Images from PPTX/DOCX | `unzip` | Not guaranteed on Windows. |

These are precisely the tools that are hardest to install reliably across a
fleet of mixed macOS / Windows / Linux machines, and several were already
broken locally.

**The fix:** replace all of them with a single bundled CLI whose every
dependency is a **pure-Python wheel**. No system binaries. Identical install
on every OS. The skill now calls one command — `llm-wiki …` — for all
conversion, image extraction, and caption caching.

---

## 2. What was built

```
.claude/skills/llm-wiki/
├── SKILL.md                     # updated: calls `llm-wiki …`, not markitdown/poppler/unzip
├── pyproject.toml               # package metadata + pinned deps + console-script entry point
├── README.md                    # short install + usage card
├── PACKAGING.md                 # this file
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
    └── caption_cache.py         # UNCHANGED zero-dependency fallback (standalone)
```

### 2.1 Dependencies (all pip wheels, no system binaries)

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

`python3` (>=3.9) is the only prerequisite the installer assumes; `uv`
provides/manages the rest.

### 2.2 The CLI surface

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

### 2.3 Design notes / guarantees

- **Caption cache is byte-keyed and format-compatible.** Captions are keyed
  by the SHA-256 of the image *bytes*, not its path, so the same image is
  described exactly once. The on-disk JSON
  (`<project>/.llm-wiki/image-caption-cache.json`) uses the identical schema
  (`caption` / `mimeType` / `model` / `capturedAt`) as the standalone
  `scripts/caption_cache.py` and the original TS pipeline — the three share
  one file with no migration. Writes are atomic (temp file + `os.replace`).
- **The agent still does the captioning.** `caption get`/`put` are split so
  the agent reads the image with its own multimodal capability in between.
  The CLI never calls an LLM — it stays provider-agnostic.
- **Noise filter is built in.** `extract-images` drops sub-3 KB files
  (logos, bullet decorations). Override with `--min-bytes 0` to keep all.
- **Zero-dependency fallback preserved.** `scripts/caption_cache.py` is left
  untouched so caching still works on a machine where the CLI can't be
  installed (the agent reads docs directly and uses the script for the cache).

### 2.4 Known limitation

`convert.py`'s PPTX path uses `python-pptx` shape iteration, which **does not
see SmartArt text** (SmartArt lives in raw slide XML, `ppt/slides/slideN.xml`
`<a:t>` runs). For SmartArt-heavy decks, parse that XML manually. This
matches the pre-existing limitation of the toolchain.

---

## 3. Installation

### Per machine

```bash
# macOS / Linux
./install.sh

# Windows (PowerShell)
.\install.ps1
```

Each installer:

1. Installs [`uv`](https://docs.astral.sh/uv/) if it isn't already present.
2. Runs `uv tool install --force <skill-dir>` — builds the package and puts
   the `llm-wiki` command on the PATH inside an **isolated environment**
   (it never touches the system/Anaconda Python).
3. Runs `llm-wiki doctor` to confirm all dependencies import.

Verify any time:

```bash
llm-wiki doctor
llm-wiki --version
```

### Manual / no-installer route

```bash
# from the skill folder, with uv available:
uv tool install --force .

# or into an existing venv with plain pip:
pip install .
```

---

## 4. How the skill uses it (integration points)

`SKILL.md` was updated so the **Multimodal Ingest** procedure calls the CLI.
The relevant steps:

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"

# ② convert text -> Markdown
llm-wiki convert "input.pdf" --out "$WIKI/raw/papers/<slug>.md"

# ③ extract embedded images (3 KB noise filter is built in)
llm-wiki extract-images "input.pdf" --out-dir "$WIKI/raw/assets/<slug>"

# ④ caption each image — cache first, then the agent looks
llm-wiki caption get "$WIKI" "raw/assets/<slug>/img-1.png"
#   HIT\t<caption>  -> reuse, don't re-describe
#   MISS\t<sha>     -> agent reads the image, writes a caption, then:
llm-wiki caption put "$WIKI" "<sha>" "<model-id>" "image/png" "the caption text"

# frontmatter hashes / naming
llm-wiki hash "input.pdf"          # provenance hash of the original binary
cat "$WIKI/raw/papers/<slug>.md" | llm-wiki hash-text   # body hash for frontmatter
llm-wiki slug "Q3 Ops Review.pptx" # -> q3-ops-review
```

If the CLI is unavailable and can't be installed, `SKILL.md` instructs the
agent to fall back to `scripts/caption_cache.py` and read documents directly
— **not** to reach for markitdown/poppler (intentionally removed).

---

## 5. Company-wide distribution

Two routes, depending on how Claude Code is run:

### Route A — Claude Code plugin + internal marketplace (recommended)

Host this folder as a plugin in a company git repo. Wrap it with a
`.claude-plugin/plugin.json` manifest pointing at `skills/llm-wiki/`. Then
every machine:

```text
/plugin marketplace add <org>/<repo>
/plugin install llm-wiki
```

The plugin's setup step runs `install.sh` / `install.ps1`. Updates ship by
pushing to the repo — no re-imaging machines.

> Not yet added: the `.claude-plugin/plugin.json` manifest and a `uv.lock`
> lockfile (so every machine resolves identical dependency versions). Add
> both before publishing to the marketplace.

### Route B — standalone

Drop this folder into `~/.claude/skills/llm-wiki/` on each machine and run
the installer once. Update with `git pull` + re-running the installer.

Either way, **the CLI is the only binary to install**, and `uv` reduces that
to a single command on every OS.

---

## 6. Verification performed

Built into a clean environment and exercised end-to-end against real
fixtures:

- `doctor` — all 7 dependencies import; reports version + supported extensions.
- `convert` — PDF, PPTX, CSV, HTML produce correct Markdown (PDF page markers,
  PPTX slide headings, CSV/HTML tables and lists).
- `extract-images` — extracts a noisy PNG from a PDF; correctly **drops** a
  sub-3 KB solid-color image via the noise filter.
- `caption get/put` — round-trips MISS → put → HIT; writes the expected
  `image-caption-cache.json` schema atomically.
- `hash` / `hash-text` / `slug` — produce expected digests and slugs.

(`uv` was not present on the build machine, so verification used a `pip
install` of the same package into a throwaway venv; the installers bring `uv`
in on a fresh box.)
