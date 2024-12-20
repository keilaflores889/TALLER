from flask import current_app as app
from app.conexion.Conexion import Conexion


class AgendaDao:

    def getAgendas(self):
        agendaSQL = """
        SELECT id_agenda_medica, nombre_medico, dia, turno
        FROM agenda_medica
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(agendaSQL)
            resultados = cur.fetchall()  # Trae todos los datos de la consulta

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_agenda_medica': fila[0],
                    'nombre_medico': fila[1],
                    'dia': fila[2],
                    'turno': fila[3],
                }
                for fila in resultados
            ]


        except Exception as e:
            app.logger.error(f"Error al obtener todas las agendas médicas: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getAgendaById(self, id_agenda_medica):
        agendaSQL = """
        SELECT id_agenda_medica, nombre_medico, dia, turno
        FROM agenda_medica
        WHERE id_agenda_medica=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(agendaSQL, (id_agenda_medica,))
            fila = cur.fetchone()  # Obtener una sola fila
            if fila:
                return {
                    "id_agenda_medica": fila[0],
                    "nombre_medico": fila[1],
                    "dia": fila[2],
                    "turno": fila[3],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener agenda por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarAgenda(self, nombre_medico, dia, turno):
        insertAgendaSQL = """
        INSERT INTO agenda_medica (nombre_medico, dia, turno)
        VALUES (%s, %s, %s)
        RETURNING id_agenda_medica
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertAgendaSQL, (nombre_medico, dia, turno))
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

    def updateAgenda(self, id_agenda_medica, nombre_medico, dia, turno):
        updateAgendaSQL = """
        UPDATE agenda_medica
        SET nombre_medico=%s, dia=%s, turno=%s
        WHERE id_agenda_medica=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateAgendaSQL, (nombre_medico, dia, turno, id_agenda_medica))
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
