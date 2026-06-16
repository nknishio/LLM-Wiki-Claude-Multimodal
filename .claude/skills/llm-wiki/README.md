# llm-wiki skill + CLI

The `llm-wiki` Claude skill plus a bundled **`llm-wiki` CLI** that handles
everything the multimodal-ingest path needs in pure Python:

- **doc -> Markdown** for PDF / PPTX / DOCX / XLSX / CSV / HTML
- **embedded-image extraction** from PDFs and Office files
- **SHA-256 caption caching** (dedups vision work; agent does the captioning)

No `markitdown`, no `poppler`, no `pandoc`, no `unzip` -- every dependency
is a pip wheel, so installs are identical on macOS, Windows, and Linux.

## Install (per machine)

```bash
# macOS / Linux
./install.sh

# Windows (PowerShell)
.\install.ps1
```

The installer bootstraps [`uv`](https://docs.astral.sh/uv/) if needed, then
runs `uv tool install` to put `llm-wiki` on your PATH in an isolated env
(it never touches the system Python). Verify with:

```bash
llm-wiki doctor      # checks every dependency imports
llm-wiki --version
```

## CLI usage

```bash
llm-wiki convert input.pdf --out raw/papers/slug.md   # doc -> Markdown
llm-wiki extract-images input.pptx --out-dir raw/assets/slug
llm-wiki caption get  "$WIKI" raw/assets/slug/img-1.png   # HIT/MISS
llm-wiki caption put  "$WIKI" <sha> <model> image/png "caption text"
llm-wiki hash raw/papers/slug.pdf        # sha256 of the original binary
cat body.md | llm-wiki hash-text         # sha256 of frontmatter body
llm-wiki slug "Q3 Ops Review.pptx"       # -> q3-ops-review
```

## Distribute to the whole company

Two routes, depending on how you run Claude Code:

1. **Claude Code plugin + internal marketplace.** Host this folder as a
   plugin in a company git repo (`.claude-plugin/plugin.json` wrapping
   `skills/llm-wiki/`). Machines run `/plugin marketplace add <org>/repo`
   then `/plugin install llm-wiki`. The plugin's install step runs
   `install.sh` / `install.ps1`. Updates ship by pushing to the repo.
2. **Standalone.** Drop this folder into `~/.claude/skills/llm-wiki/` and
   run the installer once. Update by `git pull` + re-running the installer.

Either way the CLI is the only binary to install, and `uv` makes that one
command on every OS.
