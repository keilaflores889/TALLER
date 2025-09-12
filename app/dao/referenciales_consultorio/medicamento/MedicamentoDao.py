# Data Access Object - DAO
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
