# Gate QA determinista · N11–N36 v3 editorial

## Contrato de ejecución

`validate_block_c_v2.py` es un gate de publicación de solo lectura. Audita los paquetes `N11-v3-editorial` a `N36-v3-editorial`, emite un objeto JSON Lines por paquete y no consulta la red ni toma un `qa-report.json` anterior como prueba. El resultado depende únicamente de los bytes presentes, del PDF renderizado y de los metadatos declarados. El nombre del validador se conserva por el alcance originalmente solicitado; el contrato efectivo queda fijado a la reconstrucción limpia v3.

```bash
python3 validate_block_c_v2.py --start 11 --end 36
```

Los límites son inclusivos y deben satisfacer `11 <= start <= end <= 36`. La salida es estable y portable: no contiene fecha, `mtime` ni rutas absolutas. El código de salida es `0` sólo si todos los paquetes pasan, `1` si existe al menos un `FAIL` y `2` si ocurre un error de ejecución. Un paquete ausente es `FAIL`, no se omite.

El gate toma una huella de todos los bytes del paquete antes y después de auditarlo. Si otro proceso cambia un archivo durante la ejecución, el paquete falla por instantánea inconsistente y debe repetirse cuando la reconstrucción haya quedado quieta.

Dependencias: Python, `numpy`, Pillow, `pdfplumber`, `pypdf` y `pdftoppm` de Poppler. Los paquetes se procesan de a uno y los raster temporales se eliminan al terminar.

## Criterios de aprobación por documento

Todos los controles son obligatorios.

