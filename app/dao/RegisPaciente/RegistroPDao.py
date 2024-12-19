from flask import current_app as app
from app.conexion.Conexion import Conexion


class RegistroPDao:

    def getRegistrosP(self):
        registropSQL = """
        SELECT id_paciente, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad
        FROM paciente
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registropSQL)
            pacientes = cur.fetchall()  # Trae todos los datos del registro

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_paciente': paciente[0]
                    ,'nombre': paciente[1]
                    ,'apellido': paciente[2]
                    ,'cedula_identidad': paciente[3]
                    ,'fecha_nacimiento': paciente[4]
                    ,'fecha_registro': paciente[5]
                    ,'telefono': paciente[6]
                    ,'id_ciudad': paciente[7]
                }
                for paciente in pacientes
            ]


        except Exception as e:
            app.logger.error(f"Error al obtener todas los registros: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getRegistroPById(self, id_paciente):
        registropSQL = """
        SELECT id_paciente, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad
        FROM paciente
        WHERE id_paciente=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registropSQL, (id_paciente,))
            pacienteEncontrada = cur.fetchone()  # Obtener una sola fila
            if pacienteEncontrada:
                return {
                    'id_paciente': pacienteEncontrada[0],
                    'nombre': pacienteEncontrada[1],
                    'apellido': pacienteEncontrada[2],
                    'cedula_identidad': pacienteEncontrada[3],
                    'fecha_nacimiento': pacienteEncontrada[4],
                    'fecha_registro': pacienteEncontrada[5],
                    'telefono': pacienteEncontrada[6],
                    'id_ciudad': pacienteEncontrada[7],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener registro por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarRegistroP(self, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad):
        insertRegistropSQL = """
        INSERT INTO paciente (nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_paciente
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertRegistropSQL, (nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad))
            registrop_id = cur.fetchone()[0]
            con.commit()
            return registrop_id


        except Exception as e:
            app.logger.error(f"Error al insertar registro: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateRegistroP(self, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_paciente):
        updateRegistropSQL = """
        UPDATE paciente
        SET nombre=%s, apellido=%s, cedula_identidad=%s, fecha_nacimiento=%s, fecha_registro=%s, telefono=%s, id_ciudad=%s
        WHERE id_paciente=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateRegistropSQL, (nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_paciente))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar registro: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteRegistroP(self, id_paciente):
        deleteRegistropSQL = """
        DELETE FROM paciente
        WHERE id_paciente=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteRegistropSQL, (id_paciente,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al eliminar registro: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
