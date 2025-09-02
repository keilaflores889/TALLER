# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion

class DisponibilidadDao:

    def getDisponibilidades(self):
        sql = """
        SELECT d.id_disponibilidad, d.id_medico, d.disponibilidad_hora_inicio, 
               d.disponibilidad_hora_fin, d.disponibilidad_fecha, d.disponibilidad_cupos,
               m.nombre || ' ' || m.apellido AS medico_nombre
        FROM disponibilidad_horaria d
        JOIN medico m ON d.id_medico = m.id_medico
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            disponibilidades = cur.fetchall()
            return [
                {
                    'id_disponibilidad': d[0],
                    'id_medico': d[1],
                    'disponibilidad_hora_inicio': str(d[2]),
                    'disponibilidad_hora_fin': str(d[3]),
                    'disponibilidad_fecha': str(d[4]),
                    'disponibilidad_cupos': d[5],
                    'medico_nombre': d[6]
                } for d in disponibilidades
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidades: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getDisponibilidadById(self, id_disponibilidad):
        sql = """
        SELECT d.id_disponibilidad, d.id_medico, d.disponibilidad_hora_inicio, 
               d.disponibilidad_hora_fin, d.disponibilidad_fecha, d.disponibilidad_cupos,
               m.nombre || ' ' || m.apellido AS medico_nombre
        FROM disponibilidad_horaria d
        JOIN medico m ON d.id_medico = m.id_medico
        WHERE d.id_disponibilidad = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_disponibilidad,))
            d = cur.fetchone()
            if d:
                return {
                    'id_disponibilidad': d[0],
                    'id_medico': d[1],
                    'disponibilidad_hora_inicio': str(d[2]),
                    'disponibilidad_hora_fin': str(d[3]),
                    'disponibilidad_fecha': str(d[4]),
                    'disponibilidad_cupos': d[5],
                    'medico_nombre': d[6]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidad: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def existeDisponibilidad(self, id_medico, hora_inicio, hora_fin, fecha, excluir_id=None):
        """
        Verifica si ya existe una disponibilidad con los mismos datos.
        Si se pasa excluir_id, ignora ese registro (para update).
        """
        sql = """
        SELECT COUNT(*) 
        FROM disponibilidad_horaria
        WHERE id_medico = %s
          AND disponibilidad_fecha = %s
          AND disponibilidad_hora_inicio = %s
          AND disponibilidad_hora_fin = %s
        """
        params = [id_medico, fecha, hora_inicio, hora_fin]
        if excluir_id:
            sql += " AND id_disponibilidad <> %s"
            params.append(excluir_id)

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, tuple(params))
            cantidad = cur.fetchone()[0]
            return cantidad > 0
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado: {str(e)}")
            return True  # Para evitar insertar si hay error
        finally:
            cur.close()
            con.close()

    def guardarDisponibilidad(self, id_medico, hora_inicio, hora_fin, fecha, cupos):
        if self.existeDisponibilidad(id_medico, hora_inicio, hora_fin, fecha):
            app.logger.warning("Disponibilidad duplicada detectada")
            return False  # No se guarda duplicado

        sql = """
        INSERT INTO disponibilidad_horaria(id_medico, disponibilidad_hora_inicio, 
                                           disponibilidad_hora_fin, disponibilidad_fecha, disponibilidad_cupos)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_disponibilidad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico, hora_inicio, hora_fin, fecha, cupos))
            new_id = cur.fetchone()[0]
            con.commit()
            return new_id
        except Exception as e:
            app.logger.error(f"Error al insertar disponibilidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateDisponibilidad(self, id_disponibilidad, id_medico, hora_inicio, hora_fin, fecha, cupos):
        if self.existeDisponibilidad(id_medico, hora_inicio, hora_fin, fecha, excluir_id=id_disponibilidad):
            app.logger.warning("Disponibilidad duplicada detectada en update")
            return False  # No se actualiza duplicado

        sql = """
        UPDATE disponibilidad_horaria
        SET id_medico=%s,
            disponibilidad_hora_inicio=%s,
            disponibilidad_hora_fin=%s,
            disponibilidad_fecha=%s,
            disponibilidad_cupos=%s
        WHERE id_disponibilidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico, hora_inicio, hora_fin, fecha, cupos, id_disponibilidad))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar disponibilidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteDisponibilidad(self, id_disponibilidad):
        sql = "DELETE FROM disponibilidad_horaria WHERE id_disponibilidad=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_disponibilidad,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar disponibilidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
