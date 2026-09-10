#!/usr/bin/env python3
"""Build source-grounded, bespoke METSI infographics for N12 through N36."""

from __future__ import annotations

import html
import json
import math
import re
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "editorial-standard" / "infographic-rebuild-candidates-v2"
OUT = ROOT / "editorial-standard" / "infographic-rebuild-candidates-v3"
VALIDATOR = Path("/Users/diegocarralbal/.codex/skills/metsi-build-reference-grade-infographics/scripts/validate_infographic.py")

PAPER = "#F6F4EE"
WHITE = "#FFFFFF"
INK = "#272525"
MID = "#4D4D4D"
TILE = "#E6E6E6"
BORDER = "#CCCCCC"
VOLT = "#CFFF00"

LAYOUTS = {
    "N12": "split",
    "N13": "converge",
    "N14": "service",
    "N15": "lens",
    "N16": "contradiction",
    "N17": "braid",
    "N18": "strata",
    "N19": "comparison",
    "N20": "gates",
    "N21": "governance",
    "N22": "hypothesis",
    "N23": "slice",
    "N24": "portfolio",
    "N25": "flowboard",
    "N26": "ecosystem",
    "N27": "strata",
    "N28": "scenario_matrix",
    "N29": "recovery",
    "N30A": "dashboard",
    "N30B": "incident_loop",
    "N31": "decision_tree",
    "N32": "permission_matrix",
    "N33": "lifecycle",
    "N34": "bidirectional",
    "N35": "argument",
    "N36": "double_loop",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap(value: str, chars: int) -> list[str]:
    return textwrap.wrap(" ".join(value.split()), width=chars, break_long_words=False, break_on_hyphens=False) or [""]


def text(x: float, y: float, value: str, size: int = 24, weight: int = 500,
         chars: int = 28, anchor: str = "start", color: str = INK,
         line_height: float = 1.22) -> str:
    rows = wrap(value, chars)
    spans = []
    for i, row in enumerate(rows):
        dy = 0 if i == 0 else size * line_height
        spans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{esc(row)}</tspan>')
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Inter, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">'
            + "".join(spans) + "</text>")


def path(d: str, dotted: bool = False, arrow: bool = True, color: str = BORDER, width: float = 3) -> str:
    dash = ' stroke-dasharray="7 9"' if dotted else ""
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}{marker}/>'


def card(i: int, label: str, x: float, y: float, w: float, h: float,
         fill: str = WHITE, shape: str = "rect", chars: int | None = None) -> str:
    char_width = chars or max(14, int(w / 14))
    if shape == "diamond":
        pts = f"{x+w/2:.1f},{y:.1f} {x+w:.1f},{y+h/2:.1f} {x+w/2:.1f},{y+h:.1f} {x:.1f},{y+h/2:.1f}"
        obj = f'<polygon points="{pts}" fill="{fill}" stroke="{MID}" stroke-width="2"/>'
        tx, ty, anchor = x + w / 2, y + h / 2 - 8, "middle"
    elif shape == "circle":
        r = min(w, h) / 2
        obj = f'<circle cx="{x+w/2:.1f}" cy="{y+h/2:.1f}" r="{r:.1f}" fill="{fill}" stroke="{MID}" stroke-width="2"/>'
        tx, ty, anchor = x + w / 2, y + h / 2 - 8, "middle"
    elif shape == "cut":
        pts = f"{x:.1f},{y:.1f} {x+w-22:.1f},{y:.1f} {x+w:.1f},{y+22:.1f} {x+w:.1f},{y+h:.1f} {x:.1f},{y+h:.1f}"
        obj = f'<polygon points="{pts}" fill="{fill}" stroke="{MID}" stroke-width="2"/>'
        tx, ty, anchor = x + 22, y + 55, "start"
    else:
        obj = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{fill}" stroke="{MID}" stroke-width="2"/>'
        tx, ty, anchor = x + 22, y + 55, "start"
    number = text(x + 18, y + 26, f"{i:02d}", 18, 800, 4, color=MID) if shape not in {"diamond", "circle"} else text(x+w/2, y+30, f"{i:02d}", 18, 800, 4, anchor="middle", color=MID)
    label_text = text(tx, ty, label, 23, 700, char_width, anchor=anchor)
    port = f'<circle cx="{x+w-10:.1f}" cy="{y+10:.1f}" r="6" fill="{VOLT}" stroke="{MID}" stroke-width="1.5"/>'
    return f'<g id="n{i}">{obj}{number}{label_text}{port}</g>'


