-- N16 · Prototipo relacional ejecutable de los nueve hechos de constancias.
-- Caso ficticio; SQLite sólo para prueba docente privada. No es esquema de producción.
-- C-106 se prueba en bases separadas con politica EPISODIO o INTENTO; no se adopta ninguna.
PRAGMA foreign_keys = ON;

CREATE TABLE PERSONA (
  id_persona TEXT PRIMARY KEY
);

CREATE TABLE TRAMITE (
  id_tramite TEXT PRIMARY KEY,
  id_persona TEXT NOT NULL REFERENCES PERSONA(id_persona),
  estado_actual TEXT NOT NULL DEFAULT 'Recibido'
    CHECK (estado_actual IN ('Recibido','En revisión','Requiere acción','Resuelto','Baja registrada')),
  UNIQUE (id_tramite, id_persona)
);

CREATE TABLE CAMBIO_ESTADO (
  id_cambio TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL REFERENCES TRAMITE(id_tramite),
  estado_anterior TEXT NOT NULL,
  estado_nuevo TEXT NOT NULL,
  fecha TEXT NOT NULL,
  actor TEXT NOT NULL
);

CREATE TABLE OBSERVACION (
  id_observacion TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL REFERENCES TRAMITE(id_tramite),
  estado TEXT NOT NULL DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA','CONTESTADA')),
  UNIQUE (id_observacion, id_tramite)
);
CREATE UNIQUE INDEX una_observacion_activa_por_tramite
  ON OBSERVACION(id_tramite) WHERE estado='ACTIVA';

CREATE TABLE RESPUESTA (
  id_respuesta TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL,
  id_observacion TEXT NOT NULL,
  id_persona TEXT NOT NULL,
  fecha_recepcion TEXT NOT NULL,
  referencia_contenido TEXT NOT NULL,
  canal TEXT NOT NULL,
  clave_idempotencia TEXT NOT NULL,
  FOREIGN KEY (id_observacion,id_tramite) REFERENCES OBSERVACION(id_observacion,id_tramite),
  FOREIGN KEY (id_tramite,id_persona) REFERENCES TRAMITE(id_tramite,id_persona),
  UNIQUE (id_observacion,clave_idempotencia)
);

CREATE TABLE DECISION (
  id_decision TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL UNIQUE REFERENCES TRAMITE(id_tramite),
  resultado TEXT NOT NULL,
  fecha_firma TEXT NOT NULL,
  UNIQUE (id_decision,id_tramite)
);

CREATE TABLE BAJA (
  id_baja TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL UNIQUE REFERENCES TRAMITE(id_tramite),
  fecha_registro TEXT NOT NULL,
  actor TEXT NOT NULL
);

CREATE TABLE AVISO (
  id_aviso TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL,
  id_destinatario TEXT NOT NULL,
  finalidad TEXT NOT NULL CHECK (finalidad IN ('OBSERVACION','DECISION')),
  id_observacion TEXT,
  id_decision TEXT,
  canal TEXT NOT NULL,
  fecha_generacion TEXT NOT NULL,
  resultado_entrega TEXT NOT NULL CHECK (resultado_entrega IN ('FALLIDO','ENTREGADO')),
  fecha_entrega_verificada TEXT,
  CHECK (
    (finalidad='OBSERVACION' AND id_observacion IS NOT NULL AND id_decision IS NULL)
    OR (finalidad='DECISION' AND id_decision IS NOT NULL AND id_observacion IS NULL)
  ),
  CHECK (
    (resultado_entrega='FALLIDO' AND fecha_entrega_verificada IS NULL)
    OR (resultado_entrega='ENTREGADO' AND fecha_entrega_verificada IS NOT NULL)
  ),
  FOREIGN KEY (id_tramite,id_destinatario) REFERENCES TRAMITE(id_tramite,id_persona),
  FOREIGN KEY (id_observacion,id_tramite) REFERENCES OBSERVACION(id_observacion,id_tramite),
  FOREIGN KEY (id_decision,id_tramite) REFERENCES DECISION(id_decision,id_tramite)
);

