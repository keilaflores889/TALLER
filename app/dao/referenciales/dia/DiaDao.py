# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion
import re

class DiaDao:

    def getDias(self):
        diaSQL = """
        SELECT id_dia, descripcion
        FROM dia
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(diaSQL)
            dias = cur.fetchall()  # trae datos de la bd

            # Transformar los datos en una lista de diccionarios
            return [{'id_dia': dia[0], 'descripcion': dia[1]} for dia in dias]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los dias: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getDiaById(self, id_dia):
        diaSQL = """
        SELECT id_dia, descripcion
        FROM dia WHERE id_dia=%s
        """
        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(diaSQL, (id_dia,))
            diaEncontrada = cur.fetchone()  # Obtener una sola fila
            if diaEncontrada:
                return {
                    "id_dia": diaEncontrada[0],
                    "descripcion": diaEncontrada[1]
                }  # Retornar los datos de los dias
            else:
                return None  # Retornar None si no se encuentra el dia
        except Exception as e:
            app.logger.error(f"Error al obtener dia: {str(e)}")
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
        patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(patron, descripcion):
            return False, "La descripción solo puede contener letras y espacios"
        
        return True, None

    def _verificar_duplicado(self, descripcion, id_dia=None):
        """
        Verifica si ya existe un día con la misma descripción.
        Si id_dia se proporciona, excluye ese registro de la búsqueda (para edición).
        Retorna True si existe duplicado, False si no existe.
        """
        if id_dia:
            sql = """
            SELECT COUNT(*) FROM dia 
            WHERE LOWER(TRIM(descripcion)) = LOWER(TRIM(%s)) 
            AND id_dia != %s
            """
            params = (descripcion, id_dia)
        else:
            sql = """
            SELECT COUNT(*) FROM dia 
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

    def guardarDia(self, descripcion):
        # Validar descripción
        es_valido, mensaje_error = self._validar_descripcion(descripcion)
        if not es_valido:
            app.logger.warning(f"Validación fallida: {mensaje_error}")
            return {"error": mensaje_error, "success": False}
        
        # Verificar duplicados
        if self._verificar_duplicado(descripcion):
            app.logger.warning(f"Intento de insertar día duplicado: {descripcion}")
            return {"error": "Ya existe un día con esta descripción", "success": False}
        
        insertDiaSQL = """
        INSERT INTO dia(descripcion) VALUES(%s) RETURNING id_dia
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        # Ejecucion exitosa
        try:
            cur.execute(insertDiaSQL, (descripcion.strip(),))
            dia_id = cur.fetchone()[0]
            con.commit()  # se confirma la insercion
            return dia_id

        # Si algo fallo entra aqui
        except Exception as e:
            app.logger.error(f"Error al insertar dia: {str(e)}")
            con.rollback()  # retroceder si hubo error
            return {"error": "Error al guardar el día", "success": False}

        # Siempre se va ejecutar
        finally:
            cur.close()
            con.close()

    def updateDia(self, id_dia, descripcion):
        # Validar descripción
        es_valido, mensaje_error = self._validar_descripcion(descripcion)
        if not es_valido:
            app.logger.warning(f"Validación fallida: {mensaje_error}")
            return {"error": mensaje_error, "success": False}
        
        # Verificar duplicados (excluyendo el registro actual)
        if self._verificar_duplicado(descripcion, id_dia):
            app.logger.warning(f"Intento de actualizar a día duplicado: {descripcion}")
            return {"error": "Ya existe un día con esta descripción", "success": False}
        
        updateDiaSQL = """
        UPDATE dia
        SET descripcion=%s
        WHERE id_dia=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateDiaSQL, (descripcion.strip(), id_dia,))
            filas_afectadas = cur.rowcount  # Obtener el número de filas afectadas
            con.commit()

            return filas_afectadas > 0  # Retornar True si se actualizó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al actualizar dia: {str(e)}")
            con.rollback()
            return {"error": "Error al actualizar el día", "success": False}

        finally:
            cur.close()
            con.close()

    def deleteDia(self, id):
        deleteDiaSQL = """
        DELETE FROM dia
        WHERE id_dia=%s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteDiaSQL, (id,))
            rows_affected = cur.rowcount
            con.commit()

            return rows_affected > 0  # Retornar True si se eliminó al menos una fila

        except Exception as e:
            app.logger.error(f"Error al eliminar dia: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()