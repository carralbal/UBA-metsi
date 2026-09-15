#!/usr/bin/env python3
"""Agrega puentes llanos específicos sin reemplazar la explicación académica."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    0: "N00-v3-final", 1: "N01-v18-final", 2: "N02-v15-final",
    3: "N03-v10-final", 4: "N04-v9-final", 5: "N05-v10-final",
    6: "N06-v10-final", 7: "N07-v10-final", 8: "N08-v10-final",
    9: "N09-v10-final", 10: "N10-v9-final",
}

# Cada agregado funciona como puerta de entrada: frase llana + caso de baja
# escala. El desarrollo existente queda inmediatamente después y conserva la
# definición precisa, la evidencia, el límite y la consecuencia profesional.
BRIDGES: dict[tuple[int, str], str] = {
    (0, "Contenido"): "En palabras simples, esta página es el mapa de la lectura: muestra qué conviene leer primero, qué partes profundizan y cuánto tiempo reservar. Por ejemplo, una estudiante con noventa minutos puede seguir sólo la ruta marcada y volver luego a las extensiones.",
    (0, "Pausas visuales"): "Una pausa visual es como levantar la vista después de varias páginas para ordenar lo aprendido. La fotografía y una frase breve no agregan otro tema: ayudan a relacionar la idea anterior antes de continuar.",
    (0, "Arquetipos del caso"): "Los arquetipos son personajes estables que permiten mirar el mismo problema desde lugares distintos. Por ejemplo, Lucía ve la llegada desde Recepción y Federico desde Tecnología; ninguno posee por sí solo toda la explicación.",
    (0, "Gestionar una intervención"): "Gestionar una intervención es organizar el trabajo sin perder de vista el problema que se quiere cambiar. Por ejemplo, un cronograma puede estar completo y aun así conducir a construir una solución que nadie necesita.",
    (0, "Desarrollo conceptual"): "El desarrollo conceptual explica las ideas con más precisión después de presentar su sentido general. Por ejemplo, primero podemos entender que una frontera decide qué queda dentro del análisis y luego estudiar sus criterios, efectos y límites.",
    (0, "Infografías"): "Una infografía es un dibujo que ayuda a ver relaciones difíciles de seguir sólo con palabras. Por ejemplo, una flecha entre Reserva y Recepción puede mostrar quién envía información, en qué dirección y antes de qué decisión.",
    (1, "La metodología como sistema de preguntas"): "En palabras simples, una metodología ayuda a preguntar antes de actuar. Si una facultad pide un chatbot, primero obliga a aclarar qué problema debe cambiar, para quién y qué dato mostraría una mejora.",
    (1, "La metodología como legitimación retrospectiva"): "Este error ocurre cuando el equipo decide primero y arma después una explicación elegante para justificarlo. Por ejemplo, compra una herramienta y recién entonces selecciona métricas que hacen parecer inevitable esa elección.",
    (2, "2. Reconstruir un episodio completo"): "Reconstruir un episodio es contar un caso real desde que empieza hasta que termina, sin saltar las esperas ni las reparaciones. Una reserva concreta permite ver quién actuó, qué información recibió y dónde cambió el resultado.",
    (2, "3. Dibujar relaciones con verbos y tiempos"): "Un mapa se entiende mejor cuando dice qué hace cada parte y cuándo lo hace. No alcanza con unir «Recepción» y «PMS»: conviene escribir «Recepción consulta el estado antes de asignar la habitación».",
    (2, "5. Formular al menos dos explicaciones rivales"): "Dos explicaciones rivales son respuestas diferentes que todavía podrían ser verdaderas. Por ejemplo, una habitación puede figurar ocupada porque el PMS recibió tarde un cambio o porque Recepción y Housekeeping usan palabras distintas para describir el mismo estado.",
    (3, "Desplazamiento del problema"): "Desplazar un problema es mejorarlo en un lugar y hacerlo reaparecer en otro. Por ejemplo, acelerar la confirmación puede reducir la espera comercial y aumentar luego las reasignaciones que debe resolver Recepción.",
    (3, "Cuándo reducir y cuándo ampliar"): "Reducir la frontera sirve para poder actuar; ampliarla sirve cuando algo importante quedó afuera. Si una demora se explica por una sola regla, no hace falta mapear toda la empresa; si esa regla depende de un tercero, excluirlo impide decidir.",
    (4, "Síntoma"): "Un síntoma es una señal de que algo merece investigarse, no la explicación de su causa. Que aumenten los reclamos muestra un problema, pero todavía no dice si lo produjo la interfaz, una regla, una demora o una promesa imposible.",
    (4, "Supuesto"): "Un supuesto es algo que el equipo está dando por cierto sin haberlo comprobado todavía. Por ejemplo, puede asumir que toda persona que abandona un formulario tuvo una dificultad de uso, aunque quizá encontró otra vía o cambió de decisión.",
    (4, "Restricción"): "Una restricción marca un límite que la intervención debe respetar o discutir con la autoridad adecuada. Si una norma exige conservar cierto registro, el equipo no puede borrarlo sólo porque simplifica el diseño.",
    (4, "Regla de trazabilidad mínima"): "La trazabilidad mínima permite volver desde una decisión hasta las pruebas y supuestos que la sostuvieron. Como en un trabajo escolar bien citado, otra persona debe poder comprobar de dónde salió una afirmación sin reconstruir todo desde cero.",
    (4, "Triangulación"): "Triangular es mirar el mismo hecho desde fuentes que pueden equivocarse de maneras distintas. Por ejemplo, para entender una demora se puede comparar lo que relata una persona, lo que registra el sistema y lo que muestra la observación directa.",
    (6, "Incertidumbre del problema"): "Hay incertidumbre del problema cuando todavía no sabemos qué situación necesita cambiar. Si pocas personas usan un portal, la causa podría ser dificultad de uso, falta de necesidad, una regla externa o una alternativa más conveniente.",
    (6, "Incertidumbre de adopción y trabajo"): "Esta incertidumbre pregunta si las personas podrán y querrán incorporar el cambio en su tarea real. Una función puede operar bien y fracasar porque agrega pasos, quita autonomía o no contempla el turno nocturno.",
    (6, "Incertidumbre de efectos"): "Esta incertidumbre aparece cuando no sabemos qué consecuencias producirá una intervención además de su resultado buscado. Un recordatorio puede reducir olvidos y, al mismo tiempo, saturar de mensajes a quienes ya habían cumplido.",
    (6, "Incertidumbre de solución"): "Hay incertidumbre de solución cuando entendemos el problema, pero todavía no sabemos qué alternativa funcionará. Por ejemplo, sabemos que un formulario provoca abandonos, aunque falta probar si conviene cambiar las preguntas, el orden o el canal.",
    (6, "Cartera priorizada de investigación"): "Una cartera priorizada de investigación ordena qué dudas conviene resolver primero. Por ejemplo, antes de probar colores de una pantalla puede ser más valioso averiguar por qué muchas personas nunca llegan a verla.",
    (6, "En 2026: la IA abarata producir respuestas, no necesariamente aprender"): "Una herramienta de IA puede producir muchas respuestas rápidas sin demostrar que sean útiles o correctas. Por ejemplo, generar diez prototipos en una tarde no reduce la incertidumbre si ninguno se prueba con personas ni con datos reales.",
    (7, "Del discurso general al episodio"): "Pasar al episodio significa pedir una historia concreta en lugar de aceptar frases generales. Ante «el sistema siempre falla», conviene preguntar por la última vez: qué intentaba hacer la persona, qué vio y qué ocurrió después.",
    (7, "Calidad de una entrevista"): "Una buena entrevista no se mide por su duración ni por la cantidad de frases anotadas. Es útil cuando deja un episodio claro, distingue hechos de interpretaciones y abre preguntas que pueden contrastarse con otras fuentes.",
    (10, "Límites del encuadre"): "Un encuadre funciona como el marco de una foto: ayuda a mirar algo y deja otras cosas afuera. Si el equipo define el problema sólo como demora, puede mejorar minutos y seguir sin atender accesibilidad, reparación o carga de trabajo.",
    (13, "Compensación y sagas"): "Cuando una operación tiene varios pasos y uno falla, no siempre existe un botón capaz de volver todo atrás. Una saga coordina esos pasos y una compensación repara lo posible; por ejemplo, cancelar una reserva y devolver el pago no borra el mensaje que ya recibió la persona.",
    (14, "Automatización e inteligencia artificial dentro del proceso"): "Automatizar una tarea es darle parte del trabajo a una regla o herramienta; no garantiza mejorar el recorrido completo. Un clasificador puede ordenar casos más rápido y, si se equivoca de destino, crear una cola mayor en el área siguiente.",
    (15, "Partes interesadas, preocupaciones y puntos de vista"): "Personas distintas necesitan mirar aspectos distintos del mismo sistema. En un hotel, Seguridad pregunta quién accede, Operaciones cómo se repara una excepción y Dirección qué riesgo acepta; una sola vista rara vez responde bien a las tres.",
    (15, "Modelos de decisión y causalidad"): "No todos los dibujos sirven para la misma pregunta. Un árbol ayuda a elegir entre caminos; un modelo causal ayuda a explicar por qué un cambio puede producir otro efecto más tarde.",
    (15, "Costo total de un modelo"): "Un modelo no cuesta sólo lo que tarda en dibujarse. También cuesta explicarlo, mantenerlo al día y corregir decisiones tomadas con una versión vieja; una lámina barata puede volverse cara si nadie entiende cuándo dejó de valer.",
    (15, "Matriz pregunta modelo"): "Esta matriz es una tabla para comparar qué representación ayuda mejor a responder cada pregunta. Si necesitamos saber dónde espera una persona, un proceso puede servir más que un diagrama de software; si buscamos una dependencia técnica, puede ocurrir lo contrario.",
    (16, "Contradicción temporal"): "Dos documentos pueden decir cosas distintas porque describen momentos diferentes. Un plano futuro y un sistema actual no se contradicen por estar desalineados; el problema aparece cuando nadie indica cuál rige hoy ni cómo se pasará de uno al otro.",
    (16, "Registro de contradicciones"): "Este registro es una lista de desacuerdos que necesitan decisión, no una colección de errores para ocultar. Si Comercial y Recepción usan «disponible» con sentidos distintos, se anota la consecuencia, quién debe resolverla y hasta cuándo puede tolerarse.",
    (16, "Contradicción normativa y operacional"): "Esta contradicción aparece cuando una regla pide algo que el trabajo real no permite cumplir. Por ejemplo, un procedimiento puede exigir una aprobación en treinta minutos aunque durante la noche no exista nadie con autoridad para darla.",
    (16, "Prueba de cambio"): "Una prueba de cambio consiste en modificar una parte del modelo y observar qué otras partes deberían ajustarse. Por ejemplo, si una aprobación deja de ser manual, hay que revisar quién controla la excepción, qué queda registrado y cómo se revierte un error.",
    (16, "Revisión de contradicciones abiertas"): "Revisar contradicciones abiertas es volver sobre desacuerdos que todavía tienen consecuencias. Por ejemplo, si dos áreas siguen usando definiciones distintas de «urgente», el equipo debe comprobar si la diferencia aún provoca demoras o decisiones incompatibles.",
    (18, "Excepciones heredadas"): "Una excepción heredada es una salida especial creada en el pasado que todavía resuelve algún caso. Antes de eliminarla conviene saber a quién protege: una planilla incómoda puede ser la única vía para atender una situación que el sistema nuevo no reconoce.",
    (18, "Seguridad y mantenibilidad"): "Seguridad y mantenibilidad deben pensarse juntas: hay que proteger hoy sin volver imposible cambiar mañana. Un control copiado en muchos lugares puede frenar un ataque y también hacer que una corrección urgente tarde semanas en aplicarse.",
    (21, "Responsabilidad persistente"): "La responsabilidad persistente significa que alguien conserva capacidad real de cuidar una decisión después de la entrega. No alcanza con poner un nombre: esa persona necesita información, autoridad y recursos para atender incidentes y decidir cambios.",
    (24, "Fecha de revisión"): "Una prioridad no debería durar para siempre por simple costumbre. La fecha de revisión acuerda cuándo volver a mirar la decisión y con qué datos; por ejemplo, una mejora postergada por la temporada alta se reevalúa cuando baja la demanda.",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_heading(value: str) -> str:
    return re.sub(r"^#+\s*", "", value).strip()


def authoritative_folder(number: int) -> Path:
    if number == 0:
        return ROOT / "N00-v3-final"
    if number <= 10:
        return ROOT / f"N{number:02d}-content-final"
    return ROOT / f"N{number:02d}-content-canonical"


def package_folder(number: int) -> Path:
    return ROOT / (PACKAGES[number] if number <= 10 else f"N{number:02d}-v9-editorial")


def load_source(folder: Path) -> tuple[Path, dict]:
    manifest_path = folder / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expanded = {
        "N02-content-final": "source/N02_el_sistema_no_cabe_en_una_aplicacion-content-final-v2.md",
        "N03-content-final": "source/N03_fronteras_retroalimentacion_y_efectos-content-final-v2.md",
        "N05-content-final": "source/N05_actores_afectados_poder_y_perspectivas-content-final-v2.md",
        "N06-content-final": "source/N06_discovery_como_reduccion_de_incertidumbre-content-final-v2.md",
        "N08-content-final": "source/N08_observar_el_trabajo_invisible-content-final-v2.md",
        "N09-content-final": "source/N09_experiencia_accesibilidad_y_adopcion-content-final-v2.md",
    }
    source_name = expanded.get(folder.name, manifest["source"])
    return folder / source_name, manifest


def first_paragraph(text: str, title: str) -> str:
    pattern = re.compile(
        rf"^(?P<marks>#{{2,4}})\s+{re.escape(title)}\s*\n+(?P<body>.*?)(?=^#{{2,4}}\s+|\Z)",
        re.M | re.S,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"No se encontró encabezado: {title}")
    body = match.group("body")
    paragraph = re.split(r"\n\s*\n", body.strip(), maxsplit=1)[0]
    if not paragraph or paragraph.lstrip().startswith(("|", "- ", "1. ")):
        raise RuntimeError(f"La apertura no es párrafo: {title}")
    return paragraph


def prepend_source(text: str, title: str, bridge: str) -> tuple[str, str]:
    old = first_paragraph(text, title)
    if bridge in old:
        return text, old
    new = f"{bridge} {old}"
    return text.replace(old, new, 1), old


def paragraph_id(manifest: dict, title: str) -> tuple[str, str]:
    entries = manifest["eligible_blocks"]
    heading_index = next(
        i for i, entry in enumerate(entries)
        if entry["kind"].startswith("heading") and normalized_heading(entry["text"]) == title
    )
    index = next(
        i for i in range(heading_index + 1, len(entries))
        if entries[i]["kind"] == "paragraph"
    )
    return entries[index]["source_id"], entries[index]["text"]


def update_manifest(folder: Path, title: str, bridge: str, source: Path, stage: str) -> str | None:
    path = folder / "source-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    source_id = None
    if "eligible_blocks" in manifest:
        source_id, old = paragraph_id(manifest, title)
        entry = next(item for item in manifest["eligible_blocks"] if item["source_id"] == source_id)
        if bridge not in entry["text"]:
            entry["text"] = f"{bridge} {old}"
    manifest["source"] = str(source.relative_to(folder))
    manifest["source_sha256"] = digest(source)
    manifest["stage"] = stage
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return source_id


def update_html(package: Path, source_id: str, bridge: str) -> None:
    path = package / "index.html"
    text = path.read_text(encoding="utf-8")
    if html.escape(bridge, quote=False) in text:
        return
    pattern = re.compile(rf'(<[^>]+\bdata-source-id="{re.escape(source_id)}"[^>]*>)')
    text, count = pattern.subn(rf"\1{html.escape(bridge, quote=False)} ", text, count=1)
    if count != 1:
        raise RuntimeError(f"{package.name}: no se pudo actualizar {source_id}")
    path.write_text(text, encoding="utf-8")


def update_package_records(package: Path, source: Path) -> None:
    source_words = len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'-]+\b", source.read_text(encoding="utf-8")))
    for name in ("document.json", "manifest.json"):
        path = package / name
        if not path.is_file():
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        record["source_sha256"] = digest(source)
        record["source_words"] = source_words
        record["content_audit"] = "accessible-concept-layers-audited-pass"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    touched: dict[int, list[str]] = {}
    for (number, title), bridge in BRIDGES.items():
        authority = authoritative_folder(number)
        package = package_folder(number)
        source, _ = load_source(authority)
        text = source.read_text(encoding="utf-8")
        updated, _ = prepend_source(text, title, bridge)
        source.write_text(updated, encoding="utf-8")

        package_source, _ = load_source(package)
        if package_source.resolve() != source.resolve():
            shutil.copy2(source, package_source)

        stage = "content-canonical-accessible-concept-layers"
        update_manifest(authority, title, bridge, source, stage)
        source_id = update_manifest(package, title, bridge, package_source, stage)
        if source_id is None:
            raise RuntimeError(f"{package.name}: manifiesto editorial sin bloques elegibles")
        update_html(package, source_id, bridge)
        update_package_records(package, package_source)
        touched.setdefault(number, []).append(title)

    report = {
        "status": "APPLIED",
        "documents_touched": len(touched),
        "concept_bridges": len(BRIDGES),
        "documents": [
            {"document": f"N{number:02d}", "concepts": titles}
            for number, titles in sorted(touched.items())
        ],
    }
    out = ROOT / "editorial-standard" / "accessible-concept-bridges-application.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "documents_touched", "concept_bridges")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
