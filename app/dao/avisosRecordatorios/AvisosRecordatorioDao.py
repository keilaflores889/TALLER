from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime

class AvisoRecordatorioDao:

    # ==============================
    #   HELPER: SANITIZAR ENTEROS
    # ==============================
    @staticmethod
    def sanitize_int(value):
        """Convierte a int o retorna None si es inválido"""
        if value in (None, "", "undefined", "null"):
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    # ==============================
    #   HELPER: VALIDAR FECHA/HORA
    # ==============================
    @staticmethod
    def validar_fecha_hora_futura(fecha_cita, hora_cita):
        """Valida que la fecha y hora de la cita sean futuras"""
        from datetime import datetime, date, time
        
        if not fecha_cita or not hora_cita:
            return False, "Fecha y hora son obligatorias"
        
        # Convertir a objetos date/time si vienen como strings
        if isinstance(fecha_cita, str):
            try:
                fecha_cita = datetime.strptime(fecha_cita, "%Y-%m-%d").date()
            except:
                return False, "Formato de fecha inválido"
        
        if isinstance(hora_cita, str):
            try:
                hora_cita = datetime.strptime(hora_cita, "%H:%M").time()
            except:
                return False, "Formato de hora inválido"
        
        # Combinar fecha y hora
        fecha_hora_cita = datetime.combine(fecha_cita, hora_cita)
        ahora = datetime.now()
        
        if fecha_hora_cita < ahora:
            return False, "La fecha de la cita deben ser futuras"
        
        return True, None

    # ==============================
    #   LISTAR TODOS LOS AVISOS
    # ==============================
    def getAvisos(self):
        sql = """
        SELECT a.id_aviso,
            p.nombre || ' ' || p.apellido AS paciente,
            p.telefono AS telefono_paciente,
            per.nombre || ' ' || per.apellido AS personal,
            m.nombre || ' ' || m.apellido AS medico,
            c.nombre_consultorio,
            a.fecha_cita,
            a.hora_cita,
            a.forma_envio,
            a.mensaje,
            a.estado_envio,
            a.estado_confirmacion
        FROM avisos_recordatorios a
        JOIN paciente p ON a.id_paciente = p.id_paciente
        JOIN personal per ON a.id_personal = per.id_personal
        LEFT JOIN medico m ON a.id_medico = m.id_medico
        JOIN consultorio c ON a.codigo = c.codigo
        ORDER BY a.fecha_cita DESC, a.hora_cita DESC;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            rows = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]

            def convert(row):
                data = dict(zip(columnas, row))
                if data.get("fecha_cita") and hasattr(data["fecha_cita"], "isoformat"):
                    data["fecha_cita"] = data["fecha_cita"].isoformat()
                if data.get("hora_cita") and hasattr(data["hora_cita"], "strftime"):
                    data["hora_cita"] = data["hora_cita"].strftime("%H:%M")
                return data

            return [convert(row) for row in rows]
        except Exception as e:
            app.logger.error(f"Error en AvisoRecordatorioDao.getAvisos: {e}")
            return []
        finally:
            cur.close()
            con.close()

    # ==============================
#   VERIFICAR DUPLICADO
# ==============================
    def existeDuplicado(self, id_paciente, id_medico, fecha_cita, hora_cita, id_aviso_excluir=None):
        """
        Verifica si existe un aviso duplicado.
        :param id_aviso_excluir: ID del aviso a excluir de la validación (útil en updates)
        """
        sql = """
        SELECT COUNT(*) 
        FROM avisos_recordatorios
        WHERE id_paciente = %s 
        AND COALESCE(id_medico, 0) = COALESCE(%s, 0)
        AND fecha_cita = %s
        AND hora_cita = %s
        AND (%s IS NULL OR id_aviso != %s);
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_paciente, id_medico, fecha_cita, hora_cita, id_aviso_excluir, id_aviso_excluir))
            count = cur.fetchone()[0]
            return count > 0
        except Exception as e:
            app.logger.error(f"Error en AvisoRecordatorioDao.existeDuplicado: {e}")
            return False
        finally:
            cur.close()
            con.close()


    # ==============================
    #   OBTENER UN AVISO POR ID
    # ==============================
    def getAvisoById(self, id_aviso):
        sql = """
        SELECT a.id_aviso,
            p.id_paciente,
            p.nombre || ' ' || p.apellido AS paciente_nombre,
            p.telefono AS telefono_paciente,
            per.id_personal,
            per.nombre || ' ' || per.apellido AS personal_nombre,
            a.id_medico,
            m.nombre || ' ' || m.apellido AS medico_nombre,
            c.codigo,
            c.nombre_consultorio,
            a.fecha_cita,
            a.hora_cita,
            a.forma_envio,
            a.mensaje,
            a.estado_envio,
            a.estado_confirmacion
        FROM avisos_recordatorios a
        JOIN paciente p ON a.id_paciente = p.id_paciente
        JOIN personal per ON a.id_personal = per.id_personal
        LEFT JOIN medico m ON a.id_medico = m.id_medico
        JOIN consultorio c ON a.codigo = c.codigo
        WHERE a.id_aviso = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_aviso,))
            row = cur.fetchone()
            if not row:
                return None

            columnas = [desc[0] for desc in cur.description]
            data = dict(zip(columnas, row))

            if data.get("fecha_cita") and hasattr(data["fecha_cita"], "isoformat"):
                data["fecha_cita"] = data["fecha_cita"].isoformat()
            if data.get("hora_cita") and hasattr(data["hora_cita"], "strftime"):
                data["hora_cita"] = data["hora_cita"].strftime("%H:%M")

            return data
        except Exception as e:
            app.logger.error(f"Error en AvisoRecordatorioDao.getAvisoById: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # ==============================
    #   AGREGAR AVISO
    # ==============================
    def addAviso(self, aviso):
        sql = """
        INSERT INTO avisos_recordatorios (
            id_paciente, id_personal, id_medico, codigo,
            fecha_cita, hora_cita,
            forma_envio, mensaje, estado_envio, estado_confirmacion
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id_aviso;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            # Procesar fecha_cita
            fecha_cita = aviso.get("fecha_cita")
            if fecha_cita:
                fecha_cita = datetime.strptime(fecha_cita, "%Y-%m-%d").date()
            
            # Procesar hora_cita
            hora_cita = aviso.get("hora_cita")
            if hora_cita:
                hora_cita = datetime.strptime(hora_cita, "%H:%M").time()

            # ✅ VALIDAR QUE LA FECHA/HORA SEAN FUTURAS
            es_valida, mensaje_error = self.validar_fecha_hora_futura(fecha_cita, hora_cita)
            if not es_valida:
                raise ValueError(mensaje_error)

            # ✅ Sanitizar todos los campos numéricos
            id_paciente = self.sanitize_int(aviso.get("id_paciente"))
            id_personal = self.sanitize_int(aviso.get("id_personal"))
            id_medico = self.sanitize_int(aviso.get("id_medico"))
            codigo = self.sanitize_int(aviso.get("codigo"))

            # ✅ Validar campos obligatorios
            if not id_paciente:
                raise ValueError("id_paciente es requerido y debe ser un número válido")
            if not id_personal:
                raise ValueError("id_personal es requerido y debe ser un número válido")
            if not codigo:
                raise ValueError("codigo (consultorio) es requerido y debe ser un número válido")

            # ✅ Validar duplicado antes de insertar
            if self.existeDuplicado(id_paciente, id_medico, fecha_cita, hora_cita):
                raise ValueError(
                    "Ya existe un aviso para este paciente, médico, fecha y hora. No se puede duplicar."
                )

            # ✅ Procesar mensaje (puede ser vacío o None)
            mensaje = aviso.get("mensaje", "")
            if mensaje is None:
                mensaje = ""

            cur.execute(sql, (
                id_paciente,
                id_personal,
                id_medico,
                codigo,
                fecha_cita,
                hora_cita,
                aviso["forma_envio"],
                mensaje,
                aviso.get("estado_envio", "Pendiente"),
                aviso.get("estado_confirmacion", "Pendiente")
            ))
            id_aviso = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"✅ Aviso {id_aviso} creado exitosamente")
            return id_aviso
        except ValueError as ve:
            con.rollback()
            app.logger.error(f"Error de validación en addAviso: {ve}")
            return None
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error en AvisoRecordatorioDao.addAviso: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            return None
        finally:
            cur.close()
            con.close()

    # ==============================
    #   ACTUALIZAR AVISO
    # ==============================
    def updateAviso(self, id_aviso, aviso):
        # ✅ DEBUG: Ver qué mensaje está llegando
        app.logger.info(f"[DAO] Actualizando aviso {id_aviso}")
        mensaje_recibido = aviso.get('mensaje', '')
        app.logger.info(f"[DAO] Mensaje recibido: '{mensaje_recibido[:100] if mensaje_recibido else 'VACÍO'}'...")
        
        # ✅ Primero obtenemos el aviso actual para preservar campos
        aviso_actual = self.getAvisoById(id_aviso)
        if not aviso_actual:
            app.logger.error(f"[DAO] ❌ No se encontró el aviso {id_aviso}")
            return False
        
        # ✅ Usar valores del aviso actual como fallback
        id_paciente = aviso.get("id_paciente", aviso_actual.get("id_paciente"))
        id_personal = aviso.get("id_personal", aviso_actual.get("id_personal"))
        id_medico = aviso.get("id_medico", aviso_actual.get("id_medico"))
        codigo = aviso.get("codigo", aviso_actual.get("codigo"))
        fecha_cita = aviso.get("fecha_cita", aviso_actual.get("fecha_cita"))
        hora_cita = aviso.get("hora_cita", aviso_actual.get("hora_cita"))
        forma_envio = aviso.get("forma_envio", aviso_actual.get("forma_envio"))
        estado_envio = aviso.get("estado_envio", aviso_actual.get("estado_envio", "Pendiente"))
        estado_confirmacion = aviso.get("estado_confirmacion", aviso_actual.get("estado_confirmacion", "Pendiente"))
        
        # ✅ CRÍTICO: El mensaje puede venir como string vacío '' o None
        if 'mensaje' in aviso:
            mensaje = aviso['mensaje'] if aviso['mensaje'] is not None else ''
        else:
            mensaje = aviso_actual.get('mensaje', '')
        
        app.logger.info(f"[DAO] Mensaje final a guardar: '{mensaje[:100] if mensaje else 'VACÍO'}'...")
        
        sql = """
        UPDATE avisos_recordatorios SET
            id_paciente = %s,
            id_personal = %s,
            id_medico = %s,
            codigo = %s,
            fecha_cita = %s,
            hora_cita = %s,
            forma_envio = %s,
            mensaje = %s,
            estado_envio = %s,
            estado_confirmacion = %s
        WHERE id_aviso = %s;
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            # Procesar fecha_cita
            if fecha_cita:
                if isinstance(fecha_cita, str):
                    fecha_cita = datetime.strptime(fecha_cita, "%Y-%m-%d").date()

            # Procesar hora_cita
            if hora_cita:
                if isinstance(hora_cita, str):
                    hora_cita = datetime.strptime(hora_cita, "%H:%M").time()

        

            # ✅ Sanitizar con la función helper
            id_paciente = self.sanitize_int(id_paciente)
            id_personal = self.sanitize_int(id_personal)
            id_medico = self.sanitize_int(id_medico)
            codigo = self.sanitize_int(codigo)

            # ✅ Validar campos obligatorios en update también
            if not id_paciente:
                raise ValueError("id_paciente es requerido")
            if not id_personal:
                raise ValueError("id_personal es requerido")
            if not codigo:
                raise ValueError("codigo (consultorio) es requerido")

            # ✅ Validar duplicado antes de insertar
            if self.existeDuplicado(id_paciente, id_medico, fecha_cita, hora_cita, id_aviso_excluir=id_aviso):
                raise ValueError(
                    "Ya existe un aviso para este paciente, médico, fecha y hora. No se puede duplicar."
                )

            app.logger.info(f"[DAO] Ejecutando UPDATE...")
            app.logger.info(f"[DAO] Parámetros: id_paciente={id_paciente}, id_personal={id_personal}, mensaje_len={len(mensaje) if mensaje else 0}")

            cur.execute(sql, (
                id_paciente,
                id_personal,
                id_medico,
                codigo,
                fecha_cita,
                hora_cita,
                forma_envio,
                mensaje,
                estado_envio,
                estado_confirmacion,
                id_aviso
            ))
            
            filas_afectadas = cur.rowcount
            con.commit()
            
            app.logger.info(f"[DAO] ✅ UPDATE ejecutado correctamente. Filas afectadas: {filas_afectadas}")
            
            # ✅ VERIFICACIÓN ADICIONAL: Leer de nuevo el registro para confirmar
            cur.execute("SELECT mensaje FROM avisos_recordatorios WHERE id_aviso = %s", (id_aviso,))
            verificacion = cur.fetchone()
            if verificacion:
                app.logger.info(f"[DAO] 🔍 Verificación - Mensaje en BD: '{verificacion[0][:100] if verificacion[0] else 'VACÍO'}'...")
            
            return True
        except ValueError as ve:
            con.rollback()
            app.logger.error(f"[DAO] ❌ Error de validación en UPDATE: {ve}")
            return False
        except Exception as e:
            con.rollback()
            app.logger.error(f"[DAO] ❌ Error en UPDATE: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            return False
        finally:
            cur.close()
            con.close()

    # ==============================
    #   ELIMINAR AVISO
    # ==============================
    def deleteAviso(self, id_aviso):
        sql = "DELETE FROM avisos_recordatorios WHERE id_aviso = %s;"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_aviso,))
            con.commit()
            app.logger.info(f"✅ Aviso {id_aviso} eliminado exitosamente")
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error en AvisoRecordatorioDao.deleteAviso {id_aviso}: {e}")
            return False
        finally:
            cur.close()
            con.close()