from flask import current_app as app
from app.conexion.Conexion import Conexion


class AgendaDao:

    def getAgendas(self):
        agendaSQL = """
        SELECT am.id_agenda_medica, am.id_medico, am.id_dia, am.id_turno,
               m.nombre AS medico_nombre, m.apellido AS medico_apellido,
               d.descripcion AS dia, t.descripcion AS turno
        FROM agenda_medica am
        JOIN medico m ON am.id_medico = m.id_medico
        JOIN dia d ON am.id_dia = d.id_dia
        JOIN turno t ON am.id_turno = t.id_turno
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(agendaSQL)
            agendas = cur.fetchall()  # Trae todos los datos de la consulta

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_agenda_medica': agendas[0],
                    'id_medico': agendas[1],
                    'id_dia': agendas[2],
                    'id_turno': agendas[3],
                    'medico_nombre': agendas[4],
                    'medico_apellido': agendas[5],
                    'dia': agendas[6],
                    'turno': agendas[7],
                    
                }
                for agendas in agendas
            ]


        except Exception as e:
            app.logger.error(f"Error al obtener todas las agendas médicas: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getAgendaById(self, id_agenda_medica):
        agendaSQL = """
       SELECT am.id_agenda_medica, am.id_medico, am.id_dia, am.id_turno,
               m.nombre AS medico_nombre, m.apellido AS medico_apellido,
               d.descripcion AS dia, t.descripcion AS turno
        FROM agenda_medica am
        JOIN medico m ON am.id_medico = m.id_medico
        JOIN dia d ON am.id_dia = d.id_dia
        JOIN turno t ON am.id_turno = t.id_turno
        WHERE am.id_agenda_medica = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(agendaSQL, (id_agenda_medica,))
            agenda = cur.fetchone()  # Obtener una sola fila
            if agenda:
                return {
                    'id_agenda_medica': agenda[0],
                    'id_medico': agenda[1],
                    'id_dia': agenda[2],
                    'id_turno': agenda[3],
                    'medico_nombre': agenda[4],
                    'medico_apellido': agenda[5],
                    'dia': agenda[6],
                    'turno': agenda[7],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener agenda por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarAgenda(self, id_medico, id_dia, id_turno):
        insertAgendaSQL = """
        INSERT INTO agenda_medica (id_medico, id_dia, id_turno)
        VALUES (%s, %s, %s)
        RETURNING id_agenda_medica
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertAgendaSQL, (id_medico, id_dia, id_turno,))
            agenda_id = cur.fetchone()[0]
            con.commit()
            return agenda_id


        except Exception as e:
            app.logger.error(f"Error al insertar agenda: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateAgenda(self, id_agenda_medica, id_medico, id_dia, id_turno):
        updateAgendaSQL = """
        UPDATE agenda_medica
        SET id_medico=%s, id_dia=%s, id_turno=%s
        WHERE id_agenda_medica=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateAgendaSQL, (id_medico, id_dia, id_turno, id_agenda_medica,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar agenda: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteAgenda(self, id_agenda_medica):
        deleteAgendaSQL = """
        DELETE FROM agenda_medica
        WHERE id_agenda_medica=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteAgendaSQL, (id_agenda_medica,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al eliminar agenda: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
