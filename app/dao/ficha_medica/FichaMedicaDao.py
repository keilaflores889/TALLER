from flask import current_app as app
from app.conexion.Conexion import Conexion

class FichaMedicaDao:

    def __init__(self):
        self.conn = Conexion().getConexion()

    # ============================
    # Validación de datos
    # ============================
    def _validar_datos(self, data):
        campos_obligatorios = [
            "id_paciente", "id_medico", "cedula", "edad", "fecha_registro",
            "alergias", "enfermedades", "diagnosticos", "sintomas",
            "tratamientos", "cirugias_realizadas", "recetas_medicas",
            "motivos_consultas", "observaciones", "estado"
        ]

        for campo in campos_obligatorios:
            valor = data.get(campo)
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                raise ValueError(f"El campo '{campo}' es obligatorio y no puede estar vacío")

        # Validar edad como número entero no negativo
        try:
            edad = int(data.get("edad"))
        except ValueError:
            raise ValueError("Edad debe ser un número entero")
        if edad < 0:
            raise ValueError("Edad inválida")

        data["edad"] = edad  # asegura que siempre sea int

    # ============================
    # Obtener todas las fichas médicas
    # ============================
    def getFichas(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT f.*, 
                       p.nombre AS paciente_nombre, p.apellido AS paciente_apellido,
                       m.nombre AS medico_nombre, m.apellido AS medico_apellido,
                       ARRAY_REMOVE(ARRAY_AGG(fm.id_medicamento), NULL) AS medicamentos_ids,
                       ARRAY_REMOVE(ARRAY_AGG(md.nombre_medicamento), NULL) AS medicamentos_nombres
                FROM ficha_medica f
                INNER JOIN paciente p ON f.id_paciente = p.id_paciente
                INNER JOIN medico m ON f.id_medico = m.id_medico
                LEFT JOIN ficha_medicamento fm ON f.id_ficha_medica = fm.id_ficha_medica
                LEFT JOIN medicamento md ON fm.id_medicamento = md.id_medicamento
                GROUP BY f.id_ficha_medica, p.nombre, p.apellido, m.nombre, m.apellido
                ORDER BY f.id_ficha_medica DESC
            """)
            rows = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            fichas = []
            for row in rows:
                fila = dict(zip(columnas, row))
                meds_ids = fila.pop("medicamentos_ids") or []
                meds_nombres = fila.pop("medicamentos_nombres") or []
                fila["medicamentos"] = [{"id_medicamento": i, "nombre_medicamento": n} 
                                        for i, n in zip(meds_ids, meds_nombres)]
                fichas.append(fila)
            cursor.close()
            return fichas
        except Exception as e:
            app.logger.error(f"Error al obtener fichas médicas: {str(e)}")
            return []

    # ============================
    # Obtener ficha por ID
    # ============================
    def getFichaById(self, id_ficha):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT f.*, 
                       p.nombre AS paciente_nombre, p.apellido AS paciente_apellido,
                       m.nombre AS medico_nombre, m.apellido AS medico_apellido,
                       ARRAY_REMOVE(ARRAY_AGG(fm.id_medicamento), NULL) AS medicamentos_ids,
                       ARRAY_REMOVE(ARRAY_AGG(md.nombre_medicamento), NULL) AS medicamentos_nombres
                FROM ficha_medica f
                INNER JOIN paciente p ON f.id_paciente = p.id_paciente
                INNER JOIN medico m ON f.id_medico = m.id_medico
                LEFT JOIN ficha_medicamento fm ON f.id_ficha_medica = fm.id_ficha_medica
                LEFT JOIN medicamento md ON fm.id_medicamento = md.id_medicamento
                WHERE f.id_ficha_medica=%s
                GROUP BY f.id_ficha_medica, p.nombre, p.apellido, m.nombre, m.apellido
            """, (id_ficha,))
            row = cursor.fetchone()
            if not row:
                return None
            columnas = [desc[0] for desc in cursor.description]
            fila = dict(zip(columnas, row))
            meds_ids = fila.pop("medicamentos_ids") or []
            meds_nombres = fila.pop("medicamentos_nombres") or []
            fila["medicamentos"] = [{"id_medicamento": i, "nombre_medicamento": n} 
                                    for i, n in zip(meds_ids, meds_nombres)]
            cursor.close()
            return fila
        except Exception as e:
            app.logger.error(f"Error al obtener ficha médica: {str(e)}")
            return None

    # ============================
    # Agregar nueva ficha médica
    # ============================
    def addFicha(self, data):
        try:
            self._validar_datos(data)  # <--- validación
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO ficha_medica(
                    id_paciente, id_medico, cedula, edad, fecha_registro,
                    alergias, enfermedades, diagnosticos, sintomas,
                    tratamientos, cirugias_realizadas, recetas_medicas,
                    motivos_consultas, observaciones, estado
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id_ficha_medica
            """, (
                data.get("id_paciente"),
                data.get("id_medico"),
                data.get("cedula"),
                data.get("edad"),
                data.get("fecha_registro"),
                data.get("alergias"),
                data.get("enfermedades"),
                data.get("diagnosticos"),
                data.get("sintomas"),
                data.get("tratamientos"),
                data.get("cirugias_realizadas"),
                data.get("recetas_medicas"),
                data.get("motivos_consultas"),
                data.get("observaciones"),
                data.get("estado")
            ))
            id_ficha = cursor.fetchone()[0]
            self.conn.commit()

            # Insertar medicamentos
            medicamentos = data.get("medicamentos") or []
            for m in medicamentos:
                cursor.execute("""
                    INSERT INTO ficha_medicamento(id_ficha_medica, id_medicamento)
                    VALUES (%s,%s)
                """, (id_ficha, m['id']))
            self.conn.commit()
            cursor.close()
            return id_ficha
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al insertar ficha médica: {str(e)}")
            return None

    # ============================
    # Actualizar ficha médica
    # ============================
    def updateFicha(self, id_ficha, data):
        try:
            self._validar_datos(data)  # <--- validación
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE ficha_medica SET
                    id_paciente=%s,
                    id_medico=%s,
                    cedula=%s,
                    edad=%s,
                    fecha_registro=%s,
                    alergias=%s,
                    enfermedades=%s,
                    diagnosticos=%s,
                    sintomas=%s,
                    tratamientos=%s,
                    cirugias_realizadas=%s,
                    recetas_medicas=%s,
                    motivos_consultas=%s,
                    observaciones=%s,
                    estado=%s
                WHERE id_ficha_medica=%s
            """, (
                data.get("id_paciente"),
                data.get("id_medico"),
                data.get("cedula"),
                data.get("edad"),
                data.get("fecha_registro"),
                data.get("alergias"),
                data.get("enfermedades"),
                data.get("diagnosticos"),
                data.get("sintomas"),
                data.get("tratamientos"),
                data.get("cirugias_realizadas"),
                data.get("recetas_medicas"),
                data.get("motivos_consultas"),
                data.get("observaciones"),
                data.get("estado"),
                id_ficha
            ))

            # Borrar medicamentos existentes
            cursor.execute("DELETE FROM ficha_medicamento WHERE id_ficha_medica=%s", (id_ficha,))
            # Insertar los nuevos
            medicamentos = data.get("medicamentos") or []
            for m in medicamentos:
                cursor.execute("""
                    INSERT INTO ficha_medicamento(id_ficha_medica, id_medicamento)
                    VALUES (%s,%s)
                """, (id_ficha, m['id']))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al actualizar ficha médica: {str(e)}")
            return False

    # ============================
    # Eliminar ficha médica
    # ============================
    def deleteFicha(self, id_ficha):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM ficha_medica WHERE id_ficha_medica=%s", (id_ficha,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.conn.rollback()
            app.logger.error(f"Error al eliminar ficha médica: {str(e)}")
            return False
