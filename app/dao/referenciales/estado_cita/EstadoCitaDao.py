import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class EstadoCitaDao:

    # ============================
    # OBTENER DATOS
    # ============================

    def getEstadosCitas(self):
        sql = """
        SELECT id_estado, descripcion
        FROM estado_cita
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            estados = cur.fetchall()
            return [{'id_estado': e[0], 'descripcion': e[1]} for e in estados]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los estados de cita: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getEstadoCitaById(self, id_estado):
        sql = """
        SELECT id_estado, descripcion
        FROM estado_cita
        WHERE id_estado = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_estado,))
            estado = cur.fetchone()
            if estado:
                return {"id_estado": estado[0], "descripcion": estado[1]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener estado de cita: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def validarDescripcion(self, descripcion):
        """
        Permite letras (incluyendo ñ y acentuadas), números y espacios.
        """
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]+$"
        return bool(re.match(patron, descripcion))

    def existeDescripcion(self, descripcion):
        """
        Verifica si ya existe un estado de cita con esa descripción.
        """
        sql = """
        SELECT 1 FROM estado_cita WHERE descripcion = %s
        """
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

    def existeDescripcionExceptoId(self, descripcion, id_estado):
        """
        Verifica si existe otro estado con esa descripción, excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM estado_cita WHERE descripcion = %s AND id_estado != %s
        """
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

    # ============================
    # CRUD
    # ============================

    def guardarEstadoCita(self, descripcion):
        sql = """
        INSERT INTO estado_cita (descripcion)
        VALUES (%s)
        RETURNING id_estado
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            id_estado = cur.fetchone()[0]
            con.commit()
            return id_estado
        except Exception as e:
            app.logger.error(f"Error al insertar estado de cita: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateEstadoCita(self, id_estado, descripcion):
        sql = """
        UPDATE estado_cita
        SET descripcion = %s
        WHERE id_estado = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_estado))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar estado de cita: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteEstadoCita(self, id_estado):
        sql = """
        DELETE FROM estado_cita
        WHERE id_estado = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_estado,))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar estado de cita: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
