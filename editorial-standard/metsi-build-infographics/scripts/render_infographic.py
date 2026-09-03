#!/usr/bin/env python3
"""Render a METSI-style infographic from a small JSON specification."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import textwrap
from pathlib import Path

INK = "#272525"
SECONDARY = "#4D4D4D"
PAPER = "#FFFFFF"
TILE = "#E6E6E6"
BORDER = "#CCCCCC"
BLUE = "#DCE5E8"
SAND = "#ECE4D7"
CYAN = "#D8EEF0"
STONE = "#F4F3EF"


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def lines(text: object, width: int) -> list[str]:
    value = " ".join(str(text or "").split())
    if not value:
        return []
    # Compound technical terms often contain slashes or hyphens.  Expose those
    # punctuation marks as legal wrap points, then remove the temporary spaces
    # from each rendered line so the visible wording is unchanged.
    breakable = re.sub(r"([/-])(?=\S)", r"\1 ", value)
    wrapped = textwrap.wrap(
        breakable,
        width=max(8, width),
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [line.replace("/ ", "/").replace("- ", "-") for line in wrapped]


def text_block(x: float, y: float, content: object, size: int, weight: int, wrap: int,
               line_height: float = 1.35, color: str = INK, anchor: str = "start") -> tuple[str, float]:
    wrapped = lines(content, wrap)
    parts = [f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="Inter, Arial, sans-serif" '
             f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">']
    for index, line in enumerate(wrapped):
        dy = 0 if index == 0 else size * line_height
        parts.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{esc(line)}</tspan>')
    parts.append("</text>")
    height = size + max(0, len(wrapped) - 1) * size * line_height
    return "".join(parts), height


def card_style(style: str) -> tuple[str, str, int]:
    if style == "outline":
        return PAPER, BORDER, 2
    if style == "plain":
        return PAPER, "none", 0
    return TILE, BORDER, 1


def render_grid(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])
    columns = max(1, min(int(spec.get("columns", 3)), 5))
    gap = 24
    card_w = (content_w - gap * (columns - 1)) / columns
    wrap = max(16, int(card_w / 13))
    style = spec.get("style", "filled")
    fill, stroke, sw = card_style(style)
    pad = 26
    rows = math.ceil(len(items) / columns)
    row_heights = []
    for row in range(rows):
        heights = []
        for item in items[row * columns:(row + 1) * columns]:
            title_count = max(1, len(lines(item.get("title", ""), wrap)))
            body_count = len(lines(item.get("body", ""), wrap + 3))
            number_h = 34 if item.get("number") else 0
            heights.append(pad * 2 + number_h + title_count * 40 + body_count * 42 + (14 if body_count else 0))
        row_heights.append(max(110, max(heights, default=110)))
    out = []
    y = top
    for row in range(rows):
        for col in range(columns):
            index = row * columns + col
            if index >= len(items):
                break
            item = items[index]
            x = content_x + col * (card_w + gap)
            h = row_heights[row]
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{card_w:.1f}" height="{h:.1f}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
            ty = y + pad + 22
            if item.get("number"):
                block, bh = text_block(x + pad, ty, item["number"], 27, 700, 10, color=SECONDARY)
                out.append(block); ty += bh + 16
            block, bh = text_block(x + pad, ty, item.get("title", ""), 34, 700, wrap)
            out.append(block); ty += bh + 16
            if item.get("body"):
                block, _ = text_block(x + pad, ty, item["body"], 29, 400, wrap + 3, 1.42)
                out.append(block)
        y += row_heights[row] + gap
    return out, int(y - gap)


def render_comparison(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    converted = []
    for item in spec.get("items", []):
        converted.append({"title": spec.get("left_label", "Antes"), "body": item.get("left", "")})
        converted.append({"title": spec.get("right_label", "Después"), "body": item.get("right", "")})
    copy = dict(spec, type="grid", columns=2, items=converted)
    return render_grid(copy, content_x, top, content_w)


def render_flow(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])
    count = len(items)
    if not count:
        return [], top
    orientation = spec.get("orientation", "auto")
    nodes, connectors = [], []

    def node_height(item: dict, width: float) -> float:
        usable_width = max(160, width - 48)
        title_wrap = max(12, int(usable_width / 16))
        body_wrap = max(14, int(usable_width / 14.5))
        number_h = 57 if item.get("number") else 0
        title_h = 32 + max(0, len(lines(item.get("title", ""), title_wrap)) - 1) * 43.2
        body_lines = lines(item.get("body", ""), body_wrap)
        body_h = (28 + max(0, len(body_lines) - 1) * 39.2 + 12) if body_lines else 0
        return max(176, 56 + number_h + title_h + body_h)

    layout = "horizontal"
    if orientation == "vertical":
        layout = "vertical"
    elif orientation == "zigzag" or count >= 5:
        layout = "zigzag"

    if layout == "horizontal":
        gap = 34
        w = (content_w - gap * (count - 1)) / count
        h = max(node_height(item, w) for item in items)
        positions = [(content_x + i * (w + gap), top, w, h) for i in range(count)]
    elif layout == "vertical":
        gap, w = 24, content_w
        positions = []
        y = top
        for item in items:
            h = node_height(item, w)
            positions.append((content_x, y, w, h))
            y += h + gap
    else:
        # Five or more text-rich steps use a two-column serpentine path. The
        # center gutter is reserved exclusively for connectors.
        columns, column_gap, row_gap = 2, 92, 30
        w = (content_w - column_gap) / columns
        row_heights = []
        for row in range(math.ceil(count / columns)):
            row_items = items[row * columns:(row + 1) * columns]
            row_heights.append(max(node_height(item, w) for item in row_items))
        positions = []
        y = top
        for index, item in enumerate(items):
            row, col = divmod(index, columns)
            if row and col == 0:
                y += row_heights[row - 1] + row_gap
            x = content_x + col * (w + column_gap)
            positions.append((x, y, w, row_heights[row]))

    for i, item in enumerate(items):
        targets = item.get("next", [i + 1] if i + 1 < count else [])
        x, y, w, h = positions[i]
        for target in targets:
            if not 0 <= int(target) < count:
                continue
            tx, ty, tw, th = positions[int(target)]
            if layout == "horizontal":
                x1, y1, x2, y2 = x + w, y + h / 2, tx, ty + th / 2
                path = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
            elif layout == "vertical":
                x1, y1, x2, y2 = x + w / 2, y + h, tx + tw / 2, ty
                path = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
            else:
                gutter_x = content_x + w + 46
                if int(target) // 2 == i // 2:
                    x1, y1, x2, y2 = x + w, y + h / 2, tx, ty + th / 2
                    path = f"M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}"
                else:
                    x1, y1 = x, y + h / 2
                    x2, y2 = tx + tw, ty + th / 2
                    path = f"M {x1:.1f} {y1:.1f} H {gutter_x:.1f} V {y2:.1f} H {x2:.1f}"
            connectors.append(f'<path d="{path}" stroke="{BORDER}" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')
        fill, stroke, sw = card_style(spec.get("style", "outline"))
        nodes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        ty0 = y + 34
        if item.get("number"):
            block, bh = text_block(x + 24, ty0, item["number"], 27, 700, 8, color=SECONDARY)
            nodes.append(block); ty0 += bh + 14
        usable_width = max(160, w - 48)
        block, bh = text_block(x + 24, ty0, item.get("title", ""), 32, 700, max(12, int(usable_width / 16)))
        nodes.append(block); ty0 += bh + 12
        if item.get("body"):
            block, _ = text_block(x + 24, ty0, item["body"], 28, 400, max(14, int(usable_width / 14.5)), 1.4)
            nodes.append(block)
    bottom = max(y + h for x, y, w, h in positions)
    return connectors + nodes, int(bottom)


def render_cycle(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:6]
    if not items:
        return [], top
    cx, cy = content_x + content_w / 2, top + 340
    radius = min(content_w * .32, 330)
    node_w, node_h = 250, 136
    connectors, nodes, positions = [], [], []
    for i in range(len(items)):
        angle = -math.pi / 2 + i * 2 * math.pi / len(items)
        positions.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    for i, (px, py) in enumerate(positions):
        qx, qy = positions[(i + 1) % len(positions)]
        connectors.append(f'<path d="M {px:.1f} {py:.1f} Q {cx:.1f} {cy:.1f} {qx:.1f} {qy:.1f}" stroke="{BORDER}" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')
        x, y = px - node_w / 2, py - node_h / 2
        nodes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{node_w}" height="{node_h}" rx="9" fill="{PAPER}" stroke="{BORDER}" stroke-width="2"/>')
        block, bh = text_block(px, y + 44, items[i].get("title", ""), 31, 700, 16, anchor="middle")
        nodes.append(block)
        if items[i].get("body"):
            block, _ = text_block(px, y + 50 + bh, items[i]["body"], 27, 400, 20, 1.35, anchor="middle")
            nodes.append(block)
    if spec.get("center"):
        nodes.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="108" fill="{TILE}" stroke="{BORDER}" stroke-width="2"/>')
        block, _ = text_block(cx, cy - 8, spec["center"], 35, 700, 14, 1.25, anchor="middle")
        nodes.append(block)
    return connectors + nodes, int(cy + radius + node_h / 2)


def render_hub(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:10]
    cx, cy = content_x + content_w / 2, top + 360
    radius = min(content_w * .37, 390)
    out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="128" fill="{TILE}" stroke="{BORDER}" stroke-width="2"/>']
    block, _ = text_block(cx, cy - 8, spec.get("center", "Sistema"), 38, 700, 14, 1.25, anchor="middle")
    out.append(block)
    for i, item in enumerate(items):
        angle = -math.pi / 2 + i * 2 * math.pi / max(1, len(items))
        px, py = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {px:.1f} {py:.1f}" stroke="{BORDER}" stroke-width="3" stroke-dasharray="5 7" fill="none"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="78" fill="{PAPER}" stroke="{BORDER}" stroke-width="2"/>')
        block, _ = text_block(px, py - 8, item.get("title", ""), 29, 700, 13, 1.25, anchor="middle")
        out.append(block)
    return out, int(cy + radius + 96)


def render_system_map(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    """Render a landscape system map with five complete concept modules.

    Labels have their own white cards and never sit on connector lines or
    geometric objects.  Five items are supported because the course frequently
    uses responsibility/power maps with an odd final dimension.
    """
    items = spec.get("items", [])[:5]
    if not items:
        return [], top
    cx, cy = content_x + content_w / 2, top + 326
    card_w, card_h = min(292, content_w * .265), 154
    xs = [content_x + card_w / 2, cx, content_x + content_w - card_w / 2]
    positions = [(xs[0], top + 84), (xs[1], top + 84), (xs[2], top + 84)]
    if len(items) > 3:
        positions.extend([(content_x + content_w * .30, top + 585),
                          (content_x + content_w * .70, top + 585)])
    positions = positions[:len(items)]
    connectors: list[str] = []
    nodes: list[str] = []
    for index, (item, (px, py)) in enumerate(zip(items, positions)):
        edge_y = py + card_h / 2 if py < cy else py - card_h / 2
        connectors.append(
            f'<path d="M {cx:.1f} {cy:.1f} Q {px:.1f} {cy:.1f} {px:.1f} {edge_y:.1f}" '
            f'stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7" fill="none"/>'
        )
        connectors.append(f'<circle cx="{px:.1f}" cy="{edge_y:.1f}" r="6" fill="{CYAN if index % 2 else SAND}" stroke="{SECONDARY}" stroke-width="1.5"/>')
        x, y = px - card_w / 2, py - card_h / 2
        nodes.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{card_w:.1f}" height="{card_h}" rx="9" fill="{PAPER}" stroke="{BORDER}" stroke-width="2"/>')
        icon_kind = item.get("icon", "nodes")
        if icon_kind in {"stack", "technology", "model", "tasks", "structure", "repair"}:
            icon_kind = {"technology": "database", "tasks": "task", "structure": "rules", "repair": "decision"}.get(icon_kind, "nodes")
        nodes.append(line_icon(icon_kind, x + 38, py, .34))
        block, _ = text_block(x + 74, py - 14, item.get("title", ""), 27, 700, 13, 1.2)
        nodes.append(block)
    nodes.append(iso_box(cx, cy - 55, 174, 68, 78, BLUE, SAND, STONE))
    label_w, label_h = min(350, content_w * .38), 84
    nodes.append(
        f'<rect x="{cx-label_w/2:.1f}" y="{cy+78:.1f}" width="{label_w:.1f}" height="{label_h}" '
        f'rx="10" fill="{PAPER}" stroke="{BORDER}" stroke-width="2"/>'
    )
    block, _ = text_block(cx, cy + 113, spec.get("center", "Sistema"), 29, 700, 18, 1.16, anchor="middle")
    nodes.append(block)
    return connectors + nodes, int(top + 690)


def render_layers(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:6]
    out = []
    layer_h, gap = 118, 18
    for i, item in enumerate(items):
        inset = i * 42
        x, y = content_x + inset, top + i * (layer_h + gap)
        w = content_w - inset * 2
        fill = TILE if i % 2 == 0 else PAPER
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{layer_h}" rx="9" fill="{fill}" stroke="{BORDER}" stroke-width="2"/>')
        block, _ = text_block(x + 28, y + 48, item.get("title", ""), 34, 700, max(20, int(w / 18)))
        out.append(block)
        if item.get("body"):
            block, _ = text_block(x + w * .48, y + 48, item["body"], 28, 400, max(22, int(w / 16)))
            out.append(block)
    return out, int(top + len(items) * (layer_h + gap) - gap)


def render_panels(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:6]
    columns = 3 if len(items) > 3 else max(1, len(items))
    rows = math.ceil(len(items) / columns)
    gap, panel_h = 30, 286
    panel_w = (content_w - gap * (columns - 1)) / columns
    out = []
    for i, item in enumerate(items):
        row, col = divmod(i, columns)
        x, y = content_x + col * (panel_w + gap), top + row * (panel_h + gap)
        if col:
            out.append(f'<line x1="{x-gap/2:.1f}" y1="{y:.1f}" x2="{x-gap/2:.1f}" y2="{y+panel_h:.1f}" stroke="{BORDER}" stroke-width="2" stroke-dasharray="4 6"/>')
        out.append(f'<circle cx="{x+52:.1f}" cy="{y+62:.1f}" r="38" fill="{TILE}" stroke="{BORDER}" stroke-width="2"/>')
        out.append(f'<path d="M {x+32:.1f} {y+62:.1f} H {x+72:.1f} M {x+52:.1f} {y+42:.1f} V {x+52:.1f} {y+82:.1f}" stroke="{SECONDARY}" stroke-width="3"/>')
        block, bh = text_block(x, y + 132, item.get("title", ""), 33, 700, max(16, int(panel_w / 14)))
        out.append(block)
        if item.get("body"):
            block, _ = text_block(x, y + 144 + bh, item["body"], 28, 400, max(17, int(panel_w / 13)), 1.4)
            out.append(block)
    return out, int(top + rows * panel_h + (rows - 1) * gap)


def render_assembly(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:6]
    count = max(1, len(items))
    gap = 24
    node_w = (content_w - gap * (count - 1)) / count
    center_x, center_y = content_x + content_w / 2, top + 410
    connectors, nodes = [], []
    for index, item in enumerate(items):
        x = content_x + index * (node_w + gap)
        nodes.append(f'<path d="M{x:.1f} {top+42}l{node_w/2:.1f} -28l{node_w/2:.1f} 28l{-node_w/2:.1f} 28z" fill="{PAPER}" stroke="{BORDER}" stroke-width="2"/>')
        block, _ = text_block(x + node_w/2, top + 50, item.get("title", ""), 30, 700, 13, anchor="middle")
        nodes.append(block)
        port_x = center_x - 58 + index * (116 / max(1, count - 1))
        connectors.append(f'<path d="M{x+node_w/2:.1f} {top+115} V {top+235} Q {x+node_w/2:.1f} {top+290} {port_x:.1f} {center_y-105:.1f}" stroke="{BORDER}" stroke-width="3" stroke-dasharray="5 7" fill="none" marker-end="url(#arrow)"/>')
    nodes.append(f'<path d="M{center_x-150:.1f} {center_y-80:.1f}l150 -62l150 62v145l-150 62l-150-62z" fill="{TILE}" stroke="{BORDER}" stroke-width="2"/>')
    block, _ = text_block(center_x, center_y + 8, spec.get("center", "Resultado"), 37, 700, 17, anchor="middle")
    nodes.append(block)
    return connectors + nodes, int(center_y + 220)


def render_orbit(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:5]
    cx, cy = content_x + content_w / 2, top + 360
    out = []
    for index in range(len(items), 0, -1):
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{72+index*48}" fill="none" stroke="{BORDER}" stroke-width="2"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="92" fill="{INK}"/>')
    block, _ = text_block(cx, cy - 10, spec.get("center", "Sistema"), 35, 700, 15, color=PAPER, anchor="middle")
    out.append(block)
    for index, item in enumerate(items):
        angle = -math.pi + index * math.pi / max(1, len(items)-1)
        r = 120 + index * 42
        px, py = cx + r * math.cos(angle), cy + r * math.sin(angle)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="9" fill="{SECONDARY}"/>')
        block, _ = text_block(px, py - 24, item.get("title", ""), 29, 700, 15, anchor="middle")
        out.append(block)
    return out, int(cy + 330)


def render_icon_field(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:6]
    columns = 2
    rows = math.ceil(len(items) / columns)
    cell_w, cell_h = content_w / 2, 260
    text_w = max(160, cell_w - 150)
    title_wrap = max(12, int(text_w / 15))
    body_wrap = max(15, int(text_w / 13))
    out = []
    for index, item in enumerate(items):
        row, col = divmod(index, columns)
        x, y = content_x + col * cell_w, top + row * cell_h
        if col:
            out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y+cell_h-30:.1f}" stroke="{BORDER}" stroke-width="2" stroke-dasharray="4 7"/>')
        out.append(f'<circle cx="{x+58:.1f}" cy="{y+62:.1f}" r="38" fill="none" stroke="{INK}" stroke-width="3"/>')
        out.append(f'<path d="M{x+38:.1f} {y+62:.1f}h40M{x+58:.1f} {y+42:.1f}v40" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
        block, bh = text_block(x+118, y+54, item.get("title", ""), 34, 700, title_wrap)
        out.append(block)
        if item.get("body"):
            block, _ = text_block(x+118, y+70+bh, item["body"], 29, 400, body_wrap, 1.4)
            out.append(block)
    return out, int(top + rows * cell_h)


def iso_box(cx: float, y: float, w: float, depth: float, height: float,
            top_fill: str = STONE, left_fill: str = SAND, right_fill: str = BLUE) -> str:
    x0, x1 = cx - w / 2, cx + w / 2
    ym = y + depth / 2
    yb = y + depth
    return (
        f'<polygon points="{cx:.1f},{y:.1f} {x1:.1f},{ym:.1f} {cx:.1f},{yb:.1f} {x0:.1f},{ym:.1f}" fill="{top_fill}" stroke="{SECONDARY}" stroke-width="2"/>'
        f'<polygon points="{x0:.1f},{ym:.1f} {cx:.1f},{yb:.1f} {cx:.1f},{yb+height:.1f} {x0:.1f},{ym+height:.1f}" fill="{left_fill}" stroke="{SECONDARY}" stroke-width="2"/>'
        f'<polygon points="{cx:.1f},{yb:.1f} {x1:.1f},{ym:.1f} {x1:.1f},{ym+height:.1f} {cx:.1f},{yb+height:.1f}" fill="{right_fill}" stroke="{SECONDARY}" stroke-width="2"/>'
    )


def iso_stack(cx: float, y: float, w: float = 118, layers: int = 3) -> str:
    out = []
    for i in range(layers - 1, -1, -1):
        out.append(iso_box(cx, y + i * 25, w, 42, 22,
                           STONE if i % 2 == 0 else PAPER, SAND, BLUE))
    return "".join(out)


def line_icon(kind: str, cx: float, cy: float, scale: float = 1.0) -> str:
    s, c, sw = scale, INK, 3
    if kind in {"database", "source"}:
        return (f'<ellipse cx="{cx:.1f}" cy="{cy-28*s:.1f}" rx="{38*s:.1f}" ry="{14*s:.1f}" fill="{STONE}" stroke="{c}" stroke-width="{sw}"/>'
                f'<path d="M{cx-38*s:.1f} {cy-28*s:.1f}v{54*s:.1f}c0 {10*s:.1f} {17*s:.1f} {15*s:.1f} {38*s:.1f} {15*s:.1f}s{38*s:.1f}-{5*s:.1f} {38*s:.1f}-{15*s:.1f}v{-54*s:.1f}" fill="{BLUE}" stroke="{c}" stroke-width="{sw}"/>'
                f'<path d="M{cx+5*s:.1f} {cy+5*s:.1f}l{12*s:.1f} {12*s:.1f}l{22*s:.1f}-{27*s:.1f}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind in {"stack", "technology", "model"}:
        return iso_stack(cx, cy - 55*s, 108*s, 3)
    if kind in {"rules", "governance", "decision"}:
        return (f'<path d="M{cx:.1f} {cy-43*s:.1f}l{42*s:.1f} {42*s:.1f}l{-42*s:.1f} {42*s:.1f}l{-42*s:.1f}-{42*s:.1f}z" fill="{STONE}" stroke="{c}" stroke-width="{sw}"/>'
                f'<path d="M{cx:.1f} {cy-58*s:.1f}v{15*s:.1f}M{cx-58*s:.1f} {cy-1*s:.1f}h{16*s:.1f}M{cx+42*s:.1f} {cy-1*s:.1f}h{16*s:.1f}" stroke="{c}" stroke-width="{sw}"/>'
                f'<path d="M{cx-15*s:.1f} {cy-2*s:.1f}h{30*s:.1f}M{cx:.1f} {cy-19*s:.1f}v{34*s:.1f}M{cx-12*s:.1f} {cy+20*s:.1f}h{24*s:.1f}" stroke="{c}" stroke-width="{sw}"/>')
    if kind in {"nodes", "data", "evidence"}:
        pts = [(-34, -18), (-8, -36), (22, -18), (37, 14), (4, 36), (-31, 19)]
        path = " ".join(f"{cx+x*s:.1f},{cy+y*s:.1f}" for x, y in pts)
        dots = "".join(f'<circle cx="{cx+x*s:.1f}" cy="{cy+y*s:.1f}" r="{6*s:.1f}" fill="{SAND}" stroke="{c}" stroke-width="2"/>' for x, y in pts)
        return f'<polyline points="{path}" fill="none" stroke="{c}" stroke-width="{sw}"/>{dots}'
    if kind in {"person", "people", "actor"}:
        return (f'<circle cx="{cx:.1f}" cy="{cy-31*s:.1f}" r="{15*s:.1f}" fill="{PAPER}" stroke="{c}" stroke-width="{sw}"/>'
                f'<path d="M{cx-28*s:.1f} {cy+35*s:.1f}v{-22*s:.1f}c0{-18*s:.1f} {13*s:.1f}{-30*s:.1f} {28*s:.1f}{-30*s:.1f}s{28*s:.1f} {12*s:.1f} {28*s:.1f} {30*s:.1f}v{22*s:.1f}M{cx:.1f} {cy+4*s:.1f}v{36*s:.1f}" fill="none" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')
    if kind in {"task", "process", "document"}:
        return (f'<path d="M{cx-42*s:.1f} {cy-38*s:.1f}h{58*s:.1f}l{24*s:.1f} {24*s:.1f}v{62*s:.1f}h{-82*s:.1f}z" fill="{STONE}" stroke="{c}" stroke-width="{sw}"/>'
                f'<path d="M{cx+16*s:.1f} {cy-38*s:.1f}v{24*s:.1f}h{24*s:.1f}M{cx-24*s:.1f} {cy-2*s:.1f}h{45*s:.1f}M{cx-24*s:.1f} {cy+15*s:.1f}h{45*s:.1f}" fill="none" stroke="{c}" stroke-width="{sw}"/>')
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{40*s:.1f}" fill="none" stroke="{c}" stroke-width="{sw}"/>'
            f'<path d="M{cx-19*s:.1f} {cy:.1f}h{38*s:.1f}M{cx:.1f} {cy-19*s:.1f}v{38*s:.1f}" stroke="{c}" stroke-width="{sw}" stroke-linecap="round"/>')


def render_iso_evidence(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:4]
    count = max(1, len(items))
    col_w = content_w / count
    label_y, icon_y = top + 30, top + 190
    center_x, center_y = content_x + content_w / 2, top + 500
    out, connectors = [], []
    for index, item in enumerate(items):
        cx = content_x + col_w * (index + .5)
        block, bh = text_block(cx, label_y, item.get("title", ""), 28, 700, 15, 1.2, anchor="middle")
        out.append(block)
        if item.get("body"):
            block, _ = text_block(cx, label_y + bh + 12, item.get("body", ""), 23, 400, 20, 1.3, SECONDARY, "middle")
            out.append(block)
        out.append(line_icon(item.get("icon", "nodes"), cx, icon_y, .78))
        port_y = top + 302
        out.append(f'<circle cx="{cx:.1f}" cy="{port_y:.1f}" r="7" fill="{SECONDARY}"/>')
        target_x = center_x - 112 + index * (224 / max(1, count-1))
        connectors.append(f'<path d="M{cx:.1f} {port_y:.1f}V{top+370:.1f}Q{cx:.1f} {top+415:.1f} {target_x:.1f} {center_y-64:.1f}" fill="none" stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7" marker-end="url(#arrowDark)"/>')
    out = connectors + out
    out.append(iso_box(center_x, center_y-95, 270, 96, 125, BLUE, SAND, STONE))
    out.append(f'<path d="M{center_x-72:.1f} {center_y-62:.1f}l72 36l72-36l-72-36z" fill="{PAPER}" stroke="{SECONDARY}" stroke-width="2"/>')
    block, _ = text_block(center_x, center_y+168, spec.get("center", "Evidencia"), 35, 700, 18, 1.2, anchor="middle")
    out.append(block)
    return out, int(center_y + 220)


def render_iso_sociotechnical(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = (spec.get("items", []) + [{}, {}, {}, {}])[:4]
    cx, cy = content_x + content_w/2, top + 270
    out = []
    # central routing cube and ports
    out.append(iso_box(cx, cy-35, 82, 38, 48, STONE, SAND, BLUE))
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        px, py = cx + 70*math.cos(angle), cy + 70*math.sin(angle)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{SECONDARY}"/>')
    # people: left cluster
    lx, ly = content_x + 150, cy
    out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="76" fill="none" stroke="{SECONDARY}" stroke-width="2"/>' )
    for dx, dy in [(-50, 0), (0, -45), (48, 6), (0, 47)]:
        out.append(f'<circle cx="{lx+dx:.1f}" cy="{ly+dy:.1f}" r="27" fill="{STONE}" stroke="{SECONDARY}" stroke-width="2"/>')
        out.append(line_icon("person", lx+dx, ly+dy, .34))
    out.append(f'<path d="M{lx+92:.1f} {ly:.1f}H{cx-70:.1f}" stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7"/>')
    # technology stack: top
    tx, ty = cx, top + 105
    out.append(iso_stack(tx, ty, 138, 4))
    out.append(f'<path d="M{tx:.1f} {ty+130:.1f}V{cy-70:.1f}" stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7"/>')
    # tasks: bottom sequence
    task_y = top + 440
    for i in range(4):
        px = cx - 180 + i*120
        out.append(iso_box(px, task_y, 82, 30, 56, PAPER, SAND if i%2==0 else CYAN, STONE))
        if i < 3:
            out.append(f'<path d="M{px+45:.1f} {task_y+45:.1f}H{px+75:.1f}" stroke="{SECONDARY}" stroke-width="2" stroke-dasharray="4 6" marker-end="url(#arrowDark)"/>')
    out.append(f'<path d="M{cx:.1f} {cy+70:.1f}V{task_y-20:.1f}" stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7"/>')
    # structure plates: right
    rx, ry = content_x + content_w - 150, cy - 45
    for i in range(4):
        px, py = rx + (i%2)*58, ry + (i//2)*94
        out.append(f'<polygon points="{px-52:.1f},{py-30:.1f} {px+24:.1f},{py-5:.1f} {px+24:.1f},{py+44:.1f} {px-52:.1f},{py+19:.1f}" fill="{STONE if i%2==0 else BLUE}" stroke="{SECONDARY}" stroke-width="2"/>')
    out.append(f'<path d="M{cx+70:.1f} {cy:.1f}H{rx-85:.1f}" stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7"/>')
    positions = [(lx, top+390), (tx, top+24), (cx, task_y+118), (rx, top+390)]
    for item, (px, py) in zip(items, positions):
        block, bh = text_block(px, py, item.get("title", ""), 28, 700, 17, 1.2, anchor="middle")
        out.append(block)
        if item.get("body"):
            block, _ = text_block(px, py+bh+10, item.get("body", ""), 22, 400, 22, 1.28, SECONDARY, "middle")
            out.append(block)
    block, _ = text_block(cx, cy + 92, spec.get("center", "Sistema"), 30, 700, 16, 1.2, anchor="middle")
    out.append(block)
    return out, int(top + 620)


def render_iso_ecosystem(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    items = spec.get("items", [])[:6]
    cx, cy = content_x + content_w/2, top + 270
    out = [iso_stack(cx, cy-88, 166, 4)]
    block, _ = text_block(cx, cy+116, spec.get("center", "Sistema"), 34, 700, 18, 1.2, anchor="middle")
    out.append(block)
    if len(items) <= 4:
        positions = [
            (content_x+150, top+105), (content_x+150, top+385),
            (content_x+content_w-150, top+105), (content_x+content_w-150, top+385),
        ]
    else:
        positions = [
            (content_x+150, top+70), (content_x+150, top+270), (content_x+150, top+470),
            (content_x+content_w-150, top+70), (content_x+content_w-150, top+270), (content_x+content_w-150, top+470),
        ]
    for index, (item, (px, py)) in enumerate(zip(items, positions)):
        icon_kind = item.get("icon", ["database", "person", "rules", "nodes", "task", "decision"][index])
        out.append(line_icon(icon_kind, px, py, .72))
        title_y = py + 76
        block, bh = text_block(px, title_y, item.get("title", ""), 27, 700, 17, 1.2, anchor="middle")
        out.append(block)
        if item.get("body"):
            block, _ = text_block(px, title_y+10+bh, item.get("body", ""), 22, 400, 19, 1.28, SECONDARY, "middle")
            out.append(block)
        start_y = py + 44
        end_y = cy if px < cx else cy
        out.append(f'<path d="M{px:.1f} {start_y:.1f}Q{(px+cx)/2:.1f} {(start_y+end_y)/2:.1f} {cx:.1f} {end_y:.1f}" fill="none" stroke="{SECONDARY}" stroke-width="2.2" stroke-dasharray="4 7"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{start_y:.1f}" r="7" fill="{CYAN if index%2 else SAND}" stroke="{SECONDARY}" stroke-width="1.5"/>')
    return out, int(top + (600 if len(items) > 4 else 520))


def render_isometric_system(spec: dict, content_x: int, top: int, content_w: int) -> tuple[list[str], int]:
    variant = spec.get("variant", "evidence")
    if variant == "sociotechnical":
        return render_iso_sociotechnical(spec, content_x, top, content_w)
    if variant in {"ecosystem", "governance"}:
        return render_iso_ecosystem(spec, content_x, top, content_w)
    return render_iso_evidence(spec, content_x, top, content_w)


def render(spec: dict) -> str:
    width = int(spec.get("width", 1344))
    margin = int(width * 0.09)
    content_w = width - 2 * margin
    parts = []
    y = 78
    if spec.get("title"):
        title_size = 48 if width >= 900 else 38
        title_wrap = 40 if width >= 900 else 26
        block, bh = text_block(margin, y, spec["title"], title_size, 700, title_wrap, 1.18)
        parts.append(block); y += bh + 28
    if spec.get("subtitle"):
        block, bh = text_block(margin, y, spec["subtitle"], 24, 400, 78, 1.45, SECONDARY)
        parts.append(block); y += bh + 46
    kind = spec.get("type", "grid")
    if kind == "comparison":
        body, bottom = render_comparison(spec, margin, y, content_w)
    elif kind in {"flow", "timeline"}:
        body, bottom = render_flow(spec, margin, y, content_w)
    elif kind == "cycle":
        body, bottom = render_cycle(spec, margin, y, content_w)
    elif kind == "system-map":
        body, bottom = render_system_map(spec, margin, y, content_w)
    elif kind in {"radial", "hub"}:
        body, bottom = render_hub(spec, margin, y, content_w)
    elif kind == "layers":
        body, bottom = render_layers(spec, margin, y, content_w)
    elif kind == "panels":
        body, bottom = render_panels(spec, margin, y, content_w)
    elif kind == "isometric-system":
        body, bottom = render_isometric_system(spec, margin, y, content_w)
    elif kind == "assembly":
        body, bottom = render_assembly(spec, margin, y, content_w)
    elif kind == "orbit":
        body, bottom = render_orbit(spec, margin, y, content_w)
    elif kind in {"atlas", "icon-field"}:
        body, bottom = render_icon_field(spec, margin, y, content_w)
    else:
        body, bottom = render_grid(spec, margin, y, content_w)
    parts.extend(body)
    height = max(int(spec.get("height", 0)), bottom + 78, 420)
    defs = f'<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="{BORDER}"/></marker><marker id="arrowDark" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="{SECONDARY}"/></marker></defs>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(spec.get("alt", spec.get("title", "Infografía")))}">'
            f'{defs}<rect width="100%" height="100%" fill="{PAPER}"/>' + "".join(parts) + "</svg>\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.write_text(render(spec), encoding="utf-8")


if __name__ == "__main__":
    main()
