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
               per.nombre || ' ' || per.apellido AS personal,
               c.nombre_consultorio,
               a.fecha_cita,
               a.hora_cita,
               a.hora_recordatorio,
               a.forma_envio,
               a.mensaje,
               a.estado_envio
        FROM avisos_recordatorios a
        JOIN paciente p ON a.id_paciente = p.id_paciente
        JOIN personal per ON a.id_personal = per.id_personal
        JOIN consultorio c ON a.codigo = c.codigo
        ORDER BY a.id_aviso;
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
                if data.get("hora_recordatorio") and hasattr(data["hora_recordatorio"], "strftime"):
                    data["hora_recordatorio"] = data["hora_recordatorio"].strftime("%H:%M")
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
               p.nombre || ' ' || p.apellido AS paciente_nombre,
               per.id_personal,
               per.nombre || ' ' || per.apellido AS personal_nombre,
               c.codigo,
               c.nombre_consultorio,
               a.fecha_cita,
               a.hora_cita,
               a.hora_recordatorio,
               a.forma_envio,
               a.mensaje,
               a.estado_envio
        FROM avisos_recordatorios a
        JOIN paciente p ON a.id_paciente = p.id_paciente
        JOIN personal per ON a.id_personal = per.id_personal
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
            if data.get("hora_recordatorio") and hasattr(data["hora_recordatorio"], "strftime"):
                data["hora_recordatorio"] = data["hora_recordatorio"].strftime("%H:%M")

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
            id_paciente, id_personal, codigo,
            fecha_cita, hora_cita, hora_recordatorio,
            forma_envio, mensaje, estado_envio
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

            hora_recordatorio = aviso.get("hora_recordatorio")
            if hora_recordatorio:
                hora_recordatorio = datetime.strptime(hora_recordatorio, "%H:%M").time()

            # ✅ Sanitizar codigo
            codigo = aviso.get("codigo")
            if codigo in ("", None):
                codigo = None
            else:
                codigo = int(codigo)

            cur.execute(sql, (
                aviso["id_paciente"],
                aviso["id_personal"],
                codigo,
                fecha_cita,
                hora_cita,
                hora_recordatorio,
                aviso["forma_envio"],
                aviso["mensaje"],
                aviso.get("estado_envio", "Pendiente")
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
        sql = """
        UPDATE avisos_recordatorios SET
            id_paciente = %s,
            id_personal = %s,
            codigo = %s,
            fecha_cita = %s,
            hora_cita = %s,
            hora_recordatorio = %s,
            forma_envio = %s,
            mensaje = %s,
            estado_envio = %s
        WHERE id_aviso = %s;
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

            hora_recordatorio = aviso.get("hora_recordatorio")
            if hora_recordatorio:
                hora_recordatorio = datetime.strptime(hora_recordatorio, "%H:%M").time()

            # ✅ Sanitizar codigo
            codigo = aviso.get("codigo")
            if codigo in ("", None):
                codigo = None
            else:
                codigo = int(codigo)

            cur.execute(sql, (
                aviso["id_paciente"],
                aviso["id_personal"],
                codigo,
                fecha_cita,
                hora_cita,
                hora_recordatorio,
                aviso["forma_envio"],
                aviso["mensaje"],
                aviso.get("estado_envio", "Pendiente"),
                id_aviso
            ))
            con.commit()
            return True
        except Exception as e:
            con.rollback()
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
