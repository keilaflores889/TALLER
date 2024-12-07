from flask import current_app as app
from app.conexion.Conexion import Conexion


class RegistroCDao:

    def getRegistrosC(self):
        registrocSQL = """
        SELECT id_cita, id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta
        FROM cita
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registrocSQL)
            citas = cur.fetchall()  # Trae todos los datos de la consulta

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_cita': cita[0],
                    'id_paciente': cita[1],
                    'id_medico': cita[2],
                    'id_especialidad': cita[3],
                    'fecha_cita': cita[4],
                    'hora': cita[5],
                    'id_estado': cita[6],
                    'motivo_consulta': cita[7],
                
                }
                for cita in citas
            ]


        except Exception as e:
            app.logger.error(f"Error al obtener todas las citas: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getRegistroCById(self, id_cita):
        registrocSQL = """
       SELECT id_cita, id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta
        FROM cita
        WHERE id_cita=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registrocSQL, (id_cita,))
            cita = cur.fetchone()  # Obtener una sola fila
            if cita:
                return {
                    'id_cita': cita[0],
                    'id_paciente': cita[1],
                    'id_medico': cita[2],
                    'id_especialidad': cita[3],
                    'fecha_cita': cita[4],
                    'hora': cita[5],
                    'id_estado': cita[6],
                    'motivo_consulta': cita[7],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener cita por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarRegistroC(self, id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta):
        insertRegistrocSQL = """
        INSERT INTO cita (id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_cita
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertRegistrocSQL, (id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta))
            cita_id = cur.fetchone()[0]
            con.commit()
            return cita_id


        except Exception as e:
            app.logger.error(f"Error al insertar cita: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateRegistroC(self, id_cita, id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta):
        updateCitaSQL = """
        UPDATE cita
        SET id_cita=%s, id_paciente=%s, id_medico=%s, id_especialidad=%s, fecha_cita=%s, hora=%s, id_estado=%s, motivo_consulta=%s
        WHERE id_cita=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateCitaSQL, (id_cita, id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar cita: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteRegistroC(self, id_cita):
        deleteRegistrocSQL = """
        DELETE FROM cita
        WHERE id_cita=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteRegistrocSQL, (id_cita,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al eliminar cita: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
