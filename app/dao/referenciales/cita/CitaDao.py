from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime

class CitaDao:

    def getCitas(self):
        citaSQL = """
        SELECT id, nombrepaciente, motivoconsulta, medico, fecha, hora
        FROM citas
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(citaSQL)
            citas = cur.fetchall()  # Trae datos de la bd

            # Transformar los datos en una lista de diccionarios y convertir fecha/hora a cadena
            return [{
                'id': cita[0],
                'nombrepaciente': cita[1],
                'motivoconsulta': cita[2],
                'medico': cita[3],
                'fecha': cita[4].strftime('%Y-%m-%d') if cita[4] else None,  # Convertir fecha a string
                'hora': cita[5].strftime('%H:%M:%S') if cita[5] else None  # Convertir hora a string
            } for cita in citas]

        except Exception as e:
            app.logger.error(f"Error al obtener todas las citas: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getCitaById(self, id):
        citaSQL = """
        SELECT id, nombrepaciente, motivoconsulta, medico, fecha, hora
        FROM citas WHERE id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(citaSQL, (id,))
            citaEncontrada = cur.fetchone()  # Obtener una sola fila
            if citaEncontrada:
                return {
                    "id": citaEncontrada[0],
                    "nombrepaciente": citaEncontrada[1],
                    "motivoconsulta": citaEncontrada[2],
                    "medico": citaEncontrada[3],
                    "fecha": citaEncontrada[4].strftime('%Y-%m-%d') if citaEncontrada[4] else None,  # Convertir fecha
                    "hora": citaEncontrada[5].strftime('%H:%M:%S') if citaEncontrada[5] else None  # Convertir hora
                }  # Retornar los datos de la cita
            else:
                return None  # Retornar None si no se encuentra la cita
        except Exception as e:
            app.logger.error(f"Error al obtener cita: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarCita(self, nombrepaciente, motivoconsulta, medico, fecha, hora):
        insertCitaSQL = """
        INSERT INTO citas (nombrepaciente, motivoconsulta, medico, fecha, hora) 
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertCitaSQL, (nombrepaciente, motivoconsulta, medico, fecha, hora))
            cita_id = cur.fetchone()[0]
            con.commit()  # Confirmar la inserción
            return cita_id  # Retorna el id de la nueva cita

        except Exception as e:
            app.logger.error(f"Error al insertar cita: {str(e)}")
            con.rollback()  # Revertir si hubo error
            return False

        finally:
            cur.close()
            con.close()

    def updateCita(self, id, nombrepaciente, motivoconsulta, medico, fecha, hora):
        updateCitaSQL = """
        UPDATE citas
        SET nombrepaciente=%s, motivoconsulta=%s, medico=%s, fecha=%s, hora=%s
        WHERE id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateCitaSQL, (nombrepaciente, motivoconsulta, medico, fecha, hora, id,))
            filas_afectadas = cur.rowcount  # Obtener el número de filas afectadas
            con.commit()

            return filas_afectadas > 0  # Retornar True si se actualizó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al actualizar cita: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteCita(self, id):
        deleteCitaSQL = """
        DELETE FROM citas
        WHERE id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteCitaSQL, (id,))
            rows_affected = cur.rowcount
            con.commit()

            return rows_affected > 0  # Retornar True si se eliminó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al eliminar cita: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
