#!/usr/bin/env python3
"""Run reproducible, bounded checks for the N16 fictional A/P1 candidate.

This is a teaching sketch, not a production model or BPMN equivalence proof.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import test_n16_er_nine_facts_private_20261023 as base
import test_n16_semantic_repairs_private_v2_20261023 as p1


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "QA-A-P1-private-20261028.json"


def database_A_P1() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    for source in (base.SCHEMA, p1.EXTENSION, ROOT / "ER-reglas-A-v3.sql"):
        connection.executescript(source.read_text(encoding="utf-8"))
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    return connection


def same_observation_relations(checks: list[str]) -> None:
    """Follow C-107 through two serial observations of one person/tramite."""
    c = database_A_P1()
    person, tr = base.case(c, "107-A")
    base.observation(c, "O-107-A", tr)
    base.notice(c, "A-107-A-f", tr, person, obj="O-107-A")
    base.repair(c, "RP-107-A", tr, person, obj="O-107-A", failed="A-107-A-f")
    base.notice(c, "A-107-A-ok", tr, person, obj="O-107-A", delivered=True)
    base.close(c, "RP-107-A", "A-107-A-ok")
    base.change(c, "107-A", tr, "En revisión", "Requiere acción")
    c.execute("INSERT INTO RESPUESTA VALUES (?,?,?,?,?,?,?,?)",
              ("R-107-A", tr, "O-107-A", person, base.T2, "DOC-107-A", "humano", "TRY-107-A"))
    base.change(c, "107-A", tr, "Requiere acción", "En revisión")
    c.execute("UPDATE OBSERVACION SET estado='CONTESTADA' WHERE id_observacion='O-107-A'")
    base.observation(c, "O-107-B", tr)
    base.rejects("C107_old_notice_cannot_advance_new_observation", lambda: base.change(
        c, "107-A", tr, "En revisión", "Requiere acción"), checks)
    base.notice(c, "A-107-B-f", tr, person, obj="O-107-B")
    base.repair(c, "RP-107-B", tr, person, obj="O-107-B", failed="A-107-B-f")
    base.rejects("C107_old_notice_cannot_close_new_repair", lambda: base.close(
        c, "RP-107-B", "A-107-A-ok"), checks)
    base.notice(c, "A-107-B-ok", tr, person, obj="O-107-B", delivered=True)
    base.close(c, "RP-107-B", "A-107-B-ok")
    base.rejects("C107_A_otra_observacion_no_vincula", lambda: c.execute(
        "INSERT INTO REPARACION_AVISO VALUES (?,?)", ("RP-107-A", "A-107-B-ok")), checks)
    base.rejects("C107_A_otra_observacion_no_reabre_reparacion", lambda: base.repair(
        c, "RP-107-A-otro", tr, person, obj="O-107-A", failed="A-107-A-f"), checks)
    base.change(c, "107-A", tr, "En revisión", "Requiere acción")
    assert c.execute("SELECT count(*) FROM REPARACION WHERE estado='ABIERTA'").fetchone()[0] == 0
    c.close()


def closure_and_policy_guards(checks: list[str]) -> None:
    c = database_A_P1()
    person, tr = base.case(c, "A-GUARD")
    base.observation(c, "O-A-GUARD", tr)
    base.notice(c, "A-A-GUARD-f", tr, person, obj="O-A-GUARD")
    base.rejects("A_response_requires_visible_delivered_state", lambda: c.execute(
        "INSERT INTO RESPUESTA VALUES (?,?,?,?,?,?,?,?)",
        ("R-A-GUARD", tr, "O-A-GUARD", person, base.T2, "DOC-A-GUARD", "web", "TRY-A-GUARD")), checks)
    base.rejects("A_rejects_per_attempt_repair", lambda: base.repair(
        c, "RP-A-GUARD-B", tr, person, obj="O-A-GUARD",
        failed="A-A-GUARD-f", policy="INTENTO"), checks)
    base.repair(c, "RP-A-GUARD", tr, person, obj="O-A-GUARD", failed="A-A-GUARD-f")
    base.notice(c, "A-A-GUARD-ok", tr, person, obj="O-A-GUARD", delivered=True)
    base.rejects("A_state_waits_for_repair_closure", lambda: base.change(
        c, "A-GUARD", tr, "En revisión", "Requiere acción"), checks)
    base.close(c, "RP-A-GUARD", "A-A-GUARD-ok")
    base.change(c, "A-GUARD", tr, "En revisión", "Requiere acción")
    c.close()


def main() -> None:
    checks: list[str] = []
    original_base = base.database
    original_p1 = p1.database_v2
    base.database = database_A_P1
    p1.database_v2 = database_A_P1
    try:
        p1.four_counterexamples(checks)
        p1.initial_state_bypass(checks)
        for scenario in (base.scenario_101, base.scenario_102, base.scenario_103,
                         base.scenario_104, base.scenario_105):
            scenario(checks)
        c106 = base.scenario_106("EPISODIO", checks)
        same_observation_relations(checks)
        closure_and_policy_guards(checks)
    finally:
        base.database = original_base
        p1.database_v2 = original_p1
    assert c106 == {"tramites": 1, "avisos": 3, "reparaciones": 1,
                    "reparaciones_abiertas": 0}
    hours = (datetime.fromisoformat(base.T3) - datetime.fromisoformat(base.T0)).total_seconds() / 3600
    assert hours == 49
    report = {
        "status": "PASS_PRIVATE_RELATIONAL_A_P1_LIMITED",
        "assumptions": ["A: one repair episode, all attempts retained", "P1: active observation blocks resolution"],
        "cases": ["C-101", "C-102", "C-103", "C-104", "C-105", "C-106-A", "C-107 serial observations"],
        "rejected_invalid_moves": checks,
        "rejected_count": len(checks),
        "c106": {**c106, "single_episode_hours": hours},
        "limits": [
            "A/P1 are didactic assumptions, not FCE policy.",
            "C-107 has a serial state trace and rejects linking a second observation to the first repair; full independent BPMN/ER equivalence remains open.",
            "SQLite triggers do not establish permissions, immutable history, concurrency, privacy, retention, or real timing.",
            "BPMN XML structure was checked separately, but no independent modeler import or teacher correction of v11 has happened.",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "cases", "rejected_count", "c106")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