def layer(i: int, label: str, x: float, y: float, w: float, depth: float = 38) -> str:
    top = f"{x:.1f},{y:.1f} {x+w:.1f},{y:.1f} {x+w+depth:.1f},{y+depth:.1f} {x+depth:.1f},{y+depth:.1f}"
    face = f"{x+depth:.1f},{y+depth:.1f} {x+w+depth:.1f},{y+depth:.1f} {x+w+depth:.1f},{y+depth+54:.1f} {x+depth:.1f},{y+depth+54:.1f}"
    side = f"{x+w:.1f},{y:.1f} {x+w+depth:.1f},{y+depth:.1f} {x+w+depth:.1f},{y+depth+54:.1f} {x+w:.1f},{y+54:.1f}"
    return (f'<g id="n{i}"><polygon points="{top}" fill="{WHITE if i%2 else TILE}" stroke="{MID}" stroke-width="2"/>'
            f'<polygon points="{face}" fill="{TILE}" stroke="{MID}" stroke-width="2"/>'
            f'<polygon points="{side}" fill="{BORDER}" stroke="{MID}" stroke-width="2"/>'
            f'{text(x+depth+20,y+depth+36,label,23,700,35)}'
            f'{text(x-54,y+34,f"{i:02d}",18,800,4,color=MID)}</g>')


def line_edges(pairs: list[tuple[int, int]], relation: str = "flow") -> list[dict]:
    return [{"id": f"e{k}", "from": f"n{a}", "to": f"n{b}", "relation": relation,
             "source": ["s1"], "meaning": f"{relation}: {a} hacia {b}"}
            for k, (a, b) in enumerate(pairs, 1)]


def layout_split(items):
    pos = [(90,330),(90,650),(650,420),(650,650),(1230,330),(1230,650)]
    connectors = [path("M 410 400 H 650"), path("M 410 720 H 650", dotted=True),
                  path("M 970 490 H 1230"), path("M 970 720 H 1230", dotted=True),
                  path("M 810 540 V 650"), path("M 1390 500 V 650", dotted=True)]
    nodes = [card(i+1,it["title"],*pos[i],320,150,TILE if i in {1,2,4} else WHITE) for i,it in enumerate(items)]
    extra = [f'<path d="M 590 275 V 865" stroke="{VOLT}" stroke-width="14"/>',
             text(595,890,"EVENTO",18,800,10), text(975,890,"ESTADO Y AUTORIDAD",18,800,22)]
    return connectors + nodes + extra, line_edges([(1,3),(2,4),(3,5),(4,6),(3,4),(5,6)], "authority")


def layout_converge(items):
    ys=[290,510,730]
    connectors=[path(f"M 420 {y+70} C 560 {y+70}, 600 555, 735 555", dotted=i>0) for i,y in enumerate(ys)]
    connectors += [path("M 1015 555 C 1120 555, 1140 410, 1260 410"), path("M 1015 555 C 1120 555, 1140 700, 1260 700"), path("M 1450 770 C 1110 940, 760 920, 735 625", dotted=True)]
    nodes=[card(i+1,items[i]["title"],90,ys[i],330,140,TILE if i==1 else WHITE) for i in range(3)]
    nodes += [card(4,items[3]["title"],735,450,280,210,WHITE,"diamond",20), card(5,items[4]["title"],1260,330,430,160,TILE), card(6,items[5]["title"],1260,620,430,160,WHITE)]
    return connectors+nodes+[text(735,330,"CONVERGENCIA DE INTENCIÓN",19,800,30)], line_edges([(1,4),(2,4),(3,4),(4,5),(4,6),(6,4)],"transformation")


def layout_service(items):
    xs=[70,350,630,910,1190,1470]; y=500
    connectors=[path(f"M {xs[i]+220} 580 H {xs[i+1]}") for i in range(5)]
    connectors += [path("M 1020 690 C 1020 865, 500 865, 500 690",dotted=True), path("M 1580 690 V 860 H 1320",dotted=True)]
    nodes=[card(i+1,it["title"],xs[i],y-(70 if i%2==0 else -30),220,190,TILE if i in {2,5} else WHITE,chars=16) for i,it in enumerate(items)]
    return connectors+nodes+[text(80,900,"COLA Y EXCEPCIÓN",19,800,24),text(1400,900,"REPARACIÓN",19,800,18)], line_edges([(1,2),(2,3),(3,4),(4,5),(5,6),(4,2),(6,5)],"flow")


