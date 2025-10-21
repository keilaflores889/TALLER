# TratamientoDao.py
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TratamientoDao:

    # Listar todos los tratamientos
    def getTratamientos(self):
        sql = """
        SELECT t.id_tratamiento,
               t.id_consulta_detalle,
               t.id_medico,
               t.id_paciente,
               t.descripcion_tratamiento,
               t.fecha_tratamiento,
               t.duracion_estimada,
               t.costo_estimado,
               t.estado,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM tratamientos t
        LEFT JOIN medico m ON t.id_medico = m.id_medico
        LEFT JOIN paciente p ON t.id_paciente = p.id_paciente
        ORDER BY t.fecha_tratamiento DESC, t.id_tratamiento DESC;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener un tratamiento por id
    def getTratamientoById(self, id_tratamiento):
        sql = """
        SELECT t.id_tratamiento,
               t.id_consulta_detalle,
               t.id_medico,
               t.id_paciente,
               t.descripcion_tratamiento,
               t.fecha_tratamiento,
               t.duracion_estimada,
               t.costo_estimado,
               t.estado,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM tratamientos t
        LEFT JOIN medico m ON t.id_medico = m.id_medico
        LEFT JOIN paciente p ON t.id_paciente = p.id_paciente
        WHERE t.id_tratamiento = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tratamiento,))
            row = cur.fetchone()
            if row:
                columnas = [desc[0] for desc in cur.description]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tratamiento {id_tratamiento}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # Obtener tratamientos por consulta detalle
    def getTratamientosByConsultaDetalle(self, id_consulta_detalle):
        sql = """
        SELECT t.id_tratamiento,
               t.id_consulta_detalle,
               t.id_medico,
               t.id_paciente,
               t.descripcion_tratamiento,
               t.fecha_tratamiento,
               t.duracion_estimada,
               t.costo_estimado,
               t.estado,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM tratamientos t
        LEFT JOIN medico m ON t.id_medico = m.id_medico
        LEFT JOIN paciente p ON t.id_paciente = p.id_paciente
        WHERE t.id_consulta_detalle = %s
        ORDER BY t.fecha_tratamiento DESC;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_consulta_detalle,))
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos de consulta {id_consulta_detalle}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener tratamientos por paciente
    def getTratamientosByPaciente(self, id_paciente):
        sql = """
        SELECT t.id_tratamiento,
               t.id_consulta_detalle,
               t.id_medico,
               t.id_paciente,
               t.descripcion_tratamiento,
               t.fecha_tratamiento,
               t.duracion_estimada,
               t.costo_estimado,
               t.estado,
               m.nombre || ' ' || m.apellido AS medico_nombre
        FROM tratamientos t
        LEFT JOIN medico m ON t.id_medico = m.id_medico
        WHERE t.id_paciente = %s
        ORDER BY t.fecha_tratamiento DESC;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_paciente,))
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos del paciente {id_paciente}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener tratamientos por médico
    def getTratamientosByMedico(self, id_medico):
        sql = """
        SELECT t.id_tratamiento,
               t.id_consulta_detalle,
               t.id_medico,
               t.id_paciente,
               t.descripcion_tratamiento,
               t.fecha_tratamiento,
               t.duracion_estimada,
               t.costo_estimado,
               t.estado,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM tratamientos t
        LEFT JOIN paciente p ON t.id_paciente = p.id_paciente
        WHERE t.id_medico = %s
        ORDER BY t.fecha_tratamiento DESC;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico,))
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos del médico {id_medico}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Agregar un tratamiento
    def addTratamiento(self, tratamiento):
        sql = """
        INSERT INTO tratamientos (
            id_consulta_detalle,
            id_medico,
            id_paciente,
            descripcion_tratamiento,
            fecha_tratamiento,
            duracion_estimada,
            costo_estimado,
            estado
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_tratamiento;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                tratamiento['id_consulta_detalle'],
                tratamiento['id_medico'],
                tratamiento['id_paciente'],
                tratamiento['descripcion_tratamiento'],
                tratamiento.get('fecha_tratamiento'),
                tratamiento.get('duracion_estimada'),
                tratamiento.get('costo_estimado'),
                tratamiento.get('estado', 'pendiente')
            ))
            id_tratamiento = cur.fetchone()[0]
            con.commit()
            return id_tratamiento
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al agregar tratamiento: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # Actualizar tratamiento
    def updateTratamiento(self, id_tratamiento, tratamiento):
        sql = """
        UPDATE tratamientos SET
            id_medico = %s,
            id_paciente = %s,
            descripcion_tratamiento = %s,
            fecha_tratamiento = %s,
            duracion_estimada = %s,
            costo_estimado = %s,
            estado = %s
        WHERE id_tratamiento = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                tratamiento['id_medico'],
                tratamiento['id_paciente'],
                tratamiento['descripcion_tratamiento'],
                tratamiento.get('fecha_tratamiento'),
                tratamiento.get('duracion_estimada'),
                tratamiento.get('costo_estimado'),
                tratamiento.get('estado', 'pendiente'),
                id_tratamiento
            ))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar tratamiento {id_tratamiento}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    def updateTratamientoParcial(self, id_tratamiento, tratamiento):
        """Actualiza solo costo, duración y estado del tratamiento"""
        sql = """
        UPDATE tratamientos SET
            duracion_estimada = %s,
            costo_estimado = %s,
            estado = %s
        WHERE id_tratamiento = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                tratamiento.get('duracion_estimada'),
                tratamiento.get('costo_estimado'),
                tratamiento.get('estado', 'pendiente'),
                id_tratamiento
            ))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar tratamiento parcial {id_tratamiento}: {e}")
            return False
        finally:
            cur.close()
            con.close()


    # Eliminar tratamiento
    def deleteTratamiento(self, id_tratamiento):
        sql = "DELETE FROM tratamientos WHERE id_tratamiento = %s;"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tratamiento,))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar tratamiento {id_tratamiento}: {e}")
            return False
        finally:
            cur.close()
            con.close()