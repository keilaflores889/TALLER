# Data Access Object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoAnalisisDao:

    def getTiposAnalisis(self):
        sql = """
        SELECT id_tipo_analisis, descripcion_analisis
        FROM tipo_analisis
        ORDER BY id_tipo_analisis
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            tipos = cur.fetchall()
            return [
                {"id_tipo_analisis": t[0], "descripcion_analisis": t[1]}
                for t in tipos
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener tipos de análisis: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoAnalisisById(self, id_tipo_analisis):
        sql = """
        SELECT id_tipo_analisis, descripcion_analisis
        FROM tipo_analisis
        WHERE id_tipo_analisis=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_analisis,))
            row = cur.fetchone()
            if row:
                return {"id_tipo_analisis": row[0], "descripcion_analisis": row[1]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de análisis: {str(e)}")
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

    def analisisExiste(self, descripcion):
        """
        Verifica si ya existe un tipo de análisis con la misma descripción (ignora mayúsculas/minúsculas).
        """
        sql = """
        SELECT 1 FROM tipo_analisis WHERE UPPER(descripcion_analisis) = UPPER(%s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de análisis: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def analisisExisteExceptoId(self, descripcion, id_tipo_analisis):
        """
        Verifica si existe otro tipo de análisis con la misma descripción, excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM tipo_analisis 
        WHERE UPPER(descripcion_analisis) = UPPER(%s)
          AND id_tipo_analisis != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_tipo_analisis))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de análisis (excepto id): {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # CRUD
    # ============================

    def guardarTipoAnalisis(self, descripcion):
        """
        Inserta un tipo de análisis.
        """
        sql = """
        INSERT INTO tipo_analisis(descripcion_analisis)
        VALUES(%s) RETURNING id_tipo_analisis
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            id_tipo_analisis = cur.fetchone()[0]
            con.commit()
            return id_tipo_analisis
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de análisis: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoAnalisis(self, id_tipo_analisis, descripcion):
        """
        Actualiza la descripción de un tipo de análisis.
        """
        sql = """
        UPDATE tipo_analisis
        SET descripcion_analisis=%s
        WHERE id_tipo_analisis=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_tipo_analisis))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de análisis: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoAnalisis(self, id_tipo_analisis):
        sql = """
        DELETE FROM tipo_analisis WHERE id_tipo_analisis=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_analisis,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de análisis: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()