# Data Access Object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoProcedimientoDao:

    def getTiposProcedimiento(self):
        sql = """
        SELECT id_tipo_procedimiento, procedimiento, descripcion, duracion
        FROM tipo_procedimiento_medico
        ORDER BY id_tipo_procedimiento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            procedimientos = cur.fetchall()
            return [
                {
                    "id_tipo_procedimiento": p[0],
                    "procedimiento": p[1],
                    "descripcion": p[2],
                    "duracion": p[3]
                }
                for p in procedimientos
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener tipos de procedimiento: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoProcedimientoById(self, id_tipo_procedimiento):
        sql = """
        SELECT id_tipo_procedimiento, procedimiento, descripcion, duracion
        FROM tipo_procedimiento_medico
        WHERE id_tipo_procedimiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_procedimiento,))
            row = cur.fetchone()
            if row:
                return {
                    "id_tipo_procedimiento": row[0],
                    "procedimiento": row[1],
                    "descripcion": row[2],
                    "duracion": row[3]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de procedimiento: {str(e)}")
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

    def procedimientoExiste(self, procedimiento):
        """
        Verifica si ya existe un tipo de procedimiento con el mismo nombre (ignora mayúsculas/minúsculas).
        """
        sql = """
        SELECT 1 FROM tipo_procedimiento_medico WHERE UPPER(procedimiento) = UPPER(%s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (procedimiento,))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de procedimiento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def procedimientoExisteExceptoId(self, procedimiento, id_tipo_procedimiento):
        """
        Verifica si existe otro tipo de procedimiento con el mismo nombre, excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM tipo_procedimiento_medico 
        WHERE UPPER(procedimiento) = UPPER(%s)
          AND id_tipo_procedimiento != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (procedimiento, id_tipo_procedimiento))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de procedimiento (excepto id): {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # CRUD
    # ============================

    def guardarTipoProcedimiento(self, procedimiento, descripcion, duracion):
        """
        Inserta un tipo de procedimiento.
        """
        sql = """
        INSERT INTO tipo_procedimiento_medico(procedimiento, descripcion, duracion)
        VALUES(%s, %s, %s) RETURNING id_tipo_procedimiento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (procedimiento, descripcion, duracion))
            id_tipo_procedimiento = cur.fetchone()[0]
            con.commit()
            return id_tipo_procedimiento
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoProcedimiento(self, id_tipo_procedimiento, procedimiento, descripcion, duracion):
        """
        Actualiza un tipo de procedimiento.
        """
        sql = """
        UPDATE tipo_procedimiento_medico
        SET procedimiento=%s,
            descripcion=%s,
            duracion=%s
        WHERE id_tipo_procedimiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (procedimiento, descripcion, duracion, id_tipo_procedimiento))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoProcedimiento(self, id_tipo_procedimiento):
        sql = """
        DELETE FROM tipo_procedimiento_medico WHERE id_tipo_procedimiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_procedimiento,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()