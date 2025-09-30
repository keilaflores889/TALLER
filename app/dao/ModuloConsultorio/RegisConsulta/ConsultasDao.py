from flask import current_app as app
from app.conexion.Conexion import Conexion

class ConsultasDao:

    def __init__(self):
        self.conn = Conexion().getConexion()

    # ============================
    # Validación de datos CABECERA
    # ============================
    def _validar_datos_cabecera(self, data):
        campos_obligatorios = [
            "id_personal", "id_consultorio", "id_medico", "id_paciente",
            "fecha_cita", "hora_cita"
        ]

        for campo in campos_obligatorios:
            valor = data.get(campo)
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío")

        if data.get("duracion_minutos"):
            try:
                duracion = int(data.get("duracion_minutos"))
                if duracion <= 0:
                    raise ValueError("La duración debe ser un número positivo")
                data["duracion_minutos"] = duracion
            except ValueError:
                raise ValueError("La duración debe ser un número entero válido")

    # ============================
    # Validación de datos DETALLE
    # ============================
    def _validar_datos_detalle(self, data):
        campos_obligatorios = [
            "id_consulta_cab", "id_sintoma", "diagnostico", "tratamiento"
        ]

        for campo in campos_obligatorios:
            valor = data.get(campo)
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío")

    # ============================
    # CONSULTAS CABECERA
    # ============================
    def getConsultasCabecera(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cc.id_consulta_cab, cc.id_personal, cc.id_consultorio, 
                    cc.id_medico, cc.id_paciente,
                    TO_CHAR(cc.fecha_cita, 'YYYY-MM-DD') AS fecha_cita,
                    TO_CHAR(cc.hora_cita, 'HH24:MI:SS') AS hora_cita,
                    cc.duracion_minutos, cc.estado,
                    p.nombre || ' ' || p.apellido AS nombre_personal,
                    c.nombre_consultorio AS nombre_consultorio,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    pac.nombre || ' ' || pac.apellido AS nombre_paciente
                FROM consultas_cabecera cc
                INNER JOIN personal p ON cc.id_personal = p.id_personal
                INNER JOIN consultorio c ON cc.id_consultorio = c.codigo
                INNER JOIN medico m ON cc.id_medico = m.id_medico
                INNER JOIN paciente pac ON cc.id_paciente = pac.id_paciente
                ORDER BY cc.fecha_cita DESC, cc.hora_cita DESC
            """)
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            consultas = [dict(zip(columnas, row)) for row in rows]
            cursor.close()
            return consultas
        except Exception as e:
            app.logger.error(f"Error al obtener consultas cabecera: {str(e)}")
            return []

    def getConsultaCabeceraById(self, id_consulta_cab):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cc.id_consulta_cab, cc.id_personal, cc.id_consultorio, 
                    cc.id_medico, cc.id_paciente,
                    TO_CHAR(cc.fecha_cita, 'YYYY-MM-DD') AS fecha_cita,
                    TO_CHAR(cc.hora_cita, 'HH24:MI:SS') AS hora_cita,
                    cc.duracion_minutos, cc.estado,
                    p.nombre || ' ' || p.apellido AS nombre_personal,
                    c.nombre_consultorio AS nombre_consultorio,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    pac.nombre || ' ' || pac.apellido AS nombre_paciente
                FROM consultas_cabecera cc
                INNER JOIN personal p ON cc.id_personal = p.id_personal
                INNER JOIN consultorio c ON cc.id_consultorio = c.codigo
                INNER JOIN medico m ON cc.id_medico = m.id_medico
                INNER JOIN paciente pac ON cc.id_paciente = pac.id_paciente
                WHERE cc.id_consulta_cab = %s
            """, (id_consulta_cab,))
            row = cursor.fetchone()
            if not row:
                return None
            columnas = [desc[0] for desc in cursor.description]
            consulta = dict(zip(columnas, row))
            cursor.close()
            return consulta
        except Exception as e:
            app.logger.error(f"Error al obtener consulta cabecera: {str(e)}")
            return None

    # ============================
    # INSERT / UPDATE / DELETE CABECERA
    # ============================
    def addConsultaCabecera(self, data):
        try:
            self._validar_datos_cabecera(data)
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO consultas_cabecera(
                    id_personal, id_consultorio, id_medico, id_paciente,
                    fecha_cita, hora_cita, duracion_minutos, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_consulta_cab
            """, (
                data.get("id_personal"),
                data.get("id_consultorio"),
                data.get("id_medico"),
                data.get("id_paciente"),
                data.get("fecha_cita"),
                data.get("hora_cita"),
                data.get("duracion_minutos") if data.get("duracion_minutos") else None,
                data.get("estado", "programada")
            ))
            id_consulta_cab = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return id_consulta_cab
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al insertar consulta cabecera: {str(e)}")
            return None

    def updateConsultaCabecera(self, id_consulta_cab, data):
        try:
            self._validar_datos_cabecera(data)
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE consultas_cabecera SET
                    id_personal = %s,
                    id_consultorio = %s,
                    id_medico = %s,
                    id_paciente = %s,
                    fecha_cita = %s,
                    hora_cita = %s,
                    duracion_minutos = %s,
                    estado = %s
                WHERE id_consulta_cab = %s
            """, (
                data.get("id_personal"),
                data.get("id_consultorio"),
                data.get("id_medico"),
                data.get("id_paciente"),
                data.get("fecha_cita"),
                data.get("hora_cita"),
                data.get("duracion_minutos") if data.get("duracion_minutos") else None,
                data.get("estado", "programada"),
                id_consulta_cab
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar consulta cabecera: {str(e)}")
            return False

    def deleteConsultaCabecera(self, id_consulta_cab):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM consultas_cabecera WHERE id_consulta_cab = %s", (id_consulta_cab,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al eliminar consulta cabecera: {str(e)}")
            return False

    # ============================
    # CONSULTAS DETALLE
    # ============================
    def getConsultasDetalle(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cd.id_consulta_detalle, cd.id_consulta_cab, cd.id_sintoma,
                    cd.pieza_dental, cd.diagnostico, cd.tratamiento, cd.procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                ORDER BY cd.id_consulta_detalle DESC
            """)
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            detalles = [dict(zip(columnas, row)) for row in rows]
            cursor.close()
            return detalles
        except Exception as e:
            app.logger.error(f"Error al obtener consultas detalle: {str(e)}")
            return []

    def getConsultaDetalleById(self, id_consulta_detalle):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cd.id_consulta_detalle, cd.id_consulta_cab, cd.id_sintoma,
                    cd.pieza_dental, cd.diagnostico, cd.tratamiento, cd.procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                WHERE cd.id_consulta_detalle = %s
            """, (id_consulta_detalle,))
            row = cursor.fetchone()
            if not row:
                return None
            columnas = [desc[0] for desc in cursor.description]
            detalle = dict(zip(columnas, row))
            cursor.close()
            return detalle
        except Exception as e:
            app.logger.error(f"Error al obtener consulta detalle: {str(e)}")
            return None

    def getDetallesByConsultaCab(self, id_consulta_cab):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cd.id_consulta_detalle, cd.id_consulta_cab, cd.id_sintoma,
                    cd.pieza_dental, cd.diagnostico, cd.tratamiento, cd.procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                WHERE cd.id_consulta_cab = %s
                ORDER BY cd.id_consulta_detalle
            """, (id_consulta_cab,))
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            detalles = [dict(zip(columnas, row)) for row in rows]
            cursor.close()
            return detalles
        except Exception as e:
            app.logger.error(f"Error al obtener detalles por consulta: {str(e)}")
            return []

    def addConsultaDetalle(self, data):
        try:
            self._validar_datos_detalle(data)
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO consultas_detalle(
                    id_consulta_cab, id_sintoma, pieza_dental,
                    diagnostico, tratamiento, procedimiento
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_consulta_detalle
            """, (
                data.get("id_consulta_cab"),
                data.get("id_sintoma"),
                data.get("pieza_dental") if data.get("pieza_dental") else None,
                data.get("diagnostico"),
                data.get("tratamiento"),
                data.get("procedimiento") if data.get("procedimiento") else None
            ))
            id_consulta_detalle = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return id_consulta_detalle
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al insertar consulta detalle: {str(e)}")
            return None

    def updateConsultaDetalle(self, id_consulta_detalle, data):
        try:
            self._validar_datos_detalle(data)
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE consultas_detalle SET
                    id_consulta_cab = %s,
                    id_sintoma = %s,
                    pieza_dental = %s,
                    diagnostico = %s,
                    tratamiento = %s,
                    procedimiento = %s
                WHERE id_consulta_detalle = %s
            """, (
                data.get("id_consulta_cab"),
                data.get("id_sintoma"),
                data.get("pieza_dental") if data.get("pieza_dental") else None,
                data.get("diagnostico"),
                data.get("tratamiento"),
                data.get("procedimiento") if data.get("procedimiento") else None,
                id_consulta_detalle
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar consulta detalle: {str(e)}")
            return False

    def deleteConsultaDetalle(self, id_consulta_detalle):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM consultas_detalle WHERE id_consulta_detalle = %s", (id_consulta_detalle,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al eliminar consulta detalle: {str(e)}")
            return False

    # ============================
    # CONSULTA COMPLETA (cabecera + detalles)
    # ============================
    def getConsultaCompleta(self, id_consulta_cab):
        try:
            cabecera = self.getConsultaCabeceraById(id_consulta_cab)
            if not cabecera:
                return None
            detalles = self.getDetallesByConsultaCab(id_consulta_cab)
            cabecera["detalles"] = detalles
            return cabecera
        except Exception as e:
            app.logger.error(f"Error al obtener consulta completa: {str(e)}")
            return None
