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

    def analisisExiste(self, descripcion):
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

    def guardarTipoAnalisis(self, descripcion):
        if not descripcion or not descripcion.strip():
            app.logger.error("Descripción vacía al intentar guardar tipo de análisis")
            return False

        if self.analisisExiste(descripcion):
            app.logger.error(f"Ya existe un análisis con la descripción: {descripcion}")
            return False

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
        if not descripcion or not descripcion.strip():
            app.logger.error("Descripción vacía al intentar actualizar tipo de análisis")
            return False

        if self.analisisExiste(descripcion):
            app.logger.error(f"Ya existe un análisis con la descripción: {descripcion}")
            return False

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
