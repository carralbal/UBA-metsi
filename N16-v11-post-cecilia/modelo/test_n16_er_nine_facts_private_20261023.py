#!/usr/bin/env python3
"""Exercise the nine-fact N16 relational sketch with fictitious C-101…C-107.

This proves only specified SQLite constraints and triggers in a private teaching
model. It does not prove a production schema, BPMN equivalence, privacy, or a
choice between repair-by-episode and repair-by-attempt.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "ER-nueve-hechos-base.sql"
REPORT = ROOT / "QA-ER-nueve-hechos-private.json"
T0 = "2026-10-21T10:00:00+00:00"
T1 = "2026-10-21T11:00:00+00:00"
T2 = "2026-10-22T09:00:00+00:00"
T3 = "2026-10-23T11:00:00+00:00"


def database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(SCHEMA.read_text(encoding="utf8"))
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    return connection


def case(c: sqlite3.Connection, code: str, *, review: bool = True) -> tuple[str, str]:
    person, procedure = f"P-{code}", f"T-{code}"
    c.execute("INSERT INTO PERSONA VALUES (?)", (person,))
    c.execute("INSERT INTO TRAMITE(id_tramite,id_persona) VALUES (?,?)", (procedure, person))
    if review:
        change(c, code, procedure, "Recibido", "En revisión")
    return person, procedure


def change(c: sqlite3.Connection, code: str, procedure: str, before: str, after: str) -> None:
    n = c.execute("SELECT count(*) FROM CAMBIO_ESTADO WHERE id_tramite=?", (procedure,)).fetchone()[0]
    c.execute("INSERT INTO CAMBIO_ESTADO VALUES (?,?,?,?,?,?)",
              (f"CE-{code}-{n + 1}", procedure, before, after, T3, "Mesa"))


def observation(c: sqlite3.Connection, oid: str, procedure: str) -> None:
    c.execute("INSERT INTO OBSERVACION(id_observacion,id_tramite) VALUES (?,?)", (oid, procedure))


def decision(c: sqlite3.Connection, did: str, procedure: str) -> None:
    c.execute("INSERT INTO DECISION VALUES (?,?,?,?)", (did, procedure, "Aprobada", T0))


def notice(c: sqlite3.Connection, nid: str, procedure: str, person: str, *,
           obj: str, purpose: str = "OBSERVACION", delivered: bool = False,
           delivered_at: str = T2) -> None:
    c.execute("INSERT INTO AVISO VALUES (?,?,?,?,?,?,?,?,?,?)", (
        nid, procedure, person, purpose,
        obj if purpose == "OBSERVACION" else None,
        obj if purpose == "DECISION" else None,
        "humano" if delivered else "digital", T0,
        "ENTREGADO" if delivered else "FALLIDO",
        delivered_at if delivered else None,
    ))


def repair(c: sqlite3.Connection, rid: str, procedure: str, person: str, *,
           obj: str, failed: str, policy: str = "EPISODIO", purpose: str = "OBSERVACION") -> None:
    c.execute("""INSERT INTO REPARACION
        (id_reparacion,id_tramite,id_destinatario,finalidad,id_observacion,id_decision,
         politica,id_aviso_fallido_inicial,responsable,fecha_apertura)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            rid, procedure, person, purpose,
            obj if purpose == "OBSERVACION" else None,
            obj if purpose == "DECISION" else None,
            policy, failed, "Mesa", T0,
        ))


def close(c: sqlite3.Connection, rid: str, delivered: str) -> None:
    c.execute("""UPDATE REPARACION SET estado='CERRADA',id_aviso_cierre=?,fecha_cierre=?
                 WHERE id_reparacion=?""", (delivered, T3, rid))


def rejects(label: str, action, checks: list[str]) -> None:
    try:
        action()
    except sqlite3.IntegrityError:
        checks.append(label)
    else:
        raise AssertionError(f"Accepted invalid case: {label}")


def scenario_101(checks: list[str]) -> None:
    c = database()
    person, tr = case(c, "101")
    rejects("C101_resuelto_sin_decision", lambda: change(c, "101", tr, "En revisión", "Resuelto"), checks)
    decision(c, "D-101", tr)
    rejects("C101_firma_sin_entrega", lambda: change(c, "101", tr, "En revisión", "Resuelto"), checks)
    notice(c, "A-101", tr, person, obj="D-101", purpose="DECISION", delivered=True)
    change(c, "101", tr, "En revisión", "Resuelto")
    assert c.execute("SELECT estado_actual FROM TRAMITE WHERE id_tramite=?", (tr,)).fetchone()[0] == "Resuelto"
    assert c.execute("SELECT count(*) FROM CAMBIO_ESTADO WHERE id_tramite=?", (tr,)).fetchone()[0] == 2
    c.close()


