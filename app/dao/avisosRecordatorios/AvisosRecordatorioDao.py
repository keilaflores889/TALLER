from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime

class AvisoRecordatorioDao:

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
    #   OBTENER UN AVISO POR ID
    # ==============================
    def getAvisoById(self, id_aviso):
        sql = """
        SELECT a.id_aviso,
            p.id_paciente,
            p.nombre || ' ' || p.apellido AS paciente,
            p.telefono AS telefono_paciente,
            per.id_personal,
            per.nombre || ' ' || per.apellido AS personal,
            a.id_medico,
            m.nombre || ' ' || m.apellido AS medico,
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
            fecha_cita = aviso.get("fecha_cita")
            if fecha_cita:
                fecha_cita = datetime.strptime(fecha_cita, "%Y-%m-%d").date()

            hora_cita = aviso.get("hora_cita")
            if hora_cita:
                hora_cita = datetime.strptime(hora_cita, "%H:%M").time()

            # ✅ Sanitizar codigo
            codigo = aviso.get("codigo")
            if codigo in ("", None):
                codigo = None
            else:
                codigo = int(codigo)

            # ✅ Sanitizar id_medico
            id_medico = aviso.get("id_medico")
            if id_medico in ("", None):
                id_medico = None
            else:
                id_medico = int(id_medico)

            cur.execute(sql, (
                aviso["id_paciente"],
                aviso["id_personal"],
                id_medico,
                codigo,
                fecha_cita,
                hora_cita,
                aviso["forma_envio"],
                aviso["mensaje"],
                aviso.get("estado_envio", "Pendiente"),
                aviso.get("estado_confirmacion", "Pendiente")
            ))
            id_aviso = cur.fetchone()[0]
            con.commit()
            return id_aviso
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error en AvisoRecordatorioDao.addAviso: {e}")
            return None
        finally:
            cur.close()
            con.close()

    # ==============================
#   ACTUALIZAR AVISO
# ==============================
    def updateAviso(self, id_aviso, aviso):
        # ✅ DEBUG: Ver qué mensaje está llegando
        print(f"\n[DAO] Actualizando aviso {id_aviso}")
        mensaje_recibido = aviso.get('mensaje', '')
        print(f"[DAO] Mensaje recibido: '{mensaje_recibido[:100] if mensaje_recibido else 'VACÍO'}'...")
        print(f"[DAO] Tipo de mensaje: {type(mensaje_recibido)}")
        print(f"[DAO] Longitud del mensaje: {len(mensaje_recibido) if mensaje_recibido else 0}")
        print(f"[DAO] Estado envío: {aviso.get('estado_envio')}")
        
        # ✅ Primero obtenemos el aviso actual para preservar campos
        aviso_actual = self.getAvisoById(id_aviso)
        if not aviso_actual:
            print(f"[DAO] ❌ No se encontró el aviso {id_aviso}")
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
        # Debemos preservar el que venga, incluso si es vacío
        if 'mensaje' in aviso:
            mensaje = aviso['mensaje'] if aviso['mensaje'] is not None else ''
        else:
            mensaje = aviso_actual.get('mensaje', '')
        
        print(f"[DAO] Mensaje final a guardar: '{mensaje[:100] if mensaje else 'VACÍO'}'...")
        
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

            # Sanitizar codigo
            if codigo in ("", None):
                codigo = None
            else:
                codigo = int(codigo)

            # Sanitizar id_medico
            if id_medico in ("", None):
                id_medico = None
            else:
                id_medico = int(id_medico)

            print(f"[DAO] Ejecutando UPDATE...")
            print(f"[DAO] Parámetros: id_paciente={id_paciente}, id_personal={id_personal}, mensaje_len={len(mensaje) if mensaje else 0}")

            cur.execute(sql, (
                id_paciente,
                id_personal,
                id_medico,
                codigo,
                fecha_cita,
                hora_cita,
                forma_envio,
                mensaje,  # ✅ Aquí va el mensaje (puede ser '' o con contenido)
                estado_envio,
                estado_confirmacion,
                id_aviso
            ))
            
            filas_afectadas = cur.rowcount
            con.commit()
            
            print(f"[DAO] ✅ UPDATE ejecutado correctamente. Filas afectadas: {filas_afectadas}")
            
            # ✅ VERIFICACIÓN ADICIONAL: Leer de nuevo el registro para confirmar
            cur.execute("SELECT mensaje FROM avisos_recordatorios WHERE id_aviso = %s", (id_aviso,))
            verificacion = cur.fetchone()
            if verificacion:
                print(f"[DAO] 🔍 Verificación - Mensaje en BD: '{verificacion[0][:100] if verificacion[0] else 'VACÍO'}'...")
            
            return True
        except Exception as e:
            con.rollback()
            print(f"[DAO] ❌ Error en UPDATE: {e}")
            import traceback
            traceback.print_exc()
            app.logger.error(f"Error en AvisoRecordatorioDao.updateAviso {id_aviso}: {e}")
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
            return True
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error en AvisoRecordatorioDao.deleteAviso {id_aviso}: {e}")
            return False
        finally:
            cur.close()
            con.close()