def layout_lens(items):
    connectors=[path("M 470 560 H 680",color=VOLT,width=6),path("M 890 560 H 1090",color=VOLT,width=6)]
    around=[(640,260),(980,260),(640,700),(980,700)]
    connectors += [path(f"M 790 520 L {x+150} {y+75}",dotted=True) for x,y in around]
    connectors += [path(f"M {x+300} {y+75} C 1120 {y+75}, 1110 560, 1260 560",dotted=True) for x,y in around[1::2]]
    nodes=[card(1,items[0]["title"],100,450,370,210,TILE,"cut",24)]
    nodes += [card(i+2,items[i+1]["title"],*around[i],300,150,WHITE if i%2 else TILE) for i in range(4)]
    nodes += [card(6,items[5]["title"],1260,450,440,220,WHITE,"diamond",24)]
    return connectors+nodes+[f'<circle cx="790" cy="560" r="105" fill="{WHITE}" stroke="{MID}" stroke-width="3"/>',text(790,548,"LENTE",30,800,10,"middle"),text(790,590,"DE ANÁLISIS",20,800,14,"middle")], line_edges([(1,2),(1,3),(1,4),(1,5),(2,6),(3,6),(4,6),(5,6)],"evidence")


def layout_contradiction(items):
    ys=[290,510,730]
    connectors=[path(f"M 430 {y+70} C 610 {y+70}, 590 555, 750 555",dotted=True) for y in ys]
    connectors += [path("M 1010 555 H 1260"),path("M 1010 555 C 1140 555, 1120 750, 1260 750"),path("M 1480 820 C 1280 940, 880 930, 880 675",dotted=True)]
    nodes=[card(i+1,items[i]["title"],90,ys[i],340,140,TILE if i==1 else WHITE) for i in range(3)]
    nodes += [card(4,items[3]["title"],750,425,260,260,WHITE,"circle",20),card(5,items[4]["title"],1260,380,430,170,TILE),card(6,items[5]["title"],1260,670,430,170,WHITE)]
    return connectors+nodes+[text(750,330,"MISMO EPISODIO",19,800,22)],line_edges([(1,4),(2,4),(3,4),(4,5),(4,6),(6,4)],"evidence")


def layout_braid(items):
    ys=[300,440,580,720]
    connectors=[]
    for i,y in enumerate(ys):
        mid=470+(i%2)*90
        connectors.append(path(f"M 390 {y+55} C 600 {y+55}, {mid} 520, 900 570",dotted=i%2==1,width=4))
    connectors += [path("M 1120 570 H 1370"),path("M 1580 650 C 1330 900, 820 900, 900 680",dotted=True)]
    nodes=[card(i+1,items[i]["title"],80,ys[i],310,110,TILE if i%2 else WHITE,chars=22) for i in range(4)]
    nodes += [card(5,items[4]["title"],900,450,220,240,WHITE,"diamond",20),card(6,items[5]["title"],1370,455,350,210,TILE,"cut",23)]
    return connectors+nodes+[text(650,280,"CUATRO LÓGICAS",19,800,24),text(1420,750,"CONDICIÓN DE SALIDA",19,800,28)],line_edges([(1,5),(2,5),(3,5),(4,5),(5,6),(6,5)],"dependency")


def layout_strata(items):
    connectors=[]; nodes=[]
    for i,it in enumerate(items):
        x=260+i*70; y=760-i*88; w=780-i*35
        nodes.append(layer(i+1,it["title"],x,y,w))
        connectors.append(path(f"M {x+w+50} {y+40} H 1490",dotted=True,arrow=False))
    nodes.append(f'<g id="spine"><path d="M 220 820 L 680 240" stroke="{VOLT}" stroke-width="16"/><circle cx="220" cy="820" r="10" fill="{VOLT}"/></g>')
    return connectors+nodes+[text(1450,250,"CAPACIDAD CONSERVADA",20,800,28,"end")],line_edges([(1,2),(2,3),(3,4),(4,5),(5,6)],"dependency")


def layout_comparison(items):
    connectors=[path("M 900 360 V 430",color=VOLT,width=6)]
    xs=[90,500,910,1320]
    connectors += [path(f"M 900 360 C 900 400, {x+165} 400, {x+165} 450",dotted=True) for x in xs]
    connectors += [path(f"M {x+165} 650 V 800 H 900",dotted=i%2==0) for i,x in enumerate(xs)]
    nodes=[card(1,items[0]["title"],480,250,840,120,TILE,"cut",48)]
    nodes += [card(i+2,items[i+1]["title"],xs[i],450,330,200,WHITE if i%2 else TILE,chars=22) for i in range(4)]
    nodes += [card(6,items[5]["title"],650,800,500,130,WHITE,"diamond",30)]
    return connectors+nodes+[text(900,720,"MISMA PRUEBA",20,800,18,"middle")],line_edges([(1,2),(1,3),(1,4),(1,5),(2,6),(3,6),(4,6),(5,6)],"evidence")


