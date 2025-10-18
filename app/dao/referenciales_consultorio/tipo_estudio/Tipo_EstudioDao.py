# Data Access Object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoEstudioDao:

    def getTiposEstudio(self):
        sql = """
        SELECT id_tipo_estudio, descripcion_estudio
        FROM tipo_estudio
        ORDER BY id_tipo_estudio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            estudios = cur.fetchall()
            return [
                {"id_tipo_estudio": e[0], "descripcion_estudio": e[1]}
                for e in estudios
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener tipos de estudio: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoEstudioById(self, id_tipo_estudio):
        sql = """
        SELECT id_tipo_estudio, descripcion_estudio
        FROM tipo_estudio
        WHERE id_tipo_estudio=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_estudio,))
            row = cur.fetchone()
            if row:
                return {"id_tipo_estudio": row[0], "descripcion_estudio": row[1]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de estudio: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def validarTexto(self, texto):
        """Permite letras (incluyendo ñ y acentuadas), números, espacios, barra, guion, comas y puntos."""
        patron = r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s\/\-\,\.]+$"
        return bool(re.match(patron, texto))

    def validarPalabraConSentido(self, texto):
        """Valida que el texto contenga al menos una vocal."""
        patron = r"[aeiouáéíóúAEIOUÁÉÍÓÚ]"
        return bool(re.search(patron, texto))

    def estudioExiste(self, descripcion):
        """
        Verifica si ya existe un tipo de estudio con la misma descripción (ignora mayúsculas/minúsculas).
        """
        sql = """
        SELECT 1 FROM tipo_estudio WHERE UPPER(descripcion_estudio) = UPPER(%s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de estudio: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def estudioExisteExceptoId(self, descripcion, id_tipo_estudio):
        """
        Verifica si existe otro tipo de estudio con la misma descripción, excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM tipo_estudio 
        WHERE UPPER(descripcion_estudio) = UPPER(%s)
          AND id_tipo_estudio != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_tipo_estudio))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de estudio (excepto id): {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # CRUD
    # ============================

    def guardarTipoEstudio(self, descripcion):
        """
        Inserta un tipo de estudio.
        """
        sql = """
        INSERT INTO tipo_estudio(descripcion_estudio)
        VALUES(%s) RETURNING id_tipo_estudio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            id_tipo_estudio = cur.fetchone()[0]
            con.commit()
            return id_tipo_estudio
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoEstudio(self, id_tipo_estudio, descripcion):
        """
        Actualiza la descripción de un tipo de estudio.
        """
        sql = """
        UPDATE tipo_estudio
        SET descripcion_estudio=%s
        WHERE id_tipo_estudio=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_tipo_estudio))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoEstudio(self, id_tipo_estudio):
        sql = """
        DELETE FROM tipo_estudio WHERE id_tipo_estudio=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_estudio,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()