1. **Paquete v3 y PDF nuevo.** Deben existir HTML, CSS, manifiestos, fuente empaquetada, PDF crudo v3 y PDF final v3. Ambos PDF deben abrir en modo estricto, el final debe terminar correctamente, no estar cifrado, ser distinto del crudo y tener exclusivamente páginas A4 dentro de una tolerancia de 1 punto.
2. **Cobertura canónica exacta.** El SHA-256 real de la fuente debe coincidir con `manifest.json`; `document.json` debe ser idéntico al manifiesto. La secuencia de `data-source-id` en HTML debe ser exactamente igual —misma cardinalidad, orden y unicidad— a `eligible_blocks`. Cada bloque debe dejar fragmentos verificables en la capa de texto del PDF. El informe de integridad sólo se contrasta; nunca sustituye estas mediciones.
3. **Sin repetición textual exacta.** Dos bloques sustantivos de doce palabras o más no pueden ser idénticos.
4. **Seis referentes reales.** Deben existir seis personas nominalmente distintas y seis fichas HTML, cada una con un raster local distinto, decodificable, hash correcto y texto alternativo. Se prohíben monogramas, iniciales, `portrait-unavailable`, perfiles sin foto, imágenes generadas y sustituciones de identidad.
5. **Créditos y derechos fail-closed.** Cada retrato debe tener página de identidad/fuente HTTPS, creador o línea de crédito, nombre y URL HTTPS de licencia, estado de derechos no pendiente y evidencia aprobada. La evidencia puede estar en el registro del retrato, en `image-rights-manifest.json`, en `portrait-registry.json` o en un `portrait-sources*.md`; debe corresponder al mismo nombre y, cuando se declara, al mismo hash. Una procedencia heredada sin derechos reconfirmados falla.
6. **Pausas y cierre.** Deben existir exactamente dos pausas internas, la primera físicamente en p5. La tapa, p4, ambas pausas y la última página deben alcanzar los cuatro bordes en la geometría PDF y no mostrar canaletas blancas en el raster. P4 debe ser una apertura oscura real. La última página debe usar el activo de fósforos, conservar alt, leyenda, folio y pie.
7. **Hotel Horizonte.** Fuente, HTML y PDF deben nombrar `Hotel Horizonte` y el artefacto correspondiente `HH-NN`.
8. **Contenido, índice y rutas.** Los H2 canónicos, las secciones numeradas, sus títulos y el índice de p2 deben coincidir en cantidad y orden. Cada sección debe declarar una de las seis rutas METSI, las seis deben estar presentes y la secuencia HTML debe coincidir con la extraída del PDF.
9. **Títulos acompañados.** Cada H2, H3 y H4 debe compartir página física con el primer bloque sustantivo que le sigue.
10. **Medios cerrados.** Toda imagen informativa debe resolver dentro del paquete, decodificar, tener alt, estar inventariada y coincidir con un único SHA-256 declarado. Los retratos recurrentes de Hotel Horizonte pueden declararse decorativos únicamente cuando el mismo componente imprime junto a cada imagen el nombre y el rol completos; en ese caso usan `alt=""` y `aria-hidden="true"` para evitar una lectura redundante. También se validan referencias locales de HTML/CSS y se rechaza cualquier escape de directorio.
11. **Sin plantillas visibles ni repetición exacta.** Se rechazan contact sheets, support sheets, monogramas, fuentes de imagen reutilizadas, medios distintos con bytes idénticos y páginas raster byte a byte repetidas. Las palabras académicas normales —por ejemplo, “plantilla” dentro de una crítica conceptual— no disparan este control.
12. **Infografías justificadas y distintas.** Debe existir una o, cuando el argumento realmente lo requiere, dos infografías SVG usadas una vez. Sus familias y hashes deben ser distintos y no vacíos. No se completa una cuota visual repitiendo diagramas genéricos. Cada hash debe coincidir con el archivo. El SVG debe ser XML válido, tener `viewBox`, contener sus etiquetas declaradas, no usar `foreignObject` ni elipsis de truncación y no superponer textos o formas semánticas en coordenadas exactamente iguales.
13. **Sin placeholders, LFS ni rutas privadas.** Se inspeccionan todos los archivos textuales y cabeceras de todos los archivos del paquete. Se bloquean punteros Git LFS, marcadores de trabajo pendiente, fallbacks visibles y rutas de usuario, temporales o `file://`.
14. **PDF accesible.** El catálogo debe declarar `/Lang es-AR`, `/Marked true` y `/StructTreeRoot`; el HTML debe declarar `es-AR`. Cada alt de imagen visible debe aparecer en una figura semántica del PDF.
15. **URLs completas y anotadas.** Todas las URL HTTPS de la fuente deben aparecer completas en la capa de texto y como anotaciones URI exactas. No puede faltar ni sobrar una URL externa; todas deben estar confinadas a las páginas de Referencias base. El enlace de pie se trata por separado.
16. **Folios y pie.** Todas las páginas deben incluir el folio físico de dos dígitos, la línea `Diego Carralbal, 2026 · linkedin.com/in/carralbal` y exactamente una anotación al perfil del autor.
17. **Densidad raster.** Toda página ordinaria debe ocupar al menos el 55 % de la altura física según filas de tinta del raster a 72 dpi. Se excluyen estructuralmente tapa, Contenido, Referentes, p4, las dos pausas y el cierre. Una excepción adicional sólo se acepta si `manifest.json` declara `density_exceptions` como lista de objetos con `page`, un `role` permitido y una justificación sustantiva de al menos 24 caracteres. Las funciones admitidas son `orientation_apparatus`, `reference_apparatus`, `assessment_apparatus` y `accessibility_apparatus`; una declaración inválida hace fallar el gate.
18. **Sin vacíos ni recortes.** Ninguna página puede estar vacía en objetos PDF o en raster, y ninguna palabra extraída puede quedar fuera de la caja física.
19. **Registro editorial.** La fuente no puede dirigirse personalmente al lector mediante pronombres o formas directas tipificadas, ni usar raya em o raya en rodeada de espacios como inciso. Los guiones internos y los rangos bibliográficos permanecen permitidos.

## Evidencia y límites deliberados

El gate detecta colisiones exactas y truncación estructural en SVG; no afirma reemplazar una revisión humana de legibilidad perceptual. El análisis de sangrado combina geometría PDF —prueba principal— con raster para detectar canaletas blancas; una fotografía naturalmente clara en el borde no se confunde con margen si la geometría llega al corte. La identidad real y los derechos de retrato se prueban mediante manifiestos explícitos y no mediante reconocimiento facial o inferencias de red.

Un `PASS` no puede obtenerse escribiendo valores de aprobación en un informe: página, hashes, IDs, texto, imágenes, enlaces, estructura y densidad se vuelven a calcular en cada ejecución.
