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
            
    def _validar_consulta_duplicada(self, data, id_consulta_cab=None):
        """Valida que no exista una consulta duplicada en la misma fecha, hora y consultorio"""
        try:
            cursor = self.conn.cursor()
            
            if id_consulta_cab:
                # Para UPDATE: excluir el registro actual
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM consultas_cabecera 
                    WHERE id_consultorio = %s 
                    AND fecha_cita = %s 
                    AND hora_cita = %s
                    AND id_consulta_cab != %s
                """, (
                    data.get("id_consultorio"),
                    data.get("fecha_cita"),
                    data.get("hora_cita"),
                    id_consulta_cab
                ))
            else:
                # Para INSERT
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM consultas_cabecera 
                    WHERE id_consultorio = %s 
                    AND fecha_cita = %s 
                    AND hora_cita = %s
                """, (
                    data.get("id_consultorio"),
                    data.get("fecha_cita"),
                    data.get("hora_cita")
                ))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            if count > 0:
                raise ValueError(
                    f"Ya existe una consulta programada en el consultorio "
                    f"'{data.get('id_consultorio')}' para la fecha {data.get('fecha_cita')} "
                    f"a las {data.get('hora_cita')}"
                )
        except ValueError:
            raise
        except Exception as e:
            app.logger.error(f"Error al validar consulta duplicada: {str(e)}")
            raise ValueError("Error al validar disponibilidad de la consulta")

    def getFichaMedicaPaciente(self, id_paciente):
        try:
            sql = """
                SELECT *
                FROM ficha_medica
                WHERE id_paciente = %s
            """
            cursor = self.conn.cursor()
            cursor.execute(sql, (id_paciente,))
        except Exception as e:
            print(f"Error al obtener ficha médica del paciente: {e}")
            return None
    
    
    

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
            self._validar_consulta_duplicada(data)
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
            self._validar_consulta_duplicada(data, id_consulta_cab)
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
                    cd.id_tipo_diagnostico, cd.id_tipo_procedimiento,
                    td.tipo_diagnostico AS tipo_diagnostico,
                    tp.procedimiento AS tipo_procedimiento,
                    s.descripcion_sintoma
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                LEFT JOIN tipo_diagnostico td ON cd.id_tipo_diagnostico = td.id_tipo_diagnostico
                LEFT JOIN tipo_procedimiento_medico tp ON cd.id_tipo_procedimiento = tp.id_tipo_procedimiento
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
                    cd.id_tipo_diagnostico,
                    cd.id_tipo_procedimiento,
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
                    id_tipo_diagnostico, id_tipo_procedimiento
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
                    cd.id_tipo_diagnostico,
                    cd.id_tipo_procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma,
                    cc.id_medico,
                    cc.id_paciente,
                    TO_CHAR(cc.fecha_cita, 'YYYY-MM-DD') AS fecha_cita,
                    TO_CHAR(cc.hora_cita, 'HH24:MI:SS') AS hora_cita,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    p.nombre || ' ' || p.apellido AS nombre_paciente,
                    con.nombre_consultorio AS nombre_consultorio,
                    COALESCE(td.tipo_diagnostico, 'Sin tipo') AS descripcion_tipo_diagnostico,
                    COALESCE(tp.procedimiento, 'Sin tipo') AS descripcion_tipo_procedimiento
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                INNER JOIN consultas_cabecera cc ON cd.id_consulta_cab = cc.id_consulta_cab
                INNER JOIN medico m ON cc.id_medico = m.id_medico
                INNER JOIN paciente p ON cc.id_paciente = p.id_paciente
                LEFT JOIN consultorio con ON cc.id_consultorio = con.codigo
                LEFT JOIN tipo_diagnostico td ON cd.id_tipo_diagnostico = td.id_tipo_diagnostico
                LEFT JOIN tipo_procedimiento_medico tp ON cd.id_tipo_procedimiento = tp.id_tipo_procedimiento
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
                    cd.id_tipo_procedimiento,
                    s.descripcion_sintoma AS descripcion_sintoma,
                    COALESCE(td.tipo_diagnostico, 'Sin tipo') AS descripcion_tipo_diagnostico,
                    COALESCE(tp.procedimiento, 'Sin tipo') AS descripcion_tipo_procedimiento
                FROM consultas_detalle cd
                INNER JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                LEFT JOIN tipo_diagnostico td ON cd.id_tipo_diagnostico = td.id_tipo_diagnostico
                LEFT JOIN tipo_procedimiento_medico tp ON cd.id_tipo_procedimiento = tp.id_tipo_procedimiento
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


    def _validar_detalle_duplicado(self, data, id_consulta_detalle=None):
        """Valida que no exista un detalle duplicado con el mismo síntoma en la misma consulta"""
        try:
            cursor = self.conn.cursor()
            
            if id_consulta_detalle:
                # Para UPDATE
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM consultas_detalle 
                    WHERE id_consulta_cab = %s 
                    AND id_sintoma = %s
                    AND COALESCE(pieza_dental, '') = COALESCE(%s, '')
                    AND id_consulta_detalle != %s
                """, (
                    data.get("id_consulta_cab"),
                    data.get("id_sintoma"),
                    data.get("pieza_dental"),
                    id_consulta_detalle
                ))
            else:
                # Para INSERT
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM consultas_detalle 
                    WHERE id_consulta_cab = %s 
                    AND id_sintoma = %s
                    AND COALESCE(pieza_dental, '') = COALESCE(%s, '')
                """, (
                    data.get("id_consulta_cab"),
                    data.get("id_sintoma"),
                    data.get("pieza_dental")
                ))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            if count > 0:
                pieza_info = f" en la pieza dental '{data.get('pieza_dental')}'" if data.get("pieza_dental") else ""
                raise ValueError(
                    f"Ya existe un detalle con el mismo síntoma{pieza_info} en esta consulta"
                )
        except ValueError:
            raise
        except Exception as e:
            app.logger.error(f"Error al validar detalle duplicado: {str(e)}")
            raise ValueError("Error al validar duplicidad del detalle")

    def addConsultaDetalle(self, data):
        try:
            self._validar_datos_detalle(data)
            self._validar_detalle_duplicado(data) 
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO consultas_detalle(
                    id_consulta_cab, id_sintoma, pieza_dental,
                    diagnostico, tratamiento, procedimiento, 
                    id_tipo_diagnostico, id_tipo_procedimiento
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_consulta_detalle
            """, (
                data["id_consulta_cab"],
                data["id_sintoma"],
                data.get("pieza_dental"),
                data["diagnostico"],
                data["tratamiento"],
                data.get("procedimiento"),
                data.get("id_tipo_diagnostico"),
                data.get("id_tipo_procedimiento")
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
            self._validar_detalle_duplicado(data, id_consulta_detalle)
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE consultas_detalle SET
                    id_consulta_cab = %s,
                    id_sintoma = %s,
                    pieza_dental = %s,
                    diagnostico = %s,
                    tratamiento = %s,
                    procedimiento = %s,
                    id_tipo_diagnostico = %s,
                    id_tipo_procedimiento = %s
                WHERE id_consulta_detalle = %s
            """, (
                data.get("id_consulta_cab"),
                data.get("id_sintoma"),
                data.get("pieza_dental"),
                data.get("diagnostico"),
                data.get("tratamiento"),
                data.get("procedimiento"),
                data.get("id_tipo_diagnostico"),
                data.get("id_tipo_procedimiento"),
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
    # Validación de datos DIAGNÓSTICO
    # ============================
    def _validar_datos_diagnostico(self, data):
        """Validar solo campos realmente obligatorios"""
        campos_obligatorios = ["id_consulta_detalle", "descripcion_diagnostico"]
        
        for campo in campos_obligatorios:
            valor = data.get(campo)
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío")
        
        # ✅ VALIDAR id_tipo_diagnostico solo si viene en data
        if "id_tipo_diagnostico" in data:
            tipo_diag = data.get("id_tipo_diagnostico")
            if tipo_diag is not None and tipo_diag != "":
                try:
                    data["id_tipo_diagnostico"] = int(tipo_diag)
                except (ValueError, TypeError):
                    raise ValueError("El id_tipo_diagnostico debe ser un número entero válido")


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
                    d.descripcion_diagnostico,
                    TO_CHAR(d.fecha_diagnostico, 'YYYY-MM-DD') AS fecha_diagnostico,
                    d.pieza_dental,
                    COALESCE(td.tipo_diagnostico, 'Sin tipo') AS tipo_diagnostico_descripcion
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


    def _validar_diagnostico_duplicado(self, data, id_diagnostico=None):
        """Valida que no exista un diagnóstico duplicado exactamente igual"""
        try:
            cursor = self.conn.cursor()
            
            descripcion_nueva = data.get("descripcion_diagnostico", "").strip().lower()
            
            app.logger.info(f"🔍 Validando duplicado: descripcion='{descripcion_nueva}', id_consulta_detalle={data.get('id_consulta_detalle')}")
            
            if id_diagnostico:
                # Para UPDATE
                cursor.execute("""
                    SELECT LOWER(TRIM(descripcion_diagnostico))
                    FROM diagnosticos 
                    WHERE id_diagnostico = %s
                """, (id_diagnostico,))
                
                result = cursor.fetchone()
                descripcion_actual = result[0] if result else None
                
                if descripcion_actual and descripcion_actual == descripcion_nueva:
                    app.logger.info("✅ Descripción no cambió, permitir actualización")
                    cursor.close()
                    return
                
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM diagnosticos 
                    WHERE id_consulta_detalle = %s 
                    AND LOWER(TRIM(descripcion_diagnostico)) = %s
                    AND id_diagnostico != %s
                """, (
                    data.get("id_consulta_detalle"),
                    descripcion_nueva,
                    id_diagnostico
                ))
            else:
                # Para INSERT
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM diagnosticos 
                    WHERE id_consulta_detalle = %s 
                    AND LOWER(TRIM(descripcion_diagnostico)) = %s
                """, (
                    data.get("id_consulta_detalle"),
                    descripcion_nueva
                ))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            app.logger.info(f"🔍 Duplicados encontrados: {count}")
            
            if count > 0:
                app.logger.warning("⚠️ DUPLICADO DETECTADO - Rechazando operación")
                raise ValueError("Ya existe un diagnóstico con la misma descripción en este detalle de consulta")
                
        except ValueError:
            raise
        except Exception as e:
            app.logger.error(f"Error al validar diagnóstico duplicado: {str(e)}")
            raise ValueError("Error al validar duplicidad del diagnóstico")


    def addDiagnostico(self, data):
        """Agrega un nuevo diagnóstico detallado con pieza_dental de consulta_detalle si no se proporciona"""
        try:
            # ✅ VALIDAR DATOS
            self._validar_datos_diagnostico(data)
            self._validar_diagnostico_duplicado(data)
            
            cursor = self.conn.cursor()
            
            # Si no se proporciona pieza_dental, obtenerla de consultas_detalle
            pieza_dental = data.get("pieza_dental")
            if not pieza_dental:
                cursor.execute("""
                    SELECT pieza_dental 
                    FROM consultas_detalle 
                    WHERE id_consulta_detalle = %s
                """, (data.get("id_consulta_detalle"),))
                result = cursor.fetchone()
                pieza_dental = result[0] if result else None
            
            # ✅ LOG PARA DEBUG
            app.logger.info(f"🔍 Insertando diagnóstico con id_tipo_diagnostico: {data.get('id_tipo_diagnostico')}")
            
            cursor.execute("""
                INSERT INTO diagnosticos(
                    id_consulta_detalle,
                    id_medico,
                    id_paciente,
                    id_tipo_diagnostico,
                    descripcion_diagnostico,
                    fecha_diagnostico,
                    pieza_dental
                )
                VALUES (%s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE), %s)
                RETURNING id_diagnostico
            """, (
                data.get("id_consulta_detalle"),
                data.get("id_medico"),
                data.get("id_paciente"),
                data.get("id_tipo_diagnostico"),  # ✅ Asegurar que se envíe
                data.get("descripcion_diagnostico"),
                data.get("fecha_diagnostico"),
                pieza_dental
            ))
            id_diagnostico = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return id_diagnostico
        except ValueError as ve:
            self.conn.rollback()
            app.logger.warning(f"⚠️ Validación fallida: {str(ve)}")
            raise
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al insertar diagnóstico: {str(e)}")
            return None


    def updateDiagnostico(self, id_diagnostico, data):
        """Actualiza un diagnóstico específico con validación de duplicados"""
        try:
            cursor = self.conn.cursor()
            
            # ✅ Obtener id_consulta_detalle actual
            cursor.execute("""
                SELECT id_consulta_detalle 
                FROM diagnosticos 
                WHERE id_diagnostico = %s
            """, (id_diagnostico,))
            
            result = cursor.fetchone()
            if not result:
                cursor.close()
                return False
            
            id_consulta_detalle_actual = result[0]
            
            # ✅ Si se intenta actualizar la descripción, validar duplicados
            if "descripcion_diagnostico" in data:
                if "id_consulta_detalle" not in data:
                    data["id_consulta_detalle"] = id_consulta_detalle_actual
                
                # Validar duplicado (solo si la descripción cambió)
                self._validar_diagnostico_duplicado(data, id_diagnostico)
            
            # ✅ Construir query de actualización
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
            
            if "fecha_diagnostico" in data:
                campos_actualizar.append("fecha_diagnostico = %s")
                valores.append(data.get("fecha_diagnostico"))
            
            if not campos_actualizar:
                cursor.close()
                return False
            
            valores.append(id_diagnostico)
            query = f"UPDATE diagnosticos SET {', '.join(campos_actualizar)} WHERE id_diagnostico = %s"
            
            cursor.execute(query, valores)
            self.conn.commit()
            cursor.close()
            return True
            
        except ValueError:
            raise
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
        
    # ============================
    # TRATAMIENTOS
    # ============================
    def _validar_datos_tratamiento(self, data):
        campos_obligatorios = ["id_consulta_detalle", "id_medico", "id_paciente", "descripcion_tratamiento"]
        
        for campo in campos_obligatorios:
            valor = data.get(campo)
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío")

    def getTratamientosByConsultaDetalle(self, id_consulta_detalle):
        """Obtiene todos los tratamientos de una consulta detalle específica"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    t.id_tratamiento,
                    t.id_consulta_detalle,
                    t.id_medico,
                    t.id_paciente,
                    t.descripcion_tratamiento,
                    TO_CHAR(t.fecha_tratamiento, 'YYYY-MM-DD') AS fecha_tratamiento,
                    t.duracion_estimada,
                    t.costo_estimado,
                    t.estado,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    p.nombre || ' ' || p.apellido AS nombre_paciente
                FROM tratamientos t
                INNER JOIN medico m ON t.id_medico = m.id_medico
                INNER JOIN paciente p ON t.id_paciente = p.id_paciente
                WHERE t.id_consulta_detalle = %s
                ORDER BY t.fecha_tratamiento DESC, t.id_tratamiento DESC
            """, (id_consulta_detalle,))
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            tratamientos = [dict(zip(columnas, row)) for row in rows]
            cursor.close()
            return tratamientos
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos: {str(e)}")
            return []


    def _validar_tratamiento_duplicado(self, data, id_tratamiento=None):
        """Valida que no exista un tratamiento duplicado exactamente igual"""
        try:
            cursor = self.conn.cursor()
            
            # ✅ Obtener la descripción actual si estamos actualizando
            descripcion_nueva = data.get("descripcion_tratamiento", "").strip().lower()
            
            if id_tratamiento:
                # Para UPDATE: Obtener la descripción actual del registro
                cursor.execute("""
                    SELECT LOWER(TRIM(descripcion_tratamiento))
                    FROM tratamientos 
                    WHERE id_tratamiento = %s
                """, (id_tratamiento,))
                
                result = cursor.fetchone()
                descripcion_actual = result[0] if result else None
                
                # Si la descripción NO cambió, no validar duplicado
                if descripcion_actual and descripcion_actual == descripcion_nueva:
                    cursor.close()
                    return  # ✅ No es duplicado, es el mismo registro
                
                # Validar contra otros registros
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tratamientos 
                    WHERE id_consulta_detalle = %s 
                    AND LOWER(TRIM(descripcion_tratamiento)) = %s
                    AND id_tratamiento != %s
                """, (
                    data.get("id_consulta_detalle"),
                    descripcion_nueva,
                    id_tratamiento
                ))
            else:
                # Para INSERT
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM tratamientos 
                    WHERE id_consulta_detalle = %s 
                    AND LOWER(TRIM(descripcion_tratamiento)) = %s
                """, (
                    data.get("id_consulta_detalle"),
                    descripcion_nueva
                ))
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            if count > 0:
                raise ValueError("Ya existe un tratamiento con la misma descripción en este detalle de consulta")
        except ValueError:
            raise
        except Exception as e:
            app.logger.error(f"Error al validar tratamiento duplicado: {str(e)}")
            raise ValueError("Error al validar duplicidad del tratamiento")



    def addTratamiento(self, data):
        """Agrega un nuevo tratamiento con la fecha de la consulta"""
        try:
            self._validar_datos_tratamiento(data)
            self._validar_tratamiento_duplicado(data)
            cursor = self.conn.cursor()
            
            # Obtener la fecha_cita de la consulta
            cursor.execute("""
                SELECT cc.fecha_cita
                FROM consultas_detalle cd
                INNER JOIN consultas_cabecera cc ON cd.id_consulta_cab = cc.id_consulta_cab
                WHERE cd.id_consulta_detalle = %s
            """, (data.get("id_consulta_detalle"),))
            
            result = cursor.fetchone()
            fecha_consulta = result[0] if result else None
            
            cursor.execute("""
                INSERT INTO tratamientos(
                    id_consulta_detalle,
                    id_medico,
                    id_paciente,
                    descripcion_tratamiento,
                    fecha_tratamiento,
                    duracion_estimada,
                    costo_estimado,
                    estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_tratamiento
            """, (
                data.get("id_consulta_detalle"),
                data.get("id_medico"),
                data.get("id_paciente"),
                data.get("descripcion_tratamiento"),
                fecha_consulta,
                data.get("duracion_estimada"),
                data.get("costo_estimado"),
                data.get("estado", "pendiente")
            ))
            id_tratamiento = cursor.fetchone()[0]
            self.conn.commit()
            cursor.close()
            return id_tratamiento
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al insertar tratamiento: {str(e)}")
            return None

    def updateTratamiento(self, id_tratamiento, data):
        """Actualiza un tratamiento específico con validación de duplicados"""
        try:
            cursor = self.conn.cursor()
            
            # ✅ Obtener id_consulta_detalle actual
            cursor.execute("""
                SELECT id_consulta_detalle 
                FROM tratamientos 
                WHERE id_tratamiento = %s
            """, (id_tratamiento,))
            
            result = cursor.fetchone()
            if not result:
                cursor.close()
                return False
            
            id_consulta_detalle_actual = result[0]
            
            # ✅ Si se intenta actualizar la descripción, validar duplicados
            if "descripcion_tratamiento" in data:
                if "id_consulta_detalle" not in data:
                    data["id_consulta_detalle"] = id_consulta_detalle_actual
                
                # Validar duplicado (solo si la descripción cambió)
                self._validar_tratamiento_duplicado(data, id_tratamiento)
            
            # ✅ Construir query de actualización
            campos_actualizar = []
            valores = []
            
            if "descripcion_tratamiento" in data:
                campos_actualizar.append("descripcion_tratamiento = %s")
                valores.append(data.get("descripcion_tratamiento"))
            
            if "duracion_estimada" in data:
                campos_actualizar.append("duracion_estimada = %s")
                valores.append(data.get("duracion_estimada"))
            
            if "costo_estimado" in data:
                campos_actualizar.append("costo_estimado = %s")
                valores.append(data.get("costo_estimado"))
            
            if "estado" in data:
                campos_actualizar.append("estado = %s")
                valores.append(data.get("estado"))
            
            if not campos_actualizar:
                cursor.close()
                return False
            
            valores.append(id_tratamiento)
            query = f"UPDATE tratamientos SET {', '.join(campos_actualizar)} WHERE id_tratamiento = %s"
            
            cursor.execute(query, valores)
            self.conn.commit()
            cursor.close()
            return True
            
        except ValueError:
            raise
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar tratamiento: {str(e)}")
            return False
    
    def deleteTratamiento(self, id_tratamiento):
        """Elimina un tratamiento específico"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tratamientos WHERE id_tratamiento = %s", (id_tratamiento,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al eliminar tratamiento: {str(e)}")
            return False

    def getFichaMedicaPaciente(self, id_paciente):
        """Obtiene toda la información para generar la ficha médica del paciente"""
        try:
            cursor = self.conn.cursor()
            
            # Log inicial
            app.logger.info(f"Consultando ficha médica para paciente ID: {id_paciente}")
            
            # Obtener datos del paciente con sus consultas, diagnósticos y tratamientos
            cursor.execute("""
                SELECT 
                    -- Datos del paciente
                    p.id_paciente,
                    p.nombre || ' ' || p.apellido AS nombre_completo,
                    p.cedula_entidad,
                    TO_CHAR(p.fecha_nacimiento, 'DD/MM/YYYY') AS fecha_nacimiento,
                    EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento)) AS edad,
                    p.telefono,
                    p.direccion,
                    p.correo,
                    c.descripcion AS ciudad,
                    
                    -- Datos de la consulta
                    cc.id_consulta_cab,
                    TO_CHAR(cc.fecha_cita, 'DD/MM/YYYY') AS fecha_consulta,
                    cc.hora_cita,
                    cc.estado AS estado_consulta,
                    m.nombre || ' ' || m.apellido AS nombre_medico,
                    con.nombre_consultorio,
                    
                    -- Datos del detalle
                    cd.id_consulta_detalle,
                    s.descripcion_sintoma,
                    cd.pieza_dental,
                    cd.diagnostico,
                    cd.tratamiento,
                    cd.procedimiento,
                    td.tipo_diagnostico,
                    tp.procedimiento AS tipo_procedimiento,
                    
                    -- Diagnósticos adicionales
                    d.id_diagnostico,
                    d.descripcion_diagnostico,
                    TO_CHAR(d.fecha_diagnostico, 'DD/MM/YYYY') AS fecha_diagnostico,
                    
                    -- Tratamientos adicionales
                    t.id_tratamiento,
                    t.descripcion_tratamiento,
                    TO_CHAR(t.fecha_tratamiento, 'DD/MM/YYYY') AS fecha_tratamiento,
                    t.estado AS estado_tratamiento
                    
                FROM paciente p
                LEFT JOIN ciudad c ON p.id_ciudad = c.id_ciudad
                LEFT JOIN consultas_cabecera cc ON p.id_paciente = cc.id_paciente
                LEFT JOIN medico m ON cc.id_medico = m.id_medico
                LEFT JOIN consultorio con ON cc.id_consultorio = con.codigo
                LEFT JOIN consultas_detalle cd ON cc.id_consulta_cab = cd.id_consulta_cab
                LEFT JOIN sintoma s ON cd.id_sintoma = s.id_sintoma
                LEFT JOIN tipo_diagnostico td ON cd.id_tipo_diagnostico = td.id_tipo_diagnostico
                LEFT JOIN tipo_procedimiento_medico tp ON cd.id_tipo_procedimiento = tp.id_tipo_procedimiento
                LEFT JOIN diagnosticos d ON cd.id_consulta_detalle = d.id_consulta_detalle
                LEFT JOIN tratamientos t ON cd.id_consulta_detalle = t.id_consulta_detalle
                
                WHERE p.id_paciente = %s
                ORDER BY cc.fecha_cita DESC, cc.hora_cita DESC
            """, (id_paciente,))
            
            rows = cursor.fetchall()
            
            app.logger.info(f"Filas recuperadas: {len(rows)}")
            
            if not rows or rows[0][0] is None:
                cursor.close()
                app.logger.warning(f"No se encontró paciente con ID {id_paciente}")
                return None
            
            # Estructurar los datos
            datos_paciente = {
                'id_paciente': rows[0][0],
                'nombre_completo': rows[0][1],
                'cedula': rows[0][2],
                'fecha_nacimiento': rows[0][3],
                'edad': rows[0][4],
                'telefono': rows[0][5],
                'direccion': rows[0][6],
                'correo': rows[0][7],
                'ciudad': rows[0][8],
                'consultas': []
            }
            
            app.logger.info(f"Paciente encontrado: {datos_paciente['nombre_completo']}")
            
            # Agrupar consultas
            consultas_dict = {}
            for row in rows:
                id_consulta = row[9]
                if id_consulta and id_consulta not in consultas_dict:
                    consultas_dict[id_consulta] = {
                        'id_consulta_cab': id_consulta,
                        'fecha_consulta': row[10],
                        'hora_cita': row[11],
                        'estado': row[12],
                        'medico': row[13],
                        'consultorio': row[14],
                        'detalles': []
                    }
                
                # Agregar detalles
                id_detalle = row[15]
                if id_detalle and id_consulta:
                    detalle_existente = next(
                        (d for d in consultas_dict[id_consulta]['detalles'] 
                        if d.get('id_consulta_detalle') == id_detalle),
                        None
                    )
                    
                    if not detalle_existente:
                        detalle = {
                            'id_consulta_detalle': id_detalle,
                            'sintoma': row[16],
                            'pieza_dental': row[17],
                            'diagnostico': row[18],
                            'tratamiento': row[19],
                            'procedimiento': row[20],
                            'tipo_diagnostico': row[21],
                            'tipo_procedimiento': row[22],
                            'diagnosticos_adicionales': [],
                            'tratamientos_adicionales': []
                        }
                        consultas_dict[id_consulta]['detalles'].append(detalle)
                    else:
                        detalle = detalle_existente
                    
                    # Agregar diagnósticos adicionales
                    id_diagnostico = row[23]
                    if id_diagnostico:
                        diag_adicional = {
                            'id_diagnostico': id_diagnostico,
                            'descripcion': row[24],
                            'fecha': row[25]
                        }
                        if diag_adicional not in detalle['diagnosticos_adicionales']:
                            detalle['diagnosticos_adicionales'].append(diag_adicional)
                    
                    # Agregar tratamientos adicionales
                    id_tratamiento = row[26]
                    if id_tratamiento:
                        trat_adicional = {
                            'id_tratamiento': id_tratamiento,
                            'descripcion': row[27],
                            'fecha': row[28],
                            'estado': row[29]
                        }
                        if trat_adicional not in detalle['tratamientos_adicionales']:
                            detalle['tratamientos_adicionales'].append(trat_adicional)
            
            datos_paciente['consultas'] = list(consultas_dict.values())
            
            app.logger.info(f"Total de consultas encontradas: {len(datos_paciente['consultas'])}")
            
            cursor.close()
            return datos_paciente
            
        except Exception as e:
            app.logger.error(f"Error al obtener ficha médica del paciente: {str(e)}")
            import traceback
            app.logger.error(f"Traceback completo: {traceback.format_exc()}")
            return None
        
    
    
    