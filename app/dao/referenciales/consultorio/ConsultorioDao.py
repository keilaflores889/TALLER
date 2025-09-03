# Data Access Object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion

class ConsultorioDao:

    def getConsultorios(self):
        sql = """
        SELECT codigo, nombre_consultorio, direccion, telefono, correo
        FROM consultorio
        ORDER BY codigo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            consultorios = cur.fetchall()
            return [
                {
                    "codigo": c[0],
                    "nombre_consultorio": c[1],
                    "direccion": c[2],
                    "telefono": c[3],
                    "correo": c[4]
                }
                for c in consultorios
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener consultorios: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getConsultorioById(self, codigo):
        sql = """
        SELECT codigo, nombre_consultorio, direccion, telefono, correo
        FROM consultorio
        WHERE codigo = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (codigo,))
            row = cur.fetchone()
            if row:
                return {
                    "codigo": row[0],
                    "nombre_consultorio": row[1],
                    "direccion": row[2],
                    "telefono": row[3],
                    "correo": row[4]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener consultorio: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def existeDuplicado(self, nombre_consultorio, correo):
        """
        Verifica si ya existe un consultorio con el mismo nombre o correo.
        """
        sql = """
        SELECT 1 FROM consultorio
        WHERE UPPER(nombre_consultorio) = UPPER(%s) OR UPPER(correo) = UPPER(%s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_consultorio, correo))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de consultorio: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def guardarConsultorio(self, nombre_consultorio, direccion, telefono, correo):
        sql = """
        INSERT INTO consultorio(nombre_consultorio, direccion, telefono, correo)
        VALUES (%s, %s, %s, %s) RETURNING codigo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_consultorio, direccion, telefono, correo))
            codigo = cur.fetchone()[0]
            con.commit()
            return codigo
        except Exception as e:
            app.logger.error(f"Error al insertar consultorio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateConsultorio(self, codigo, nombre_consultorio, direccion, telefono, correo):
        sql = """
        UPDATE consultorio
        SET nombre_consultorio=%s,
            direccion=%s,
            telefono=%s,
            correo=%s
        WHERE codigo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre_consultorio, direccion, telefono, correo, codigo))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar consultorio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteConsultorio(self, codigo):
        sql = """
        DELETE FROM consultorio WHERE codigo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (codigo,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar consultorio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
