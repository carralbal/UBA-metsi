# Fuente editorial · N15 y N16, edición sin coma inicial

En la p. 3, el crédito bibliográfico de Peter Senge, *The Fifth Discipline*, comienza con una coma aislada antes de «Revised Edition. Currency · 2006». La corrección del 28/10/2026 quita únicamente el glifo inicial, sin reescribir el crédito. Al consolidar las fuentes fieles, eliminar esa coma del `<small>` correspondiente. El script de aplicación exacta al PDF público es `scripts/normalize_n15_n16_referentes_20261028.py`.

La fuente fiel y QA histórico de N15 están en `work/UBA-metsi-publication/output/source-recovery-20261024/N15-imac-source-private/working/N15/` y `pedagogy/N15/QA-DIGITAL-v3-20261024.md`. N16 conserva el paquete post-Cecilia `work/UBA-metsi-three-N-release-20261026/N16-v11-post-cecilia/`; no regenerar desde un HTML anterior que pierda las láminas y el caso C-107.
