#!/usr/bin/env python3
"""Try four explicit N16 repairs in a private in-memory teaching sketch.

This tests policy P1 (active observations block resolution), not an approved
institutional choice or an equivalence proof for the BPMN and ER models.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import test_n16_er_nine_facts_private_20261023 as base


ROOT = Path(__file__).resolve().parent
EXTENSION = ROOT / "ER-reglas-P1-v2.sql"
REPORT = ROOT / "QA-reglas-P1-private.json"


def database_v2() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(base.SCHEMA.read_text(encoding="utf8"))
    connection.executescript(EXTENSION.read_text(encoding="utf8"))
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    return connection


def reject(label: str, action, out: list[str]) -> None:
    try:
        action()
    except sqlite3.IntegrityError:
        out.append(label)
    else:
        raise AssertionError(f"Invalid move accepted in private v2: {label}")


def four_counterexamples(out: list[str]) -> None:
    c = database_v2()
    person, tr = base.case(c, "V2-ACTIVE")
    base.observation(c, "O-V2-ACTIVE", tr)
    base.decision(c, "D-V2-ACTIVE", tr)
    base.notice(c, "A-V2-ACTIVE", tr, person, obj="D-V2-ACTIVE", purpose="DECISION", delivered=True)
    reject("active_observation_blocks_resolution_P1", lambda: base.change(c, "V2-ACTIVE", tr, "En revisión", "Resuelto"), out)
    assert c.execute("SELECT estado_actual FROM TRAMITE WHERE id_tramite=?", (tr,)).fetchone()[0] == "En revisión"
    c.close()

    c = database_v2()
    _, tr = base.case(c, "V2-UPDATE")
    before = c.execute("SELECT count(*) FROM CAMBIO_ESTADO WHERE id_tramite=?", (tr,)).fetchone()[0]
    reject("direct_state_update_without_history", lambda: c.execute(
        "UPDATE TRAMITE SET estado_actual='Resuelto' WHERE id_tramite=?", (tr,)), out)
    after = c.execute("SELECT count(*) FROM CAMBIO_ESTADO WHERE id_tramite=?", (tr,)).fetchone()[0]
    assert before == after == 1
    c.close()

    c = database_v2()
    _, tr = base.case(c, "V2-ANSWER")
    base.observation(c, "O-V2-ANSWER", tr)
    reject("answered_observation_without_response", lambda: c.execute(
        "UPDATE OBSERVACION SET estado='CONTESTADA' WHERE id_observacion='O-V2-ANSWER'"), out)
    c.close()

    c = database_v2()
    person, tr = base.case(c, "V2-TIME")
    base.observation(c, "O-V2-TIME", tr)
    base.notice(c, "A-V2-TIME", tr, person, obj="O-V2-TIME", delivered=True, delivered_at=base.T3)
    reject("state_change_dated_before_delivery", lambda: c.execute(
        "INSERT INTO CAMBIO_ESTADO VALUES (?,?,?,?,?,?)",
        ("CE-V2-TIME-2", tr, "En revisión", "Requiere acción", base.T0, "Mesa")), out)
    c.close()


def initial_state_bypass(out: list[str]) -> None:
    c = database_v2()
    c.execute("INSERT INTO PERSONA VALUES ('P-V2-INITIAL')")
    reject("initial_state_without_history", lambda: c.execute(
        "INSERT INTO TRAMITE(id_tramite,id_persona,estado_actual) VALUES (?,?,?)",
        ("T-V2-INITIAL", "P-V2-INITIAL", "Resuelto")), out)
    c.close()


def baseline_valid_cases(out: list[str]) -> dict:
    # Reuse the old eight fictional scenarios against the new, private rules.
    original_database = base.database
    base.database = database_v2
    try:
        for fn in (base.scenario_101, base.scenario_102, base.scenario_103,
                   base.scenario_104, base.scenario_105):
            fn(out)
        c106 = {policy: base.scenario_106(policy, out) for policy in ("EPISODIO", "INTENTO")}
        base.scenario_107(out)
        return c106
    finally:
        base.database = original_database


def main() -> None:
    rejects: list[str] = []
    four_counterexamples(rejects)
    initial_state_bypass(rejects)
    c106 = baseline_valid_cases(rejects)
    result = {
        "status": "PASS_PRIVATE_P1_POLICY_CANDIDATE_NOT_CANONICAL",
        "four_previous_counterexamples_now_rejected": rejects[:4],
        "extra_initial_state_bypass_rejected": rejects[4],
        "all_rejected_moves": len(rejects),
        "c106_alternative_counts": c106,
        "limits": [
            "P1 active-observation policy is only an explicit trial; team must choose block versus traced withdrawal.",
            "SQLite triggers and rowid are a teaching control, not immutable audit or production authorization.",
            "No BPMN trace equivalence, concurrency, role permissions, privacy or real timestamps tested.",
        ],
    }
    assert len(result["four_previous_counterexamples_now_rejected"]) == 4
    assert len(rejects) == 29
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps({k: result[k] for k in ("status", "all_rejected_moves", "c106_alternative_counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
