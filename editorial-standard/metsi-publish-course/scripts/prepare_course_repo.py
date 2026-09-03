#!/usr/bin/env python3
"""Prepare or update a reproducible METSI course repository."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_slug(value: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise ValueError("slug must contain only lowercase letters, numbers, and single hyphens")
    return value


def require_package(package: Path) -> None:
    required = ["index.html", "metsi.css", "document.json"]
    missing = [name for name in required if not (package / name).is_file()]
    if missing:
        raise ValueError("package is missing: " + ", ".join(missing))
    if any(path.is_symlink() for path in package.rglob("*")):
        raise ValueError("package must not contain symbolic links")


def archive_existing(target: Path, archive_root: Path, stamp: str) -> None:
    if not target.exists():
        return
    archive_root.mkdir(parents=True, exist_ok=True)
    destination = archive_root / f"{target.name}-{stamp}"
    counter = 1
    while destination.exists():
        destination = archive_root / f"{target.name}-{stamp}-{counter}"
        counter += 1
    shutil.move(str(target), str(destination))


def copy_package(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, symlinks=False)


def render_index(classes: list[dict]) -> str:
    cards = []
    for item in classes:
        cards.append(
            '<a class="class-card" href="' + html.escape(item["path"], quote=True) + '">'
            '<span class="class-card__label">METSI</span>'
            '<strong>' + html.escape(item["title"]) + '</strong>'
            '<span>Ver clase</span></a>'
        )
    return """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UBA METSI</title><meta name="description" content="Curso público de Metodología de Sistemas de Información">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="metsi.css"></head>
<body><main><header><p class="eyebrow">UBA</p><h1>Metodología de Sistemas de Información</h1>
<p>Curso completo · materiales, clases e infografías</p></header>
<section aria-label="Clases">""" + "".join(cards) + """</section></main></body></html>
"""


INDEX_CSS = """*{box-sizing:border-box}html{font-family:Inter,Arial,sans-serif;color:#272525;background:#fff}body{margin:0}main{width:min(981px,calc(100vw - 40px));margin:32px auto}header{padding:64px 63px;background:#000;color:#fff;border-radius:10.8px}.eyebrow{font-size:62.1px;line-height:1.1;font-weight:700;margin:0}h1{font-size:36px;line-height:1.25;margin:12px 0 20px}header p:last-child{margin:0;font-size:18px}section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;padding:48px 63px}.class-card{display:flex;min-height:190px;flex-direction:column;justify-content:space-between;padding:24px;color:inherit;text-decoration:none;background:#e6e6e6;border:1px solid #ccc;border-radius:6.3px}.class-card__label{font-size:14px;font-weight:700}.class-card strong{font-size:22.5px;line-height:1.25}.class-card span:last-child{text-decoration:underline;text-underline-offset:3px}@media(max-width:720px){main{width:calc(100vw - 20px);margin:10px auto}header{padding:40px 22px}.eyebrow{font-size:48px}h1{font-size:30px}section{grid-template-columns:1fr;padding:30px 0}}"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("repo_dir", type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--repo-name", default="UBA-metsi")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    package = args.package.resolve()
    repo = args.repo_dir.resolve()
    slug = safe_slug(args.slug)
    require_package(package)
    repo.mkdir(parents=True, exist_ok=True)

    source_target = repo / "course" / "classes" / slug
    site_target = repo / "site" / "classes" / slug
    if (source_target.exists() or site_target.exists()) and not args.replace:
        raise ValueError(f"class {slug} exists; pass --replace for an intentional update")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.replace:
        archive_existing(source_target, repo / "archive" / "classes", stamp)
        archive_existing(site_target, repo / "archive" / "site", stamp)
    source_target.parent.mkdir(parents=True, exist_ok=True)
    site_target.parent.mkdir(parents=True, exist_ok=True)
    copy_package(package, source_target)
    copy_package(package, site_target)

    manifest_path = repo / "course-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"course": "UBA METSI", "repository": args.repo_name, "classes": []}
    entry = {"slug": slug, "title": args.title, "path": f"classes/{slug}/", "updated_at": utc_now()}
    classes = [item for item in manifest.get("classes", []) if item.get("slug") != slug]
    classes.append(entry)
    classes.sort(key=lambda item: item["slug"])
    manifest["classes"] = classes
    rendered_manifest = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    manifest_path.write_text(rendered_manifest, encoding="utf-8")

    site = repo / "site"
    site.mkdir(parents=True, exist_ok=True)
    (site / "course-manifest.json").write_text(rendered_manifest, encoding="utf-8")
    (site / "index.html").write_text(render_index(classes), encoding="utf-8")
    (site / "metsi.css").write_text(INDEX_CSS + "\n", encoding="utf-8")

    skill_root = Path(__file__).resolve().parent.parent
    workflow_dir = repo / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill_root / "assets" / "deploy-pages.yml", workflow_dir / "deploy-pages.yml")
    shutil.copy2(skill_root / "assets" / "course.gitignore", repo / ".gitignore")
    config = {
        "repository": args.repo_name,
        "visibility": "public",
        "branch": "main",
        "hosting": "github-pages-actions",
        "domain": "standard",
        "owner_resolution": "gh api user --jq .login",
    }
    (repo / "publish-config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repo_dir": str(repo), "class": entry, "classes": len(classes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
