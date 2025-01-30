# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion

class UsuarioDao:

    def getUsuarios(self):
        usuariosSQL = """
        SELECT id_usuario, nickname, clave, estado
        FROM usuarios
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(usuariosSQL)
            usuarios = cur.fetchall()  # Trae datos de la BD

            # Transformar los datos en una lista de diccionarios
            return [{'id_usuario': usuario[0], 'nickname': usuario[1], 'clave': usuario[2], 'estado': usuario[3]} for usuario in usuarios]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los usuarios: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getUsuarioById(self, id_usuario):
        usuarioSQL = """
        SELECT id_usuario, nickname, clave, estado
        FROM usuarios WHERE id_usuario=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(usuarioSQL, (id_usuario,))
            usuarioEncontrado = cur.fetchone()  # Obtener una sola fila
            if usuarioEncontrado:
                return {
                    "id_usuario": usuarioEncontrado[0],
                    "nickname": usuarioEncontrado[1],
                    "clave": usuarioEncontrado[2],
                    "estado": usuarioEncontrado[3]
                }  # Retornar los datos del usuario
            else:
                return None  # Retornar None si no se encuentra el usuario
        except Exception as e:
            app.logger.error(f"Error al obtener usuario: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarUsuario(self, nickname, clave, estado):
        insertUsuarioSQL = """
        INSERT INTO usuarios(nickname, clave, estado) 
        VALUES(%s, %s, %s) RETURNING id_usuario
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertUsuarioSQL, (nickname, clave, estado))
            usuario_id = cur.fetchone()[0]
            con.commit()  # Confirmar la inserción
            return usuario_id

        except Exception as e:
            app.logger.error(f"Error al insertar usuario: {str(e)}")
            con.rollback()  # Retroceder si hubo error
            return False

        finally:
            cur.close()
            con.close()

    def updateUsuario(self, id_usuario, nickname, clave, estado):
        updateUsuarioSQL = """
        UPDATE usuarios
        SET nickname=%s, clave=%s, estado=%s
        WHERE id_usuario=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateUsuarioSQL, (nickname, clave, estado, id_usuario))
            filas_afectadas = cur.rowcount  # Número de filas afectadas
            con.commit()
            return filas_afectadas > 0  # Retornar True si se actualizó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al actualizar usuario: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteUsuario(self, id_usuario):
        deleteUsuarioSQL = """
        DELETE FROM usuarios
        WHERE id_usuario=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteUsuarioSQL, (id_usuario,))
            rows_affected = cur.rowcount
            con.commit()
            return rows_affected > 0  # Retornar True si se eliminó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al eliminar usuario: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()