def layout_gates(items):
    xs=[110,650,1190]
    connectors=[path("M 430 480 H 650"),path("M 970 480 H 1190"),path("M 810 620 V 780",dotted=True),path("M 1350 620 V 780",dotted=True)]
    nodes=[]
    for i,x in enumerate(xs):
        nodes.append(card(i+1,items[i]["title"],x,390,320,180,TILE if i==1 else WHITE,"cut",22))
    nodes += [card(4,items[3]["title"],650,750,320,150,WHITE),card(5,items[4]["title"],1190,750,320,150,TILE),card(6,items[5]["title"],1490,390,230,180,WHITE,"diamond",16)]
    connectors += [path("M 1510 480 H 1490"),path("M 1510 825 H 1605 V 570",dotted=True)]
    return connectors+nodes+[text(270,330,"HITO 01",18,800,12,"middle"),text(810,330,"HITO 02",18,800,12,"middle"),text(1350,330,"HITO 03",18,800,12,"middle")],line_edges([(1,2),(2,3),(3,6),(2,4),(3,5),(5,6)],"decision")


def layout_governance(items):
    around=[(90,300),(90,700),(1240,300),(1240,700)]
    connectors=[path(f"M {x+(360 if x<900 else 0)} {y+80} L 900 555",dotted=True) for x,y in around]
    connectors += [path("M 900 675 V 820",color=VOLT,width=5),path("M 1210 870 H 1510",dotted=True)]
    nodes=[card(1,items[0]["title"],650,390,500,290,TILE,"diamond",30)]
    nodes += [card(i+2,items[i+1]["title"],*around[i],360,160,WHITE if i%2 else TILE) for i in range(4)]
    nodes += [card(6,items[5]["title"],590,820,620,120,WHITE,"cut",38)]
    return connectors+nodes+[text(900,300,"CUATRO GOBIERNOS",20,800,24,"middle")],line_edges([(2,1),(3,1),(4,1),(5,1),(1,6)],"authority")


def layout_hypothesis(items):
    connectors=[path("M 390 540 H 610"),path("M 910 540 C 1040 540, 1040 370, 1180 370"),path("M 910 540 C 1040 540, 1040 710, 1180 710"),path("M 1500 370 C 1600 370,1600 540,1510 540"),path("M 1500 710 C 1600 710,1600 540,1510 540"),path("M 1510 540 H 1610"),path("M 1700 620 C 1480 920, 760 920, 760 650",dotted=True)]
    nodes=[card(1,items[0]["title"],80,450,310,180,TILE),card(2,items[1]["title"],610,430,300,220,WHITE,"diamond",22),card(3,items[2]["title"],1180,290,320,160,TILE),card(4,items[3]["title"],1180,630,320,160,WHITE),card(5,items[4]["title"],1510,450,190,180,WHITE,"diamond",16),card(6,items[5]["title"],610,780,520,130,TILE,"cut",34)]
    return connectors+nodes+[text(1340,255,"APOYO",18,800,10,"middle"),text(1340,825,"CONTRADICCIÓN",18,800,18,"middle")],line_edges([(1,2),(2,3),(2,4),(3,5),(4,5),(5,6),(6,2)],"evidence")


def layout_slice(items):
    connectors=[]; nodes=[]
    for i in range(3):
        y=320+i*170
        nodes.append(card(i+1,items[i]["title"],90,y,1050,125,TILE if i%2 else WHITE,"cut",55))
        connectors.append(path(f"M 1140 {y+62} H 1350",dotted=True))
    nodes += [card(4,items[3]["title"],1350,320,360,150,WHITE),card(5,items[4]["title"],1350,530,360,150,TILE),card(6,items[5]["title"],1350,740,360,150,WHITE)]
    nodes.append(f'<g id="slice"><path d="M 620 275 V 865" stroke="{VOLT}" stroke-width="48" opacity="0.85"/><path d="M 600 275 H 640" stroke="{MID}" stroke-width="2"/><path d="M 600 865 H 640" stroke="{MID}" stroke-width="2"/></g>')
    return connectors+nodes+[text(620,250,"SLICE VERTICAL",20,800,18,"middle")],line_edges([(1,4),(2,4),(3,4),(4,5),(5,6)],"boundary")


def layout_portfolio(items):
    connectors=[path("M 900 310 V 420",color=VOLT,width=6),path("M 570 540 H 710"),path("M 1090 540 H 1230"),path("M 900 650 V 790",dotted=True),path("M 420 730 C 520 850,650 850,710 850",dotted=True),path("M 1380 730 C 1280 850,1150 850,1090 850",dotted=True)]
    nodes=[card(4,items[3]["title"],350,250,1100,100,TILE,"cut",64),card(5,items[4]["title"],710,420,380,230,WHITE,"diamond",23),card(1,items[0]["title"],90,450,480,170,TILE),card(2,items[1]["title"],1230,450,480,170,WHITE),card(3,items[2]["title"],90,690,480,140,WHITE),card(6,items[5]["title"],1230,690,480,140,TILE)]
    return connectors+nodes+[text(900,740,"RENUNCIA EXPLÍCITA",20,800,24,"middle")],line_edges([(4,5),(1,5),(2,5),(3,5),(5,6)],"decision")


