# Data Access Object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class MedicamentoDao:

    def getMedicamentos(self):
        sql = """
        SELECT id_medicamento, nombre_medicamento, dosis, indicaciones, forma_farmaceutica
        FROM medicamento
        ORDER BY id_medicamento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            medicamentos = cur.fetchall()
            return [
                {
                    "id_medicamento": m[0],
                    "nombre_medicamento": m[1],
                    "dosis": m[2],
                    "indicaciones": m[3],
                    "forma_farmaceutica": m[4]
                }
                for m in medicamentos
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener medicamentos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getMedicamentoById(self, id_medicamento):
        sql = """
        SELECT id_medicamento, nombre_medicamento, dosis, indicaciones, forma_farmaceutica
        FROM medicamento
        WHERE id_medicamento = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medicamento,))
            row = cur.fetchone()
            if row:
                return {
                    "id_medicamento": row[0],
                    "nombre_medicamento": row[1],
                    "dosis": row[2],
                    "indicaciones": row[3],
                    "forma_farmaceutica": row[4]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener medicamento: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def validarTexto(self, texto):
        """Permite letras (incluyendo ñ y acentuadas), espacios y barra diagonal."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s/]+$"
        return bool(re.match(patron, texto))

    def validarIndicaciones(self, texto):
        """Permite letras, espacios, /, comas, puntos y otros caracteres comunes en indicaciones médicas."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s/\,\.\;\:\(\)\-]+$"
        return bool(re.match(patron, texto))

    def validarPalabraConSentido(self, texto):
        """Valida que el texto contenga al menos una vocal."""
        patron = r"[aeiouáéíóúAEIOUÁÉÍÓÚ]"
        return bool(re.search(patron, texto))

    def validarDosis(self, dosis):
        """Permite letras, números, espacios y caracteres comunes en dosis (mg, ml, %, /, -, .)."""
        patron = r"^[A-Za-z0-9\s\.\,\-\/\%]+$"
        return bool(re.match(patron, dosis))

    def existeDuplicado(self, nombre_medicamento, dosis, forma_farmaceutica):
        """
        Verifica si ya existe un medicamento con el mismo nombre, dosis y forma farmacéutica.
        """
        sql = """
        SELECT 1 FROM medicamento
        WHERE UPPER(nombre_medicamento) = UPPER(%s)
          AND UPPER(dosis) = UPPER(%s)
          AND UPPER(forma_farmaceutica) = UPPER(%s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_medicamento, dosis, forma_farmaceutica))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de medicamento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def existeDuplicadoExceptoId(self, nombre_medicamento, dosis, forma_farmaceutica, id_medicamento):
        """
        Verifica si existe otro medicamento con el mismo nombre, dosis y forma farmacéutica, 
        excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM medicamento
        WHERE UPPER(nombre_medicamento) = UPPER(%s)
          AND UPPER(dosis) = UPPER(%s)
          AND UPPER(forma_farmaceutica) = UPPER(%s)
          AND id_medicamento != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_medicamento, dosis, forma_farmaceutica, id_medicamento))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de medicamento (excepto id): {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # CRUD
    # ============================

    def guardarMedicamento(self, nombre_medicamento, dosis, indicaciones, forma_farmaceutica):
        sql = """
        INSERT INTO medicamento(nombre_medicamento, dosis, indicaciones, forma_farmaceutica)
        VALUES (%s, %s, %s, %s) RETURNING id_medicamento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_medicamento, dosis, indicaciones, forma_farmaceutica))
            id_medicamento = cur.fetchone()[0]
            con.commit()
            return id_medicamento
        except Exception as e:
            app.logger.error(f"Error al insertar medicamento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateMedicamento(self, id_medicamento, nombre_medicamento, dosis, indicaciones, forma_farmaceutica):
        sql = """
        UPDATE medicamento
        SET nombre_medicamento=%s,
            dosis=%s,
            indicaciones=%s,
            forma_farmaceutica=%s
        WHERE id_medicamento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_medicamento, dosis, indicaciones, forma_farmaceutica, id_medicamento))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar medicamento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteMedicamento(self, id_medicamento):
        sql = """
        DELETE FROM medicamento WHERE id_medicamento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medicamento,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar medicamento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()