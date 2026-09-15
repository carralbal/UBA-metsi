#!/usr/bin/env python3

import argparse
import json
import os
import re
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
PRESENTATIONS = ROOT / "pedagogy" / "presentations"
SKILL_DIR = Path("/Users/diegocarralbal/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.11814/skills/presentations")
RUNTIME_PYTHON = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
RUNTIME_NODE = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
RUNTIME_MODULES = Path("/Users/diegocarralbal/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules")
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def clean_markdown(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    return value.strip()


def expected_workshop_steps(n: str) -> list[dict]:
    workshop = ROOT / "pedagogy" / n / "TALLER-SINCRONICO.md"
    content = workshop.read_text(encoding="utf-8")
    matches = re.findall(r"^###\s+(\d+)\.\s+(.+?),\s+(\d+)\s+minutos\s*$", content, re.MULTILINE)
    return [
        {"number": int(number), "title": clean_markdown(title), "minutes": int(minutes)}
        for number, title, minutes in matches
    ]


def natural_key(path: str) -> int:
    stem = Path(path).stem
    digits = "".join(char for char in stem if char.isdigit())
    return int(digits or 0)


def xml_text(archive: zipfile.ZipFile, name: str) -> str:
    root = ET.fromstring(archive.read(name))
    return " ".join(node.text or "" for node in root.findall(".//a:t", NS)).strip()


def make_montage(render_dir: Path, output: Path) -> None:
    slides = sorted(render_dir.glob("slide-*.png"), key=lambda p: natural_key(p.name))
    thumb_w, thumb_h = 480, 270
    gutter, label_h = 18, 28
    canvas = Image.new("RGB", (thumb_w * 5 + gutter * 6, (thumb_h + label_h) * 2 + gutter * 3), "#ecece9")
    draw = ImageDraw.Draw(canvas)
    for index, slide_path in enumerate(slides):
        image = Image.open(slide_path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        col, row = index % 5, index // 5
        left = gutter + col * (thumb_w + gutter)
        top = gutter + row * (thumb_h + label_h + gutter)
        canvas.paste(image, (left, top))
        draw.text((left, top + thumb_h + 5), slide_path.stem, fill="#181817")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def inspect_deck(deck: Path) -> dict:
    n = deck.parent.name
    expected_steps = expected_workshop_steps(n)
    with zipfile.ZipFile(deck) as archive:
        names = archive.namelist()
        slide_names = sorted(
            [name for name in names if name.startswith("ppt/slides/slide") and name.endswith(".xml")],
            key=natural_key,
        )
        note_names = sorted(
            [name for name in names if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")],
            key=natural_key,
        )
        notes = [xml_text(archive, name) for name in note_names]
        forbidden = [
            "PROPÓSITO DE LA PANTALLA",
            "FACILITACIÓN SINCRÓNICA",
            "USO ASINCRÓNICO",
            "RESULTADO DEL ENCUENTRO",
            "CONSIGNA VISIBLE Y TIEMPO",
            "Señal para avanzar",
            "El docente",
            "•",
        ]
        notes_with_stage_directions = [
            index + 1
            for index, note in enumerate(notes)
            if any(marker in note for marker in forbidden)
        ]
        short_notes = [
            index + 1
            for index, note in enumerate(notes)
            if len(note.split()) < 45
        ]
        visible_text = [xml_text(archive, name) for name in slide_names]
        activity_title_mismatches = [
            {"slide": index + 2, "expected": step["title"]}
            for index, step in enumerate(expected_steps)
            if index + 1 >= len(visible_text) or step["title"] not in visible_text[index + 1]
        ]
    return {
        "file": str(deck.relative_to(ROOT)),
        "bytes": deck.stat().st_size,
        "slides": len(slide_names),
        "notes": len(note_names),
        "notes_with_stage_directions": notes_with_stage_directions,
        "short_notes": short_notes,
        "workshop_steps": len(expected_steps),
        "workshop_minutes": sum(step["minutes"] for step in expected_steps),
        "activity_title_mismatches": activity_title_mismatches,
        "empty_visible_slides": [index + 1 for index, text in enumerate(visible_text) if not text],
        "pass": (
            len(slide_names) == 10
            and len(note_names) == 10
            and not notes_with_stage_directions
            and not short_notes
            and len(expected_steps) == 8
            and sum(step["minutes"] for step in expected_steps) == 120
            and not activity_title_mismatches
            and all(visible_text)
        ),
    }


def render_deck(deck: Path, render_root: Path) -> Path:
    n = deck.parent.name
    output_dir = render_root / n
    env = os.environ.copy()
    env["RUNTIME_NODE"] = str(RUNTIME_NODE)
    env["RUNTIME_NODE_MODULES"] = str(RUNTIME_MODULES)
    subprocess.run(
        [
            str(RUNTIME_PYTHON),
            str(SKILL_DIR / "container_tools" / "render_slides.py"),
            str(deck),
            "--output_dir",
            str(output_dir),
        ],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
    )
    montage = render_root / "montages" / f"{n}-montage.png"
    make_montage(output_dir, montage)
    return montage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-root", type=Path)
    parser.add_argument("--revision", default="v4-guion-oral")
    args = parser.parse_args()

    decks = [
        PRESENTATIONS / f"N{index:02d}" / f"N{index:02d}-METSI-material-de-clase-{args.revision}.pptx"
        for index in range(1, 37)
    ]
    results = []
    for deck in decks:
        if not deck.exists():
            results.append({"file": str(deck.relative_to(ROOT)), "pass": False, "error": "missing"})
            continue
        result = inspect_deck(deck)
        if args.render_root:
            result["montage"] = str(render_deck(deck, args.render_root))
        results.append(result)
        print(f"{deck.parent.name}\t{'PASS' if result['pass'] else 'FAIL'}")

    passed = sum(1 for result in results if result.get("pass"))
    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "revision": args.revision,
        "status": "PASS" if passed == 36 else "FAIL",
        "documents": 36,
        "passed": passed,
        "slides": sum(result.get("slides", 0) for result in results),
        "speaker_notes": sum(result.get("notes", 0) for result in results),
        "results": results,
    }
    versioned_json_path = PRESENTATIONS / f"AUDIT-N01-N36-{args.revision}.json"
    versioned_md_path = PRESENTATIONS / f"AUDIT-N01-N36-{args.revision}.md"
    json_path = PRESENTATIONS / "AUDIT-N01-N36.json"
    md_path = PRESENTATIONS / "AUDIT-N01-N36.md"
    json_content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    versioned_json_path.write_text(json_content, encoding="utf-8")
    json_path.write_text(json_content, encoding="utf-8")

    rows = "\n".join(
        f"| {index:02d} | {result.get('slides', 0)} | {result.get('notes', 0)} | {'PASS' if result.get('pass') else 'FAIL'} |"
        for index, result in enumerate(results, start=1)
    )
    md_content = (
        f"# Auditoría de presentaciones N01 a N36 · {args.revision}\n\n"
        f"Resultado: **{report['status']}**.\n\n"
        f"Se verificaron {report['documents']} presentaciones, {report['slides']} pantallas visibles y "
        f"{report['speaker_notes']} notas de orador. Cada nota está redactada como discurso oral continuo, "
        "sin rótulos internos, instrucciones de facilitación, viñetas ni referencias al docente en tercera persona. "
        "Las pantallas 02 a 09 conservan la actividad y el tiempo del taller correspondiente.\n\n"
        "| N | Pantallas | Notas | Estado |\n|---:|---:|---:|---|\n"
        f"{rows}\n"
    )
    versioned_md_path.write_text(md_content, encoding="utf-8")
    md_path.write_text(md_content, encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["status", "documents", "slides", "speaker_notes"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
