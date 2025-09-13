# Data access object - DAO para tipo_estudio
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoEstudioDao:

    def getTiposEstudio(self):
        sql = """
        SELECT id_tipo_estudio, descripcion_estudio
        FROM tipo_estudio
        ORDER BY descripcion_estudio ASC
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            estudios = cur.fetchall()
            return [{'id_tipo_estudio': est[0], 'descripcion_estudio': est[1]} for est in estudios]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los tipos de estudio: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoEstudioById(self, id_tipo_estudio):
        sql = """
        SELECT id_tipo_estudio, descripcion_estudio
        FROM tipo_estudio
        WHERE id_tipo_estudio = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_estudio,))
            estudio = cur.fetchone()
            if estudio:
                return {"id_tipo_estudio": estudio[0], "descripcion_estudio": estudio[1]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de estudio: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def estudioExiste(self, descripcion_estudio):
        sql = """
        SELECT 1 FROM tipo_estudio WHERE UPPER(descripcion_estudio) = UPPER(%s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion_estudio,))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de estudio: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def guardarTipoEstudio(self, descripcion_estudio):
        sql = """
        INSERT INTO tipo_estudio(descripcion_estudio)
        VALUES (%s)
        RETURNING id_tipo_estudio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            if not descripcion_estudio or not descripcion_estudio.strip():
                app.logger.error("Descripción vacía o nula al intentar guardar tipo de estudio")
                return False

            if self.estudioExiste(descripcion_estudio):
                app.logger.error(f"Ya existe un estudio con la descripción: {descripcion_estudio}")
                return False

            cur.execute(sql, (descripcion_estudio,))
            id_estudio = cur.fetchone()[0]
            con.commit()
            return id_estudio
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoEstudio(self, id_tipo_estudio, descripcion_estudio):
        sql = """
        UPDATE tipo_estudio
        SET descripcion_estudio = %s
        WHERE id_tipo_estudio = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion_estudio, id_tipo_estudio))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoEstudio(self, id_tipo_estudio):
        sql = """
        DELETE FROM tipo_estudio
        WHERE id_tipo_estudio = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_estudio,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
