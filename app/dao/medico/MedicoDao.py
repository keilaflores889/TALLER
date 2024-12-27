from flask import current_app as app
from app.conexion.Conexion import Conexion


class MedicoDao:

    def getMedicos(self):
        medicoSQL = """
       SELECT m.id_medico, m.nombre, m.apellido, m.id_especialidad, m.num_registro, e.descripcion AS especialidad
       FROM medico m
       JOIN especialidad e ON m.id_especialidad = e.id_especialidad
       """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(medicoSQL)
            medicos = cur.fetchall()  # Trae todos los datos de la consulta

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_medico': medico[0],
                    'nombre': medico[1],
                    'apellido': medico[2],
                    'id_especialidad': medico[3],
                    'num_registro': medico[4],
                    'especialidad': medico[5],
                }
                for medico in medicos
            ]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los médicos: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getMedicoById(self, id_medico):
        medicoSQL = """
        SELECT m.id_medico, m.nombre, m.apellido, m.id_especialidad, m.num_registro, e.descripcion AS especialidad
        FROM medico m
        JOIN especialidad e ON m.id_especialidad = e.id_especialidad
        WHERE m.id_medico = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(medicoSQL, (id_medico,))
            medico = cur.fetchone()  # Obtener una sola fila
            if medico:
                return {
                    'id_medico': medico[0],
                    'nombre': medico[1],
                    'apellido': medico[2],
                    'id_especialidad': medico[3],
                    'num_registro': medico[4],
                    'especialidad': medico[5],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener médico por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarMedico(self, nombre, apellido, id_especialidad, num_registro):
        insertMedicoSQL = """
        INSERT INTO medico (nombre, apellido, id_especialidad, num_registro)
        VALUES (%s, %s, %s, %s)
        RETURNING id_medico
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertMedicoSQL, (nombre, apellido, id_especialidad, num_registro,))
            medico_id = cur.fetchone()[0]
            con.commit()
            return medico_id

        except Exception as e:
            app.logger.error(f"Error al insertar médico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateMedico(self, id_medico, nombre, apellido, id_especialidad, num_registro):
        updateMedicoSQL = """
        UPDATE medico
        SET nombre=%s, apellido=%s, id_especialidad=%s, num_registro=%s
        WHERE id_medico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateMedicoSQL, (nombre, apellido, id_especialidad, num_registro, id_medico,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar médico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteMedico(self, id_medico):
        deleteMedicoSQL = """
        DELETE FROM medico
        WHERE id_medico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteMedicoSQL, (id_medico,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al eliminar médico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()