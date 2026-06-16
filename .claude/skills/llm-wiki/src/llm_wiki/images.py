"""Embedded-image extraction, pure Python (no poppler / unzip needed).

PDFs go through PyMuPDF; Office files (PPTX/DOCX/XLSX) are zip containers,
so their media is read with the stdlib `zipfile`. Standalone images are
copied. Noise (icons, bullets, decorations) is filtered by a byte-size
floor -- the same cheap heuristic the skill documents, no image library.
"""
import os
import shutil
import zipfile

DEFAULT_MIN_BYTES = 3072  # ~3 KB -- below this is almost always an icon/logo

_OFFICE_MEDIA_PREFIX = {
    ".pptx": "ppt/media/",
    ".docx": "word/media/",
    ".xlsx": "xl/media/",
}

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}


def _keep(size: int, min_bytes: int) -> bool:
    return size >= min_bytes


def _extract_pdf(path: str, out_dir: str, min_bytes: int) -> list:
    import fitz

    written = []
    with fitz.open(path) as doc:
        seen = set()
        for pno in range(doc.page_count):
            for img in doc.get_page_images(pno, full=True):
                xref = img[0]
                if xref in seen:
                    continue
                seen.add(xref)
                info = doc.extract_image(xref)
                data = info["image"]
                if not _keep(len(data), min_bytes):
                    continue
                ext = info.get("ext", "png")
                name = "img-p{}-{}.{}".format(pno + 1, xref, ext)
                dest = os.path.join(out_dir, name)
                with open(dest, "wb") as fh:
                    fh.write(data)
                written.append(dest)
    return written


def _extract_office(path: str, out_dir: str, prefix: str, min_bytes: int) -> list:
    written = []
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if not info.filename.startswith(prefix):
                continue
            if os.path.splitext(info.filename)[1].lower() not in _IMAGE_EXTS:
                continue
            if not _keep(info.file_size, min_bytes):
                continue
            dest = os.path.join(out_dir, os.path.basename(info.filename))
            with zf.open(info) as src, open(dest, "wb") as fh:
                shutil.copyfileobj(src, fh)
            written.append(dest)
    return written


def extract_images(path: str, out_dir: str, min_bytes: int = DEFAULT_MIN_BYTES) -> list:
    """Extract embedded images to out_dir. Returns the list of files written."""
    os.makedirs(out_dir, exist_ok=True)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return _extract_pdf(path, out_dir, min_bytes)
    if ext in _OFFICE_MEDIA_PREFIX:
        return _extract_office(path, out_dir, _OFFICE_MEDIA_PREFIX[ext], min_bytes)
    if ext in _IMAGE_EXTS:
        dest = os.path.join(out_dir, os.path.basename(path))
        shutil.copyfile(path, dest)
        return [dest]
    return []
