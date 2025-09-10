# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion

class EstadoCitaDao:

    def getEstadosCitas(self):
        estadocitaSQL = """
        SELECT id_estado, descripcion
        FROM estado_cita
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(estadocitaSQL)
            estadoscitas = cur.fetchall()
            return [{'id_estado': e[0], 'descripcion': e[1]} for e in estadoscitas]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los Estados de Cita: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getEstadoCitaById(self, id_estado):
        estadocitaSQL = """
        SELECT id_estado, descripcion
        FROM estado_cita WHERE id_estado=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(estadocitaSQL, (id_estado,))
            estadocitaEncontrada = cur.fetchone()
            if estadocitaEncontrada:
                return {
                    "id_estado": estadocitaEncontrada[0],
                    "descripcion": estadocitaEncontrada[1]
                }
            else:
                return None
        except Exception as e:
            app.logger.error(f"Error al obtener el estado de cita: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def guardarEstadoCita(self, descripcion):
        insertEstadoCitaSQL = """
        INSERT INTO estado_cita(descripcion) VALUES(%s) RETURNING id_estado
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertEstadoCitaSQL, (descripcion,))
            estadocita_id = cur.fetchone()[0]
            con.commit()
            return estadocita_id
        except Exception as e:
            app.logger.error(f"Error al insertar estado de cita: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateEstadoCita(self, id_estado, descripcion):
        updateEstadoCitaSQL = """
        UPDATE estado_cita
        SET descripcion=%s
        WHERE id_estado=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateEstadoCitaSQL, (descripcion, id_estado,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar Estado de Cita: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteEstadoCita(self, id_estado):
        deleteEstadoCitaSQL = """
        DELETE FROM estado_cita
        WHERE id_estado=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteEstadoCitaSQL, (id_estado,))
            rows_affected = cur.rowcount
            con.commit()
            return rows_affected > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar Estado de Cita: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # Nuevo método: verifica si ya existe un estado con la misma descripción
    def existeDescripcion(self, descripcion):
        sql = "SELECT 1 FROM estado_cita WHERE descripcion = %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de descripción: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # Nuevo método: verifica si existe descripción igual para otro id distinto (para update)
    def existeDescripcionExceptoId(self, descripcion, id_estado):
        sql = "SELECT 1 FROM estado_cita WHERE descripcion = %s AND id_estado <> %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_estado))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de descripción (excepto id): {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