def layout_flowboard(items):
    xs=[80,470,860,1250]
    connectors=[path(f"M {xs[i]+320} 560 H {xs[i+1]}") for i in range(3)]
    nodes=[card(1,items[0]["title"],80,270,320,140,TILE),card(2,items[1]["title"],470,270,320,140,WHITE)]
    board_labels=[items[2]["title"],items[3]["title"],items[4]["title"],items[5]["title"]]
    for i,x in enumerate(xs):
        nodes.append(f'<g id="board{i}"><rect x="{x}" y="465" width="320" height="310" fill="{WHITE if i%2 else TILE}" stroke="{MID}" stroke-width="2"/>{text(x+18,500,["DEMANDA","EN CURSO","VALIDACIÓN","SALIDA"][i],19,800,18)}{text(x+24,585,board_labels[i],23,700,21)}</g>')
    nodes += [f'<g id="n{i+3}"><circle cx="{xs[i]+285}" cy="{740}" r="7" fill="{VOLT}" stroke="{MID}" stroke-width="1.5"/>{text(xs[i]+24,730,f"{i+3:02d}",18,800,4,color=MID)}</g>' for i in range(4)]
    return connectors+nodes+[text(900,850,"LÍMITE DE TRABAJO EN CURSO",20,800,30,"middle"),path("M 470 820 H 1180",arrow=False,color=VOLT,width=8)],line_edges([(1,3),(2,3),(3,4),(4,5),(5,6)],"flow")


def layout_ecosystem(items):
    cx,cy=900,560; r=330
    pts=[]; connectors=[]; nodes=[]
    for i in range(1,6):
        a=-math.pi/2+(i-1)*2*math.pi/5
        x=cx+r*math.cos(a); y=cy+r*math.sin(a); pts.append((x,y))
        connectors.append(path(f"M {cx} {cy} L {x:.1f} {y:.1f}",dotted=True))
        nodes.append(card(i+1,items[i]["title"],x-145,y-75,290,150,TILE if i%2 else WHITE,chars=20))
    nodes.append(card(1,items[0]["title"],cx-190,cy-125,380,250,WHITE,"diamond",25))
    connectors.append(path(f"M {pts[-1][0]:.1f} {pts[-1][1]:.1f} C 400 930, 430 260, {pts[0][0]:.1f} {pts[0][1]:.1f}",dotted=True))
    return connectors+nodes+[text(cx,225,"ECOSISTEMA DE CAPACIDADES",20,800,30,"middle")],line_edges([(2,1),(3,1),(4,1),(5,1),(6,1),(6,2)],"dependency")


def layout_scenario_matrix(items):
    nodes=[card(1,items[0]["title"],90,260,430,130,TILE,"cut",28)]
    ys=[430,600,770]
    for i,y in enumerate(ys): nodes.append(card(i+2,items[i+1]["title"],320,y,870,120,WHITE if i%2 else TILE,"cut",52))
    nodes += [card(5,items[4]["title"],1250,430,440,180,TILE),card(6,items[5]["title"],1250,700,440,180,WHITE,"diamond",26)]
    connectors=[path(f"M 520 {y+60} H 1250",dotted=True) for y in ys]+[path("M 1470 610 V 700",color=VOLT,width=5),path("M 1470 880 C 1060 960, 480 940, 480 890",dotted=True)]
    for x in [650,850,1050]: connectors.append(path(f"M {x} 410 V 900",arrow=False,color=BORDER,width=2))
    return connectors+nodes+[text(760,415,"ESCENARIOS Y ATRIBUTOS EN TENSIÓN",20,800,36,"middle")],line_edges([(1,2),(1,3),(1,4),(2,5),(3,5),(4,5),(5,6)],"evidence")


def layout_recovery(items):
    connectors=[]; nodes=[]
    xs=[120,380,640,900]
    for i,x in enumerate(xs):
        nodes.append(card(i+1,items[i]["title"],x,360+i*70,230,150,TILE if i%2 else WHITE,"cut",16))
        if i<3: connectors.append(path(f"M {x+230} {435+i*70} H {xs[i+1]}",dotted=i==2))
    nodes += [card(5,items[4]["title"],1160,390,300,190,WHITE),card(6,items[5]["title"],1370,700,350,190,TILE,"diamond",22)]
    connectors += [path("M 1130 645 H 1210 V 580",dotted=True),path("M 1460 580 C 1590 580,1580 700,1545 700"),path("M 1370 795 C 1100 970,520 940,520 650",dotted=True)]
    return connectors+nodes+[text(600,300,"CAPAS DE RECUPERACIÓN",20,800,28,"middle"),text(1410,330,"PROMESA OPERATIVA",20,800,28,"middle")],line_edges([(1,2),(2,3),(3,4),(4,5),(5,6),(6,3)],"feedback")


