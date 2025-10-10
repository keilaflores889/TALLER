import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class CargoDao:

    # ============================
    # OBTENER DATOS
    # ============================

    def getCargos(self):
        sql = """
        SELECT id_cargo, descripcion
        FROM cargo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            cargos = cur.fetchall()
            return [{'id_cargo': c[0], 'descripcion': c[1]} for c in cargos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los cargos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getCargoById(self, id_cargo):
        sql = """
        SELECT id_cargo, descripcion
        FROM cargo
        WHERE id_cargo = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_cargo,))
            cargo = cur.fetchone()
            if cargo:
                return {"id_cargo": cargo[0], "descripcion": cargo[1]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener cargo: {str(e)}")
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
        Verifica si ya existe un cargo con esa descripción.
        """
        sql = """
        SELECT 1 FROM cargo WHERE descripcion = %s
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

    def existeDescripcionExceptoId(self, descripcion, id_cargo):
        """
        Verifica si existe otro cargo con esa descripción, excluyendo el id actual.
        """
        sql = """
        SELECT 1 FROM cargo WHERE descripcion = %s AND id_cargo != %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_cargo))
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

    def guardarCargo(self, descripcion):
        sql = """
        INSERT INTO cargo (descripcion)
        VALUES (%s)
        RETURNING id_cargo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            id_cargo = cur.fetchone()[0]
            con.commit()
            return id_cargo
        except Exception as e:
            app.logger.error(f"Error al insertar cargo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateCargo(self, id_cargo, descripcion):
        sql = """
        UPDATE cargo
        SET descripcion = %s
        WHERE id_cargo = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, id_cargo))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar cargo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteCargo(self, id_cargo):
        sql = """
        DELETE FROM cargo
        WHERE id_cargo = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_cargo,))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar cargo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
