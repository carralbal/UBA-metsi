-- N16, supuesto didáctico A: episodio único de reparación por objeto/finalidad.
-- Capa privada sobre ER-nueve-hechos-base.sql y ER-reglas-P1-v2.sql.
-- No es la política institucional ni esquema listo para producción.

CREATE TRIGGER v3_solo_episodio
BEFORE INSERT ON REPARACION
WHEN NEW.politica <> 'EPISODIO'
BEGIN
  SELECT RAISE(ABORT,'A: esta candidata no admite reparacion por intento');
END;

CREATE TRIGGER v3_respuesta_sigue_estado_entregado
BEFORE INSERT ON RESPUESTA
WHEN (SELECT t.estado_actual FROM TRAMITE t WHERE t.id_tramite=NEW.id_tramite)<>'Requiere acción'
BEGIN
  SELECT RAISE(ABORT,'respuesta antes de estado habilitado por entrega');
END;

CREATE TRIGGER v3_reparacion_de_observacion_activa
BEFORE INSERT ON REPARACION
WHEN NEW.finalidad='OBSERVACION' AND NOT EXISTS (
  SELECT 1 FROM OBSERVACION o
  WHERE o.id_observacion=NEW.id_observacion
    AND o.id_tramite=NEW.id_tramite AND o.estado='ACTIVA'
)
BEGIN
  SELECT RAISE(ABORT,'reparacion de observacion no activa');
END;

CREATE TRIGGER v3_estado_exige_reparacion_cerrada
BEFORE INSERT ON CAMBIO_ESTADO
WHEN NEW.estado_nuevo IN ('Requiere acción','Resuelto')
BEGIN
  SELECT CASE WHEN NEW.estado_nuevo='Requiere acción' AND EXISTS (
    SELECT 1 FROM REPARACION r
    WHERE r.id_tramite=NEW.id_tramite
      AND r.finalidad='OBSERVACION' AND r.estado='ABIERTA'
  ) THEN RAISE(ABORT,'A: observacion con reparacion abierta') END;
  SELECT CASE WHEN NEW.estado_nuevo='Resuelto' AND EXISTS (
    SELECT 1 FROM REPARACION r
    WHERE r.id_tramite=NEW.id_tramite AND r.estado='ABIERTA'
  ) THEN RAISE(ABORT,'A: tramite con reparacion abierta') END;
END;
