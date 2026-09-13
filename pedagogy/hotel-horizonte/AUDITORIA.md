# Auditoría del sistema Hotel Horizonte

Fecha: 12 de septiembre de 2026.  
Estado: candidato piloto.

## Cobertura

- N01 a N36 cuentan con un microartefacto y una función acumulativa explícita.
- Los ocho bloques cuentan con un hito formal y una pregunta de enlace.
- El dossier conserva afirmaciones, decisiones, modelos, objeciones, deuda y versiones.
- La organización combina equipos estables, parejas temporales, roles rotativos y evidencia individual.
- La evaluación combina producto grupal, bitácora individual y revisión entre pares.
- La guía docente incluye perturbaciones, recuperación, accesibilidad y declaración de uso de IA.

## Decisiones pedagógicas cerradas para el piloto

1. Equipos de tres o cuatro integrantes durante todo el curso.
2. Ocho entregas formales, una por bloque, no treinta y seis entregas extensas.
3. Microartefactos por N integrados a un único dossier vivo y versionado.
4. Una bitácora individual por hito.
5. Revisión entre equipos antes de cada entrega formal.
6. Recuperación mediante nueva versión trazable, sin borrar la anterior.

## Verificación automática

Ejecutar:

```text
python3 pedagogy/hotel-horizonte/validate_hotel_horizonte.py
```

Resultado obtenido: `PASS`, nueve documentos troncales, ocho hitos, trazabilidad N01 a N36 y decisiones de agrupamiento presentes.

## Próxima prueba

Un profesor y dos ayudantes deben simular los hitos A y B con un equipo ficticio, medir carga y detectar cualquier dato que el sistema presuponga sin haberlo entregado como evidencia.
