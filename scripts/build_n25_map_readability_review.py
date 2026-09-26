#!/usr/bin/env python3
"""Build an isolated infographic review; never replace an approved asset or PDF."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pedagogy/readability-pilots/N25/mapa-legible"
SOURCE = ROOT / "pedagogy/readability-pilots/N25/N25-lectura-pedagogica-v1.md"
parts = []
nodes = []
edges = []


def text(x, y, label, size=28, weight=400, anchor="start", serif=False):
    family = "Georgia,serif" if serif else "Arial,Helvetica,sans-serif"
    parts.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#202020">{html.escape(label)}</text>')


def path(d, arrow=False, dash=False):
    parts.append(f'<path d="{d}" fill="none" stroke="#777A76" stroke-width="2"' + (' marker-end="url(#arrow)"' if arrow else '') + (' stroke-dasharray="5 7"' if dash else '') + '/>')


def group(identifier, label, source, purpose, draw):
    nodes.append(dict(id=identifier, label=label, role="process", source=[source], purpose=purpose))
    parts.append(f'<g id="{identifier}" aria-label="{html.escape(label)}">')
    draw()
    parts.append('</g>')


def flow(identifier, y, labels, source, feedback=False):
    centers = [145, 373, 600, 827, 1055]
    for i in range(4):
        path(f'M{centers[i]+36} {y} H{centers[i+1]-42}', True)
        edges.append(dict(id=f"{identifier}-e{i}", **{"from":f"{identifier}-{i}", "to":f"{identifier}-{i+1}"}, relation="flow", source=[source], meaning="El paso anterior conduce al siguiente; se conserva el mismo cambio." if not feedback else "La información permite pasar a la acción siguiente."))
    if feedback:
        path(f'M1089 {y} H1180 V1430 H20 V{y} H109', True, True)
        edges.append(dict(id="revisar-efecto", **{"from":f"{identifier}-4", "to":f"{identifier}-0"}, relation="feedback", source=[source], meaning="El efecto observado puede generar una nueva señal para revisar la decisión."))
    for i, (a,b) in enumerate(labels):
        x = centers[i]
        def draw(x=x, i=i, a=a, b=b):
            parts.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{"#CFFF00" if i==0 else "#F7F6F2"}" stroke="#202020" stroke-width="2"/>')
            text(x,y+10,f"{i+1:02d}",28,700,"middle")
            text(x,y+68,a,28,700,"middle")
            text(x,y+102,b,28,400,"middle")
        group(f"{identifier}-{i}",f"{a} {b}",source,"Hacer explícito un hito del recorrido.",draw)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    claim = "Para mejorar un cambio hay que seguirlo hasta su uso, distinguir trabajo de espera y comprobar qué cambia con la información recibida."
    alt = "Mapa en cuatro franjas. Primero sigue la misma modificación desde la demanda hasta el uso, con dos relojes: necesidad y compromiso. Después separa 46 días en 8 de trabajo y 38 de espera, desglosados en cuatro causas. Compara cuatro decisiones antes y después. Cierra con un circuito de señal, autoridad, decisión, cambio y efecto observado."
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1620" viewBox="0 0 1200 1620" role="img" aria-labelledby="title desc">')
    parts.append(f'<title id="title">N25 · Dónde espera un cambio</title><desc id="desc">{alt}</desc>')
    parts.append('<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#777A76"/></marker></defs><rect width="1200" height="1620" fill="#F7F6F2"/>')
    parts.append('<g id="encabezado"><path d="M52 36 H126 L116 52 H42 Z" fill="#CFFF00"/>')
    text(154,53,"METSI · N25 · MAPA DE DECISIÓN",24,700)
    text(52,118,"46 días para un cambio.",52,400,serif=True)
    text(52,182,"Sólo 8 fueron de trabajo.",52,400,serif=True)
    text(52,226,"Hotel Horizonte: una modificación del registro de reasignaciones.")
    path('M52 250 H1148')
    parts.append('</g>')
    text(52,293,"01   Seguir el mismo cambio hasta su uso",32,700)
    flow("recorrido",342,[("Demanda","reconocida"),("Definición","compartida"),("Cambio","integrado"),("Validación","en Operaciones"),("Capacidad","en uso")],"movimiento1")
    group("reloj-demanda","Desde la necesidad", "movimiento1", "No ocultar la espera anterior al compromiso.", lambda:text(52,493,"Desde la necesidad: cuánto espera quien pide el cambio."))
    group("reloj-compromiso","Desde el compromiso", "movimiento1", "Distinguir el tiempo de trabajo comprometido.", lambda:text(52,531,"Desde el compromiso: cuánto tarda el trabajo que el equipo aceptó."))
    path('M52 555 H1148')
    text(52,597,"02   Separar trabajo y espera",32,700)
    def metrics():
        text(52,663,"8",62,700)
        text(109,646,"días de trabajo",30,700)
        text(109,682,"Definir, construir, probar y corregir.",28)
        text(644,663,"38",62,700)
        text(731,646,"días de espera",30,700)
        text(731,682,"Cuatro causas por investigar.",28)
        # Exact relative lengths: 8/46 and 38/46, not decorative proportions.
        parts.append('<rect x="52" y="705" width="190.61" height="26" fill="#CFFF00"/><rect x="242.61" y="705" width="905.39" height="26" fill="#C9CBC8"/>')
        text(52,775,"9 días: definición pendiente")
        text(644,775,"12 días: ambiente no disponible")
        text(52,813,"11 días: revisión técnica")
        text(644,813,"6 días: validación de Operaciones")
    group("trabajo-espera","8 días de trabajo y 38 de espera","metodo","Separar la actividad de las cuatro colas observadas.",metrics)
    path('M52 843 H1148')
    text(52,885,"03   Cambiar cómo se organiza el trabajo",32,700)
    rows = [
        ("wip","Trabajo en curso","7 correcciones activas","3 correcciones activas"),
        ("validacion","Validación","Una vez por mes","Una vez por semana"),
        ("operaciones","Operaciones","Recibe contexto al final","Participa desde el diseño"),
        ("respuesta","Retroalimentación","El mensaje se envía","Cambia una regla o acción"),
    ]
    for index,(identifier,label,before,after) in enumerate(rows):
        y = 942 + index*73
        path(f'M754 {y-9} H798',True)
        text(52,y,label,28,700)
        group(identifier+"-antes",before,"hh25",f"{label}: práctica anterior.",lambda:text(381,y,before,28))
        group(identifier+"-despues",after,"hh25",f"{label}: intervención acordada.",lambda:text(824,y,after,28))
        edges.append(dict(id=identifier+"-cambio", **{"from":identifier+"-antes", "to":identifier+"-despues"},relation="transformation",source=["hh25"],meaning=f"{label}: cambio de práctica que el equipo prueba, no garantía universal de mejora."))
        path(f'M52 {y+26} H1148')
    text(52,1245,"04   Comprobar qué cambió después de escuchar",32,700)
    flow("circuito",1300,[("Señal","con contexto"),("Destinatario","con autoridad"),("Decisión","a tiempo"),("Regla o acción","modificada"),("Efecto","observado")],"movimiento3",True)
    group("limite","No toda espera debe eliminarse","limites","Conservar controles de seguridad, accesibilidad y calidad.",lambda:(text(52,1487,"No toda espera debe eliminarse.",30,700),text(52,1525,"Hay que reducir demoras sin quitar controles que protegen a las personas.")))
    path('M52 1551 H1148')
    text(52,1590,"Terminar más cambios no alcanza: tienen que funcionar en el servicio.",24)
    parts.append('</svg>')
    svg = '\n'.join(parts)
    (OUT/"N25-mapa-legible.svg").write_text(svg)
    sections = [
        ("hh25","Hotel Horizonte: el tiempo que el tablero no mostraba"),
        ("movimiento1","Movimiento 1 · Seguir la unidad de valor de punta a punta"),
        ("metodo","Instrumento HH-25: mapa de flujo real"),
        ("movimiento3","Movimiento 3 · Cerrar feedback y gobernar el flujo"),
        ("limites","Límites y tensiones"),
    ]
    # Preserve exact source headings, including later editorial revisions.
    headings = [line.lstrip('# ') for line in SOURCE.read_text().splitlines() if line.startswith('##')]
    for identifier,label in sections:
        if label not in headings:
            raise ValueError(f"Source heading not found: {label}")
    manifest = dict(title="Dónde espera un cambio",claim=claim,source=str(SOURCE.relative_to(ROOT)),source_sections=[dict(id=i,heading=h,summary=h) for i,h in sections],nodes=nodes,edges=edges,target_width_mm=176,minimum_content_font_px=28,minimum_content_font_pt=round(28*176/1200*72/25.4,2),status="REVIEW_NOT_INTEGRATED")
    (OUT/"content-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (OUT/"alt-text.md").write_text(alt+'\n')
    (OUT/"review.html").write_text('''<!doctype html><html lang="es-AR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>N25 · Mapa de decisión</title><style>body{margin:0;background:#dddcd7;font-family:Arial,sans-serif}main{max-width:900px;margin:28px auto;padding:24px;background:#fff}h1{font-size:22px}p{line-height:1.5}img{display:block;width:100%;height:auto}@media print{body{background:white}main{margin:0;padding:0}header{display:none}img{width:176mm}}</style><main><header><h1>N25 · Revisión de legibilidad</h1><p>Gráfico propuesto para una página vertical completa. Conserva el recorrido, los dos relojes, la distinción entre trabajo y espera, las cuatro intervenciones y el circuito de aprendizaje. Las explicaciones tienen un mínimo de 11,6 puntos a 176 mm de ancho.</p></header><img src="N25-mapa-legible.svg" alt="'''+html.escape(alt)+'''"></main></html>''')
    print(OUT)


if __name__ == '__main__':
    main()