def layout_dashboard(items):
    nodes=[]; connectors=[]
    xs=[120,500,880]
    for i,x in enumerate(xs):
        nodes.append(card(i+1,items[i]["title"],x,300,320,180,TILE if i==1 else WHITE))
        connectors.append(path(f"M {x+160} 480 V 600",dotted=True))
    nodes += [card(4,items[3]["title"],260,600,820,120,WHITE,"cut",48),card(5,items[4]["title"],1250,340,420,180,TILE,"diamond",25),card(6,items[5]["title"],1250,700,420,160,WHITE)]
    connectors += [path("M 1080 660 H 1250"),path("M 1460 520 V 700",color=VOLT,width=5),path("M 1460 860 C 1050 960,700 900,700 720",dotted=True)]
    return connectors+nodes+[text(680,265,"SEÑALES EN CUATRO ESCALAS",20,800,30,"middle")],line_edges([(1,4),(2,4),(3,4),(4,5),(5,6),(6,4)],"evidence")


def layout_incident_loop(items):
    cx,cy=900,620; rx,ry=560,220; nodes=[]; connectors=[]; positions=[]
    for i in range(6):
        a=-math.pi/2+i*2*math.pi/6; positions.append((cx+rx*math.cos(a),cy+ry*math.sin(a)))
    for i,(x,y) in enumerate(positions):
        nx,ny=positions[(i+1)%6]; connectors.append(path(f"M {x:.1f} {y:.1f} Q {cx:.1f} {cy:.1f} {nx:.1f} {ny:.1f}",dotted=i==5))
        nodes.append(card(i+1,items[i]["title"],x-145,y-70,290,140,TILE if i%2 else WHITE,chars=20))
    nodes.append(f'<g id="center"><circle cx="{cx}" cy="{cy}" r="112" fill="{WHITE}" stroke="{MID}" stroke-width="3"/>{text(cx,555,"ACCIÓN",29,800,12,"middle")}{text(cx,598,"SEGURA",29,800,12,"middle")}</g>')
    return connectors+nodes,line_edges([(1,2),(2,3),(3,4),(4,5),(5,6),(6,1)],"feedback")


def layout_decision_tree(items):
    center=(750,470,300,220)
    leaves=[(90,270),(90,500),(90,730),(1370,270),(1370,730)]
    connectors=[]
    for x,y in leaves: connectors.append(path(f"M {750 if x<900 else 1050} 580 C {600 if x<900 else 1200} 580, {x+170} {y+75}, {x+170} {y+75}",dotted=True))
    nodes=[card(6,items[5]["title"],*center,WHITE,"diamond",22)]
    for i,(x,y) in enumerate(leaves): nodes.append(card(i+1,items[i]["title"],x,y,340,150,TILE if i%2 else WHITE))
    return connectors+nodes+[text(900,300,"PUERTA DE PERTINENCIA",20,800,28,"middle")],line_edges([(6,1),(6,2),(6,3),(6,4),(6,5)],"decision")


def layout_permission_matrix(items):
    nodes=[]; connectors=[]
    nodes.append(f'<g id="matrix"><rect x="330" y="280" width="1080" height="590" fill="{WHITE}" stroke="{MID}" stroke-width="2"/><path d="M 870 280 V 870" stroke="{BORDER}" stroke-width="2"/><path d="M 330 575 H 1410" stroke="{BORDER}" stroke-width="2"/><path d="M 330 870 L 1410 280" stroke="{VOLT}" stroke-width="14" opacity=".72"/></g>')
    pos=[(370,690),(1080,340),(430,360),(990,680),(700,490)]
    for i,(x,y) in enumerate(pos): nodes.append(card(i+1,items[i]["title"],x,y,300,130,TILE if i%2 else WHITE,chars=20))
    nodes.append(card(6,items[5]["title"],1430,500,300,180,WHITE,"cut",20))
    connectors=[path("M 1410 575 H 1430"),path("M 1580 680 V 790 H 870",dotted=True)]
    return connectors+nodes+[text(300,910,"MENOR IMPACTO",18,800,18),text(1410,910,"MAYOR IMPACTO",18,800,18,"end"),text(285,310,"MAYOR AUTONOMÍA",18,800,20,"middle")],line_edges([(1,6),(2,6),(3,6),(4,6),(5,6)],"authority")


def layout_lifecycle(items):
    return layout_incident_loop(items)


