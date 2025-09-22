from flask import current_app as app
from app.conexion.Conexion import Conexion

class RegistroCDao:

    def estados_que_usan_cupo(self):
        """Estados que OCUPAN un cupo de la agenda"""
        return [3, 4, 10]  # Confirmado, Realizado, Reservado

    def estado_es_cancelado(self, id_estado):
        """Estados que NO ocupan cupo (liberan cupo)"""
        return id_estado in [14, 15]  # Cancelado, No Asistió, etc.

    # ===== NUEVOS MÉTODOS DE VALIDACIÓN DE HORARIOS =====
    def validar_horario_medico_disponibilidad(self, id_medico, fecha_cita, hora_cita):
        """
        Valida si la hora de la cita está dentro de la disponibilidad horaria del médico
        
        Args:
            id_medico: ID del médico
            fecha_cita: Fecha de la cita (formato: YYYY-MM-DD)
            hora_cita: Hora de la cita (formato: HH:MM)
        
        Returns:
            True si está dentro del horario, False si no
        """
        validarDisponibilidadSQL = """
        SELECT disponibilidad_hora_inicio, disponibilidad_hora_fin, disponibilidad_cupos
        FROM disponibilidad_horaria 
        WHERE id_medico = %s 
        AND disponibilidad_fecha = %s
        ORDER BY disponibilidad_hora_inicio
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(validarDisponibilidadSQL, (id_medico, fecha_cita))
            disponibilidades = cur.fetchall()
            
            if not disponibilidades:
                app.logger.warning(f"No hay disponibilidad definida para médico {id_medico} el {fecha_cita}")
                return False
            
            # Convertir hora_cita a objeto time para comparar
            from datetime import datetime, time
            if isinstance(hora_cita, str):
                hora_obj = datetime.strptime(hora_cita, '%H:%M').time()
            else:
                hora_obj = hora_cita
            
            # Verificar si la hora está dentro de algún rango de disponibilidad
            for disponibilidad in disponibilidades:
                hora_inicio = disponibilidad[0]
                hora_fin = disponibilidad[1] 
                cupos_disponibles = disponibilidad[2]
                
                if hora_inicio <= hora_obj <= hora_fin:
                    if cupos_disponibles > 0:
                        app.logger.info(f"Hora {hora_cita} válida para médico {id_medico} el {fecha_cita} (rango: {hora_inicio}-{hora_fin}, cupos: {cupos_disponibles})")
                        return True
                    else:
                        app.logger.warning(f"Sin cupos en disponibilidad para médico {id_medico} el {fecha_cita} en horario {hora_inicio}-{hora_fin}")
                        return False
            
            app.logger.warning(f"Hora {hora_cita} fuera del horario de disponibilidad del médico {id_medico} el {fecha_cita}")
            return False
            
        except Exception as e:
            app.logger.error(f"Error al validar disponibilidad horaria: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def obtener_disponibilidad_medico(self, id_medico, fecha_cita):
        """
        Obtiene la disponibilidad horaria de un médico para una fecha específica
        
        Args:
            id_medico: ID del médico
            fecha_cita: Fecha específica (YYYY-MM-DD)
        
        Returns:
            Lista de disponibilidades
        """
        consultaDisponibilidadSQL = """
        SELECT 
            id_disponibilidad,
            disponibilidad_hora_inicio,
            disponibilidad_hora_fin,
            disponibilidad_cupos
        FROM disponibilidad_horaria 
        WHERE id_medico = %s 
        AND disponibilidad_fecha = %s
        AND disponibilidad_cupos > 0
        ORDER BY disponibilidad_hora_inicio
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaDisponibilidadSQL, (id_medico, fecha_cita))
            disponibilidades = cur.fetchall()
            
            return [
                {
                    'id_disponibilidad': disp[0],
                    'hora_inicio': str(disp[1]),
                    'hora_fin': str(disp[2]),
                    'cupos_disponibles': disp[3]
                } for disp in disponibilidades
            ]
            
        except Exception as e:
            app.logger.error(f"Error al obtener disponibilidad del médico: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getRegistrosC(self):
        registrocSQL = """
        SELECT 
            cita.id_cita,
            cita.id_paciente,
            cita.id_medico,
            cita.id_especialidad,
            cita.id_turno,
            cita.fecha_cita,
            cita.hora,
            cita.id_estado,
            cita.motivo_consulta,
            cita.id_agenda_medica,
            paciente.nombre AS paciente_nombre,
            paciente.apellido AS paciente_apellido,
            medico.nombre AS medico_nombre,
            medico.apellido AS medico_apellido,
            especialidad.descripcion AS especialidad_descripcion,
            turno.descripcion AS turno_descripcion,
            estado_cita.descripcion AS estado_descripcion
        FROM cita
        JOIN paciente ON cita.id_paciente = paciente.id_paciente
        JOIN medico ON cita.id_medico = medico.id_medico
        JOIN especialidad ON cita.id_especialidad = especialidad.id_especialidad
        JOIN turno ON cita.id_turno = turno.id_turno
        JOIN estado_cita ON cita.id_estado = estado_cita.id_estado
        ORDER BY cita.fecha_cita DESC, cita.hora DESC
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registrocSQL)
            citas = cur.fetchall()
            return [
                {
                    'id_cita': cita[0],
                    'id_paciente': cita[1],
                    'id_medico': cita[2],
                    'id_especialidad': cita[3],
                    'id_turno': cita[4],
                    'fecha_cita': cita[5],
                    'hora': cita[6],
                    'id_estado': cita[7],
                    'motivo_consulta': cita[8],
                    'id_agenda_medica': cita[9],
                    'paciente_nombre': cita[10],
                    'paciente_apellido': cita[11],
                    'medico_nombre': cita[12],
                    'medico_apellido': cita[13],
                    'especialidad': cita[14],
                    'turno': cita[15],
                    'estado': cita[16]
                } for cita in citas
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener todas las citas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getRegistroCById(self, id_cita):
        registrocSQL = """
        SELECT 
            cita.id_cita,
            cita.id_paciente,
            cita.id_medico,
            cita.id_especialidad,
            cita.id_turno,
            cita.fecha_cita,
            cita.hora,
            cita.id_estado,
            cita.motivo_consulta,
            cita.id_agenda_medica,
            paciente.nombre AS paciente_nombre,
            paciente.apellido AS paciente_apellido,
            medico.nombre AS medico_nombre,
            medico.apellido AS medico_apellido,
            especialidad.descripcion AS especialidad_descripcion,
            turno.descripcion AS turno_descripcion,
            estado_cita.descripcion AS estado_descripcion,
            (medico.nombre || ' ' || medico.apellido || ' - ' || especialidad.descripcion) AS agenda_descripcion,
            agenda_medica.fecha_agenda,
            agenda_medica.id_turno AS agenda_turno_id
        FROM cita
        JOIN paciente ON cita.id_paciente = paciente.id_paciente
        JOIN medico ON cita.id_medico = medico.id_medico
        JOIN especialidad ON cita.id_especialidad = especialidad.id_especialidad
        JOIN turno ON cita.id_turno = turno.id_turno
        JOIN estado_cita ON cita.id_estado = estado_cita.id_estado
        LEFT JOIN agenda_medica ON cita.id_agenda_medica = agenda_medica.id_agenda_medica
        WHERE cita.id_cita = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(registrocSQL, (id_cita,))
            cita = cur.fetchone()
            if cita:
                return {
                    'id_cita': cita[0],
                    'id_paciente': cita[1],
                    'id_medico': cita[2],
                    'id_especialidad': cita[3],
                    'id_turno': cita[4],
                    'fecha_cita': cita[5],
                    'hora': cita[6],
                    'id_estado': cita[7],
                    'motivo_consulta': cita[8],
                    'id_agenda_medica': cita[9],
                    'paciente_nombre': cita[10],
                    'paciente_apellido': cita[11],
                    'medico_nombre': cita[12],
                    'medico_apellido': cita[13],
                    'especialidad': cita[14],
                    'turno': cita[15],
                    'estado': cita[16],
                    'agenda_descripcion': cita[17],
                    'agenda_fecha': str(cita[18]) if cita[18] else None,
                    'agenda_turno_id': cita[19]
                }
            else:
                return None
        except Exception as e:
            app.logger.error(f"Error al obtener cita por ID {id_cita}: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def guardarRegistroC(self, id_paciente, id_medico, id_especialidad, id_turno,
                        fecha_cita, hora, id_estado, motivo_consulta, id_agenda_medica):
        
        # ===== NUEVA VALIDACIÓN DE HORARIO CON DISPONIBILIDAD =====
        if not self.validar_horario_medico_disponibilidad(id_medico, fecha_cita, hora):
            return "FUERA_DE_HORARIO"
        
        # Verificar si ya existe la cita
        verificarSQL = """
        SELECT COUNT(*) FROM cita 
        WHERE id_medico = %s AND fecha_cita = %s AND hora = %s
        """
        
        # Verificar cupos disponibles
        verificarCuposSQL = "SELECT cupos FROM agenda_medica WHERE id_agenda_medica = %s"
        
        # Insertar nueva cita
        insertarSQL = """
        INSERT INTO cita (id_paciente, id_medico, id_especialidad, id_turno, 
                         fecha_cita, hora, id_estado, motivo_consulta, id_agenda_medica)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_cita
        """
        
        # Restar cupo
        restarCupoSQL = "UPDATE agenda_medica SET cupos = cupos - 1 WHERE id_agenda_medica = %s"
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            # Verificar duplicados
            cur.execute(verificarSQL, (id_medico, fecha_cita, hora))
            if cur.fetchone()[0] > 0:
                return "DUPLICADO"
            
            # Verificar cupos SOLO si el estado inicial ocupa cupo
            if int(id_estado) in self.estados_que_usan_cupo():
                cur.execute(verificarCuposSQL, (id_agenda_medica,))
                cupos_result = cur.fetchone()
                if not cupos_result or cupos_result[0] <= 0:
                    return "SIN_CUPOS"
            
            # Insertar cita
            cur.execute(insertarSQL, (
                id_paciente, id_medico, id_especialidad, id_turno,
                fecha_cita, hora, id_estado, motivo_consulta, id_agenda_medica
            ))
            
            cita_id = cur.fetchone()[0]
            
            # Restar cupo SOLO si el estado inicial ocupa cupo
            if int(id_estado) in self.estados_que_usan_cupo():
                cur.execute(restarCupoSQL, (id_agenda_medica,))
                app.logger.info(f"Cupo restado por crear cita con estado que ocupa cupo: {id_estado}")
            else:
                app.logger.info(f"No se restó cupo - estado {id_estado} no ocupa cupo")
            
            con.commit()
            app.logger.info(f"Cita guardada exitosamente con ID: {cita_id}")
            return cita_id
            
        except Exception as e:
            app.logger.error(f"Error al guardar cita: {str(e)}")
            con.rollback()
            return None
        finally:
            cur.close()
            con.close()

    def updateRegistroC(self, id_cita, id_paciente, id_medico, id_especialidad, id_turno,
                        fecha_cita, hora, id_estado, motivo_consulta, id_agenda_medica):
        
        # ===== NUEVA VALIDACIÓN DE HORARIO CON DISPONIBILIDAD =====
        if not self.validar_horario_medico_disponibilidad(id_medico, fecha_cita, hora):
            return "FUERA_DE_HORARIO"
        
        # Obtener datos actuales de la cita
        getAgendaSQL = "SELECT id_agenda_medica, id_estado FROM cita WHERE id_cita = %s"
        
        # Actualizar la cita
        updateCitaSQL = """
        UPDATE cita
        SET id_paciente=%s, id_medico=%s, id_especialidad=%s, id_turno=%s,
            fecha_cita=%s, hora=%s, id_estado=%s, motivo_consulta=%s, id_agenda_medica=%s
        WHERE id_cita=%s
        """
        
        # Operaciones de cupos
        devolverCupoSQL = "UPDATE agenda_medica SET cupos = cupos + 1 WHERE id_agenda_medica = %s"
        restarCupoSQL = "UPDATE agenda_medica SET cupos = cupos - 1 WHERE id_agenda_medica = %s"
        verificarCuposSQL = "SELECT cupos FROM agenda_medica WHERE id_agenda_medica = %s"

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            # Obtener datos actuales
            cur.execute(getAgendaSQL, (id_cita,))
            citaData = cur.fetchone()
            if not citaData:
                app.logger.error(f"No se encontró la cita con ID: {id_cita}")
                return False
                
            id_agenda_anterior = citaData[0]
            estado_anterior = citaData[1]

            # Convertir estados a enteros para comparación
            estado_anterior = int(estado_anterior)
            id_estado = int(id_estado)
            
            # Determinar si los estados ocupan cupo
            estado_anterior_ocupa_cupo = estado_anterior in self.estados_que_usan_cupo()
            estado_nuevo_ocupa_cupo = id_estado in self.estados_que_usan_cupo()
            
            # Verificar cupos ANTES de hacer cambios (solo si necesitamos ocupar un nuevo cupo)
            cambio_de_agenda = id_agenda_medica != id_agenda_anterior
            necesita_nuevo_cupo = False
            
            if cambio_de_agenda and estado_nuevo_ocupa_cupo:
                # Cambió de agenda Y el nuevo estado ocupa cupo
                necesita_nuevo_cupo = True
            elif not cambio_de_agenda and not estado_anterior_ocupa_cupo and estado_nuevo_ocupa_cupo:
                # Misma agenda, pero cambió de "no ocupa cupo" a "ocupa cupo"
                necesita_nuevo_cupo = True
                
            if necesita_nuevo_cupo:
                agenda_a_verificar = id_agenda_medica if cambio_de_agenda else id_agenda_anterior
                cur.execute(verificarCuposSQL, (agenda_a_verificar,))
                cupos_result = cur.fetchone()
                if not cupos_result or cupos_result[0] <= 0:
                    app.logger.error(f"Sin cupos disponibles en agenda: {agenda_a_verificar}")
                    return "SIN_CUPOS"

            # Actualizar la cita
            cur.execute(updateCitaSQL, (
                id_paciente, id_medico, id_especialidad, id_turno,
                fecha_cita, hora, id_estado, motivo_consulta, id_agenda_medica, id_cita
            ))
            
            filas_afectadas = cur.rowcount
            
            # =========== LÓGICA SIMPLIFICADA DE CUPOS ===========
            
            if cambio_de_agenda:
                # CAMBIÓ DE AGENDA
                app.logger.info(f"Cambio de agenda: {id_agenda_anterior} → {id_agenda_medica}")
                
                # 1. Liberar cupo de agenda anterior (si ocupaba cupo)
                if estado_anterior_ocupa_cupo:
                    cur.execute(devolverCupoSQL, (id_agenda_anterior,))
                    app.logger.info(f"Cupo liberado de agenda anterior: {id_agenda_anterior}")
                
                # 2. Ocupar cupo en nueva agenda (si el nuevo estado ocupa cupo)
                if estado_nuevo_ocupa_cupo:
                    cur.execute(restarCupoSQL, (id_agenda_medica,))
                    app.logger.info(f"Cupo ocupado en nueva agenda: {id_agenda_medica}")
                    
            else:
                # MISMA AGENDA - SOLO CAMBIÓ EL ESTADO
                app.logger.info(f"Cambio de estado: {estado_anterior} → {id_estado}")
                
                if estado_anterior_ocupa_cupo and not estado_nuevo_ocupa_cupo:
                    # Era ocupado → ahora es libre (ej: Confirmado → Cancelado)
                    cur.execute(devolverCupoSQL, (id_agenda_anterior,))
                    app.logger.info(f"Cupo liberado por cambio a estado libre: {id_agenda_anterior}")
                    
                elif not estado_anterior_ocupa_cupo and estado_nuevo_ocupa_cupo:
                    # Era libre → ahora es ocupado (ej: Cancelado → Confirmado)
                    cur.execute(restarCupoSQL, (id_agenda_medica,))
                    app.logger.info(f"Cupo ocupado por cambio a estado ocupado: {id_agenda_medica}")
                    
                # Si ambos ocupan cupo O ambos no ocupan cupo → NO hacer nada
                # Esto resuelve el problema: Reservado ↔ Confirmado no cambia cupos
                elif estado_anterior_ocupa_cupo and estado_nuevo_ocupa_cupo:
                    app.logger.info(f"Cambio entre estados que ocupan cupo - no se modifica cupo")
                elif not estado_anterior_ocupa_cupo and not estado_nuevo_ocupa_cupo:
                    app.logger.info(f"Cambio entre estados que no ocupan cupo - no se modifica cupo")

            con.commit()
            app.logger.info(f"Cita actualizada exitosamente: {id_cita}")
            return filas_afectadas > 0
            
        except Exception as e:
            app.logger.error(f"Error al actualizar cita {id_cita}: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteRegistroC(self, id_cita):
        # Obtener datos de la cita antes de eliminar para manejar cupos
        getCitaSQL = "SELECT id_agenda_medica, id_estado FROM cita WHERE id_cita = %s"
        deleteRegistrocSQL = "DELETE FROM cita WHERE id_cita=%s"
        devolverCupoSQL = "UPDATE agenda_medica SET cupos = cupos + 1 WHERE id_agenda_medica = %s"
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            # Obtener datos de la cita
            cur.execute(getCitaSQL, (id_cita,))
            citaData = cur.fetchone()
            
            if citaData:
                id_agenda_medica, id_estado = citaData
                
                # Eliminar la cita
                cur.execute(deleteRegistrocSQL, (id_cita,))
                filas_afectadas = cur.rowcount
                
                # Si la cita tenía un estado que usaba cupo, devolver el cupo
                if int(id_estado) in self.estados_que_usan_cupo() and id_agenda_medica:
                    cur.execute(devolverCupoSQL, (id_agenda_medica,))
                    app.logger.info(f"Cupo devuelto a agenda {id_agenda_medica} por eliminación de cita con estado {id_estado}")
                
                con.commit()
                app.logger.info(f"Cita eliminada exitosamente: {id_cita}")
                return filas_afectadas > 0
            else:
                app.logger.error(f"No se encontró la cita con ID: {id_cita}")
                return False
                
        except Exception as e:
            app.logger.error(f"Error al eliminar cita {id_cita}: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def getAgendas(self):
        consulta = """
        SELECT 
            a.id_agenda_medica,
            m.nombre || ' ' || m.apellido AS medico_nombre,
            e.descripcion AS especialidad,
            a.fecha_agenda,
            t.descripcion AS turno,
            a.cupos
        FROM agenda_medica a
        JOIN medico m ON a.id_medico = m.id_medico
        JOIN especialidad e ON a.id_especialidad = e.id_especialidad
        JOIN turno t ON a.id_turno = t.id_turno
        WHERE a.cupos > 0  -- Solo mostrar agendas con cupos disponibles
        ORDER BY a.fecha_agenda DESC
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consulta)
            agendas = cur.fetchall()
            return [
                {
                    "id_agenda_medica": fila[0],
                    "medico": fila[1],
                    "especialidad": fila[2],
                    "fecha": str(fila[3]),
                    "turno": fila[4],
                    "cupos": fila[5]
                } for fila in agendas
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener agendas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()