def scenario_102(checks: list[str]) -> None:
    c = database()
    person, tr = case(c, "102")
    observation(c, "O-102", tr)
    args = ("R-102", tr, "O-102", person, T2, "DOC-102", "web", "TRY-102")
    rejects("C102_respuesta_antes_de_entrega", lambda: c.execute(
        "INSERT INTO RESPUESTA VALUES (?,?,?,?,?,?,?,?)", args), checks)
    notice(c, "A-102", tr, person, obj="O-102", delivered=True)
    change(c, "102", tr, "En revisión", "Requiere acción")
    c.execute("INSERT INTO RESPUESTA VALUES (?,?,?,?,?,?,?,?)", args)
    rejects("C102_reenvio_idempotente_duplica", lambda: c.execute(
        "INSERT INTO RESPUESTA VALUES (?,?,?,?,?,?,?,?)", ("R-102-dup", *args[1:])), checks)
    change(c, "102", tr, "Requiere acción", "En revisión")
    c.execute("UPDATE OBSERVACION SET estado='CONTESTADA' WHERE id_observacion='O-102'")
    assert c.execute("SELECT count(*) FROM RESPUESTA").fetchone()[0] == 1
    c.close()


def scenario_103(checks: list[str]) -> None:
    c = database()
    person, tr = case(c, "103")
    observation(c, "O-103", tr)
    notice(c, "A-103-f", tr, person, obj="O-103")
    rejects("C103_fallo_no_habilita_estado", lambda: change(c, "103", tr, "En revisión", "Requiere acción"), checks)
    repair(c, "RP-103", tr, person, obj="O-103", failed="A-103-f")
    rejects("C103_fallo_no_cierra_reparacion", lambda: close(c, "RP-103", "A-103-f"), checks)
    notice(c, "A-103-h", tr, person, obj="O-103", delivered=True)
    close(c, "RP-103", "A-103-h")
    change(c, "103", tr, "En revisión", "Requiere acción")
    assert c.execute("SELECT count(*) FROM REPARACION_AVISO WHERE id_reparacion='RP-103'").fetchone()[0] == 2
    c.close()


def scenario_104(checks: list[str]) -> None:
    c = database()
    _, tr = case(c, "104", review=False)
    rejects("C104_baja_sin_registro", lambda: change(c, "104", tr, "Recibido", "Baja registrada"), checks)
    c.execute("INSERT INTO BAJA VALUES (?,?,?,?)", ("B-104", tr, T1, "Titular"))
    change(c, "104", tr, "Recibido", "Baja registrada")
    rejects("C104_baja_no_es_resuelto", lambda: change(c, "104", tr, "Baja registrada", "Resuelto"), checks)
    c.close()


def scenario_105(checks: list[str]) -> None:
    c = database()
    person, tr = case(c, "105")
    decision(c, "D-105", tr)
    notice(c, "A-105-f", tr, person, obj="D-105", purpose="DECISION")
    repair(c, "RP-105", tr, person, obj="D-105", failed="A-105-f", purpose="DECISION")
    rejects("C105_envio_fallido_no_resuelve", lambda: change(c, "105", tr, "En revisión", "Resuelto"), checks)
    notice(c, "A-105-h", tr, person, obj="D-105", purpose="DECISION", delivered=True)
    close(c, "RP-105", "A-105-h")
    change(c, "105", tr, "En revisión", "Resuelto")
    c.close()


