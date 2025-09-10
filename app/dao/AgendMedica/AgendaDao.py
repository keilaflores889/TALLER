# AgendaDao.py
from flask import current_app as app
from app.conexion.Conexion import Conexion

class AgendaDao:

    # Listar todas las agendas
    def getAgendas(self):
        sql = """
        SELECT a.id_agenda_medica,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               d.descripcion AS dia,
               t.descripcion AS turno,
               e.descripcion AS especialidad,
               c.codigo AS consultorio_id,
               c.nombre_consultorio AS consultorio_nombre,
               p.id_personal,
               p.nombre || ' ' || p.apellido AS personal_nombre,
               a.horario_disponible,
               a.cupos,
               a.estado,
               a.fecha_agenda,
               a.id_medico,
               a.id_dia,
               a.id_turno,
               a.id_especialidad
        FROM agenda_medica a
        JOIN medico m ON a.id_medico = m.id_medico
        JOIN dia d ON a.id_dia = d.id_dia
        JOIN turno t ON a.id_turno = t.id_turno
        JOIN especialidad e ON a.id_especialidad = e.id_especialidad
        JOIN consultorio c ON a.codigo = c.codigo
        JOIN personal p ON a.id_personal = p.id_personal
        ORDER BY a.id_agenda_medica;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            app.logger.error(f"Error al obtener agendas: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener una agenda por id
    def getAgendaById(self, id_agenda):
        sql = """
        SELECT a.id_agenda_medica,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               d.descripcion AS dia,
               t.descripcion AS turno,
               e.descripcion AS especialidad,
               c.codigo AS consultorio_id,
               c.nombre_consultorio AS consultorio_nombre,
               p.id_personal,
               p.nombre || ' ' || p.apellido AS personal_nombre,
               a.horario_disponible,
               a.cupos,
               a.estado,
               a.fecha_agenda,
               a.id_medico,
               a.id_dia,
               a.id_turno,
               a.id_especialidad
        FROM agenda_medica a
        JOIN medico m ON a.id_medico = m.id_medico
        JOIN dia d ON a.id_dia = d.id_dia
        JOIN turno t ON a.id_turno = t.id_turno
        JOIN especialidad e ON a.id_especialidad = e.id_especialidad
        JOIN consultorio c ON a.codigo = c.codigo
        JOIN personal p ON a.id_personal = p.id_personal
        WHERE a.id_agenda_medica = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_agenda,))
            row = cur.fetchone()
            if row:
                columnas = [desc[0] for desc in cur.description]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener agenda {id_agenda}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # ==============================
    # Validar duplicado antes de insertar o actualizar
    # ==============================
    def existeDuplicado(self, id_medico, id_dia, id_turno, codigo,
                         fecha_agenda=None, horario_disponible=None, id_agenda=None):
        sql = """
        SELECT COUNT(*)
        FROM agenda_medica
        WHERE id_medico = %s
          AND id_dia = %s
          AND id_turno = %s
          AND codigo = %s
        """
        params = [id_medico, id_dia, id_turno, codigo]

        if fecha_agenda:
            sql += " AND fecha_agenda = %s"
            params.append(fecha_agenda)
        if horario_disponible:
            sql += " AND horario_disponible = %s"
            params.append(horario_disponible)
        if id_agenda:
            sql += " AND id_agenda_medica != %s"
            params.append(id_agenda)

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, tuple(params))
            return cur.fetchone()[0] > 0
        except Exception as e:
            app.logger.error(f"Error al validar duplicado: {e}")
            return True
        finally:
            cur.close()
            con.close()

    # Agregar una agenda
    def addAgenda(self, agenda):
        if self.existeDuplicado(
            agenda['id_medico'],
            agenda['id_dia'],
            agenda['id_turno'],
            agenda['codigo'],
            fecha_agenda=agenda.get('fecha_agenda'),
            horario_disponible=agenda.get('horario_disponible')
        ):
            app.logger.warning("Intento de duplicado detectado")
            return None

        sql = """
        INSERT INTO agenda_medica (
            id_medico, id_dia, id_turno, codigo, id_personal, id_especialidad,
            fecha_agenda, horario_disponible, cupos, estado
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_agenda_medica;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                agenda['id_medico'],
                agenda['id_dia'],
                agenda['id_turno'],
                agenda['codigo'],
                agenda['id_personal'],
                agenda['id_especialidad'],
                agenda.get('fecha_agenda'),
                agenda.get('horario_disponible', ''),
                agenda.get('cupos', 0),
                agenda.get('estado', True)
            ))
            id_agenda = cur.fetchone()[0]
            con.commit()
            return id_agenda
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al agregar agenda: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # Actualizar agenda
    def updateAgenda(self, id_agenda, agenda):
        if self.existeDuplicado(
            agenda['id_medico'],
            agenda['id_dia'],
            agenda['id_turno'],
            agenda['codigo'],
            fecha_agenda=agenda.get('fecha_agenda'),
            horario_disponible=agenda.get('horario_disponible'),
            id_agenda=id_agenda
        ):
            app.logger.warning(f"Intento de duplicado detectado al actualizar {id_agenda}")
            return False

        sql = """
        UPDATE agenda_medica SET
            id_medico = %s,
            id_dia = %s,
            id_turno = %s,
            codigo = %s,
            id_personal = %s,
            id_especialidad = %s,
            horario_disponible = %s,
            cupos = %s,
            estado = %s,
            fecha_agenda = %s
        WHERE id_agenda_medica = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                agenda['id_medico'],
                agenda['id_dia'],
                agenda['id_turno'],
                agenda['codigo'],
                agenda['id_personal'],
                agenda['id_especialidad'],
                agenda.get('horario_disponible', ''),
                agenda.get('cupos', 0),
                agenda.get('estado', True),
                agenda.get('fecha_agenda'),
                id_agenda
            ))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar agenda {id_agenda}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    # Eliminar agenda
    def deleteAgenda(self, id_agenda):
        sql = "DELETE FROM agenda_medica WHERE id_agenda_medica = %s;"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_agenda,))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar agenda {id_agenda}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    # ==============================
    #   Disponibilidades de médico
    # ==============================
    def getDisponibilidadesPorMedicoFecha(self, id_medico, fecha):
        sql = """
        SELECT id_disponibilidad, disponibilidad_hora_inicio, disponibilidad_hora_fin, disponibilidad_cupos
        FROM disponibilidad_horaria
        WHERE id_medico = %s AND disponibilidad_fecha = %s
        ORDER BY disponibilidad_hora_inicio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico, fecha))
            rows = cur.fetchall()
            return [
                {
                    'id_disponibilidad': r[0],
                    'disponibilidad_hora_inicio': str(r[1]),
                    'disponibilidad_hora_fin': str(r[2]),
                    'disponibilidad_cupos': r[3]
                } for r in rows
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidades por médico y fecha: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getDisponibilidadById(self, id_disponibilidad):
        sql = """
        SELECT id_disponibilidad,
               id_medico,
               disponibilidad_hora_inicio,
               disponibilidad_hora_fin,
               disponibilidad_fecha,
               disponibilidad_cupos
        FROM disponibilidad_horaria
        WHERE id_disponibilidad = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_disponibilidad,))
            row = cur.fetchone()
            if row:
                columnas = [desc[0] for desc in cur.description]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            app.logger.error(f"Error en getDisponibilidadById({id_disponibilidad}): {e}")
            return None
        finally:
            cur.close()
            con.close()
