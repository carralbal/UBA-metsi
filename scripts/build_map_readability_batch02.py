#!/usr/bin/env python3
"""Source-grounded review assets only. Never modifies a PDF or approved map."""
from pathlib import Path
from contextlib import contextmanager
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'pedagogy/readability-pilots/mapas-tanda-02'
PAPER, INK, PALE, VOLT = '#F7F6F2', '#202020', '#E5E6E0', '#CFFF00'


def node(id, label, source, purpose, role='process'):
    return dict(id=id, label=label, role=role, source=[source], purpose=purpose)


def edge(id, start, end, source, meaning, relation='dependency'):
    return dict(id=id, **{'from': start, 'to': end}, source=[source], meaning=meaning, relation=relation)


PLANS = {
    24: dict(
        title='Todo parece urgente. ¿Qué hacemos primero?',
        claim='Priorizar requiere proteger condiciones del servicio, limitar el trabajo activo y explicar qué espera y cuándo se revisará.',
        topology='Atlas de decisión: protección previa, cuatro opciones con decisiones diferentes y registro de renuncias.',
        alt='De arriba abajo: se protege la accesibilidad; de cuatro opciones avanzan cobertura accesible e instrumentación de eventos, esperan los canales externos y no avanza por ahora la automatización de sobreventa. Se reserva capacidad para incidentes. Toda postergación registra personas afectadas, consecuencia y revisión.',
        sections={'caso': 'Hotel Horizonte: priorizar también nombra a quién esperar', 'limite': 'Movimiento 1 · Hacer visibles demora, capacidad y obligación', 'revision': 'Movimiento 3 · Revisar prioridades con evidencia y límites'},
        nodes=[
            node('proteccion', 'La accesibilidad no compite como una mejora opcional.', 'caso', 'Distinguir protección institucional de una obligación jurídica todavía no validada.', 'constraint'),
            node('opcion-accesibilidad', 'Completar cobertura accesible', 'caso', 'Evitar una exclusión en los turnos sin cobertura.'),
            node('opcion-eventos', 'Registrar mejor lo que ocurre', 'caso', 'Traducir instrumentación de eventos sin perder el concepto técnico.'),
            node('opcion-canales', 'Sumar canales externos', 'caso', 'Hacer visible la oportunidad comercial y su dependencia de un servicio estable.'),
            node('opcion-sobreventa', 'Automatizar la sobreventa', 'caso', 'Distinguir una apuesta todavía no probada.'),
            node('ahora-accesibilidad', 'AHORA · Protege el servicio', 'caso', 'Primera decisión de capacidad.', 'decision'),
            node('ahora-eventos', 'AHORA · Permite aprender', 'caso', 'Segunda decisión de capacidad.', 'decision'),
            node('espera-canales', 'ESPERA · Se posterga la expansión', 'caso', 'No confundir postergación con abandono.', 'decision'),
            node('no-sobreventa', 'NO AVANZA · Faltan pruebas sobre sus efectos', 'caso', 'Retirar por ahora una opción no suficientemente probada.', 'decision'),
            node('reserva', 'Se reserva capacidad para incidentes y soporte.', 'caso', 'No ocupar toda la capacidad teórica con iniciativas.', 'constraint'),
            node('quien', 'Quién espera', 'revision', 'Nombrar personas o áreas afectadas.', 'evidence'),
            node('consecuencia', 'Qué se pierde', 'revision', 'Registrar el efecto de demorar.', 'evidence'),
            node('revisar', 'Cuándo revisar', 'revision', 'Fijar fecha y señales para reconsiderar.', 'decision'),
        ],
        edges=[edge('e-'+a, 'opcion-'+a, b, 'caso', c, 'transformation') for a,b,c in [
            ('accesibilidad', 'ahora-accesibilidad', 'Se asigna capacidad a una protección institucional.'),
            ('eventos', 'ahora-eventos', 'Se asigna capacidad a producir evidencia útil.'),
            ('canales', 'espera-canales', 'Se posterga la expansión comercial.'),
            ('sobreventa', 'no-sobreventa', 'Se descarta por ahora la automatización hasta tener evidencia suficiente.'),
        ]],
    ),
    26: dict(
        title='La reserva está confirmada. La familia todavía no puede entrar.',
        claim='El hotel necesita acuerdos verificables con servicios autónomos y una contingencia autorizada para responder por el ingreso completo.',
        topology='Mapa de ecosistema con frontera de confianza; recorrido de contingencia y responsabilidades concretas.',
        alt='A la izquierda están las capacidades del hotel; a la derecha, canal de reservas, identidad y cerraduras. Tres intercambios cruzan una frontera de confianza. Debajo, la contingencia pasa por verificación presencial, llave limitada autorizada, doble registro y revisión posterior. Cuatro personas conservan responsabilidades distintas y se fija una condición de revisión.',
        sections={'caso': 'Hotel Horizonte: la reserva confirmada que nadie podía ejecutar', 'capacidades': 'Movimiento 1 · Delimitar promesa, capacidades y participantes', 'confianza': 'Movimiento 2 · Asignar responsabilidad, confianza y capacidad de respuesta', 'contingencia': 'Movimiento 3 · Diseñar degradación, salida y gobernanza'},
        nodes=[
            node('hotel', 'CAPACIDADES DEL HOTEL', 'capacidades', 'Agrupar capacidades internas sin reducirlas a software.', 'system'),
            node('canal', 'Canal de reservas', 'caso', 'Participante externo que confirma una venta.', 'system'),
            node('identidad', 'Servicio de identidad', 'caso', 'Participante externo que valida a la persona.', 'system'),
            node('cerraduras', 'Cerraduras', 'caso', 'Dependencia que permite emitir una llave.', 'system'),
            node('frontera', 'En cada intercambio se acuerda qué dato aceptar, quién puede corregirlo y qué hacer si no alcanza.', 'confianza', 'Explicar frontera de confianza sin equipararla a una simple frontera jurídica.', 'boundary'),
            node('verificar', 'Verificación presencial', 'caso', 'Primera acción de la contingencia autorizada.'),
            node('llave', 'Llave limitada con autorización', 'caso', 'Conservar autoridad y límites de la excepción.'),
            node('registro', 'Doble registro del episodio', 'caso', 'Conservar evidencia técnica y operativa.', 'evidence'),
            node('posterior', 'Revisión posterior y aviso al canal', 'caso', 'Reconciliar y avisar después de la respuesta inmediata.'),
            node('ricardo', 'Ricardo · Autoriza la respuesta operativa.', 'caso', 'Nombrar autoridad.', 'actor'),
            node('lucia', 'Lucía · Registra lo ocurrido en Recepción.', 'caso', 'Conservar la evidencia del episodio.', 'actor'),
            node('federico', 'Federico · Conserva la traza técnica.', 'caso', 'Hacer reconstruible la intervención técnica.', 'actor'),
            node('camila', 'Camila · Ajusta lo que promete el canal.', 'caso', 'No seguir prometiendo ingreso instantáneo.', 'actor'),
            node('revision', 'Revisar tras 20 ingresos o ante una identidad discutida.', 'caso', 'Conservar el umbral y la excepción de revisión.', 'decision'),
        ],
        edges=[
            edge('e-canal', 'canal', 'hotel', 'confianza', 'El hotel recibe una afirmación de reserva; debe verificar procedencia y vigencia.'),
            edge('e-identidad', 'identidad', 'hotel', 'confianza', 'La validación externa requiere reglas para evidencia incompleta o contradictoria.'),
            edge('e-cerraduras', 'cerraduras', 'hotel', 'confianza', 'La capacidad de acceso depende de la autorización de la cerradura.'),
            edge('e-verificar', 'verificar', 'llave', 'caso', 'La verificación presencial y la autorización habilitan una llave limitada.', 'flow'),
            edge('e-llave', 'llave', 'registro', 'caso', 'La excepción se documenta, no se entrega una llave sin rastro.', 'flow'),
            edge('e-registro', 'registro', 'posterior', 'caso', 'Los registros permiten reconciliar y avisar al canal.', 'flow'),
        ],
    ),
    27: dict(
        title='Un mensaje válido no alcanza para entregar la llave.',
        claim='Forma, significado, tiempo y acción deben acordarse juntos para que el mismo mensaje no produzca decisiones incompatibles.',
        topology='Cuatro capas del mismo contrato que convergen en una única condición de aceptación; no son cuatro etapas cronológicas.',
        alt='El estado liberada sólo confirma limpieza terminada, no una habitación asignable. Cuatro franjas distinguen forma o sintaxis, significado o semántica, tiempo y acción operacional. Las cuatro confluyen en un contrato que permite anticipar la misma consecuencia y responder ante fallas. Se proponen pruebas de duplicación, demora, desorden y versión.',
        sections={'caso': 'Hotel Horizonte: «liberada» no significaba lo mismo para todos', 'capas': 'Movimiento 1 · Acordar forma, significado, tiempo y efecto', 'fallas': 'Movimiento 2 · Proteger invariantes frente a duplicados, demoras y errores', 'pruebas': 'Movimiento 3 · Evolucionar y probar contratos sin quebrar consumidores'},
        nodes=[
            node('distincion', 'Limpieza terminada ≠ habitación lista para entregar.', 'caso', 'Hacer concreta la diferencia entre liberada y asignable.', 'constraint'),
            node('forma', 'Forma (sintaxis)', 'capas', 'Definir estructura, campos, tipos y versión.', 'constraint'),
            node('significado', 'Significado (semántica)', 'caso', 'No atribuir al mensaje una afirmación que no contiene.', 'constraint'),
            node('tiempo', 'Tiempo (vigencia y orden)', 'fallas', 'No repetir el efecto ni inventar éxito ante demora.', 'constraint'),
            node('accion', 'Acción (operación)', 'capas', 'Asignar decisión, comunicación y reparación.', 'constraint'),
            node('aceptacion', 'Todos anticipan la misma consecuencia', 'capas', 'Reunir las cuatro capas; un mensaje aceptado no basta.', 'outcome'),
            node('prueba', 'Prueba: duplicar, demorar, desordenar y cambiar la versión.', 'pruebas', 'Probar más que el caso en que todo funciona.', 'evidence'),
            node('revision', 'Revisar tras 30 transiciones o ante una entrega incorrecta.', 'caso', 'Conservar condición de revisión.', 'decision'),
        ],
        edges=[edge('e-'+id, id, 'aceptacion', 'capas', 'El acuerdo sobre '+meaning+' es necesario para compartir la consecuencia.') for id,meaning in [('forma','la forma'),('significado','el significado'),('tiempo','el tiempo'),('accion','la operación')]],
    ),
}