def scenario_106(policy: str, checks: list[str]) -> dict:
    c = database()
    person, tr = case(c, f"106-{policy}")
    obs = f"O-106-{policy}"
    observation(c, obs, tr)
    first, second, third = (f"A-106-{policy}-{n}" for n in (1, 2, 3))
    notice(c, first, tr, person, obj=obs)
    notice(c, second, tr, person, obj=obs)
    rejects(f"C106_{policy}_dos_fallos_no_habilitan_estado",
            lambda: change(c, f"106-{policy}", tr, "En revisión", "Requiere acción"), checks)
    first_r = f"RP-106-{policy}-1"
    repair(c, first_r, tr, person, obj=obs, failed=first, policy=policy)
    if policy == "EPISODIO":
        rejects("C106_episodio_no_duplica_reparacion_activa",
                lambda: repair(c, f"RP-106-{policy}-2", tr, person, obj=obs, failed=second, policy=policy), checks)
        c.execute("INSERT INTO REPARACION_AVISO VALUES (?,?)", (first_r, second))
        repair_ids = [first_r]
    else:
        rejects("C106_intento_no_agrega_segundo_fallo_a_misma_reparacion",
                lambda: c.execute("INSERT INTO REPARACION_AVISO VALUES (?,?)", (first_r, second)), checks)
        second_r = f"RP-106-{policy}-2"
        repair(c, second_r, tr, person, obj=obs, failed=second, policy=policy)
        repair_ids = [first_r, second_r]
    notice(c, third, tr, person, obj=obs, delivered=True, delivered_at=T3)
    for rid in repair_ids:
        rejects(f"C106_{policy}_{rid}_fallo_no_cierra", lambda rid=rid: close(c, rid, first), checks)
        close(c, rid, third)
        rejects(f"C106_{policy}_{rid}_cierre_doble", lambda rid=rid: close(c, rid, third), checks)
    change(c, f"106-{policy}", tr, "En revisión", "Requiere acción")
    counts = {
        "tramites": c.execute("SELECT count(*) FROM TRAMITE").fetchone()[0],
        "avisos": c.execute("SELECT count(*) FROM AVISO").fetchone()[0],
        "reparaciones": c.execute("SELECT count(*) FROM REPARACION").fetchone()[0],
        "reparaciones_abiertas": c.execute("SELECT count(*) FROM REPARACION WHERE estado='ABIERTA'").fetchone()[0],
    }
    assert counts == {"tramites": 1, "avisos": 3, "reparaciones": 1 if policy == "EPISODIO" else 2,
                      "reparaciones_abiertas": 0}
    c.close()
    return counts


def scenario_107(checks: list[str]) -> None:
    c = database()
    person, tr = case(c, "107")
    observation(c, "O-107-a", tr)
    notice(c, "A-107-a-f", tr, person, obj="O-107-a")
    repair(c, "RP-107-a", tr, person, obj="O-107-a", failed="A-107-a-f")
    notice(c, "A-107-a-h", tr, person, obj="O-107-a", delivered=True)
    change(c, "107", tr, "En revisión", "Requiere acción")
    c.execute("INSERT INTO RESPUESTA VALUES (?,?,?,?,?,?,?,?)",
              ("R-107-a", tr, "O-107-a", person, T2, "DOC-107", "humano", "TRY-107"))
    change(c, "107", tr, "Requiere acción", "En revisión")
    c.execute("UPDATE OBSERVACION SET estado='CONTESTADA' WHERE id_observacion='O-107-a'")
    observation(c, "O-107-b", tr)
    notice(c, "A-107-b-h", tr, person, obj="O-107-b", delivered=True)
    rejects("C107_aviso_otra_observacion_no_cierra", lambda: close(c, "RP-107-a", "A-107-b-h"), checks)
    rejects("C107_aviso_otra_observacion_no_vincula", lambda: c.execute(
        "INSERT INTO REPARACION_AVISO VALUES (?,?)", ("RP-107-a", "A-107-b-h")), checks)
    close(c, "RP-107-a", "A-107-a-h")
    # Same person does not make an observation from another procedure eligible.
    c.execute("INSERT INTO TRAMITE(id_tramite,id_persona) VALUES (?,?)", ("T-107-otro", person))
    rejects("C107_observacion_de_otro_tramite", lambda: notice(
        c, "A-107-cross", "T-107-otro", person, obj="O-107-a", delivered=True), checks)
    c.execute("INSERT INTO PERSONA VALUES ('P-107-otro')")
    rejects("C107_destinatario_ajeno", lambda: notice(
        c, "A-107-wrong-person", tr, "P-107-otro", obj="O-107-b", delivered=True), checks)
    rejects("C107_finalidad_sin_objeto_exclusivo", lambda: c.execute(
        "INSERT INTO AVISO VALUES (?,?,?,?,?,?,?,?,?,?)",
        ("A-107-no-target", tr, person, "OBSERVACION", None, None, "digital", T0, "FALLIDO", None)), checks)
    c.close()


def main() -> None:
    checks: list[str] = []
    for fn in (scenario_101, scenario_102, scenario_103, scenario_104, scenario_105):
        fn(checks)
    c106 = {policy: scenario_106(policy, checks) for policy in ("EPISODIO", "INTENTO")}
    scenario_107(checks)
    result = {
        "status": "PASS_PRIVATE_SQLITE_SKETCH_NOT_PRODUCTION",
        "scenario_families": ["C-101", "C-102", "C-103", "C-104", "C-105", "C-106-A", "C-106-B", "C-107"],
        "rejected_invalid_moves": len(checks),
        "rejections": checks,
        "c106_counts": c106,
        "limits": [
            "No docente review or student timing; no chosen repair policy.",
            "Direct manual update of TRAMITE bypasses the transition API in this teaching sketch.",
            "No concurrency, privacy, accessibility, retention or operational database proof.",
        ],
    }
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps({k: result[k] for k in ("status", "scenario_families", "rejected_invalid_moves", "c106_counts")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
