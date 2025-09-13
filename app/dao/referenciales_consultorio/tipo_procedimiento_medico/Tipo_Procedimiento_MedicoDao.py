# Data access object - DAO para tipo_procedimiento_medico
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoProcedimientoDao:

    def getTiposProcedimiento(self):
        sql = """
        SELECT id_tipo_procedimiento, procedimiento, descripcion, duracion
        FROM tipo_procedimiento_medico
        ORDER BY procedimiento ASC
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            procedimientos = cur.fetchall()
            return [
                {
                    'id_tipo_procedimiento': proc[0],
                    'procedimiento': proc[1],
                    'descripcion': proc[2],
                    'duracion': proc[3]
                }
                for proc in procedimientos
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los procedimientos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoProcedimientoById(self, id_tipo_procedimiento):
        sql = """
        SELECT id_tipo_procedimiento, procedimiento, descripcion, duracion
        FROM tipo_procedimiento_medico
        WHERE id_tipo_procedimiento = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_procedimiento,))
            procedimiento = cur.fetchone()
            if procedimiento:
                return {
                    "id_tipo_procedimiento": procedimiento[0],
                    "procedimiento": procedimiento[1],
                    "descripcion": procedimiento[2],
                    "duracion": procedimiento[3]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener procedimiento: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def procedimientoExiste(self, procedimiento):
        sql = """
        SELECT 1 FROM tipo_procedimiento_medico
        WHERE UPPER(procedimiento) = UPPER(%s)
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

    def guardarTipoProcedimiento(self, procedimiento, descripcion, duracion):
        sql = """
        INSERT INTO tipo_procedimiento_medico(procedimiento, descripcion, duracion)
        VALUES (%s, %s, %s)
        RETURNING id_tipo_procedimiento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            if not procedimiento or not procedimiento.strip():
                app.logger.error("Procedimiento vacío o nulo al intentar guardar")
                return False

            if self.procedimientoExiste(procedimiento):
                app.logger.error(f"Ya existe un procedimiento con el nombre: {procedimiento}")
                return False

            cur.execute(sql, (procedimiento, descripcion, duracion))
            id_procedimiento = cur.fetchone()[0]
            con.commit()
            return id_procedimiento
        except Exception as e:
            app.logger.error(f"Error al insertar procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoProcedimiento(self, id_tipo_procedimiento, procedimiento, descripcion, duracion):
        sql = """
        UPDATE tipo_procedimiento_medico
        SET procedimiento = %s,
            descripcion = %s,
            duracion = %s
        WHERE id_tipo_procedimiento = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (procedimiento, descripcion, duracion, id_tipo_procedimiento))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoProcedimiento(self, id_tipo_procedimiento):
        sql = """
        DELETE FROM tipo_procedimiento_medico
        WHERE id_tipo_procedimiento = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_procedimiento,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
