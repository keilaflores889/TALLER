from flask import current_app as app
from app.conexion.Conexion import Conexion


class RegistroPDao:

    def getRegistrosP(self):
        registropSQL = """
        SELECT id_persona, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio
        FROM persona
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registropSQL)
            personas = cur.fetchall()  # Trae todos los datos del registro

            # Transformar los datos en una lista de diccionarios
            return [
                {
                    'id_persona': persona[0]
                    ,'nombre': persona[1]
                    ,'apellido': persona[2]
                    ,'cedula_identidad': persona[3]
                    ,'fecha_nacimiento': persona[4]
                    ,'fecha_registro': persona[5]
                    ,'telefono': persona[6]
                    ,'id_ciudad': persona[7]
                    ,'id_barrio': persona[8]
                }
                for persona in personas
            ]


        except Exception as e:
            app.logger.error(f"Error al obtener todas los registros: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getRegistroPById(self, id_persona):
        registropSQL = """
        SELECT id_persona, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio
        FROM persona 
        WHERE id_persona=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registropSQL, (id_persona,))
            personaEncontrada = cur.fetchone()  # Obtener una sola fila
            if personaEncontrada:
                return {
                    'id_persona': personaEncontrada[0],
                    'nombre': personaEncontrada[1],
                    'apellido': personaEncontrada[2],
                    'cedula_identidad': personaEncontrada[3],
                    'fecha_nacimiento': personaEncontrada[4],
                    'fecha_registro': personaEncontrada[5],
                    'telefono': personaEncontrada[6],
                    'id_ciudad': personaEncontrada[7],
                    'id_barrio': personaEncontrada[8],
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener registro por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarRegistroP(self, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio):
        insertRegistropSQL = """
        INSERT INTO persona (nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_persona
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertRegistropSQL, (nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio))
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

    def updateRegistroP(self, nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio, id_persona):
        updateAgendaSQL = """
        UPDATE persona
        SET nombre=%s, apellido=%s, cedula_identidad=%s, fecha_nacimiento=%s, fecha_registro=%s, telefono=%s, id_ciudad=%s, id_barrio=%s
        WHERE id_persona=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateAgendaSQL, (nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio, id_persona))
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

    def deleteRegistroP(self, id_persona):
        deleteRegistropSQL = """
        DELETE FROM persona
        WHERE id_persona=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteRegistropSQL, (id_persona,))
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
