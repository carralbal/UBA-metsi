-- N16 · Reglas de ensayo añadidas al prototipo v1, sólo en memoria privada.
-- Hipótesis explícita P1: una observación ACTIVA bloquea Resuelto.
-- No es una política institucional aprobada ni un esquema de producción.

CREATE TRIGGER v2_observacion_activa_bloquea_resuelto
BEFORE INSERT ON CAMBIO_ESTADO
WHEN NEW.estado_nuevo='Resuelto'
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1 FROM OBSERVACION o
    WHERE o.id_tramite=NEW.id_tramite AND o.estado='ACTIVA'
  ) THEN RAISE(ABORT,'P1: observacion activa bloquea resolucion') END;
END;

CREATE TRIGGER v2_tramite_nace_recibido
BEFORE INSERT ON TRAMITE
WHEN NEW.estado_actual<>'Recibido'
BEGIN
  SELECT RAISE(ABORT,'tramite debe nacer Recibido');
END;

CREATE TRIGGER v2_estado_visible_exige_ultimo_cambio
BEFORE UPDATE OF estado_actual ON TRAMITE
WHEN NEW.estado_actual<>OLD.estado_actual
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM CAMBIO_ESTADO ce
    WHERE ce.rowid=(
      SELECT max(ce2.rowid) FROM CAMBIO_ESTADO ce2
      WHERE ce2.id_tramite=OLD.id_tramite
    )
      AND ce.id_tramite=OLD.id_tramite
      AND ce.estado_anterior=OLD.estado_actual
      AND ce.estado_nuevo=NEW.estado_actual
  ) THEN RAISE(ABORT,'estado visible sin ultimo cambio registrado') END;
END;

CREATE TRIGGER v2_contestada_exige_respuesta
BEFORE UPDATE OF estado ON OBSERVACION
WHEN NEW.estado='CONTESTADA' AND OLD.estado<>'CONTESTADA'
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM RESPUESTA r
    WHERE r.id_tramite=NEW.id_tramite
      AND r.id_observacion=NEW.id_observacion
  ) THEN RAISE(ABORT,'observacion contestada sin respuesta') END;
END;

CREATE TRIGGER v2_cambio_posterior_a_entrega
BEFORE INSERT ON CAMBIO_ESTADO
WHEN NEW.estado_nuevo IN ('Requiere acción','Resuelto')
BEGIN
  SELECT CASE WHEN NEW.estado_nuevo='Requiere acción' AND NOT EXISTS (
    SELECT 1 FROM OBSERVACION o JOIN AVISO a
      ON a.id_observacion=o.id_observacion
    WHERE o.id_tramite=NEW.id_tramite AND o.estado='ACTIVA'
      AND a.id_tramite=NEW.id_tramite
      AND a.finalidad='OBSERVACION'
      AND a.resultado_entrega='ENTREGADO'
      AND strftime('%s',a.fecha_entrega_verificada)<=strftime('%s',NEW.fecha)
  ) THEN RAISE(ABORT,'requiere accion anterior a entrega verificada') END;
  SELECT CASE WHEN NEW.estado_nuevo='Resuelto' AND NOT EXISTS (
    SELECT 1 FROM DECISION d JOIN AVISO a ON a.id_decision=d.id_decision
    WHERE d.id_tramite=NEW.id_tramite AND a.id_tramite=NEW.id_tramite
      AND a.finalidad='DECISION'
      AND a.resultado_entrega='ENTREGADO'
      AND strftime('%s',d.fecha_firma)<=strftime('%s',a.fecha_entrega_verificada)
      AND strftime('%s',a.fecha_entrega_verificada)<=strftime('%s',NEW.fecha)
  ) THEN RAISE(ABORT,'resuelto anterior a entrega verificada') END;
END;
