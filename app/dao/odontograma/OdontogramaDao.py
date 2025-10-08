from flask import current_app as app
from app.conexion.Conexion import Conexion

class OdontogramaDao:

    # ==========================
    # ODONTOGRAMAS
    # ==========================

    def getOdontogramas(self):
        """Obtener todos los odontogramas con información relacionada"""
        sql = """
        SELECT 
            o.id_odontograma,
            o.id_paciente,
            o.id_medico,
            o.fecha_registro,
            o.observaciones,
            o.estado,
            p.nombre || ' ' || p.apellido AS paciente,
            p.cedula_entidad AS cedula,
            DATE_PART('year', AGE(p.fecha_nacimiento)) AS edad,
            m.nombre || ' ' || m.apellido AS medico
        FROM odontograma o
        INNER JOIN paciente p ON o.id_paciente = p.id_paciente
        INNER JOIN medico m ON o.id_medico = m.id_medico
        ORDER BY o.fecha_registro DESC
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
            app.logger.error(f"Error al obtener odontogramas: {e}")
            return []
        finally:
            cur.close()
            con.close()

    def getOdontogramaById(self, id_odontograma):
        """Obtener un odontograma específico por ID con sus detalles"""
        sql = """
        SELECT 
            o.id_odontograma,
            o.id_paciente,
            o.id_medico,
            o.fecha_registro,
            o.observaciones,
            o.estado,
            p.nombre || ' ' || p.apellido AS paciente,
            p.cedula_entidad AS cedula,
            DATE_PART('year', AGE(p.fecha_nacimiento)) AS edad,
            m.nombre || ' ' || m.apellido AS medico
        FROM odontograma o
        INNER JOIN paciente p ON o.id_paciente = p.id_paciente
        INNER JOIN medico m ON o.id_medico = m.id_medico
        WHERE o.id_odontograma = %s
        """
        
        # Consulta para obtener detalles
        detalles_sql = """
        SELECT 
            od.id_odontograma_detalle,
            od.numero_diente AS diente,
            od.superficie,
            od.id_estado_dental,
            ed.descripcion AS estado_descripcion,
            ed.color,
            ed.simbolo
        FROM odontograma_detalle od
        INNER JOIN estado_dental ed ON od.id_estado_dental = ed.id_estado_dental
        WHERE od.id_odontograma = %s
        ORDER BY od.numero_diente, od.superficie
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            # Obtener datos principales del odontograma
            cur.execute(sql, (id_odontograma,))
            row = cur.fetchone()
            if not row:
                return None
                
            columnas = [desc[0] for desc in cur.description]
            odontograma = dict(zip(columnas, row))
            
            # Obtener detalles
            cur.execute(detalles_sql, (id_odontograma,))
            detalles_rows = cur.fetchall()
            if detalles_rows:
                detalles_columnas = [desc[0] for desc in cur.description]
                detalles = [dict(zip(detalles_columnas, detail_row)) for detail_row in detalles_rows]
                odontograma['detalle'] = detalles
            else:
                odontograma['detalle'] = []
            
            return odontograma
        except Exception as e:
            app.logger.error(f"Error al obtener odontograma {id_odontograma}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    def getOdontogramaByPaciente(self, id_paciente):
        """Obtener el odontograma más reciente de un paciente"""
        sql = """
        SELECT 
            o.id_odontograma,
            o.id_paciente,
            o.id_medico,
            o.fecha_registro,
            o.observaciones,
            o.estado,
            p.nombre || ' ' || p.apellido AS paciente,
            p.cedula_entidad AS cedula,
            DATE_PART('year', AGE(p.fecha_nacimiento)) AS edad,
            m.nombre || ' ' || m.apellido AS medico
        FROM odontograma o
        INNER JOIN paciente p ON o.id_paciente = p.id_paciente
        INNER JOIN medico m ON o.id_medico = m.id_medico
        WHERE o.id_paciente = %s
        ORDER BY o.fecha_registro DESC
        LIMIT 1
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_paciente,))
            row = cur.fetchone()
            if row:
                columnas = [desc[0] for desc in cur.description]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener odontograma del paciente {id_paciente}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    def addOdontograma(self, odontograma):
        """Crear un nuevo odontograma"""
        insert_sql = """
        INSERT INTO odontograma (
            id_paciente, id_medico, 
            fecha_registro, observaciones, estado
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING id_odontograma
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(insert_sql, (
                odontograma['id_paciente'],
                odontograma['id_medico'],
                odontograma.get('fecha_registro'),
                odontograma.get('observaciones', ''),
                odontograma.get('estado', 'Activo')
            ))
            id_odontograma = cur.fetchone()[0]
            
            con.commit()
            app.logger.info(f"Odontograma creado con ID: {id_odontograma}")
            return id_odontograma
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al crear odontograma: {e}")
            return None
        finally:
            cur.close()
            con.close()

    def updateOdontograma(self, id_odontograma, odontograma):
        """Actualizar un odontograma existente"""
        sql = """
        UPDATE odontograma SET
            observaciones = %s,
            estado = %s
        WHERE id_odontograma = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                odontograma.get('observaciones', ''),
                odontograma.get('estado', 'Activo'),
                id_odontograma
            ))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar odontograma {id_odontograma}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    def deleteOdontograma(self, id_odontograma):
        """Eliminar odontograma y sus detalles (CASCADE lo hace automáticamente)"""
        delete_sql = "DELETE FROM odontograma WHERE id_odontograma = %s"
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(delete_sql, (id_odontograma,))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar odontograma {id_odontograma}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    # ==========================
    # DETALLES DE ODONTOGRAMA (DIENTES)
    # ==========================

    def getDetallesOdontograma(self, id_odontograma):
        """Obtener todos los detalles de un odontograma"""
        sql = """
        SELECT 
            od.id_odontograma_detalle,
            od.id_odontograma,
            od.numero_diente,
            od.id_estado_dental,
            od.superficie,
            ed.descripcion AS estado_descripcion,
            ed.color,
            ed.simbolo
        FROM odontograma_detalle od
        INNER JOIN estado_dental ed ON od.id_estado_dental = ed.id_estado_dental
        WHERE od.id_odontograma = %s
        ORDER BY od.numero_diente, od.superficie
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_odontograma,))
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            app.logger.error(f"Error al obtener detalles del odontograma {id_odontograma}: {e}")
            return []
        finally:
            cur.close()
            con.close()

    def addDetalleOdontograma(self, detalle):
        """Agregar un detalle al odontograma"""
        sql = """
        INSERT INTO odontograma_detalle (
            id_odontograma, numero_diente, id_estado_dental, 
            superficie
        ) VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_odontograma, numero_diente, superficie)
        DO UPDATE SET id_estado_dental = EXCLUDED.id_estado_dental
        RETURNING id_odontograma_detalle
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                detalle['id_odontograma'],
                detalle['numero_diente'],
                detalle['id_estado_dental'],
                detalle.get('superficie', 'C')
            ))
            id_detalle = cur.fetchone()[0]
            con.commit()
            return id_detalle
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al agregar detalle de odontograma: {e}")
            return None
        finally:
            cur.close()
            con.close()

    def updateDetalleOdontograma(self, id_detalle, detalle):
        """Actualizar un detalle del odontograma"""
        sql = """
        UPDATE odontograma_detalle SET
            id_estado_dental = %s,
            superficie = %s
        WHERE id_odontograma_detalle = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (
                detalle['id_estado_dental'],
                detalle.get('superficie', 'C'),
                id_detalle
            ))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar detalle {id_detalle}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    def deleteDetalleOdontograma(self, id_detalle):
        """Eliminar un detalle del odontograma"""
        sql = "DELETE FROM odontograma_detalle WHERE id_odontograma_detalle = %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_detalle,))
            con.commit()
            return cur.rowcount > 0
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar detalle {id_detalle}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    def deleteDetallesByOdontograma(self, id_odontograma):
        """Eliminar todos los detalles de un odontograma específico"""
        sql = "DELETE FROM odontograma_detalle WHERE id_odontograma = %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_odontograma,))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar detalles del odontograma {id_odontograma}: {e}")
            return False
        finally:
            cur.close()
            con.close()

    # ==========================
    # MÉTODOS AUXILIARES
    # ==========================

    def getEstadosDentales(self):
        """Obtener todos los estados dentales activos"""
        sql = """
        SELECT id_estado_dental, descripcion, color, simbolo 
        FROM estado_dental 
        WHERE estado = TRUE
        ORDER BY descripcion
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
            app.logger.error(f"Error al obtener estados dentales: {e}")
            return []
        finally:
            cur.close()
            con.close()

    def getPacientes(self):
        """Obtener pacientes activos"""
        sql = """
        SELECT 
            id_paciente,
            nombre || ' ' || apellido AS nombre_completo,
            cedula_entidad AS cedula,
            fecha_nacimiento
        FROM paciente
        WHERE estado = 'Activo'
        ORDER BY nombre, apellido
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
            app.logger.error(f"Error al obtener pacientes: {e}")
            return []
        finally:
            cur.close()
            con.close()

    def getMedicos(self):
        """Obtener médicos activos"""
        sql = """
        SELECT 
            id_medico,
            nombre || ' ' || apellido AS nombre_completo,
            especialidad,
            cedula AS medico_cedula
        FROM medico
        WHERE estado = 'Activo'
        ORDER BY nombre, apellido
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
            app.logger.error(f"Error al obtener médicos: {e}")
            return []
        finally:
            cur.close()
            con.close()

    def existeOdontogramaPaciente(self, id_paciente):
        """Verificar si un paciente ya tiene un odontograma"""
        sql = """
        SELECT COUNT(*) 
        FROM odontograma 
        WHERE id_paciente = %s AND estado = 'Activo'
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_paciente,))
            count = cur.fetchone()[0]
            return count > 0
        except Exception as e:
            app.logger.error(f"Error al verificar odontograma del paciente {id_paciente}: {e}")
            return False
        finally:
            cur.close()
            con.close()