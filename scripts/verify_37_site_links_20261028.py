"""Verify that the live homepage exposes all 37 current PDF paths.

Read-only remote check; does not infer that the academic program is synchronized.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.parse
import urllib.request

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "site/course-manifest.json"
OUTPUT = Path(os.environ.get("METSI_LINK_REPORT", str(ROOT / "AUDITORIA-ENLACES-SITIO-37-N-20261028.json")))
URL = "https://carralbal.github.io/UBA-metsi/"


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    readings = json.loads(MANIFEST.read_text(encoding="utf-8"))["readings"]
    expected = {row["code"]: row["pdf"].split("?", 1)[0] for row in readings}
    expected_revisions = {row["code"]: row["revision"] for row in readings}
    request = urllib.request.Request(URL, headers={"User-Agent": "METSI-remote-link-audit/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        body = response.read()
        status = response.status
    tree = html.fromstring(body)
    links = collections.defaultdict(set)
    revisions = collections.defaultdict(set)
    for anchor in tree.xpath("//a[@href]"):
        href = anchor.get("href", "")
        match = re.search(r"(N\d\d)-METSI-lectura-previa[^/]*\.pdf", href)
        if not match:
            continue
        parsed = urllib.parse.urlparse(urllib.parse.urljoin(URL, href))
        path = parsed.path.removeprefix("/UBA-metsi/")
        links[match.group(1)].add(path)
        if path == expected[match.group(1)]:
            revisions[match.group(1)].update(urllib.parse.parse_qs(parsed.query).get("v", []))
    missing = sorted(set(expected) - set(links))
    mismatched = {code: sorted(paths) for code, paths in links.items() if expected[code] not in paths}
    revision_mismatches = {
        code: sorted(revisions[code]) for code, revision in expected_revisions.items()
        if revision not in revisions[code]
    }
    report = {
        "url": URL,
        "http_status": status,
        "remote_index_sha256": hashlib.sha256(body).hexdigest(),
        "expected_readings": len(expected),
        "codes_linked": len(links),
        "missing": missing,
        "manifest_path_mismatches": mismatched,
        "revision_mismatches": revision_mismatches,
        "pass": status == 200 and len(links) == 37 and not missing and not mismatched and not revision_mismatches,
        "scope_limit": "Checks live homepage paths against local manifest; academic program and PDF content are separate checks.",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
