#!/usr/bin/env python3
"""Render a structured METSI course document to a self-contained HTML package."""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path


def e(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def source_attr(block: dict) -> str:
    source_id = block.get("source_id")
    return f' data-source-id="{e(source_id)}"' if source_id else ""


def table_text(value: object) -> str:
    """Escape table text and expose safe semantic wrap points."""
    return e(value).replace("/", "/<wbr>")


def render_line_icon(name: str) -> str:
    icons = {
        "people": '<circle cx="25" cy="22" r="9"/><circle cx="55" cy="22" r="9"/><circle cx="40" cy="31" r="11"/><path d="M10 61V49c0-9 7-15 15-15h3M70 61V49c0-9-7-15-15-15h-3M23 68V54c0-10 7-17 17-17s17 7 17 17v14"/>',
        "structure": '<rect x="33" y="8" width="14" height="14" rx="3"/><rect x="8" y="58" width="16" height="14" rx="3"/><rect x="32" y="58" width="16" height="14" rx="3"/><rect x="56" y="58" width="16" height="14" rx="3"/><path d="M40 22v17M16 58V45h48v13M40 39v19"/>',
        "technology": '<rect x="10" y="15" width="42" height="52" rx="7"/><path d="M62 27c7 5 7 21 0 26M69 19c12 10 12 33 0 43"/>',
        "tasks": '<path d="M58 18a27 27 0 1 0 6 31M58 18v15H43"/><rect x="29" y="30" width="23" height="23" rx="5"/><path d="m35 42 5 5 8-11"/>',
        "database": '<ellipse cx="40" cy="18" rx="24" ry="9"/><path d="M16 18v40c0 6 11 10 24 10s24-4 24-10V18M16 38c0 6 11 10 24 10s24-4 24-10"/>',
        "voice": '<path d="M13 15h54v38H38L24 67V53H13z"/><path d="M24 28h32M24 39h21"/>',
        "repair": '<path d="M49 14a16 16 0 0 0-19 20L11 53a8 8 0 0 0 11 11l19-19a16 16 0 0 0 20-19l-10 10-9-9z"/>',
        "rules": '<path d="M40 8 65 18v19c0 16-10 27-25 35C25 64 15 53 15 37V18z"/><path d="m28 39 8 8 17-19"/>',
        "decision": '<path d="m40 8 30 32-30 32L10 40z"/><path d="m28 40 8 8 17-19"/>',
        "evidence": '<path d="M17 8h34l12 12v52H17zM51 8v13h12M27 35h24M27 47h18"/><circle cx="55" cy="55" r="11"/><path d="m63 63 9 9"/>',
        "impact": '<circle cx="40" cy="40" r="28"/><circle cx="40" cy="40" r="15"/><path d="M40 5v16M40 59v16M5 40h16M59 40h16"/>',
    }
    paths = icons.get(name, '<circle cx="40" cy="40" r="28"/><path d="M25 40h30M40 25v30"/>')
    return (f'<svg class="icon-text__svg" viewBox="0 0 80 80" aria-hidden="true" '
            f'fill="none" stroke="currentColor" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>')


def render_icon_text(block: dict) -> str:
    title = f'<h3 class="icon-text__title">{e(block.get("title"))}</h3>' if block.get("title") else ""
    subtitle = f'<p class="icon-text__subtitle">{e(block.get("subtitle"))}</p>' if block.get("subtitle") else ""
    items = []
    for item in block.get("items", []):
        heading = f'<h4>{e(item.get("title"))}</h4>' if item.get("title") else ""
        body = f'<p>{e(item.get("body"))}</p>' if item.get("body") else ""
        items.append(f'<section class="icon-text__item"{source_attr(item)}>{render_line_icon(item.get("icon", "default"))}<div>{heading}{body}</div></section>')
    return f'<section class="icon-text" aria-label="{e(block.get("alt", block.get("title", "Resumen iconográfico")))}">{title}{subtitle}<div class="icon-text__grid">' + "".join(items) + "</div></section>"


def render_grid(block: dict) -> str:
    columns = max(2, min(int(block.get("columns", 3)), 5))
    style = block.get("style", "filled")
    if style not in {"filled", "outline", "plain"}:
        style = "filled"
    items = []
    for item in block.get("items", []):
        number = f'<span class="tile__number">{e(item.get("number"))}</span>' if item.get("number") else ""
        title = f'<h3 class="tile__title">{e(item.get("title"))}</h3>' if item.get("title") else ""
        body = f'<p class="tile__body">{e(item.get("body"))}</p>' if item.get("body") else ""
        items.append(f'<div class="tile tile--{style}"{source_attr(item)}>{number}{title}{body}</div>')
    return f'<div class="grid grid--{columns}">' + "".join(items) + "</div>"


def render_diagram(block: dict) -> str:
    family = block.get("family", "bands")
    if family not in {"bands", "cycle", "sequence", "transfer", "layers", "comparison", "hub", "checklist", "panels"}:
        family = "bands"
    title = f'<h3 class="diagram__title">{e(block.get("title"))}</h3>' if block.get("title") else ""
    subtitle = f'<p class="diagram__subtitle">{e(block.get("subtitle"))}</p>' if block.get("subtitle") else ""
    items = block.get("items", [])

    if family in {"transfer", "comparison"}:
        rows = []
        for item in items:
            rows.append(
                '<div class="diagram__pair">'
                f'<div class="diagram__side"><strong>{e(item.get("left_title"))}</strong><span>{e(item.get("left"))}</span></div>'
                '<span class="diagram__arrow" aria-hidden="true">→</span>'
                f'<div class="diagram__side"><strong>{e(item.get("right_title"))}</strong><span>{e(item.get("right"))}</span></div>'
                '</div>'
            )
        body = '<div class="diagram__pairs">' + "".join(rows) + '</div>'
    elif family == "hub":
        center = f'<div class="diagram__center">{e(block.get("center", "Sistema"))}</div>'
        nodes = []
        for item in items:
            nodes.append(f'<div class="diagram__item"><strong>{e(item.get("title"))}</strong><span>{e(item.get("body"))}</span></div>')
        body = center + '<div class="diagram__hub-grid">' + "".join(nodes) + '</div>'
    elif family in {"cycle", "sequence"}:
        nodes = []
        for index, item in enumerate(items):
            if index and family == "cycle":
                nodes.append('<span class="diagram__arrow" aria-hidden="true">→</span>')
            number = f'<span class="diagram__number">{e(item.get("number"))}</span>' if item.get("number") else ""
            nodes.append(f'<div class="diagram__item">{number}<strong>{e(item.get("title"))}</strong><span>{e(item.get("body"))}</span></div>')
        if family == "cycle":
            nodes.append('<span class="diagram__return" aria-hidden="true">↺</span>')
        body = '<div class="diagram__route">' + "".join(nodes) + '</div>'
    else:
        nodes = []
        for index, item in enumerate(items):
            number = f'<span class="diagram__number">{e(item.get("number"))}</span>' if item.get("number") else ""
            nodes.append(
                f'<div class="diagram__item" style="--item-index:{index}">'
                f'{number}<strong>{e(item.get("title"))}</strong><span>{e(item.get("body"))}</span></div>'
            )
        body = '<div class="diagram__items">' + "".join(nodes) + '</div>'
    return f'<section class="diagram diagram--{family}" data-diagram-family="{family}" aria-label="{e(block.get("alt", block.get("title", "Infografía")))}">{title}{subtitle}{body}</section>'


def render_block(block: dict) -> str:
    kind = block.get("kind", "paragraph")
    attr = source_attr(block)
    if kind == "paragraph":
        return f'<p{attr}>{e(block.get("text"))}</p>'
    if kind == "dropcap-paragraph":
        return f'<p class="dropcap"{attr}>{e(block.get("text"))}</p>'
    if kind == "kicker":
        return f'<p class="mag-kicker"{attr}>{e(block.get("text"))}</p>'
    if kind == "deck":
        return f'<p class="mag-deck"{attr}>{e(block.get("text"))}</p>'
    if kind == "pullquote":
        return f'<blockquote class="mag-pullquote"{attr}>{e(block.get("text"))}</blockquote>'
    if kind == "rule":
        orientation = "vertical" if block.get("orientation") == "vertical" else "horizontal"
        return f'<div class="mag-rule mag-rule--{orientation}" aria-hidden="true"></div>'
    if kind == "subheading":
        return f'<h3{attr}>{e(block.get("text"))}</h3>'
    if kind in {"bullets", "numbered"}:
        tag = "ol" if kind == "numbered" else "ul"
        items = []
        for item in block.get("items", []):
            if isinstance(item, dict):
                items.append(f'<li{source_attr(item)}>{e(item.get("text"))}</li>')
            else:
                items.append(f'<li>{e(item)}</li>')
        return f'<{tag}{attr}>' + "".join(items) + f'</{tag}>'
    if kind in {"image", "infographic"}:
        caption = f'<figcaption>{e(block.get("caption"))}</figcaption>' if block.get("caption") else ""
        role = e(block.get("role", "ordinary"))
        span = max(1, min(int(block.get("span", 6)), 6))
        media_class = "media media--infographic" if kind == "infographic" else f"media media--{role} media--span-{span}"
        treatment = e(block.get("treatment", "none"))
        focal = e(block.get("focal", "50% 50%"))
        image = (f'<img src="{e(block.get("src"))}" alt="{e(block.get("alt"))}" loading="lazy" '
                 f'data-treatment="{treatment}" style="--focal:{focal}">')
        if block.get("mobile_src"):
            image = (f'<picture><source media="(max-width: 900px)" srcset="{e(block.get("mobile_src"))}">'
                     f'{image}</picture>')
        return f'<figure class="{media_class}"{attr}>{image}{caption}</figure>'
    if kind == "mosaic":
        items = []
        for item in block.get("items", []):
            dominant = " mosaic__item--dominant" if item.get("dominant") else ""
            items.append(
                f'<figure class="mosaic__item{dominant}"><img src="{e(item.get("src"))}" '
                f'alt="{e(item.get("alt"))}" style="--focal:{e(item.get("focal", "50% 50%"))}"></figure>'
            )
        caption = f'<p class="mosaic__caption">{e(block.get("caption"))}</p>' if block.get("caption") else ""
        return f'<section class="mosaic"{attr}>' + "".join(items) + caption + "</section>"
    if kind == "note":
        title = f'<h3>{e(block.get("title"))}</h3>' if block.get("title") else ""
        body = "".join(render_block(item) for item in block.get("blocks", []))
        return f'<aside class="mag-note"{attr}>{title}{body}</aside>'
    if kind == "grid":
        return render_grid(block)
    if kind == "diagram":
        return render_diagram(block)
    if kind == "icon-text":
        return render_icon_text(block)
    if kind == "quote":
        return f'<blockquote{attr}>{e(block.get("text"))}</blockquote>'
    if kind == "code":
        language = e(block.get("language", ""))
        label = f'<span class="code-block__language">{language}</span>' if language else ""
        return f'<div class="code-block">{label}<pre><code{attr}>{e(block.get("text"))}</code></pre></div>'
    if kind == "table":
        headers = "".join(f'<th{source_attr(item)}>{table_text(item.get("text"))}</th>' for item in block.get("headers", []))
        rows = []
        for row in block.get("rows", []):
            rows.append("<tr>" + "".join(f'<td{source_attr(item)}>{table_text(item.get("text"))}</td>' for item in row) + "</tr>")
        return f'<div class="data-table"{attr}><table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    if kind == "columns":
        columns = max(2, min(int(block.get("columns", 2)), 3))
        groups = []
        for group in block.get("items", []):
            groups.append('<div class="column">' + "".join(render_block(x) for x in group.get("blocks", [])) + '</div>')
        return f'<div class="columns columns--{columns}"{attr}>' + "".join(groups) + '</div>'
    if kind == "links":
        return '<ul class="links">' + "".join(f'<li><a href="{e(x.get("url"))}">{e(x.get("label", x.get("url")))}</a></li>' for x in block.get("items", [])) + "</ul>"
    raise ValueError(f"Unsupported block kind: {kind}")


def render_card(card: dict) -> str:
    if card.get("type") == "cover":
        lead = f'<p class="cover-lead">{e(card.get("lead"))}</p>' if card.get("lead") else ""
        cover_source = f' data-source-id="{e(card.get("title_source_id"))}"' if card.get("title_source_id") else ""
        image = ""
        if card.get("image"):
            image = f'<img class="cover-image" src="{e(card.get("image"))}" alt="{e(card.get("image_alt", ""))}" style="--focal:{e(card.get("focal", "50% 50%"))}">'
        layout = e(card.get("layout", "cover-editorial"))
        return (f'<section class="card card--cover layout--{layout}">{image}<div class="card__inner">'
                f'<p class="eyebrow">{e(card.get("eyebrow"))}</p>'
                f'<p class="discipline">{e(card.get("discipline"))}</p>'
                f'<p><span class="cover-title"{cover_source}>{e(card.get("title"))}</span></p>{lead}'
                '</div></section>')
    title_attr = f' data-source-id="{e(card.get("title_source_id"))}"' if card.get("title_source_id") else ""
    title = f'<h2{title_attr}>{e(card.get("title"))}</h2>' if card.get("title") else ""
    kicker = f'<p class="mag-kicker">{e(card.get("kicker"))}</p>' if card.get("kicker") else ""
    blocks = "".join(render_block(block) for block in card.get("blocks", []))
    variant = card.get("variant", "white")
    if variant not in {"white", "stone-light", "stone-dark"}:
        variant = "white"
    density = card.get("density", "normal")
    if density not in {"compact", "normal", "airy"}:
        density = "normal"
    role = card.get("role", "content")
    layout = e(card.get("layout", "article-2col"))
    page_side = e(card.get("page_side", "auto"))
    spread_id = e(card.get("spread_id", ""))
    accent = e(card.get("accent", "none"))
    return (f'<section class="card card--{variant} card--{density} layout--{layout}" '
            f'data-card-role="{e(role)}" data-page-side="{page_side}" data-spread-id="{spread_id}" data-accent="{accent}">'
            f'<div class="card__inner">{kicker}{title}{blocks}</div></section>')


def render_document(spec: dict) -> str:
    meta = spec.get("meta", {})
    lang = e(meta.get("lang", "es"))
    title = e(meta.get("title", "METSI"))
    description = e(meta.get("description", ""))
    mode = e(meta.get("mode", "web-cards"))
    cards = "".join(render_card(card) for card in spec.get("cards", []))
    return f'''<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <title>{title}</title>
  <link rel="stylesheet" href="metsi.css">
</head>
<body class="mode-{mode}"><main class="document">{cards}</main></body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.input.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "index.html").write_text(render_document(spec), encoding="utf-8")
    css = Path(__file__).resolve().parent.parent / "assets" / "metsi.css"
    shutil.copy2(css, args.output_dir / "metsi.css")
    shutil.copy2(args.input, args.output_dir / "document.json")


if __name__ == "__main__":
    main()
