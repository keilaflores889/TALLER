# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion
import re

class TurnoDao:

    def getTurnos(self):
        turnoSQL = """
        SELECT id_turno, descripcion
        FROM turno
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(turnoSQL)
            turnos = cur.fetchall()  # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_turno': turno[0], 'descripcion': turno[1]} for turno in turnos]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los turnos: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getTurnoById(self, id_turno):
        turnoSQL = """
        SELECT id_turno, descripcion
        FROM turno WHERE id_turno=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(turnoSQL, (id_turno,))
            turnoEncontrado = cur.fetchone()  # Obtener una sola fila
            if turnoEncontrado:
                return {
                    "id_turno": turnoEncontrado[0],
                    "descripcion": turnoEncontrado[1]
                }  # Retornar los datos del turno
            else:
                return None  # Retornar None si no se encuentra el turno
        except Exception as e:
            app.logger.error(f"Error al obtener turno: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def _validar_descripcion(self, descripcion):
        """
        Valida que la descripción solo contenga letras y espacios.
        Retorna (es_valido, mensaje_error)
        """
        if not descripcion or not descripcion.strip():
            return False, "La descripción no puede estar vacía"
        
        descripcion = descripcion.strip()
        
        # Validar longitud
        if len(descripcion) < 3:
            return False, "La descripción debe tener al menos 3 caracteres"
        
        if len(descripcion) > 50:
            return False, "La descripción no puede superar los 50 caracteres"
        
        # Validar que solo contenga letras (incluye acentos y ñ) y espacios
        patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$'
        if not re.match(patron, descripcion):
            return False, "La descripción solo puede contener letras y espacios"
        
        return True, None

    def _verificar_duplicado(self, descripcion, id_turno=None):
        """
        Verifica si ya existe un turno con la misma descripción.
        Si id_turno se proporciona, excluye ese registro de la búsqueda (para edición).
        Retorna True si existe duplicado, False si no existe.
        """
        if id_turno:
            sql = """
            SELECT COUNT(*) FROM turno 
            WHERE LOWER(TRIM(descripcion)) = LOWER(TRIM(%s)) 
            AND id_turno != %s
            """
            params = (descripcion, id_turno)
        else:
            sql = """
            SELECT COUNT(*) FROM turno 
            WHERE LOWER(TRIM(descripcion)) = LOWER(TRIM(%s))
            """
            params = (descripcion,)
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(sql, params)
            count = cur.fetchone()[0]
            return count > 0
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def guardarTurno(self, descripcion):
        # Validar descripción
        es_valido, mensaje_error = self._validar_descripcion(descripcion)
        if not es_valido:
            app.logger.warning(f"Validación fallida: {mensaje_error}")
            return {"error": mensaje_error, "success": False}
        
        # Verificar duplicados
        if self._verificar_duplicado(descripcion):
            app.logger.warning(f"Intento de insertar turno duplicado: {descripcion}")
            return {"error": "Ya existe un turno con esta descripción", "success": False}
        
        insertTurnoSQL = """
        INSERT INTO turno(descripcion) VALUES(%s) RETURNING id_turno
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertTurnoSQL, (descripcion.strip(),))
            turno_id = cur.fetchone()[0]
            con.commit()  # se confirma la insercion
            return turno_id

        # Si algo fallo entra aqui
        except Exception as e:
            app.logger.error(f"Error al insertar turno: {str(e)}")
            con.rollback()  # retroceder si hubo error
            return {"error": "Error al guardar el turno", "success": False}

        # Siempre se va ejecutar
        finally:
            cur.close()
            con.close()

    def updateTurno(self, id_turno, descripcion):
        # Validar descripción
        es_valido, mensaje_error = self._validar_descripcion(descripcion)
        if not es_valido:
            app.logger.warning(f"Validación fallida: {mensaje_error}")
            return {"error": mensaje_error, "success": False}
        
        # Verificar duplicados (excluyendo el registro actual)
        if self._verificar_duplicado(descripcion, id_turno):
            app.logger.warning(f"Intento de actualizar a turno duplicado: {descripcion}")
            return {"error": "Ya existe un turno con esta descripción", "success": False}
        
        updateTurnoSQL = """
        UPDATE turno
        SET descripcion=%s
        WHERE id_turno=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateTurnoSQL, (descripcion.strip(), id_turno,))
            filas_afectadas = cur.rowcount  # Obtener el número de filas afectadas
            con.commit()

            return filas_afectadas > 0  # Retornar True si se actualizó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al actualizar turno: {str(e)}")
            con.rollback()
            return {"error": "Error al actualizar el turno", "success": False}

        finally:
            cur.close()
            con.close()

    def deleteTurno(self, id_turno):
        deleteTurnoSQL = """
        DELETE FROM turno
        WHERE id_turno=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteTurnoSQL, (id_turno,))
            rows_affected = cur.rowcount
            con.commit()

            return rows_affected > 0  # Retornar True si se eliminó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al eliminar turno: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()