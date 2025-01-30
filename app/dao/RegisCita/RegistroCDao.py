from flask import current_app as app
from app.conexion.Conexion import Conexion

class RegistroCDao:

    def getRegistrosC(self):
        registrocSQL = """
        SELECT 
            cita.id_cita,
            cita.id_paciente,
            cita.id_medico,
            cita.id_especialidad,
            cita.fecha_cita,
            cita.hora,
            cita.id_estado,
            cita.motivo_consulta,
            paciente.nombre AS paciente_nombre,
            paciente.apellido AS paciente_apellido,
            medico.nombre AS medico_nombre,
            medico.apellido AS medico_apellido,
            especialidad.descripcion AS especialidad_descripcion,
            estado_cita.descripcion AS estado_descripcion
        FROM cita
        JOIN paciente ON cita.id_paciente = paciente.id_paciente
        JOIN medico ON cita.id_medico = medico.id_medico
        JOIN especialidad ON cita.id_especialidad = especialidad.id_especialidad
        JOIN estado_cita ON cita.id_estado = estado_cita.id_estado
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
                            'paciente_nombre': cita[8],
                            'paciente_apellido': cita[9],
                            'medico_nombre': cita[10],
                            'medico_apellido': cita[11],
                            'especialidad': cita[12],
                            'estado': cita[13]
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
        # Consulta con JOINs para obtener detalles de paciente, médico, especialidad y estado por ID
        registrocSQL = """
        SELECT 
            cita.id_cita,
            cita.id_paciente,
            cita.id_medico,
            cita.id_especialidad,
            cita.fecha_cita,
            cita.hora,
            cita.id_estado,
            cita.motivo_consulta,
            paciente.nombre AS paciente_nombre,
            paciente.apellido AS paciente_apellido,
            medico.nombre AS medico_nombre,
            medico.apellido AS medico_apellido,
            especialidad.descripcion AS especialidad_descripcion,
            estado_cita.descripcion AS estado_descripcion
        FROM cita
        JOIN paciente ON cita.id_paciente = paciente.id_paciente
        JOIN medico ON cita.id_medico = medico.id_medico
        JOIN especialidad ON cita.id_especialidad = especialidad.id_especialidad
        JOIN estado_cita ON cita.id_estado = estado_cita.id_estado
        WHERE cita.id_cita = %s
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
                            'paciente_nombre': cita[8],
                            'paciente_apellido': cita[9],
                            'medico_nombre': cita[10],
                            'medico_apellido': cita[11],
                            'especialidad': cita[12],
                            'estado': cita[13]
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
        SET id_paciente=%s, id_medico=%s, id_especialidad=%s, fecha_cita=%s, hora=%s, id_estado=%s, motivo_consulta=%s
        WHERE id_cita=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateCitaSQL, (id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta, id_cita))
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
