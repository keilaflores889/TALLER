from flask import current_app as app
from app.conexion.Conexion import Conexion


class MedicoDao:

    def getMedicos(self):
        medicoSQL = """
        SELECT id_medico, id_persona, id_especialidad
        FROM medico
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
                    'id_persona': medico[1],
                    'id_especialidad': medico[2],
                }
                for medico in medicos
            ]


        except Exception as e:
            app.logger.error(f"Error al obtener todos los medicos: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getMedicoById(self, id_medico):
        medicoSQL = """
       SELECT id_medico, id_persona, id_especialidad
        FROM medico
        WHERE id_medico=%s
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
                    'id_persona': medico[1],
                    'id_especialidad': medico[2],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener medicos por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarMedico(self, id_medico, id_persona, id_especialidad):
        insertMedicoSQL = """
        INSERT INTO medico (id_medico, id_persona, id_especialidad)
        VALUES (%s, %s, %s)
        RETURNING id_medico
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertMedicoSQL, (id_medico, id_persona, id_especialidad))
            medico_id = cur.fetchone()[0]
            con.commit()
            return medico_id


        except Exception as e:
            app.logger.error(f"Error al insertar medico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateAgenda(self, id_medico, id_persona, id_especialidad):
        updateMedicoSQL = """
        UPDATE medico
        SET id_medico=%s, id_persona=%s, id_especialidada=%s
        WHERE id_medico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateMedicoSQL, (id_medico, id_persona, id_especialidad))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar medico: {str(e)}")
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
            app.logger.error(f"Error al eliminar medico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
