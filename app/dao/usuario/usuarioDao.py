from flask import current_app as app
from app.conexion.Conexion import Conexion
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioDao:

    # Listar todos los usuarios (sin mostrar la clave)
    def getUsuarios(self):
        sql = "SELECT id_usuario, nickname, estado FROM usuarios"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            usuarios = cur.fetchall()
            return [{'id_usuario': u[0], 'nickname': u[1], 'estado': u[2]} for u in usuarios]
        except Exception as e:
            app.logger.error(f"Error al obtener usuarios: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener usuario por ID (sin mostrar la clave)
    def getUsuarioById(self, id_usuario):
        sql = "SELECT id_usuario, nickname, estado FROM usuarios WHERE id_usuario=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_usuario,))
            u = cur.fetchone()
            if u:
                return {'id_usuario': u[0], 'nickname': u[1], 'estado': u[2]}
            return None
        finally:
            cur.close()
            con.close()

    # Guardar usuario (hash automático)
    def guardarUsuario(self, nickname, clave, estado):
        sql = "INSERT INTO usuarios(nickname, clave, estado) VALUES (%s, %s, %s) RETURNING id_usuario"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            hashed = generate_password_hash(clave)
            cur.execute(sql, (nickname, hashed, estado))
            usuario_id = cur.fetchone()[0]
            con.commit()
            return usuario_id
        except Exception as e:
            app.logger.error(f"Error al guardar usuario: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # Actualizar usuario (hash automático si se cambia la clave)
    def updateUsuario(self, id_usuario, nickname, clave, estado):
        sql = "UPDATE usuarios SET nickname=%s, clave=%s, estado=%s WHERE id_usuario=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            hashed = generate_password_hash(clave)
            cur.execute(sql, (nickname, hashed, estado, id_usuario))
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

    # Eliminar usuario
    def deleteUsuario(self, id_usuario):
        sql = "DELETE FROM usuarios WHERE id_usuario=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_usuario,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        finally:
            cur.close()
            con.close()

    # Verificar login
    def verificarLogin(self, nickname, clave_ingresada):
        sql = "SELECT id_usuario, clave, estado FROM usuarios WHERE nickname=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nickname,))
            u = cur.fetchone()
            if not u:
                return False
            usuario_id, hash_guardado, estado = u
            if check_password_hash(hash_guardado, clave_ingresada) and estado:
                return {'id_usuario': usuario_id, 'nickname': nickname, 'estado': estado}
            return False
        finally:
            cur.close()
            con.close()
