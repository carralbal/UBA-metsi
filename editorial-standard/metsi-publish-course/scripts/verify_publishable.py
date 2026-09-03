#!/usr/bin/env python3
"""Fail closed when a prepared public course repository is unsafe or incomplete."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

MAX_FILE = 100 * 1024 * 1024
MAX_SITE = 1024 * 1024 * 1024
FORBIDDEN_NAMES = {
    ".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519",
}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SECRET_PATTERNS = [
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
]


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value and key in {"href", "src"}:
                self.values.append(value)


def local_target(html_file: Path, value: str, site: Path) -> Path | None:
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith(('#', 'mailto:', 'tel:', 'data:')):
        return None
    path = unquote(parsed.path)
    target = (site / path.lstrip("/")) if path.startswith("/") else (html_file.parent / path)
    if path.endswith("/"):
        target /= "index.html"
    resolved = target.resolve()
    if not resolved.is_relative_to(site.resolve()):
        raise ValueError(f"link escapes site root: {value}")
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_dir", type=Path)
    args = parser.parse_args()
    repo = args.repo_dir.resolve()
    site = repo / "site"
    errors: list[str] = []
    warnings: list[str] = []

    for required in [site / "index.html", repo / "course-manifest.json", repo / ".github" / "workflows" / "deploy-pages.yml"]:
        if not required.is_file():
            errors.append(f"missing required file: {required.relative_to(repo)}")

    site_bytes = 0
    files = [path for path in repo.rglob("*") if path.is_file() or path.is_symlink()]
    for path in files:
        rel = path.relative_to(repo)
        if path.is_symlink():
            errors.append(f"symbolic link not allowed: {rel}")
            continue
        size = path.stat().st_size
        if site in path.parents:
            site_bytes += size
        if size > MAX_FILE:
            errors.append(f"file exceeds 100 MiB: {rel}")
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"credential-like file is forbidden: {rel}")
        if size <= 2 * 1024 * 1024 and path.suffix.lower() in {".json", ".yml", ".yaml", ".txt", ".md", ".html", ".css", ".js"}:
            data = path.read_bytes()
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                errors.append(f"possible secret detected: {rel}")
    if site_bytes > MAX_SITE:
        errors.append("site artifact exceeds the supported 1 GiB target")

    if site.exists():
        for html_file in site.rglob("*.html"):
            parser_html = Links()
            parser_html.feed(html_file.read_text(encoding="utf-8", errors="replace"))
            for value in parser_html.values:
                try:
                    target = local_target(html_file, value, site)
                except ValueError as exc:
                    errors.append(f"{html_file.relative_to(repo)}: {exc}")
                    continue
                if target is not None and not target.exists():
                    errors.append(f"broken local link in {html_file.relative_to(repo)}: {value}")

    if not (repo / "LICENSE").exists():
        warnings.append("no repository license; public visibility does not grant reuse rights")
    result = {
        "ok": not errors,
        "files": len(files),
        "site_bytes": site_bytes,
        "errors": sorted(set(errors)),
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
