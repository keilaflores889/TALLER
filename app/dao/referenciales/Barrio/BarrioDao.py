# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion

class BarrioDao:

    def getBarrios(self):

        barrioSQL = """
        SELECT id_barrio, descripcion
        FROM barrio
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(barrioSQL)
            barrios = cur.fetchall() # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_barrio': barrio[0], 'descripcion': barrio[1]} for barrio in barrios]

        except Exception as e:
            app.logger.error(f"Error al obtener todas los barrios: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getBarrioById(self, id_barrio):

        barrioSQL = """
        SELECT id_barrio, descripcion
        FROM barrio WHERE id_barrio=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(barrioSQL, (id_barrio,))
            barrioEncontrada = cur.fetchone() # Obtener una sola fila
            if barrioEncontrada:
                return {
                        "id_barrio": barrioEncontrada[0],
                        "descripcion": barrioEncontrada[1]
                    }  # Retornar los datos de los barrios
            else:
                return None # Retornar None si no se encuentra el barrio
        except Exception as e:
            app.logger.error(f"Error al obtener barrio: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarBarrio(self, descripcion):

        insertBarrioSQL = """
        INSERT INTO barrio(descripcion) VALUES(%s) RETURNING id_barrio
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertBarrioSQL, (descripcion,))
            barrio_id = cur.fetchone()[0]
            con.commit() # se confirma la insercion
            return barrio_id

        # Si algo fallo entra aqui
        except Exception as e:
            app.logger.error(f"Error al insertar barrio: {str(e)}")
            con.rollback() # retroceder si hubo error
            return False

        # Siempre se va ejecutar
        finally:
            cur.close()
            con.close()

    def updateBarrio(self, id_barrio, descripcion):

        updateBarrioSQL = """
        UPDATE barrio
        SET descripcion=%s
        WHERE id_barrio=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateBarrioSQL, (descripcion, id_barrio,))
            filas_afectadas = cur.rowcount # Obtener el número de filas afectadas
            con.commit()

            return filas_afectadas > 0 # Retornar True si se actualizó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al actualizar barrio: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteBarrio(self, id_barrio):

        updateBarrioSQL = """
        DELETE FROM barrio
        WHERE id_barrio=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateBarrioSQL, (id_barrio,))
            rows_affected = cur.rowcount
            con.commit()

            return rows_affected > 0  # Retornar True si se eliminó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al eliminar ciudad: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()