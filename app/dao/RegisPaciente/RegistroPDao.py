from flask import current_app as app
from app.conexion.Conexion import Conexion


class RegistroPDao:

    def getRegistrosP(self):
        registropSQL = """
        SELECT p.id_paciente, p.nombre, p.apellido, p.cedula_entidad, p.fecha_nacimiento, 
               p.fecha_registro, p.telefono, c.descripcion AS ciudad
        FROM paciente p
        JOIN ciudad c ON p.id_ciudad = c.id_ciudad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registropSQL)
            pacientes = cur.fetchall()

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_paciente': paciente[0],
                    'nombre': paciente[1],
                    'apellido': paciente[2],
                    'cedula_entidad': paciente[3],
                    'fecha_nacimiento': paciente[4],
                    'fecha_registro': paciente[5],
                    'telefono': paciente[6],
                    'ciudad': paciente[7],
                }
                for paciente in pacientes
            ]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los pacientes: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getRegistroPById(self, id_paciente):
        registropSQL = """
        SELECT p.id_paciente, p.nombre, p.apellido, p.cedula_entidad, p.fecha_nacimiento, 
               p.fecha_registro, p.telefono, c.descripcion AS ciudad
        FROM paciente p
        JOIN ciudad c ON p.id_ciudad = c.id_ciudad
        WHERE p.id_paciente = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registropSQL, (id_paciente,))
            paciente = cur.fetchone()
            if paciente:
                return {
                    'id_paciente': paciente[0],
                    'nombre': paciente[1],
                    'apellido': paciente[2],
                    'cedula_entidad': paciente[3],
                    'fecha_nacimiento': paciente[4],
                    'fecha_registro': paciente[5],
                    'telefono': paciente[6],
                    'ciudad': paciente[7],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener paciente por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarRegistroP(self, nombre, apellido, cedula_entidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad):
        insertRegistropSQL = """
        INSERT INTO paciente (nombre, apellido, cedula_entidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_paciente
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertRegistropSQL, (nombre, apellido, cedula_entidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad))
            paciente_id = cur.fetchone()[0]
            con.commit()
            return paciente_id

        except Exception as e:
            app.logger.error(f"Error al insertar paciente: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateRegistroP(self, id_paciente, nombre, apellido, cedula_entidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad):
        updateRegistropSQL = """
        UPDATE paciente
        SET nombre = %s, apellido = %s, cedula_entidad = %s, fecha_nacimiento = %s, 
            fecha_registro = %s, telefono = %s, id_ciudad = %s
        WHERE id_paciente = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateRegistropSQL, (nombre, apellido, cedula_entidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_paciente))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar paciente: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteRegistroP(self, id_paciente):
        deleteRegistropSQL = """
        DELETE FROM paciente
        WHERE id_paciente = %s
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
            app.logger.error(f"Error al eliminar paciente: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
