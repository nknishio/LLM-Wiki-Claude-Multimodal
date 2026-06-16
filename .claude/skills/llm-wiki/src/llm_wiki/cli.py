"""`llm-wiki` CLI -- the single entry point the skill calls.

Subcommands:
  convert <input> [--out FILE]            doc -> Markdown (stdout or FILE)
  extract-images <input> --out-dir DIR    embedded images -> DIR (prints paths)
  caption get <project> <image>           -> "HIT\\t<caption>" | "MISS\\t<sha>"
  caption put <project> <sha> <model> <mime> <caption>   -> "OK"
  hash <file>                             sha256 of a file's bytes
  hash-text                               sha256 of stdin (frontmatter body hash)
  slug <name>                             slugified base name
  doctor                                  verify deps are importable

All conversion/extraction is pure Python -- no markitdown, poppler, or
pandoc. See `convert.SUPPORTED` for handled extensions.
"""
import argparse
import sys

from . import __version__, caption_cache, convert, images


def _cmd_convert(args) -> int:
    md = convert.convert(args.input)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(md + "\n")
        sys.stderr.write("wrote {} chars -> {}\n".format(len(md), args.out))
    else:
        sys.stdout.write(md)
    return 0


def _cmd_extract_images(args) -> int:
    written = images.extract_images(args.input, args.out_dir, args.min_bytes)
    for path in written:
        sys.stdout.write(path + "\n")
    sys.stderr.write("extracted {} image(s)\n".format(len(written)))
    return 0


def _cmd_caption(args) -> int:
    if args.op == "get":
        sys.stdout.write(caption_cache.get(args.project, args.image))
    else:  # put
        sys.stdout.write(
            caption_cache.put(
                args.project, args.sha, args.model, args.mime, args.caption
            )
        )
    return 0


def _cmd_hash(args) -> int:
    sys.stdout.write(caption_cache.sha256_file(args.file))
    return 0


def _cmd_hash_text(_args) -> int:
    sys.stdout.write(convert.sha256_body(sys.stdin.read()))
    return 0


def _cmd_slug(args) -> int:
    sys.stdout.write(convert.slugify(args.name))
    return 0


def _cmd_doctor(_args) -> int:
    mods = [
        ("pymupdf", "fitz"),
        ("python-pptx", "pptx"),
        ("python-docx", "docx"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("tabulate", "tabulate"),
        ("markdownify", "markdownify"),
    ]
    ok = True
    for dist, mod in mods:
        try:
            __import__(mod)
            sys.stdout.write("ok    {}\n".format(dist))
        except ImportError as exc:
            ok = False
            sys.stdout.write("MISS  {}  ({})\n".format(dist, exc))
    sys.stdout.write(
        "\nllm-wiki {} | supported: {}\n".format(
            __version__, ", ".join(convert.SUPPORTED)
        )
    )
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-wiki", description="llm-wiki skill CLI")
    p.add_argument("--version", action="version", version="llm-wiki " + __version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("convert", help="doc -> Markdown")
    c.add_argument("input")
    c.add_argument("--out", help="write to FILE instead of stdout")
    c.set_defaults(func=_cmd_convert)

    e = sub.add_parser("extract-images", help="embedded images -> dir")
    e.add_argument("input")
    e.add_argument("--out-dir", required=True)
    e.add_argument("--min-bytes", type=int, default=images.DEFAULT_MIN_BYTES)
    e.set_defaults(func=_cmd_extract_images)

    cap = sub.add_parser("caption", help="caption cache get/put")
    capsub = cap.add_subparsers(dest="op", required=True)
    g = capsub.add_parser("get")
    g.add_argument("project")
    g.add_argument("image")
    g.set_defaults(func=_cmd_caption)
    pu = capsub.add_parser("put")
    pu.add_argument("project")
    pu.add_argument("sha")
    pu.add_argument("model")
    pu.add_argument("mime")
    pu.add_argument("caption")
    pu.set_defaults(func=_cmd_caption)

    h = sub.add_parser("hash", help="sha256 of a file")
    h.add_argument("file")
    h.set_defaults(func=_cmd_hash)

    ht = sub.add_parser("hash-text", help="sha256 of stdin (body hash)")
    ht.set_defaults(func=_cmd_hash_text)

    s = sub.add_parser("slug", help="slugify a name")
    s.add_argument("name")
    s.set_defaults(func=_cmd_slug)

    d = sub.add_parser("doctor", help="verify dependencies")
    d.set_defaults(func=_cmd_doctor)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