def layout_bidirectional(items):
    xs=[80,420,760,1100]
    connectors=[path(f"M {xs[i]+260} 430 H {xs[i+1]}") for i in range(3)]
    connectors += [path("M 1360 430 H 1580 V 760 H 1180",dotted=True),path("M 900 760 H 620",dotted=True),path("M 620 760 C 400 760,300 620,300 540",dotted=True)]
    nodes=[card(i+1,items[i]["title"],x,340,260,180,TILE if i%2 else WHITE,chars=18) for i,x in enumerate(xs)]
    nodes += [card(5,items[4]["title"],920,690,420,160,TILE),card(6,items[5]["title"],360,690,420,160,WHITE,"diamond",24)]
    return connectors+nodes+[text(900,285,"CADENA HACIA LA OPERACIÓN",20,800,34,"middle"),text(900,920,"PRUEBA EN SENTIDO INVERSO",20,800,34,"middle")],line_edges([(1,2),(2,3),(3,4),(4,5),(5,6),(6,1)],"feedback")


def layout_argument(items):
    connectors=[path("M 430 370 C 620 370,610 560,760 560",dotted=True),path("M 430 560 H 760",dotted=True),path("M 430 750 C 620 750,610 560,760 560",dotted=True),path("M 1040 560 H 1280"),path("M 1490 650 V 760",color=VOLT,width=5),path("M 1280 840 C 980 940,760 870,900 680",dotted=True)]
    nodes=[card(2,items[1]["title"],90,300,340,140,TILE),card(3,items[2]["title"],90,490,340,140,WHITE),card(4,items[3]["title"],90,680,340,140,TILE),card(1,items[0]["title"],760,420,280,280,WHITE,"circle",22),card(5,items[4]["title"],1280,470,420,180,TILE,"cut",26),card(6,items[5]["title"],1280,760,420,150,WHITE)]
    return connectors+nodes+[text(250,250,"AUDIENCIAS",20,800,18,"middle"),text(1490,420,"OBJECIÓN Y TRANSFERENCIA",20,800,32,"middle")],line_edges([(2,1),(3,1),(4,1),(1,5),(5,6),(6,1)],"evidence")


def layout_double_loop(items):
    connectors=[path("M 350 500 H 650"),path("M 920 500 H 1200"),path("M 1450 580 C 1510 740,1180 820,920 720",dotted=True),path("M 650 720 C 340 860,180 700,180 580",dotted=True),path("M 920 720 C 900 930,430 930,350 650",dotted=True),path("M 1200 500 C 1100 300,740 280,650 430",color=VOLT,width=5)]
    nodes=[card(1,items[0]["title"],80,420,270,160,TILE),card(2,items[1]["title"],650,420,270,160,WHITE),card(3,items[2]["title"],1200,420,270,160,TILE),card(4,items[3]["title"],1200,690,340,160,WHITE,"cut",22),card(5,items[4]["title"],650,690,340,160,TILE),card(6,items[5]["title"],80,690,340,160,WHITE)]
    return connectors+nodes+[text(900,275,"REVISAR LA ACCIÓN",20,800,24,"middle"),text(900,940,"REVISAR EL MARCO QUE PRODUJO LA ACCIÓN",20,800,46,"middle")],line_edges([(1,2),(2,3),(3,4),(4,5),(5,6),(6,1),(3,2)],"feedback")


RENDERERS = {
    "split": layout_split, "converge": layout_converge, "service": layout_service,
    "lens": layout_lens, "contradiction": layout_contradiction, "braid": layout_braid,
    "strata": layout_strata, "comparison": layout_comparison, "gates": layout_gates,
    "governance": layout_governance, "hypothesis": layout_hypothesis, "slice": layout_slice,
    "portfolio": layout_portfolio, "flowboard": layout_flowboard, "ecosystem": layout_ecosystem,
    "scenario_matrix": layout_scenario_matrix, "recovery": layout_recovery,
    "dashboard": layout_dashboard, "incident_loop": layout_incident_loop,
    "decision_tree": layout_decision_tree, "permission_matrix": layout_permission_matrix,
    "lifecycle": layout_lifecycle, "bidirectional": layout_bidirectional,
    "argument": layout_argument, "double_loop": layout_double_loop,
}


def header(code: str, title_value: str, claim: str) -> list[str]:
    title_lines = wrap(title_value, 54)
    title_svg = text(90, 126, title_value, 54, 800, 54)
    title_h = 54 + (len(title_lines)-1)*65
    claim_y = 126 + title_h + 28
    return [
        '<g id="header">',
        f'<path d="M 82 55 H 222 L 207 76 H 67 Z" fill="{VOLT}"/>',
        text(250,74,f"{code} · MAPA CONCEPTUAL",22,800,30),
        title_svg,
        text(90,claim_y,claim,22,500,118,color=MID),
        f'<path d="M 90 {claim_y+45:.1f} H 1710" stroke="{BORDER}" stroke-width="2"/>',
        '</g>',
    ]


