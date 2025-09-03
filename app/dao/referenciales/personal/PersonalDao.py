from flask import current_app as app
from app.conexion.Conexion import Conexion

class PersonalDao:

    def getPersonal(self):
        sql = """
            SELECT p.id_personal, p.nombre, p.apellido, 
                   p.cedula, p.fecha_nacimiento, p.fecha_registro,
                   p.telefono, p.direccion, p.correo,
                   p.id_ciudad, c.descripcion AS ciudad,
                   p.id_cargo, ca.descripcion AS cargo
            FROM personal p
            LEFT JOIN ciudad c ON p.id_ciudad = c.id_ciudad
            LEFT JOIN cargo ca ON p.id_cargo = ca.id_cargo
            ORDER BY p.id_personal
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            personal = cur.fetchall()
            return [
                {
                    "id_personal": per[0],
                    "nombre": per[1],
                    "apellido": per[2],
                    "cedula": per[3],
                    "fecha_nacimiento": str(per[4]) if per[4] else None,
                    "fecha_registro": str(per[5]) if per[5] else None,
                    "telefono": per[6],
                    "direccion": per[7],
                    "correo": per[8],
                    "id_ciudad": per[9],
                    "ciudad": per[10],
                    "id_cargo": per[11],
                    "cargo": per[12]
                }
                for per in personal
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener personal: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getPersonalById(self, personal_id):
        sql = """
            SELECT p.id_personal, p.nombre, p.apellido, 
                   p.cedula, p.fecha_nacimiento, p.fecha_registro,
                   p.telefono, p.direccion, p.correo,
                   p.id_ciudad, c.descripcion AS ciudad,
                   p.id_cargo, ca.descripcion AS cargo
            FROM personal p
            LEFT JOIN ciudad c ON p.id_ciudad = c.id_ciudad
            LEFT JOIN cargo ca ON p.id_cargo = ca.id_cargo
            WHERE p.id_personal = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (personal_id,))
            per = cur.fetchone()
            if per:
                return {
                    "id_personal": per[0],
                    "nombre": per[1],
                    "apellido": per[2],
                    "cedula": per[3],
                    "fecha_nacimiento": str(per[4]) if per[4] else None,
                    "fecha_registro": str(per[5]) if per[5] else None,
                    "telefono": per[6],
                    "direccion": per[7],
                    "correo": per[8],
                    "id_ciudad": per[9],
                    "ciudad": per[10],
                    "id_cargo": per[11],
                    "cargo": per[12]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener personal por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def guardarPersonal(self, nombre, apellido, cedula, fecha_nacimiento,
                        telefono, direccion, correo, id_ciudad, id_cargo, fecha_registro=None):
        sql = """
            INSERT INTO personal (nombre, apellido, cedula, fecha_nacimiento,
                                  telefono, direccion, correo, id_ciudad, id_cargo, fecha_registro)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_personal
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre, apellido, cedula, fecha_nacimiento,
                              telefono, direccion, correo, id_ciudad, id_cargo, fecha_registro))
            personal_id = cur.fetchone()[0]
            con.commit()
            return personal_id
        except Exception as e:
            app.logger.error(f"Error al insertar personal: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
    
    def updatePersonal(self, personal_id, nombre, apellido, cedula, fecha_nacimiento,
                       telefono, direccion, correo, id_ciudad, id_cargo, fecha_registro=None):
        sql = """
            UPDATE personal
            SET nombre=%s, apellido=%s, cedula=%s, fecha_nacimiento=%s,
                telefono=%s, direccion=%s, correo=%s, id_ciudad=%s, id_cargo=%s, fecha_registro=%s
            WHERE id_personal=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre, apellido, cedula, fecha_nacimiento,
                              telefono, direccion, correo, id_ciudad, id_cargo, fecha_registro, personal_id))
            actualizado = cur.rowcount > 0
            con.commit()
            return actualizado
        except Exception as e:
            app.logger.error(f"Error al actualizar personal: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deletePersonal(self, personal_id):
        sql = "DELETE FROM personal WHERE id_personal=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (personal_id,))
            eliminado = cur.rowcount > 0
            con.commit()
            return eliminado
        except Exception as e:
            app.logger.error(f"Error al eliminar personal: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def existeDuplicado(self, cedula, correo):
        """Verifica si ya existe un personal con la misma cédula o correo"""
        sql = "SELECT COUNT(*) FROM personal WHERE cedula = %s OR correo = %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (cedula, correo))
            result = cur.fetchone()[0]
            return result > 0
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
