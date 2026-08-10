# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "bibtexparser>=1.4.0",
#   "PyYAML>=6.0",
# ]
# ///

"""Convert BibTeX entries into Hugo publication Markdown files.

Usage:
  uv run tools/bibtex_to_hugo.py refs.bib
    uv run tools/bibtex_to_hugo.py refs-a.bib refs-b.bib --merge
  uv run tools/bibtex_to_hugo.py refs.bib --output content/publications --overwrite
"""

from __future__ import annotations

import argparse
import pathlib
import re
from typing import Any

import bibtexparser
from bibtexparser.bparser import BibTexParser
import yaml


class QuotedStringDumper(yaml.SafeDumper):
    pass


def _quoted_str_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


QuotedStringDumper.add_representer(str, _quoted_str_representer)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "publication"


def clean(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"\s+", " ", value)
    value = value.replace("{", "").replace("}", "")
    return value.strip()


def normalize_doi(value: str | None) -> str:
    doi = clean(value).lower()
    if not doi:
        return ""
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.strip()


def normalize_bibtex(raw_text: str) -> str:
    # Some exporters emit bare month tokens (e.g., month=sept) that are not
    # guaranteed to be defined in BibTeX string tables.
    pattern = re.compile(r"(\bmonth\s*=\s*)([A-Za-z]+)(\s*[,}])", re.IGNORECASE)
    return pattern.sub(lambda m: f"{m.group(1)}{{{m.group(2)}}}{m.group(3)}", raw_text)


def format_patent_venue(entry: dict[str, Any]) -> str:
    entry_type = clean(entry.get("ENTRYTYPE")).lower()
    number = clean(entry.get("number"))
    if not number:
        return ""

    # Many patent records are exported as @misc with a patent number field.
    if entry_type in {"patent", "misc"}:
        return f"U.S. Patent {number}"
    return ""


def get_venue(entry: dict[str, Any]) -> str:
    patent_venue = format_patent_venue(entry)
    if patent_venue:
        return patent_venue

    for key in ("journal", "booktitle", "publisher", "school"):
        if clean(entry.get(key)):
            return clean(entry.get(key))
    return ""


def get_filename(entry: dict[str, Any], year: str, title: str) -> str:
    base = clean(entry.get("ID"))
    if base:
        return slugify(base) + ".md"
    parts = [p for p in [year, title] if p]
    return slugify("-".join(parts)) + ".md"


def dedup_key_for_entry(entry: dict[str, Any]) -> str:
    doi = normalize_doi(entry.get("doi"))
    if doi:
        return f"doi:{doi}"

    title = clean(entry.get("title"))
    year = clean(entry.get("year"))
    if title and year:
        return f"title-year:{slugify(title)}:{year}"
    if title:
        return f"title:{slugify(title)}"

    bib_id = clean(entry.get("ID"))
    if bib_id:
        return f"id:{slugify(bib_id)}"

    return ""


def entry_score(entry: dict[str, Any]) -> int:
    # Prefer richer records when duplicate keys are encountered.
    keys = ("title", "author", "year", "journal", "booktitle", "doi", "url")
    score = 0
    for key in keys:
        if clean(entry.get(key)):
            score += 1
    return score


def build_fields(entry: dict[str, Any]) -> dict[str, Any]:
    title = clean(entry.get("title")) or "Untitled Publication"
    authors = clean(entry.get("author"))
    year = clean(entry.get("year"))
    venue = get_venue(entry)
    doi = clean(entry.get("doi"))
    url = clean(entry.get("url"))

    fields: dict[str, Any] = {
        "title": title,
        "authors": authors,
        "year": int(year) if year.isdigit() else 0,
        "venue": venue,
        "summary": "",
        "build": {
            "render": "never",
            "list": "local",
        },
    }

    if doi:
        fields["doi"] = doi
    if url:
        fields["external_url"] = url

    return fields


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
    match = pattern.match(text)
    if not match:
        return {}, text

    front_raw, body = match.group(1), match.group(2)
    data = yaml.safe_load(front_raw) or {}
    if not isinstance(data, dict):
        data = {}
    return data, body


def find_existing_by_doi(out_dir: pathlib.Path) -> dict[str, pathlib.Path]:
    doi_map: dict[str, pathlib.Path] = {}
    for md_file in out_dir.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        front, _ = split_front_matter(text)
        doi_raw = front.get("doi") if isinstance(front, dict) else ""
        doi = normalize_doi(str(doi_raw) if doi_raw is not None else "")
        if doi and doi not in doi_map:
            doi_map[doi] = md_file
    return doi_map