def build_svg(code: str, title_value: str, claim: str, items: list[dict], layout_name: str) -> tuple[str, list[dict]]:
    body, edges = RENDERERS[layout_name](items)
    defs = f'''<defs><marker id="arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto"><path d="M1 1 L11 6 L1 11 Z" fill="{MID}"/></marker></defs>'''
    desc = f"{claim} La composición utiliza la topología {layout_name} para relacionar seis elementos del argumento."
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1100" viewBox="0 0 1800 1100" role="img" aria-labelledby="title desc">',
             f'<title id="title">{esc(title_value)}</title><desc id="desc">{esc(desc)}</desc>',defs,
             f'<rect width="1800" height="1100" fill="{PAPER}"/>',
             f'<rect x="42" y="34" width="1716" height="1024" rx="18" fill="none" stroke="{BORDER}" stroke-width="2"/>']
    parts += header(code,title_value,claim)
    parts += ['<g id="connectors">'] + [part for part in body if part.startswith('<path')] + ['</g>']
    parts += ['<g id="objects">'] + [part for part in body if not part.startswith('<path')] + ['</g>']
    parts += [f'<g id="footer"><path d="M 90 1000 H 1710" stroke="{BORDER}" stroke-width="2"/>{text(90,1035,"METSI · LA FORMA VISUAL RESPONDE AL ARGUMENTO",18,800,52,color=MID)}{text(1710,1035,layout_name.upper().replace("_"," "),18,800,30,"end",MID)}</g>', '</svg>']
    return "".join(parts), edges


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records=[]
    for n in range(12,37):
        src_dir=SOURCE/f"N{n:02d}"
        specs=sorted(src_dir.glob('*.spec.json'))
        target=OUT/f"N{n:02d}"; target.mkdir(parents=True,exist_ok=True)
        pieces=[]
        for idx,spec_path in enumerate(specs,1):
            data=json.loads(spec_path.read_text(encoding='utf-8'))
            code=f"N{n:02d}"+(chr(64+idx) if len(specs)>1 else "")
            layout_name=LAYOUTS[code]
            title_value=data['title'].replace(' · pieza 1','').replace(' · pieza 2','')
            claim=data['alt'].strip()
            items=data['items'][:6]
            svg,edges=build_svg(code,title_value,claim,items,layout_name)
            stem=spec_path.name.replace('-v2.spec.json','-v3')
            svg_path=target/f"{stem}.svg"
            manifest_path=target/f"{stem}-content-manifest.json"
            alt_path=target/f"{stem}-alt-text.md"
            review_path=target/f"{stem}-review.html"
            nodes=[{"id":f"n{i}","label":item['title'],"role":"process" if i<6 else "decision","source":["s1"],"purpose":"Elemento necesario del argumento visual"} for i,item in enumerate(items,1)]
            manifest={"title":title_value,"claim":claim,"source_sections":[{"id":"s1","heading":title_value,"summary":claim}],"nodes":nodes,"edges":edges,"topology":layout_name}
            svg_path.write_text(svg+'\n',encoding='utf-8')
            manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            alt_path.write_text(f"# Texto alternativo · {code}\n\n{claim}\n\nLa organización visual elegida es {layout_name.replace('_',' ')} porque vuelve visible la relación central sin convertirla en una lista de cajas equivalentes.\n",encoding='utf-8')
            review_path.write_text(f'<!doctype html><html lang="es"><meta charset="utf-8"><title>{esc(code)} · revisión</title><style>body{{margin:0;background:#ddd}}img{{display:block;width:min(100vw,1800px);height:auto;margin:auto}}</style><img src="{svg_path.name}" alt="{esc(claim)}"></html>\n',encoding='utf-8')
            proc=subprocess.run(['python3',str(VALIDATOR),str(svg_path),'--manifest',str(manifest_path)],capture_output=True,text=True)
            record={"code":code,"title":title_value,"layout":layout_name,"source_spec":str(spec_path.relative_to(ROOT)),"svg":str(svg_path.relative_to(ROOT)),"manifest":str(manifest_path.relative_to(ROOT)),"validator_exit":proc.returncode,"validator_output":proc.stdout.strip()}
            pieces.append(record); records.append(record)
        (target/'manifest.json').write_text(json.dumps({"document":f"N{n:02d}","status":"candidate-for-author-review","pieces":pieces},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    failed=[r for r in records if r['validator_exit']]
    report={"status":"PASS" if not failed else "FAIL","pieces":len(records),"topologies":sorted(set(r['layout'] for r in records)),"topology_count":len(set(r['layout'] for r in records)),"failed":[r['code'] for r in failed],"items":records}
    (OUT/'QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','pieces','topology_count','failed']},ensure_ascii=False))


if __name__ == '__main__':
    main()
