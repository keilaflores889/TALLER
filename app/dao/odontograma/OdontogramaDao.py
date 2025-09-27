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
            o.id_ficha_medica,
            'FM-' || fm.id_ficha_medica || ' - ' || p.nombre || ' ' || p.apellido AS ficha_medica,
            o.id_paciente,
            o.id_medico,
            o.fecha_registro AS fecha,
            o.observaciones,
            o.estado,
            p.nombre || ' ' || p.apellido AS paciente,
            fm.cedula AS cedula,
            DATE_PART('year', AGE(p.fecha_nacimiento)) AS edad,
            m.nombre || ' ' || m.apellido AS medico
        FROM odontograma o
        JOIN paciente p ON o.id_paciente = p.id_paciente
        JOIN medico m ON o.id_medico = m.id_medico
        JOIN ficha_medica fm ON o.id_ficha_medica = fm.id_ficha_medica
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
            o.id_ficha_medica,
            'FM-' || fm.id_ficha_medica || ' - ' || p.nombre || ' ' || p.apellido AS ficha_medica,
            o.id_paciente,
            o.id_medico,
            o.fecha_registro AS fecha,
            o.observaciones,
            o.estado,
            p.nombre || ' ' || p.apellido AS paciente,
            fm.cedula AS cedula,
            DATE_PART('year', AGE(p.fecha_nacimiento)) AS edad,
            m.nombre || ' ' || m.apellido AS medico
        FROM odontograma o
        JOIN paciente p ON o.id_paciente = p.id_paciente
        JOIN medico m ON o.id_medico = m.id_medico
        JOIN ficha_medica fm ON o.id_ficha_medica = fm.id_ficha_medica
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
            ed.color
        FROM odontograma_detalle od
        JOIN estado_dental ed ON od.id_estado_dental = ed.id_estado_dental
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

    def getOdontogramaByFicha(self, id_ficha_medica):
        """Obtener odontograma por ID de ficha médica"""
        sql = """
        SELECT 
            o.id_odontograma,
            o.id_ficha_medica,
            'FM-' || fm.id_ficha_medica || ' - ' || p.nombre || ' ' || p.apellido AS ficha_medica,
            o.id_paciente,
            o.id_medico,
            o.fecha_registro AS fecha,
            o.observaciones,
            o.estado,
            p.nombre || ' ' || p.apellido AS paciente,
            fm.cedula AS cedula,
            DATE_PART('year', AGE(p.fecha_nacimiento)) AS edad,
            m.nombre || ' ' || m.apellido AS medico
        FROM odontograma o
        JOIN paciente p ON o.id_paciente = p.id_paciente
        JOIN medico m ON o.id_medico = m.id_medico
        JOIN ficha_medica fm ON o.id_ficha_medica = fm.id_ficha_medica
        WHERE o.id_ficha_medica = %s
        ORDER BY o.fecha_registro DESC
        LIMIT 1
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_ficha_medica,))
            row = cur.fetchone()
            if row:
                columnas = [desc[0] for desc in cur.description]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener odontograma por ficha {id_ficha_medica}: {e}")
            return None
        finally:
            cur.close()
            con.close()

    def addOdontograma(self, odontograma):
        """Crear un nuevo odontograma"""
        get_ficha_sql = """
        SELECT id_paciente, id_medico 
        FROM ficha_medica 
        WHERE id_ficha_medica = %s
        """
        
        insert_sql = """
        INSERT INTO odontograma (
            id_ficha_medica, id_paciente, id_medico, 
            fecha_registro, observaciones, estado
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id_odontograma
        """
        
        update_ficha_sql = """
        UPDATE ficha_medica 
        SET tiene_odontograma = TRUE 
        WHERE id_ficha_medica = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(get_ficha_sql, (odontograma['id_ficha_medica'],))
            ficha_data = cur.fetchone()
            if not ficha_data:
                raise Exception("Ficha médica no encontrada")
            
            id_paciente, id_medico = ficha_data
            
            cur.execute(insert_sql, (
                odontograma['id_ficha_medica'],
                id_paciente,
                id_medico,
                odontograma.get('fecha_registro'),
                odontograma.get('observaciones', ''),
                odontograma.get('estado', 'Activo')
            ))
            id_odontograma = cur.fetchone()[0]
            
            cur.execute(update_ficha_sql, (odontograma['id_ficha_medica'],))
            
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
        """Eliminar odontograma y sus detalles"""
        get_ficha_sql = "SELECT id_ficha_medica FROM odontograma WHERE id_odontograma = %s"
        delete_detalles_sql = "DELETE FROM odontograma_detalle WHERE id_odontograma = %s"
        delete_sql = "DELETE FROM odontograma WHERE id_odontograma = %s"
        update_ficha_sql = "UPDATE ficha_medica SET tiene_odontograma = FALSE WHERE id_ficha_medica = %s"
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(get_ficha_sql, (id_odontograma,))
            ficha_result = cur.fetchone()
            
            if ficha_result:
                id_ficha_medica = ficha_result[0]
                cur.execute(delete_detalles_sql, (id_odontograma,))
                cur.execute(delete_sql, (id_odontograma,))
                cur.execute(update_ficha_sql, (id_ficha_medica,))
                con.commit()
                return True
            return False
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
        JOIN estado_dental ed ON od.id_estado_dental = ed.id_estado_dental
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
        sql = """
        INSERT INTO odontograma_detalle (
            id_odontograma, numero_diente, id_estado_dental, 
            superficie
        ) VALUES (%s, %s, %s, %s)
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

    def getFichasMedicas(self):
        """Obtener fichas médicas activas con formato"""
        sql = """
        SELECT 
            fm.id_ficha_medica,
            fm.id_paciente,
            p.nombre || ' ' || p.apellido AS paciente_nombre,
            fm.cedula,  
            fm.fecha_registro,
            'FM-' || fm.id_ficha_medica || ' - ' || p.nombre || ' ' || p.apellido AS ficha_label
        FROM ficha_medica fm
        JOIN paciente p ON fm.id_paciente = p.id_paciente
        WHERE fm.estado = 'Activo'
        ORDER BY fm.fecha_registro DESC
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
            app.logger.error(f"Error al obtener fichas médicas: {e}")
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

    def esFichaMedicaDisponible(self, id_ficha_medica):
        """Verificar si una ficha médica está disponible para crear odontograma"""
        sql = """
        SELECT COUNT(*) 
        FROM odontograma 
        WHERE id_ficha_medica = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_ficha_medica,))
            count = cur.fetchone()[0]
            return count == 0
        except Exception as e:
            app.logger.error(f"Error al verificar disponibilidad de ficha {id_ficha_medica}: {e}")
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