CREATE TABLE REPARACION (
  id_reparacion TEXT PRIMARY KEY,
  id_tramite TEXT NOT NULL,
  id_destinatario TEXT NOT NULL,
  finalidad TEXT NOT NULL CHECK (finalidad IN ('OBSERVACION','DECISION')),
  id_observacion TEXT,
  id_decision TEXT,
  politica TEXT NOT NULL CHECK (politica IN ('EPISODIO','INTENTO')),
  id_aviso_fallido_inicial TEXT NOT NULL REFERENCES AVISO(id_aviso),
  responsable TEXT NOT NULL CHECK (length(trim(responsable))>0),
  fecha_apertura TEXT NOT NULL,
  estado TEXT NOT NULL DEFAULT 'ABIERTA' CHECK (estado IN ('ABIERTA','CERRADA')),
  id_aviso_cierre TEXT REFERENCES AVISO(id_aviso),
  fecha_cierre TEXT,
  CHECK (
    (finalidad='OBSERVACION' AND id_observacion IS NOT NULL AND id_decision IS NULL)
    OR (finalidad='DECISION' AND id_decision IS NOT NULL AND id_observacion IS NULL)
  ),
  CHECK (
    (estado='ABIERTA' AND id_aviso_cierre IS NULL AND fecha_cierre IS NULL)
    OR (estado='CERRADA' AND id_aviso_cierre IS NOT NULL AND fecha_cierre IS NOT NULL)
  ),
  FOREIGN KEY (id_tramite,id_destinatario) REFERENCES TRAMITE(id_tramite,id_persona),
  FOREIGN KEY (id_observacion,id_tramite) REFERENCES OBSERVACION(id_observacion,id_tramite),
  FOREIGN KEY (id_decision,id_tramite) REFERENCES DECISION(id_decision,id_tramite)
);
CREATE UNIQUE INDEX un_episodio_abierto_por_observacion
  ON REPARACION(id_tramite,id_destinatario,id_observacion)
  WHERE politica='EPISODIO' AND estado='ABIERTA' AND finalidad='OBSERVACION';
CREATE UNIQUE INDEX un_episodio_abierto_por_decision
  ON REPARACION(id_tramite,id_destinatario,id_decision)
  WHERE politica='EPISODIO' AND estado='ABIERTA' AND finalidad='DECISION';
CREATE UNIQUE INDEX un_fallo_inicial_por_reparacion_de_intento
  ON REPARACION(id_aviso_fallido_inicial) WHERE politica='INTENTO';

-- Tabla de relación: no añade un décimo hecho del dominio; registra qué intentos
-- pertenecen a la reparación y deja coexistir ambos diseños C-106 en pruebas separadas.
CREATE TABLE REPARACION_AVISO (
  id_reparacion TEXT NOT NULL REFERENCES REPARACION(id_reparacion),
  id_aviso TEXT NOT NULL REFERENCES AVISO(id_aviso),
  PRIMARY KEY (id_reparacion,id_aviso)
);

CREATE TRIGGER respuesta_exige_observacion_entregada
BEFORE INSERT ON RESPUESTA
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM AVISO a
    WHERE a.id_tramite=NEW.id_tramite AND a.id_destinatario=NEW.id_persona
      AND a.id_observacion=NEW.id_observacion AND a.finalidad='OBSERVACION'
      AND a.resultado_entrega='ENTREGADO'
  ) THEN RAISE(ABORT,'respuesta sin observacion entregada') END;
END;

CREATE TRIGGER reparacion_exige_fallo_del_mismo_objeto
BEFORE INSERT ON REPARACION
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM AVISO a WHERE a.id_aviso=NEW.id_aviso_fallido_inicial
      AND a.id_tramite=NEW.id_tramite AND a.id_destinatario=NEW.id_destinatario
      AND a.finalidad=NEW.finalidad AND a.id_observacion IS NEW.id_observacion
      AND a.id_decision IS NEW.id_decision AND a.resultado_entrega='FALLIDO'
  ) THEN RAISE(ABORT,'reparacion sin fallo del mismo objeto') END;
END;
CREATE TRIGGER reparacion_registra_primer_intento
AFTER INSERT ON REPARACION
BEGIN
  INSERT INTO REPARACION_AVISO(id_reparacion,id_aviso)
    VALUES (NEW.id_reparacion,NEW.id_aviso_fallido_inicial);
END;
CREATE TRIGGER intento_de_reparacion_mismo_objeto
BEFORE INSERT ON REPARACION_AVISO
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM REPARACION r JOIN AVISO a ON a.id_aviso=NEW.id_aviso
    WHERE r.id_reparacion=NEW.id_reparacion AND r.id_tramite=a.id_tramite
      AND r.id_destinatario=a.id_destinatario AND r.finalidad=a.finalidad
      AND r.id_observacion IS a.id_observacion AND r.id_decision IS a.id_decision
  ) THEN RAISE(ABORT,'intento de otra persona, tramite u objeto') END;
  SELECT CASE WHEN (
    SELECT r.politica FROM REPARACION r WHERE r.id_reparacion=NEW.id_reparacion
  )='INTENTO' AND (
    SELECT a.resultado_entrega FROM AVISO a WHERE a.id_aviso=NEW.id_aviso
  )='FALLIDO' AND EXISTS (
    SELECT 1 FROM REPARACION_AVISO ra JOIN AVISO a ON a.id_aviso=ra.id_aviso
    WHERE ra.id_reparacion=NEW.id_reparacion AND a.resultado_entrega='FALLIDO'
  ) THEN RAISE(ABORT,'politica por intento admite un solo fallo') END;
