import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class CiudadDao:

    def getCiudades(self):
        ciudadSQL = """
        SELECT id_ciudad, descripcion
        FROM ciudad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(ciudadSQL)
            ciudades = cur.fetchall()
            return [{'id_ciudad': c[0], 'descripcion': c[1]} for c in ciudades]
        except Exception as e:
            app.logger.error(f"Error al obtener todas las ciudades: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getCiudadById(self, id):
        ciudadSQL = """
        SELECT id_ciudad, descripcion
        FROM ciudad
        WHERE id_ciudad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(ciudadSQL, (id,))
            ciudad = cur.fetchone()
            if ciudad:
                return {"id_ciudad": ciudad[0], "descripcion": ciudad[1]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener ciudad: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def validarDescripcion(self, descripcion):
        """Permite letras (incluyendo ñ y acentuadas), números y espacios."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]+$"
        return bool(re.match(patron, descripcion))

    def existeDescripcion(self, descripcion):
        """Verifica si ya existe una ciudad con esa descripción."""
        sql = """
        SELECT 1 FROM ciudad WHERE descripcion = %s
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

    def existeDescripcionExceptoId(self, descripcion, id_ciudad):
        """Verifica si existe otra ciudad con esa descripción, excluyendo el id actual."""
        sql = """
        SELECT 1 FROM ciudad WHERE descripcion = %s AND id_ciudad != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_ciudad))
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

    def guardarCiudad(self, descripcion):
        insertSQL = """
        INSERT INTO ciudad(descripcion) VALUES(%s) RETURNING id_ciudad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertSQL, (descripcion,))
            ciudad_id = cur.fetchone()[0]
            con.commit()
            return ciudad_id
        except Exception as e:
            app.logger.error(f"Error al insertar ciudad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateCiudad(self, id, descripcion):
        updateSQL = """
        UPDATE ciudad SET descripcion=%s WHERE id_ciudad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateSQL, (descripcion, id))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar ciudad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteCiudad(self, id):
        deleteSQL = """
        DELETE FROM ciudad WHERE id_ciudad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteSQL, (id,))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar ciudad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()