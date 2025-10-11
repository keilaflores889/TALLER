# Data access object - DAO
from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime  # ✅ AGREGAR ESTE IMPORT

# ✅ AGREGAR ESTA FUNCIÓN COMPLETA AQUÍ (después de los imports, antes de la clase)
def formatear_hora_12h(hora_24h):
    """Convierte hora formato 24h a 12h con a.m./p.m. en minúsculas y formato 01:00"""
    if not hora_24h:
        return None
    
    try:
        # Si hora_24h es string (ej: "14:30:00")
        if isinstance(hora_24h, str):
            # Intentar con ambos formatos
            try:
                hora_obj = datetime.strptime(hora_24h, "%H:%M:%S")
            except ValueError:
                hora_obj = datetime.strptime(hora_24h, "%H:%M")
        else:
            # Si es un objeto time
            hora_obj = datetime.combine(datetime.today(), hora_24h)
        
        # Formato con ceros a la izquierda (01, 02, etc.) y am/pm en minúsculas con puntos
        hora_formateada = hora_obj.strftime("%I:%M %p").lower()
        return hora_formateada.replace('am', 'a.m.').replace('pm', 'p.m.')  # ✅ Agregar puntos
    except Exception as e:
        app.logger.error(f"Error al formatear hora: {str(e)}")
        return str(hora_24h)

def validar_duracion_maxima(hora_inicio, hora_fin, max_horas=10):
    """Valida que la diferencia entre hora_inicio y hora_fin no supere max_horas"""
    try:
        # Convertir strings a objetos datetime
        if isinstance(hora_inicio, str):
            # ✅ Intentar primero con formato HH:MM:SS, luego HH:MM
            try:
                inicio = datetime.strptime(hora_inicio, "%H:%M:%S")
            except ValueError:
                inicio = datetime.strptime(hora_inicio, "%H:%M")
        else:
            inicio = datetime.combine(datetime.today(), hora_inicio)
            
        if isinstance(hora_fin, str):
            # ✅ Intentar primero con formato HH:MM:SS, luego HH:MM
            try:
                fin = datetime.strptime(hora_fin, "%H:%M:%S")
            except ValueError:
                fin = datetime.strptime(hora_fin, "%H:%M")
        else:
            fin = datetime.combine(datetime.today(), hora_fin)
        
        # Calcular diferencia en horas
        diferencia = (fin - inicio).total_seconds() / 3600
        
        if diferencia > max_horas:
            return {
                'valido': False,
                'mensaje': f'La jornada de atención no puede superar las {max_horas} horas. Duración actual: {diferencia:.1f} horas.'
            }
        
        if diferencia <= 0:
            return {
                'valido': False,
                'mensaje': 'La hora de fin debe ser posterior a la hora de inicio.'
            }
            
        return {'valido': True, 'duracion': diferencia}
        
    except Exception as e:
        app.logger.error(f"Error al validar duración: {str(e)}")
        return {'valido': False, 'mensaje': 'Error al validar las horas.'}

