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
    # Validación de datos DIAGNÓSTICO
    # ============================
    def _validar_datos_diagnostico(self, data):
        campos_obligatorios = ["id_consulta_detalle", "descripcion_diagnostico"]
        
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
                    cd.id_tipo_diagnostico, 
                    td.descripcion AS tipo_diagnostico,
                    s.descripcion_sintoma
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                LEFT JOIN tipo_diagnostico td ON cd.id_tipo_diagnostico = td.id_tipo_diagnostico
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

    def getConsultaDetalleByIdConInfo(self, id_consulta_detalle):
        """Obtiene un detalle específico con información completa de médico y paciente"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cd.id_consulta_detalle, 
                    cd.id_consulta_cab, 
                    cd.id_sintoma,
                    cd.pieza_dental, 
                    cd.diagnostico, 
                    cd.tratamiento, 
                    cd.procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma,
                    cc.id_medico,
                    cc.id_paciente,
                    TO_CHAR(cc.fecha_cita, 'YYYY-MM-DD') AS fecha_cita,
                    TO_CHAR(cc.hora_cita, 'HH24:MI:SS') AS hora_cita,
                    cc.estado AS estado_consulta,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    p.nombre || ' ' || p.apellido AS nombre_paciente,
                    con.nombre_consultorio AS nombre_consultorio
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                INNER JOIN consultas_cabecera cc ON cd.id_consulta_cab = cc.id_consulta_cab
                INNER JOIN medico m ON cc.id_medico = m.id_medico
                INNER JOIN paciente p ON cc.id_paciente = p.id_paciente
                LEFT JOIN consultorio con ON cc.id_consultorio = con.codigo
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
            app.logger.error(f"Error al obtener consulta detalle con info: {str(e)}")
            return None

    def getConsultaDetalleById(self, id_consulta_detalle):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    id_consulta_detalle, id_consulta_cab, id_sintoma,
                    pieza_dental, diagnostico, tratamiento, procedimiento,
                    id_tipo_diagnostico
                FROM consultas_detalle
                WHERE id_consulta_detalle = %s
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

    def getConsultasDetalleConInfo(self):
        """Obtiene todos los detalles de consulta con información de médico y paciente"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cd.id_consulta_detalle, 
                    cd.id_consulta_cab, 
                    cd.id_sintoma,
                    cd.pieza_dental, 
                    cd.diagnostico, 
                    cd.tratamiento, 
                    cd.procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma,
                    cc.id_medico,
                    cc.id_paciente,
                    TO_CHAR(cc.fecha_cita, 'YYYY-MM-DD') AS fecha_cita,
                    TO_CHAR(cc.hora_cita, 'HH24:MI:SS') AS hora_cita,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    p.nombre || ' ' || p.apellido AS nombre_paciente,
                    con.nombre_consultorio AS nombre_consultorio
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                INNER JOIN consultas_cabecera cc ON cd.id_consulta_cab = cc.id_consulta_cab
                INNER JOIN medico m ON cc.id_medico = m.id_medico
                INNER JOIN paciente p ON cc.id_paciente = p.id_paciente
                LEFT JOIN consultorio con ON cc.id_consultorio = con.codigo
                ORDER BY cd.id_consulta_detalle DESC
            """)
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            detalles = [dict(zip(columnas, row)) for row in rows]
            cursor.close()
            return detalles
        except Exception as e:
            app.logger.error(f"Error al obtener consultas detalle con info: {str(e)}")
            return []

    def getDetallesByConsultaCab(self, id_consulta_cab):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    cd.id_consulta_detalle, 
                    cd.id_consulta_cab, 
                    cd.id_sintoma,
                    cd.pieza_dental, 
                    cd.diagnostico, 
                    cd.tratamiento, 
                    cd.procedimiento,
                    cd.id_tipo_diagnostico,
                    s.descripcion_sintoma AS descripcion_sintoma,
                    COALESCE(td.tipo_diagnostico, 'Sin tipo') AS descripcion_tipo_diagnostico
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                LEFT JOIN tipo_diagnostico td ON cd.id_tipo_diagnostico = td.id_tipo_diagnostico
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
                    diagnostico, tratamiento, procedimiento, id_tipo_diagnostico
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_consulta_detalle
            """, (
                data["id_consulta_cab"],
                data["id_sintoma"],
                data.get("pieza_dental"),
                data["diagnostico"],
                data["tratamiento"],
                data.get("procedimiento"),
                data.get("id_tipo_diagnostico")
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
                    procedimiento = %s,
                    id_tipo_diagnostico = %s
                WHERE id_consulta_detalle = %s
            """, (
                data.get("id_consulta_cab"),
                data.get("id_sintoma"),
                data.get("pieza_dental"),
                data.get("diagnostico"),
                data.get("tratamiento"),
                data.get("procedimiento"),
                data.get("id_tipo_diagnostico"),
                id_consulta_detalle
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar consulta detalle: {str(e)}")
            return False

    def updateDiagnosticoPrincipal(self, id_consulta_detalle, data):
        """Actualiza solo el diagnóstico principal en consultas_detalle"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE consultas_detalle SET
                    diagnostico = %s,
                    id_tipo_diagnostico = %s
                WHERE id_consulta_detalle = %s
            """, (
                data.get("diagnostico"),
                data.get("id_tipo_diagnostico"),
                id_consulta_detalle
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar diagnóstico principal: {str(e)}")
            return False

    def updateTratamientoPrincipal(self, id_consulta_detalle, data):
        """Actualiza solo el tratamiento principal en consultas_detalle"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE consultas_detalle SET
                    tratamiento = %s
                WHERE id_consulta_detalle = %s
            """, (
                data.get("tratamiento"),
                id_consulta_detalle
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar tratamiento principal: {str(e)}")
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
    # DIAGNÓSTICOS
    # ============================
    def getDiagnosticosByConsultaDetalle(self, id_consulta_detalle):
        """Obtiene todos los diagnósticos de una consulta detalle específica"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    d.id_diagnostico,
                    d.id_consulta_detalle,
                    d.id_tipo_diagnostico,
                    d.pieza_dental,
                    d.descripcion_diagnostico,
                    d.gravedad,
                    d.estado,
                    TO_CHAR(d.fecha_diagnostico, 'YYYY-MM-DD') AS fecha_diagnostico,
                    d.observaciones,
                    COALESCE(td.descripcion, 'Sin tipo') AS tipo_diagnostico_descripcion
                FROM diagnosticos d
                LEFT JOIN tipo_diagnostico td ON d.id_tipo_diagnostico = td.id_tipo_diagnostico
                WHERE d.id_consulta_detalle = %s
                ORDER BY d.fecha_diagnostico DESC, d.id_diagnostico DESC
            """, (id_consulta_detalle,))
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            diagnosticos = [dict(zip(columnas, row)) for row in rows]
            cursor.close()
            return diagnosticos
        except Exception as e:
            app.logger.error(f"Error al obtener diagnósticos: {str(e)}")
            return []

    def addDiagnostico(self, data):
        """Agrega un nuevo diagnóstico detallado"""
        try:
            self._validar_datos_diagnostico(data)
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO diagnosticos(
                    id_consulta_detalle,
                    id_tipo_diagnostico,
                    pieza_dental,
                    descripcion_diagnostico,
                    gravedad,
                    estado,
                    fecha_diagnostico,
                    observaciones
                )
                VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE), %s)
                RETURNING id_diagnostico
            """, (
                data.get("id_consulta_detalle"),
                data.get("id_tipo_diagnostico"),
                data.get("pieza_dental"),
                data.get("descripcion_diagnostico"),
                data.get("gravedad"),
                data.get("estado", "activo"),
                data.get("fecha_diagnostico"),
                data.get("observaciones")
            ))
            id_diagnostico = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return id_diagnostico
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al insertar diagnóstico: {str(e)}")
            return None

    def updateDiagnostico(self, id_diagnostico, data):
        """Actualiza un diagnóstico específico"""
        try:
            cursor = self.conn.cursor()
            
            campos_actualizar = []
            valores = []
            
            if "id_tipo_diagnostico" in data:
                campos_actualizar.append("id_tipo_diagnostico = %s")
                valores.append(data.get("id_tipo_diagnostico"))
            
            if "pieza_dental" in data:
                campos_actualizar.append("pieza_dental = %s")
                valores.append(data.get("pieza_dental"))
            
            if "descripcion_diagnostico" in data:
                campos_actualizar.append("descripcion_diagnostico = %s")
                valores.append(data.get("descripcion_diagnostico"))
            
            if "gravedad" in data:
                campos_actualizar.append("gravedad = %s")
                valores.append(data.get("gravedad"))
            
            if "estado" in data:
                campos_actualizar.append("estado = %s")
                valores.append(data.get("estado"))
            
            if "observaciones" in data:
                campos_actualizar.append("observaciones = %s")
                valores.append(data.get("observaciones"))
            
            if not campos_actualizar:
                return False
            
            valores.append(id_diagnostico)
            query = f"UPDATE diagnosticos SET {', '.join(campos_actualizar)} WHERE id_diagnostico = %s"
            
            cursor.execute(query, valores)
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar diagnóstico: {str(e)}")
            return False

    def deleteDiagnostico(self, id_diagnostico):
        """Elimina un diagnóstico específico"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM diagnosticos WHERE id_diagnostico = %s", (id_diagnostico,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al eliminar diagnóstico: {str(e)}")
            return False

    # ============================
    # CONSULTA COMPLETA (cabecera + detalles + diagnósticos)
    # ============================
    def getConsultaCompleta(self, id_consulta_cab):
        """Obtiene consulta completa con cabecera, detalles y diagnósticos"""
        try:
            cabecera = self.getConsultaCabeceraById(id_consulta_cab)
            if not cabecera:
                return None
            
            detalles = self.getDetallesByConsultaCab(id_consulta_cab)
            
            for detalle in detalles:
                detalle["diagnosticos"] = self.getDiagnosticosByConsultaDetalle(
                    detalle["id_consulta_detalle"]
                )
            
            cabecera["detalles"] = detalles
            return cabecera
        except Exception as e:
            app.logger.error(f"Error al obtener consulta completa: {str(e)}")
            return None