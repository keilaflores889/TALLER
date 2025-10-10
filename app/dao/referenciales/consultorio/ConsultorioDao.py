import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class ConsultorioDao:
    def _normalizarTelefono(self, telefono):
        """Agrega el prefijo +595 si no lo tiene y limpia espacios."""
        if not telefono:
            return None
        telefono = telefono.strip().replace(" ", "")
        # Si comienza con 0, reemplazamos por +595
        if telefono.startswith("0"):
            telefono = "+595" + telefono[1:]
        elif not telefono.startswith("+595"):
            telefono = "+595" + telefono
        return telefono

    def _esTelefonoParaguayoValido(self, telefono):
        """Valida formato +595XXXXXXXX o +5959XXXXXXXX"""
        return bool(re.match(r'^\+595\d{8,9}$', telefono))

    def _esCorreoValido(self, correo):
        """Valida correo electrónico básico"""
        return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo))

    def existeDuplicado(self, nombre_consultorio, correo, codigo_excluir=None):
        """
        Verifica si existe un consultorio con el mismo nombre o correo.
        Si se proporciona codigo_excluir, ignora ese registro (útil para actualizaciones).
        """
        if codigo_excluir:
            sql = """
            SELECT 1 FROM consultorio
            WHERE (UPPER(nombre_consultorio) = UPPER(%s) OR UPPER(correo) = UPPER(%s))
            AND codigo != %s
            """
            params = (nombre_consultorio, correo, codigo_excluir)
        else:
            sql = """
            SELECT 1 FROM consultorio
            WHERE UPPER(nombre_consultorio) = UPPER(%s) OR UPPER(correo) = UPPER(%s)
            """
            params = (nombre_consultorio, correo)
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchone() is not None
        except Exception as e:
            app.logger.error(f"Error al verificar duplicado de consultorio: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def getConsultorios(self):
        """Obtiene todos los consultorios"""
        sql = "SELECT codigo, nombre_consultorio, direccion, telefono, correo FROM consultorio ORDER BY nombre_consultorio"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            consultorios = []
            for row in cur.fetchall():
                consultorios.append({
                    'codigo': row[0],
                    'nombre_consultorio': row[1],
                    'direccion': row[2],
                    'telefono': row[3],
                    'correo': row[4]
                })
            return consultorios
        except Exception as e:
            app.logger.error(f"Error al obtener consultorios: {str(e)}")
            raise
        finally:
            cur.close()
            con.close()

    def getConsultorioById(self, codigo):
        """Obtiene un consultorio por su código"""
        sql = "SELECT codigo, nombre_consultorio, direccion, telefono, correo FROM consultorio WHERE codigo = %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (codigo,))
            row = cur.fetchone()
            if row:
                return {
                    'codigo': row[0],
                    'nombre_consultorio': row[1],
                    'direccion': row[2],
                    'telefono': row[3],
                    'correo': row[4]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener consultorio por ID: {str(e)}")
            raise
        finally:
            cur.close()
            con.close()

    def guardarConsultorio(self, nombre_consultorio, direccion, telefono, correo):
        # Validaciones previas
        if not nombre_consultorio or len(nombre_consultorio) < 3:
            raise ValueError("El nombre del consultorio es obligatorio y debe tener al menos 3 caracteres.")

        if not correo or not self._esCorreoValido(correo):
            raise ValueError("El correo electrónico no es válido.")

        telefono = self._normalizarTelefono(telefono)
        if not self._esTelefonoParaguayoValido(telefono):
            raise ValueError("El número de teléfono no es válido. Debe ser paraguayo (+595).")

        if self.existeDuplicado(nombre_consultorio, correo):
            raise ValueError("Ya existe un consultorio con ese nombre o correo.")

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
            raise
        finally:
            cur.close()
            con.close()

    def updateConsultorio(self, codigo, nombre_consultorio, direccion, telefono, correo):
        # Validaciones
        if not nombre_consultorio or len(nombre_consultorio) < 3:
            raise ValueError("El nombre del consultorio es obligatorio y debe tener al menos 3 caracteres.")

        if not correo or not self._esCorreoValido(correo):
            raise ValueError("El correo electrónico no es válido.")

        telefono = self._normalizarTelefono(telefono)
        if not self._esTelefonoParaguayoValido(telefono):
            raise ValueError("El número de teléfono no es válido. Debe ser paraguayo (+595).")

        # Verificar duplicados excluyendo el registro actual
        if self.existeDuplicado(nombre_consultorio, correo, codigo):
            raise ValueError("Ya existe otro consultorio con ese nombre o correo.")

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
            raise
        finally:
            cur.close()
            con.close()

    def deleteConsultorio(self, codigo):
        """Elimina un consultorio por su código"""
        sql = "DELETE FROM consultorio WHERE codigo = %s"
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
            raise
        finally:
            cur.close()
            con.close()