def ordered_front_matter(data: dict[str, Any]) -> dict[str, Any]:
    preferred = [
        "title",
        "authors",
        "year",
        "venue",
        "summary",
        "doi",
        "pdf",
        "code",
        "external_url",
        "build",
    ]
    ordered: dict[str, Any] = {}
    for key in preferred:
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def render_document(front_matter: dict[str, Any], body: str) -> str:
    front = ordered_front_matter(front_matter)
    front_text = yaml.dump(
        front,
        Dumper=QuotedStringDumper,
        sort_keys=False,
        allow_unicode=False,
        default_flow_style=False,
    ).strip()
    body_text = body.strip() if body.strip() else "Add abstract, notes, and links here."
    return f"---\n{front_text}\n---\n\n{body_text}\n"


def merge_front_matter(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)

    # Migrate legacy key that conflicts with Hugo front matter semantics.
    if "url" in merged and "external_url" not in merged:
        legacy = merged.get("url")
        if isinstance(legacy, str) and legacy:
            merged["external_url"] = legacy
    if "url" in merged:
        del merged["url"]

    # Always keep these synchronized with BibTeX when available.
    for key in ("title", "authors", "venue"):
        value = incoming.get(key, "")
        if isinstance(value, str) and value:
            merged[key] = value

    year = incoming.get("year", 0)
    if isinstance(year, int) and year > 0:
        merged["year"] = year

    for key in ("doi", "external_url"):
        value = incoming.get(key, "")
        if isinstance(value, str) and value:
            merged[key] = value

    if "summary" not in merged:
        merged["summary"] = ""

    # Force publication pages to be list-only (no individual render output).
    merged["build"] = {
        "render": "never",
        "list": "local",
    }

    return merged


def render_markdown(entry: dict[str, Any]) -> str:
    return render_document(build_fields(entry), "Add abstract, notes, and links here.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert BibTeX to Hugo publication entries")
    parser.add_argument("bibfiles", type=pathlib.Path, nargs="+", help="Input .bib file(s)")
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("content/publications"),
        help="Output directory for Markdown files",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing Markdown files entirely",
    )
    mode_group.add_argument(
        "--merge",
        action="store_true",
        help="Merge BibTeX fields into existing front matter while preserving body text",
    )
    args = parser.parse_args()

    bib_paths = args.bibfiles
    out_dir = args.output

    missing = [path for path in bib_paths if not path.exists()]
    if missing:
        missing_list = ", ".join(str(path) for path in missing)
        raise SystemExit(f"BibTeX file(s) not found: {missing_list}")

    out_dir.mkdir(parents=True, exist_ok=True)

    unique_by_key: dict[str, dict[str, Any]] = {}
    duplicates_in_input = 0
    anonymous_counter = 0

    for bib_path in bib_paths:
        raw_bib = bib_path.read_text(encoding="utf-8")
        normalized_bib = normalize_bibtex(raw_bib)
        bib_parser = BibTexParser(common_strings=True)
        db = bibtexparser.loads(normalized_bib, parser=bib_parser)

        for entry in db.entries:
            key = dedup_key_for_entry(entry)
            if not key:
                key = f"anonymous:{anonymous_counter}"
                anonymous_counter += 1

            existing = unique_by_key.get(key)
            if existing is None:
                unique_by_key[key] = entry
                continue

            duplicates_in_input += 1
            if entry_score(entry) > entry_score(existing):
                unique_by_key[key] = entry

    existing_by_doi = find_existing_by_doi(out_dir)

    created = 0
    overwritten = 0
    merged = 0
    skipped = 0
    deduped_to_existing = 0

    for entry in unique_by_key.values():
        title = clean(entry.get("title"))
        year = clean(entry.get("year"))
        filename = get_filename(entry, year, title)
        out_path = out_dir / filename

        doi = normalize_doi(entry.get("doi"))
        if doi and doi in existing_by_doi:
            mapped_path = existing_by_doi[doi]
            if mapped_path != out_path:
                out_path = mapped_path
                deduped_to_existing += 1
        elif doi:
            existing_by_doi[doi] = out_path

        if out_path.exists():
            if args.merge:
                existing_text = out_path.read_text(encoding="utf-8")
                existing_front, existing_body = split_front_matter(existing_text)
                merged_front = merge_front_matter(existing_front, build_fields(entry))
                out_path.write_text(render_document(merged_front, existing_body), encoding="utf-8")
                merged += 1
            elif args.overwrite:
                out_path.write_text(render_markdown(entry), encoding="utf-8")
                overwritten += 1
            else:
                skipped += 1
            continue

        out_path.write_text(render_markdown(entry), encoding="utf-8")
        created += 1

    print(f"Input duplicates collapsed: {duplicates_in_input}")
    print(f"DOI collisions mapped to existing files: {deduped_to_existing}")
    print(f"Created: {created}")
    print(f"Overwritten: {overwritten}")
    print(f"Merged: {merged}")
    print(f"Skipped: {skipped}")
    print(f"Output: {out_dir}")


if __name__ == "__main__":
    main()
