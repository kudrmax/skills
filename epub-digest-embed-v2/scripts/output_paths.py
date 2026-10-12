#!/usr/bin/env python3
"""
output_paths.py — Choose the work dir and output file names for one run.

Names come from the book's own metadata (dc:title, dc:language), not from the
file name, which is often junk ("_OceanofPDF.com_Flourish_-_Martin_Seligman").
An earlier run is never overwritten: if any of the paths for a version already
exists, the next free version is used ("v2", "v3", ...).

Usage:
    output_paths.py --epub BOOK [--lang en|ru] [--version N]

Prints JSON: {"title", "lang", "version", "work", "epub", "md"}.
"""
import argparse
import json
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

SUFFIXES = {
    "ru": {"epub": "с конспектом", "md": "конспект"},
    "en": {"epub": "with digest", "md": "digest"},
}
FORBIDDEN = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
MAX_TITLE = 80


class BookMetadata:
    def __init__(self, epub_path):
        self.path = epub_path
        self.title, self.language = self._read()

    def _read(self):
        try:
            with zipfile.ZipFile(self.path) as zf:
                container = ET.fromstring(zf.read("META-INF/container.xml"))
                rootfile = next(el for el in container.iter() if el.tag.endswith("rootfile"))
                opf = ET.fromstring(zf.read(rootfile.get("full-path")))
        except (KeyError, StopIteration, zipfile.BadZipFile, ET.ParseError):
            return None, None
        return self._dc(opf, "title"), self._dc(opf, "language")

    @staticmethod
    def _dc(opf, name):
        for el in opf.iter():
            if el.tag.endswith("}" + name) and (el.text or "").strip():
                return el.text.strip()
        return None


def short_title(metadata):
    raw = metadata.title or os.path.splitext(os.path.basename(metadata.path))[0].replace("_", " ")
    raw = raw.split(":")[0]
    clean = re.sub(r"\s+", " ", FORBIDDEN.sub(" ", raw)).strip(" .")
    return clean[:MAX_TITLE].rstrip() or "book"


def pick_lang(requested, metadata):
    lang = (requested or metadata.language or "").lower()[:2]
    return lang if lang in SUFFIXES else "en"


def paths_for(book_dir, title, lang, version):
    tag = "" if version == 1 else f" v{version}"
    words = SUFFIXES[lang]
    return {
        "work": os.path.join(book_dir, f"{title}.digest" + ("" if version == 1 else f"-v{version}")),
        "epub": os.path.join(book_dir, f"{title} ({words['epub']}{tag}).epub"),
        "md": os.path.join(book_dir, f"{title} — {words['md']}{tag}.md"),
    }


def first_free_version(book_dir, title, lang):
    version = 1
    while any(os.path.exists(p) for p in paths_for(book_dir, title, lang, version).values()):
        version += 1
    return version


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epub", required=True)
    ap.add_argument("--lang", help="digest language; defaults to the book's dc:language")
    ap.add_argument("--version", type=int, help="reuse this run's version instead of picking a free one")
    args = ap.parse_args()

    book = os.path.abspath(args.epub)
    book_dir = os.path.dirname(book)
    if not os.access(book_dir, os.W_OK):
        book_dir = os.environ.get("TMPDIR", "/tmp")

    metadata = BookMetadata(book)
    title = short_title(metadata)
    lang = pick_lang(args.lang, metadata)
    version = args.version or first_free_version(book_dir, title, lang)

    result = {"title": title, "lang": lang, "version": version}
    result.update(paths_for(book_dir, title, lang, version))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=1)
    print()


if __name__ == "__main__":
    main()
