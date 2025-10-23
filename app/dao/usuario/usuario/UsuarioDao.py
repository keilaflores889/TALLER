from flask import current_app as app
from app.conexion.Conexion import Conexion

class UsuarioDao:

    def getUsuarios(self):
        sql = """
        SELECT 
            u.usu_id, u.usu_nick, u.usu_clave, u.usu_nro_intentos, u.usu_estado,
            f.fun_id, f.car_id, f.fun_estado,
            g.gru_id, g.gru_des,
            c.car_des
        FROM usuarios u
        JOIN funcionarios f ON u.fun_id = f.fun_id
        JOIN grupos g ON u.gru_id = g.gru_id
        JOIN cargos c ON f.car_id = c.car_id
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            usuarios = cur.fetchall()
            # Retornamos lista de dicts con info relevante (no la contraseña en texto plano)
            return [{
                "usu_id": u[0],
                "usu_nick": u[1],
                "usu_nro_intentos": u[3],
                "usu_estado": u[4],
                "fun_id": u[5],
                "car_id": u[6],
                "fun_estado": u[7],
                "gru_id": u[8],
                "gru_des": u[9],
                "car_des": u[10]
            } for u in usuarios]

        except Exception as e:
            app.logger.error(f"Error al obtener usuarios: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getUsuarioById(self, usu_id):
        sql = """
        SELECT 
            u.usu_id, u.usu_nick, u.usu_clave, u.usu_nro_intentos, u.usu_estado,
            f.fun_id, f.car_id, f.fun_estado,
            g.gru_id, g.gru_des,
            c.car_des
        FROM usuarios u
        JOIN funcionarios f ON u.fun_id = f.fun_id
        JOIN grupos g ON u.gru_id = g.gru_id
        JOIN cargos c ON f.car_id = c.car_id
        WHERE u.usu_id = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (usu_id,))
            u = cur.fetchone()
            if u:
                return {
                    "usu_id": u[0],
                    "usu_nick": u[1],
                    "usu_clave": u[2],
                    "usu_nro_intentos": u[3],
                    "usu_estado": u[4],
                    "fun_id": u[5],
                    "car_id": u[6],
                    "fun_estado": u[7],
                    "gru_id": u[8],
                    "gru_des": u[9],
                    "car_des": u[10]
                }
            else:
                return None

        except Exception as e:
            app.logger.error(f"Error al obtener usuario por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarUsuario(self, usu_nick, usu_clave, usu_nro_intentos, fun_id, gru_id, usu_estado=True):
        sql = """
        INSERT INTO usuarios(usu_nick, usu_clave, usu_nro_intentos, fun_id, gru_id, usu_estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING usu_id
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (usu_nick, usu_clave, usu_nro_intentos, fun_id, gru_id, usu_estado))
            usu_id = cur.fetchone()[0]
            con.commit()
            return usu_id
        except Exception as e:
            app.logger.error(f"Error al insertar usuario: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateUsuario(self, usu_id, usu_nick, usu_clave, usu_nro_intentos, fun_id, gru_id, usu_estado):
        sql = """
        UPDATE usuarios
        SET usu_nick=%s, usu_clave=%s, usu_nro_intentos=%s, fun_id=%s, gru_id=%s, usu_estado=%s
        WHERE usu_id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (usu_nick, usu_clave, usu_nro_intentos, fun_id, gru_id, usu_estado, usu_id))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar usuario: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteUsuario(self, usu_id):
        sql = """
        DELETE FROM usuarios
        WHERE usu_id=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (usu_id,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar usuario: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