END;

CREATE TRIGGER cierre_reparacion_exige_entrega_valida
BEFORE UPDATE OF estado,id_aviso_cierre,fecha_cierre ON REPARACION
WHEN NEW.estado='CERRADA'
BEGIN
  SELECT CASE WHEN OLD.estado<>'ABIERTA' THEN RAISE(ABORT,'reparacion ya cerrada') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM AVISO a WHERE a.id_aviso=NEW.id_aviso_cierre
      AND a.id_tramite=NEW.id_tramite AND a.id_destinatario=NEW.id_destinatario
      AND a.finalidad=NEW.finalidad AND a.id_observacion IS NEW.id_observacion
      AND a.id_decision IS NEW.id_decision AND a.resultado_entrega='ENTREGADO'
      AND strftime('%s',a.fecha_entrega_verificada)<=strftime('%s',NEW.fecha_cierre)
  ) THEN RAISE(ABORT,'cierre sin entrega valida del mismo objeto') END;
END;
CREATE TRIGGER cierre_reparacion_registra_aviso
AFTER UPDATE OF estado ON REPARACION
WHEN NEW.estado='CERRADA'
BEGIN
  INSERT INTO REPARACION_AVISO(id_reparacion,id_aviso)
    VALUES (NEW.id_reparacion,NEW.id_aviso_cierre);
END;

CREATE TRIGGER cambio_estado_exige_evidencia
BEFORE INSERT ON CAMBIO_ESTADO
BEGIN
  SELECT CASE WHEN NEW.estado_anterior<>(
    SELECT t.estado_actual FROM TRAMITE t WHERE t.id_tramite=NEW.id_tramite
  ) THEN RAISE(ABORT,'estado anterior no coincide') END;
  SELECT CASE WHEN NOT (
    (NEW.estado_anterior='Recibido' AND NEW.estado_nuevo IN ('En revisión','Baja registrada')) OR
    (NEW.estado_anterior='En revisión' AND NEW.estado_nuevo IN ('Requiere acción','Resuelto','Baja registrada')) OR
    (NEW.estado_anterior='Requiere acción' AND NEW.estado_nuevo IN ('En revisión','Baja registrada'))
  ) THEN RAISE(ABORT,'transicion no permitida') END;
  SELECT CASE WHEN NEW.estado_nuevo='Requiere acción' AND NOT EXISTS (
    SELECT 1 FROM OBSERVACION o JOIN AVISO a ON a.id_observacion=o.id_observacion
    WHERE o.id_tramite=NEW.id_tramite AND o.estado='ACTIVA'
      AND a.id_tramite=NEW.id_tramite AND a.finalidad='OBSERVACION'
      AND a.resultado_entrega='ENTREGADO'
  ) THEN RAISE(ABORT,'requiere accion sin entrega de observacion activa') END;
  SELECT CASE WHEN NEW.estado_nuevo='Resuelto' AND NOT EXISTS (
    SELECT 1 FROM DECISION d JOIN AVISO a ON a.id_decision=d.id_decision
    WHERE d.id_tramite=NEW.id_tramite AND a.id_tramite=NEW.id_tramite
      AND a.finalidad='DECISION' AND a.resultado_entrega='ENTREGADO'
      AND strftime('%s',d.fecha_firma)<=strftime('%s',a.fecha_entrega_verificada)
  ) THEN RAISE(ABORT,'resuelto sin firma y comunicacion valida') END;
  SELECT CASE WHEN NEW.estado_nuevo='Baja registrada' AND NOT EXISTS (
    SELECT 1 FROM BAJA b WHERE b.id_tramite=NEW.id_tramite
  ) THEN RAISE(ABORT,'baja sin registro') END;
  SELECT CASE WHEN NEW.estado_nuevo='En revisión' AND NEW.estado_anterior='Requiere acción'
    AND NOT EXISTS (
      SELECT 1 FROM OBSERVACION o JOIN RESPUESTA r ON r.id_observacion=o.id_observacion
      WHERE o.id_tramite=NEW.id_tramite AND o.estado='ACTIVA'
    ) THEN RAISE(ABORT,'retorno sin respuesta de observacion activa') END;
END;
CREATE TRIGGER cambio_estado_actualiza_consulta
AFTER INSERT ON CAMBIO_ESTADO
BEGIN
  UPDATE TRAMITE SET estado_actual=NEW.estado_nuevo WHERE id_tramite=NEW.id_tramite;
END;