class DisponibilidadDao:

    def getDisponibilidades(self):
        sql = """
        SELECT d.id_disponibilidad, d.id_medico, d.disponibilidad_hora_inicio, 
               d.disponibilidad_hora_fin, d.disponibilidad_fecha, d.disponibilidad_cupos,
               m.nombre || ' ' || m.apellido AS medico_nombre
        FROM disponibilidad_horaria d
        JOIN medico m ON d.id_medico = m.id_medico
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            disponibilidades = cur.fetchall()
            return [
                {
                    'id_disponibilidad': d[0],
                    'id_medico': d[1],
                    'disponibilidad_hora_inicio': formatear_hora_12h(d[2]),
                    'disponibilidad_hora_fin': formatear_hora_12h(d[3]),
                    'disponibilidad_fecha': str(d[4]),
                    'disponibilidad_cupos': d[5],
                    'medico_nombre': d[6]
                } for d in disponibilidades
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidades: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getDisponibilidadById(self, id_disponibilidad):
        sql = """
        SELECT d.id_disponibilidad, d.id_medico, d.disponibilidad_hora_inicio, 
               d.disponibilidad_hora_fin, d.disponibilidad_fecha, d.disponibilidad_cupos,
               m.nombre || ' ' || m.apellido AS medico_nombre
        FROM disponibilidad_horaria d
        JOIN medico m ON d.id_medico = m.id_medico
        WHERE d.id_disponibilidad = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_disponibilidad,))
            d = cur.fetchone()
            if d:
                return {
                    'id_disponibilidad': d[0],
                    'id_medico': d[1],
                    'disponibilidad_hora_inicio': formatear_hora_12h(d[2]),  
                    'disponibilidad_hora_fin': formatear_hora_12h(d[3]), 
                    'disponibilidad_fecha': str(d[4]),
                    'disponibilidad_cupos': d[5],
                    'medico_nombre': d[6]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidad: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getDisponibilidadesPorMedicoFecha(self, id_medico, fecha):
        """
        Retorna todas las disponibilidades de un médico en una fecha específica.
        """
        sql = """
        SELECT id_disponibilidad, disponibilidad_hora_inicio, disponibilidad_hora_fin, disponibilidad_cupos
        FROM disponibilidad_horaria
        WHERE id_medico = %s AND disponibilidad_fecha = %s
        ORDER BY disponibilidad_hora_inicio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico, fecha))
            rows = cur.fetchall()
            return [
                {
                    'id_disponibilidad': r[0],
                    'disponibilidad_hora_inicio': formatear_hora_12h(r[1]),  
                    'disponibilidad_hora_fin': formatear_hora_12h(r[2]),  
                    'disponibilidad_cupos': r[3]
                } for r in rows
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidades por médico y fecha: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def existeDisponibilidad(self, id_medico, hora_inicio, hora_fin, fecha, excluir_id=None):
        """
        Verifica si existe una disponibilidad que solapa con el intervalo [hora_inicio, hora_fin)
        para el mismo médico y fecha. Si excluir_id se pasa, lo excluye de la búsqueda (útil en updates).
        """
        # La condición NOT (existing_end <= new_start OR existing_start >= new_end)
        sql = """
        SELECT id_disponibilidad
        FROM disponibilidad_horaria
        WHERE id_medico = %s
          AND disponibilidad_fecha = %s
          AND NOT (disponibilidad_hora_fin <= %s OR disponibilidad_hora_inicio >= %s)
        """
        params = [id_medico, fecha, hora_inicio, hora_fin]
        if excluir_id:
            sql += " AND id_disponibilidad != %s"
            params.append(excluir_id)

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, tuple(params))
            existe = cur.fetchone() is not None
            if existe:
                app.logger.debug(f"Existe disponibilidad solapada: medico={id_medico}, fecha={fecha}, inicio={hora_inicio}, fin={hora_fin}, excluir_id={excluir_id}")
            return existe
        except Exception as e:
            app.logger.error(f"Error en existeDisponibilidad: {str(e)}")
            # En caso de error devolvemos False para no bloquear la lógica (mantén logs para depurar)
            return False
        finally:
            cur.close()
            con.close()

    def guardarDisponibilidad(self, id_medico, hora_inicio, hora_fin, fecha, cupos):
        # ✅ AGREGAR VALIDACIÓN DE 8 HORAS
        validacion = validar_duracion_maxima(hora_inicio, hora_fin, max_horas=10)  # ✅
        if not validacion['valido']:
            app.logger.warning(validacion['mensaje'])
            return {'error': validacion['mensaje'], 'success': False}
        
        if self.existeDisponibilidad(id_medico, hora_inicio, hora_fin, fecha):
            app.logger.warning("Disponibilidad duplicada detectada")
            return {'error': 'Ya existe una disponibilidad en ese horario.', 'success': False}

        sql = """
        INSERT INTO disponibilidad_horaria(id_medico, disponibilidad_hora_inicio, 
                                        disponibilidad_hora_fin, disponibilidad_fecha, disponibilidad_cupos)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_disponibilidad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico, hora_inicio, hora_fin, fecha, cupos))
            new_id = cur.fetchone()[0]
            con.commit()
            return {'success': True, 'id': new_id}
        except Exception as e:
            app.logger.error(f"Error al insertar disponibilidad: {str(e)}")
            con.rollback()
            return {'error': 'Error al guardar la disponibilidad.', 'success': False}
        finally:
            cur.close()
            con.close()

    def updateDisponibilidad(self, id_disponibilidad, id_medico, hora_inicio, hora_fin, fecha, cupos):
        # ✅ AGREGAR VALIDACIÓN DE 8 HORAS
        validacion = validar_duracion_maxima(hora_inicio, hora_fin, max_horas=10)  # 
        if not validacion['valido']:
            app.logger.warning(validacion['mensaje'])
            return {'error': validacion['mensaje'], 'success': False}
        
        if self.existeDisponibilidad(id_medico, hora_inicio, hora_fin, fecha, excluir_id=id_disponibilidad):
            app.logger.warning("Disponibilidad duplicada detectada en update")
            return {'error': 'Ya existe una disponibilidad en ese horario.', 'success': False}

        sql = """
        UPDATE disponibilidad_horaria
        SET id_medico=%s,
            disponibilidad_hora_inicio=%s,
            disponibilidad_hora_fin=%s,
            disponibilidad_fecha=%s,
            disponibilidad_cupos=%s
        WHERE id_disponibilidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medico, hora_inicio, hora_fin, fecha, cupos, id_disponibilidad))
            filas = cur.rowcount
            con.commit()
            return {'success': True, 'updated': filas > 0}
        except Exception as e:
            app.logger.error(f"Error al actualizar disponibilidad: {str(e)}")
            con.rollback()
            return {'error': 'Error al actualizar la disponibilidad.', 'success': False}
        finally:
            cur.close()
            con.close()

    def deleteDisponibilidad(self, id_disponibilidad):
        sql = "DELETE FROM disponibilidad_horaria WHERE id_disponibilidad=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_disponibilidad,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar disponibilidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
    