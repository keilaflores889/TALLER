import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class EspecialidadDao:

    # ============================
    # OBTENER DATOS
    # ============================

    def getEspecialidades(self):
        especialidadSQL = """
        SELECT id_especialidad, descripcion
        FROM especialidad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(especialidadSQL)
            especialidades = cur.fetchall()
            return [{'id_especialidad': especialidad[0], 'descripcion': especialidad[1]} for especialidad in especialidades]
        except Exception as e:
            app.logger.error(f"Error al obtener todas las especialidades: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getEspecialidadById(self, id_especialidad):
        especialidadSQL = """
        SELECT id_especialidad, descripcion
        FROM especialidad WHERE id_especialidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(especialidadSQL, (id_especialidad,))
            especialidadEncontrada = cur.fetchone()
            if especialidadEncontrada:
                return {
                    "id_especialidad": especialidadEncontrada[0],
                    "descripcion": especialidadEncontrada[1]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener especialidad: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def validarDescripcion(self, descripcion):
        """
        Permite letras (incluyendo ñ y acentuadas), números y espacios.
        """
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s]+$"
        return bool(re.match(patron, descripcion))

    def existeDescripcion(self, descripcion):
        """
        Verifica si ya existe una especialidad con esa descripción.
        """
        sql = """
        SELECT 1 FROM especialidad WHERE descripcion = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de descripción: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def existeDescripcionExceptoId(self, descripcion, id_especialidad):
        """
        Verifica si existe otra especialidad con esa descripción, excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM especialidad WHERE descripcion = %s AND id_especialidad != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_especialidad))
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar existencia de descripción (excepto id): {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # CRUD
    # ============================

    def guardarEspecialidad(self, descripcion):
        insertEspecialidadSQL = """
        INSERT INTO especialidad(descripcion) VALUES(%s) RETURNING id_especialidad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insertEspecialidadSQL, (descripcion,))
            especialidad_id = cur.fetchone()[0]
            con.commit()
            return especialidad_id
        except Exception as e:
            app.logger.error(f"Error al insertar especialidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateEspecialidad(self, id_especialidad, descripcion):
        updateEspecialidadSQL = """
        UPDATE especialidad
        SET descripcion=%s
        WHERE id_especialidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(updateEspecialidadSQL, (descripcion, id_especialidad,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar especialidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteEspecialidad(self, id_especialidad):
        deleteEspecialidadSQL = """
        DELETE FROM especialidad
        WHERE id_especialidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(deleteEspecialidadSQL, (id_especialidad,))
            rows_affected = cur.rowcount
            con.commit()
            return rows_affected > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar especialidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()