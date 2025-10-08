# DiagnosticoDao.py
from flask import current_app as app
from app.conexion.Conexion import Conexion

class DiagnosticoDao:

    # Listar todos los diagnósticos
    def getDiagnosticos(self):
        sql = """
        SELECT d.id_diagnostico,
               d.id_consulta_detalle,
               d.id_medico,
               d.id_paciente,
               d.id_tipo_diagnostico,
               td.tipo_diagnostico AS tipo_diagnostico,
               d.descripcion_diagnostico,
               d.fecha_diagnostico,
               d.pieza_dental,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM diagnosticos d
        LEFT JOIN tipo_diagnostico td ON d.id_tipo_diagnostico = td.id_tipo_diagnostico
        LEFT JOIN medico m ON d.id_medico = m.id_medico
        LEFT JOIN paciente p ON d.id_paciente = p.id_paciente
        ORDER BY d.fecha_diagnostico DESC, d.id_diagnostico DESC;
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
            app.logger.error(f"Error al obtener diagnósticos: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener un diagnóstico por id
    def getDiagnosticoById(self, id_diagnostico):
        sql = """
        SELECT d.id_diagnostico,
               d.id_consulta_detalle,
               d.id_medico,
               d.id_paciente,
               d.id_tipo_diagnostico,
               td.tipo_diagnostico AS tipo_diagnostico,
               d.descripcion_diagnostico,
               d.fecha_diagnostico,
               d.pieza_dental,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM diagnosticos d
        LEFT JOIN tipo_diagnostico td ON d.id_tipo_diagnostico = td.id_tipo_diagnostico
        LEFT JOIN medico m ON d.id_medico = m.id_medico
        LEFT JOIN paciente p ON d.id_paciente = p.id_paciente
        WHERE d.id_diagnostico = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_diagnostico,))
            row = cur.fetchone()
            if row:
                columnas = [desc[0] for desc in cur.description]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener diagnóstico {id_diagnostico}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # Obtener diagnósticos por consulta detalle
    def getDiagnosticosByConsultaDetalle(self, id_consulta_detalle):
        sql = """
        SELECT d.id_diagnostico,
               d.id_consulta_detalle,
               d.id_medico,
               d.id_paciente,
               d.id_tipo_diagnostico,
               td.tipo_diagnostico AS tipo_diagnostico,
               d.descripcion_diagnostico,
               d.fecha_diagnostico,
               d.pieza_dental,
               m.nombre || ' ' || m.apellido AS medico_nombre,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM diagnosticos d
        LEFT JOIN tipo_diagnostico td ON d.id_tipo_diagnostico = td.id_tipo_diagnostico
        LEFT JOIN medico m ON d.id_medico = m.id_medico
        LEFT JOIN paciente p ON d.id_paciente = p.id_paciente
        WHERE d.id_consulta_detalle = %s
        ORDER BY d.fecha_diagnostico DESC;
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
            app.logger.error(f"Error al obtener diagnósticos de consulta {id_consulta_detalle}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener diagnósticos por paciente
    def getDiagnosticosByPaciente(self, id_paciente):
        sql = """
        SELECT d.id_diagnostico,
               d.id_consulta_detalle,
               d.id_medico,
               d.id_paciente,
               d.id_tipo_diagnostico,
               td.tipo_diagnostico AS tipo_diagnostico,
               d.descripcion_diagnostico,
               d.fecha_diagnostico,
               d.pieza_dental,
               m.nombre || ' ' || m.apellido AS medico_nombre
        FROM diagnosticos d
        LEFT JOIN tipo_diagnostico td ON d.id_tipo_diagnostico = td.id_tipo_diagnostico
        LEFT JOIN medico m ON d.id_medico = m.id_medico
        WHERE d.id_paciente = %s
        ORDER BY d.fecha_diagnostico DESC;
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
            app.logger.error(f"Error al obtener diagnósticos del paciente {id_paciente}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Obtener diagnósticos por médico
    def getDiagnosticosByMedico(self, id_medico):
        sql = """
        SELECT d.id_diagnostico,
               d.id_consulta_detalle,
               d.id_medico,
               d.id_paciente,
               d.id_tipo_diagnostico,
               td.tipo_diagnostico AS tipo_diagnostico,
               d.descripcion_diagnostico,
               d.fecha_diagnostico,
               d.pieza_dental,
               p.nombre || ' ' || p.apellido AS paciente_nombre
        FROM diagnosticos d
        LEFT JOIN tipo_diagnostico td ON d.id_tipo_diagnostico = td.id_tipo_diagnostico
        LEFT JOIN paciente p ON d.id_paciente = p.id_paciente
        WHERE d.id_medico = %s
        ORDER BY d.fecha_diagnostico DESC;
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
            app.logger.error(f"Error al obtener diagnósticos del médico {id_medico}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # Agregar un diagnóstico
    def addDiagnostico(self, diagnostico):
        sql = """
        INSERT INTO diagnosticos (
            id_consulta_detalle,
            id_medico,
            id_paciente,
            id_tipo_diagnostico,
            descripcion_diagnostico,
            fecha_diagnostico,
            pieza_dental
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_diagnostico;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                diagnostico['id_consulta_detalle'],
                diagnostico['id_medico'],
                diagnostico['id_paciente'],
                diagnostico.get('id_tipo_diagnostico'),
                diagnostico['descripcion_diagnostico'],
                diagnostico.get('fecha_diagnostico'),
                diagnostico.get('pieza_dental')
            ))
            id_diagnostico = cur.fetchone()[0]
            con.commit()
            return id_diagnostico
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al agregar diagnóstico: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # Actualizar diagnóstico
    def updateDiagnostico(self, id_diagnostico, diagnostico):
        sql = """
        UPDATE diagnosticos SET
            id_medico = %s,
            id_paciente = %s,
            id_tipo_diagnostico = %s,
            descripcion_diagnostico = %s,
            fecha_diagnostico = %s,
            pieza_dental = %s
        WHERE id_diagnostico = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                diagnostico['id_medico'],
                diagnostico['id_paciente'],
                diagnostico.get('id_tipo_diagnostico'),
                diagnostico['descripcion_diagnostico'],
                diagnostico.get('fecha_diagnostico'),
                diagnostico.get('pieza_dental'),
                id_diagnostico
            ))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar diagnóstico {id_diagnostico}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    # Eliminar diagnóstico
    def deleteDiagnostico(self, id_diagnostico):
        sql = "DELETE FROM diagnosticos WHERE id_diagnostico = %s;"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_diagnostico,))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar diagnóstico {id_diagnostico}: {e}")
            return False
        finally:
            cur.close()
            con.close()