class Map:
    def __init__(self, n):
        self.n, self.plan = n, PLANS[n]
        self.dir = OUT / f'N{n}'
        self.dir.mkdir(parents=True, exist_ok=True)
        self.source = next((ROOT / f'N{n}-v10-editorial/source').glob('*.md'))
        headings = [s.lstrip('# ') for s in self.source.read_text().splitlines() if s.startswith('#')]
        for heading in self.plan['sections'].values():
            assert heading in headings, (n, heading)
        manifest = dict(title=self.plan['title'], claim=self.plan['claim'], topology=self.plan['topology'], source=str(self.source.relative_to(ROOT)), source_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(), source_sections=[dict(id=k, heading=v, summary=v) for k,v in self.plan['sections'].items()], nodes=self.plan['nodes'], edges=self.plan['edges'], target_width_mm=173, minimum_content_font_px=28, minimum_content_font_pt=round(28*173/1200*72/25.4,2), status='REVIEW_NOT_INTEGRATED')
        # Save the semantic contract before any drawing.
        (self.dir/'content-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1620" viewBox="0 0 1200 1620" role="img" aria-labelledby="title desc"><title id="title">{html.escape(self.plan["title"])}</title><desc id="desc">{html.escape(self.plan["alt"])}</desc>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#777A76"/></marker></defs>']
        self.rect(0,0,1200,1620,PAPER,False)

    def text(self,x,y,s,size=28,bold=False,serif=False,anchor='start'):
        family='Georgia,serif' if serif else 'Arial,Helvetica,sans-serif'
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{INK}">{html.escape(s)}</text>')

    def line(self,d,arrow=False,dash=False,id=None):
        self.parts.append(f'<path'+(f' id="{id}"' if id else '')+f' d="{d}" fill="none" stroke="#92958F" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+(' stroke-dasharray="6 8"' if dash else '')+'/>')

    def rect(self,x,y,w,h,fill=PALE,stroke=True):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'+(' stroke="#A5A79F" stroke-width="1.5"' if stroke else '')+'/>')

    def circle(self,x,y,label,active=False,r=26):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{VOLT if active else PAPER}" stroke="{INK}" stroke-width="2"/>')
        self.text(x,y+9,label,28,True,anchor='middle')

    @contextmanager
    def group(self,id):
        label=next((n['label'] for n in self.plan['nodes'] if n['id']==id),id)
        self.parts.append(f'<g id="{id}" aria-label="{html.escape(label,quote=True)}">')
        yield
        self.parts.append('</g>')

    def header(self,a,b,sub,size=52):
        with self.group('encabezado'):
            self.parts.append(f'<path d="M52 36 H126 L116 52 H42 Z" fill="{VOLT}"/>')
            self.text(154,53,f'METSI · N{self.n} · MAPA DE DECISIÓN',24,True)
            self.text(52,118,a,size,serif=True)
            self.text(52,182,b,size,serif=True)
            self.text(52,226,sub)
            self.line('M52 250 H1148')

    def save(self):
        self.parts.append('</svg>')
        svg=self.dir/f'N{self.n}-mapa-legible.svg'
        svg.write_text('\n'.join(self.parts)+'\n')
        (self.dir/'alt-text.md').write_text(self.plan['alt']+'\n')
        (self.dir/'review.html').write_text(f'<!doctype html><html lang="es-AR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>N{self.n} · Mapa legible</title><style>body{{margin:0;background:#deddd7;font-family:Arial}}main{{max-width:1000px;margin:24px auto;padding:24px;background:white}}img{{width:100%;display:block}}p{{line-height:1.5}}@media print{{header{{display:none}}main{{padding:0;margin:0}}img{{width:173mm}}}}</style><main><header><h1>N{self.n} · Propuesta de mapa</h1><p>{html.escape(self.plan["claim"])}</p><p>Revisión visual. Todavía no incorporado al PDF. Cuerpo mínimo previsto: 11,44 pt a 173 mm de ancho.</p></header><img src="{svg.name}" alt="{html.escape(self.plan["alt"],quote=True)}"></main></html>')
        print(svg)


def n24():
    m=Map(24)
    m.header('Todo parece urgente.', '¿Qué hacemos primero?', 'Hotel Horizonte · Elegir también implica decir qué no se hará.')
    m.text(52,295,'01   Primero: proteger lo que no puede negociarse',32,True)
    with m.group('proteccion'):
        m.rect(52,320,1096,154)
        m.text(80,364,'La accesibilidad no compite como una mejora opcional.',30,True)
        m.text(80,405,'Demorarla mantiene una exclusión. Hay un compromiso del hotel.')
        m.text(80,446,'La posible obligación legal todavía requiere verificación.')
    m.text(52,529,'02   Cuatro opciones. Sólo dos trabajos activos.',32,True)
    m.text(145,580,'QUÉ SE PROPONE Y PARA QUÉ',24,True)
    m.text(922,580,'DECISIÓN',24,True)
    rows=[
        ('accesibilidad','ahora-accesibilidad','Completar cobertura accesible',['Atender también a quienes hoy','no tienen una alternativa en ciertos turnos.'],'AHORA',['Protege','el servicio']),
        ('eventos','ahora-eventos','Registrar mejor lo que ocurre',['Instrumentar eventos: producir evidencia','y reducir reconstrucciones manuales.'],'AHORA',['Permite','aprender']),
        ('canales','espera-canales','Sumar canales externos',['Puede traer reservas, pero también ampliar','un servicio que todavía tiene fallas.'],'ESPERA',['Se posterga','la expansión']),
        ('sobreventa','no-sobreventa','Automatizar la sobreventa',['Promete más ocupación, pero sus efectos','y posibles daños todavía no se probaron.'],'NO AVANZA',['Faltan pruebas','sobre sus efectos']),
    ]
    for i,(id,dest,title,body,status,explain) in enumerate(rows):
        y=617+i*163
        m.line(f'M52 {y} H1148')
        m.line(f'M801 {y+70} H882',True,id='e-'+id)
        with m.group('opcion-'+id):
            m.circle(82,y+49,str(i+1),i<2)
            m.text(145,y+50,title,32,True)
            m.text(145,y+91,body[0])
            m.text(145,y+129,body[1])
        with m.group(dest):
            m.rect(905,y+18,243,131,VOLT if i<2 else PAPER)
            m.text(922,y+52,status,28,True)
            m.text(922,y+91,explain[0])
            m.text(922,y+126,explain[1])
    m.line('M52 1269 H1148')
    with m.group('reserva'):
        m.text(52,1314,'Se reserva capacidad para incidentes y soporte.',30,True)
    m.text(52,1384,'03   Cada postergación debe dejar por escrito',32,True)
    for id,x,title,a,b in [
        ('quien',52,'Quién espera','Las personas o áreas','que quedan afectadas.'),
        ('consecuencia',425,'Qué se pierde','El efecto de demorar','esa iniciativa.'),
        ('revisar',800,'Cuándo revisar','Una fecha y señales','para cambiar la decisión.'),
    ]:
        with m.group(id):
            m.text(x,1450,title,32,True)
            m.text(x,1492,a)
            m.text(x,1530,b)
    m.line('M52 1560 H1148')
    m.text(52,1596,'Ordenar una lista no alcanza si todo sigue en marcha.',24)
    m.save()


def n26():
    m=Map(26)
    m.header('La reserva está confirmada.', 'La familia todavía no puede entrar.', 'Hotel Horizonte · Una llegada a las 22.15 y tres dependencias externas.',48)
    m.text(52,295,'01   El servicio depende de varias partes',32,True)
    # Routes behind all containers; the dashed boundary is not an actor.
    m.line('M645 335 V795',dash=True)
    for id,y in [('canal',480),('identidad',597),('cerraduras',714)]:
        m.line(f'M760 {y} H539',True,id='e-'+id)
    with m.group('hotel'):
        m.rect(52,335,485,460)
        m.text(80,381,'CAPACIDADES DEL HOTEL',24,True)
        for y,title,body in [(438,'Inventario y reserva','Qué habitación se ofrece.'),(520,'Housekeeping','Si está limpia y disponible.'),(602,'Recepción','Asignación y excepciones.'),(684,'Pagos y registro','Pago, trazas y reparación.')]:
            m.text(80,y,title,30,True)
            m.text(80,y+38,body)
        m.text(80,768,'Resultado: completar el ingreso.',28,True)
    m.rect(760,335,388,460,PAPER)
    m.text(788,381,'SERVICIOS EXTERNOS',24,True)
    for id,y,title,body in [('canal',438,'Canal de reservas','Confirma la venta.'),('identidad',555,'Servicio de identidad','Valida a la persona.'),('cerraduras',672,'Cerraduras','Habilitan la llave.')]:
        with m.group(id):
            m.text(788,y,title,30,True)
            m.text(788,y+38,body)
    with m.group('frontera'):
        m.text(52,844,'Frontera de confianza: no aceptar un dato sin condiciones.',30,True)
        m.text(52,888,'En cada intercambio se acuerda qué dato aceptar,')
        m.text(52,925,'quién puede corregirlo y qué hacer si no alcanza.')
    m.line('M52 951 H1148')
    m.text(52,999,'02   Si la identidad no se puede confirmar',32,True)
    centers=[165,450,735,1020]
    ids=['verificar','llave','registro','posterior']
    for i in range(3):
        m.line(f'M{centers[i]+31} 1060 H{centers[i+1]-36}',True,id=['e-verificar','e-llave','e-registro'][i])
    for i,(x,id,a,b) in enumerate(zip(centers,ids,['Verificación','Llave limitada','Doble registro','Revisión posterior'],['presencial','con autorización','del episodio','y aviso al canal'])):
        with m.group(id):
            m.circle(x,1060,str(i+1),i==0)
            m.text(x,1124,a,28,True,anchor='middle')
            m.text(x,1165,b,28,anchor='middle')
    m.text(52,1216,'La contingencia tiene límites: no permite omitir controles.')
    m.line('M52 1243 H1148')
    m.text(52,1291,'03   El hotel conserva la responsabilidad',32,True)
    for id,x,y,title,body in [('ricardo',52,1344,'Ricardo','Autoriza la respuesta operativa.'),('lucia',635,1344,'Lucía','Registra lo ocurrido en Recepción.'),('federico',52,1440,'Federico','Conserva la traza técnica.'),('camila',635,1440,'Camila','Ajusta lo que promete el canal.')]:
        with m.group(id):
            m.text(x,y,title,30,True)
            m.text(x,y+38,body)
    with m.group('revision'):
        m.text(52,1533,'Revisar tras 20 ingresos o ante una identidad discutida.')
    m.line('M52 1560 H1148')
    m.text(52,1596,'Que cada servicio responda no garantiza que la familia pueda entrar.',24)
    m.save()


def n27():
    m=Map(27)
    m.header('Un mensaje válido', 'no alcanza para entregar la llave.', 'Hotel Horizonte · «Liberada» no quiere decir «asignable».',52)
    with m.group('distincion'):
        m.rect(52,270,1096,127)
        m.text(80,318,'Limpieza terminada ≠ habitación lista para entregar.',32,True)
        m.text(80,362,'También hay que comprobar la cerradura y las restricciones.')
    m.text(52,440,'CUATRO ACUERDOS SOBRE EL MISMO MENSAJE',24,True)
    rows=[
        ('forma','Forma','(sintaxis)','¿Tiene los datos necesarios?',['Campos, tipos y versión acordados.','La estructura correcta es sólo una parte.']),
        ('significado','Significado','(semántica)','¿Qué quiere decir «liberada»?',['La limpieza terminó. No afirma, por sí sola,','que se pueda entregar esa habitación.']),
        ('tiempo','Tiempo','(vigencia y orden)','¿Sigue siendo válido ahora?',['Un duplicado no repite la acción.','Una demora abre una verificación visible.']),
        ('accion','Acción','(operación)','¿Qué se hace si hay un problema?',['Definir quién decide, cómo se informa','la espera y quién corrige el error.']),
    ]
    # Each layer feeds a common acceptance condition, not the next layer.
    for i,(id,*_) in enumerate(rows):
        cy=548+i*204
        m.line(f'M1148 {cy} H1176',id='e-'+id)
    m.line('M1176 548 V1297 H600 V1320',True)
    for i,(id,title,term,question,body) in enumerate(rows):
        y=475+i*204
        with m.group(id):
            m.rect(52,y,1096,177,PALE if i%2==0 else PAPER)
            m.circle(93,y+52,str(i+1),i==0)
            m.text(145,y+61,title,34,True)
            m.text(145,y+104,term)
            m.line(f'M423 {y+23} V{y+154}')
            m.text(458,y+49,question,30,True)
            m.text(458,y+94,body[0])
            m.text(458,y+132,body[1])
    with m.group('aceptacion'):
        m.rect(52,1325,1096,161,PALE)
        m.parts.append(f'<rect x="52" y="1325" width="8" height="161" fill="{VOLT}"/>')
        m.text(80,1367,'EL CONTRATO ESTÁ COMPLETO CUANDO…',24,True)
        m.text(80,1420,'Todos anticipan la misma consecuencia',42,serif=True)
        m.text(80,1462,'y saben qué hacer ante errores, demoras o datos dudosos.')
    with m.group('prueba'):
        m.text(52,1537,'Prueba: duplicar, demorar, desordenar y cambiar la versión.')
    with m.group('revision'):
        m.text(52,1590,'Revisar tras 30 transiciones o ante una entrega incorrecta.',28)
    m.save()


def main():
    n24(); n26(); n27()
    cards=''.join(f'<article id="n{n}"><h2>N{n} · {html.escape(PLANS[n]["title"])}</h2><p>{html.escape(PLANS[n]["claim"])}</p><a href="N{n}/review.html"><img src="N{n}/N{n}-mapa-legible.svg" alt="{html.escape(PLANS[n]["alt"],quote=True)}"></a></article>' for n in PLANS)
    (OUT/'index.html').write_text('<!doctype html><html lang="es-AR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>METSI · Tres mapas para validar</title><style>body{background:#F7F6F2;color:#202020;font-family:Arial;margin:0}main{max-width:1480px;margin:0 auto;padding:36px}header{border-bottom:1px solid #999;padding-bottom:24px}h1{font:44px Georgia;margin:16px 0}p{line-height:1.6}nav a{color:#202020;margin-right:24px}section{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}h2{font-size:22px;min-height:80px}article>p{min-height:120px}img{display:block;width:100%;border:1px solid #ddd}a:focus-visible{outline:3px solid #202020}@media(max-width:1000px){section{grid-template-columns:1fr}h2,article>p{min-height:0}main{padding:18px}}</style><main><header><p>METSI · REVISIÓN EDITORIAL</p><h1>Tres mapas. Tres problemas diferentes.</h1><p>N24, N26 y N27. Más tamaño de lectura, menos texto comprimido y relaciones explícitas. Propuestas pendientes de aprobación; no modifican los PDF publicados.</p><nav><a href="#n24">N24 · Priorizar</a><a href="#n26">N26 · Dependencias</a><a href="#n27">N27 · Contratos</a></nav></header><section>'+cards+'</section></main>')


if __name__=='__main__':
    main()
