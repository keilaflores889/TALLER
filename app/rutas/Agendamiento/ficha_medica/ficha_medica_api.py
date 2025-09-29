from flask import Blueprint, jsonify, request, current_app as app, make_response
from app.dao.ficha_medica.FichaMedicaDao import FichaMedicaDao
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime



fichaapi = Blueprint('fichaapi', __name__)


@fichaapi.route('/fichas/<int:id_ficha>/pdf', methods=['GET'])
def getFichaPDF(id_ficha):
    dao = FichaMedicaDao()
    ficha = dao.getFichaById(id_ficha)
    if not ficha:
        return jsonify(success=False, error=f"No se encontró ficha con ID {id_ficha}."), 404

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    # ==========================
    # Título
    # ==========================
    titulo = Paragraph("<b><font size=16>FICHA MÉDICA</font></b>", styles['Title'])
    elements.append(titulo)
    elements.append(Spacer(1, 20))

    # ==========================
    # Fecha
    # ==========================
    fecha = datetime.date.today().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"<b>Fecha:</b> {fecha}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # ==========================
    # Tabla con estilo formulario
    # ==========================
    fecha_registro = ficha.get("fecha_registro", "")
    if fecha_registro:
     try:
        # Si viene como datetime, convertir a string
        fecha_registro = fecha_registro.strftime("%d/%m/%Y")
     except:
        fecha_registro = str(fecha_registro)
    
    meds = ficha.get("medicamentos", [])
    if meds:
        medicamentos_texto = "<br/>".join([f"• {m.get('nombre_medicamento', '')}" for m in meds])
    else:
         medicamentos_texto = "N/A"
    
    data = [
        ["Paciente", f"{ficha.get('paciente_nombre', '')} {ficha.get('paciente_apellido', '')}"],
        ["Edad", ficha.get("edad", "")],
        ["Medico", f"{ficha.get('medico_nombre', '')} {ficha.get('medico_apellido', '')}"],
        ["Fecha registro", fecha_registro],
        ["Consultorio", ficha.get("consultorio_nombre", "N/A")],
        ["Alergias", ficha.get("alergias", "")],
        ["Enfermedades", ficha.get("enfermedades", "")],
        ["Diagnóstico", ficha.get("diagnosticos", "")],
        ["Tipo Diagnóstico", ficha.get("tipo_diagnostico_descripcion", "N/A")],
        ["Síntomas", ficha.get("sintomas", "")],
        ["Tratamientos", ficha.get("tratamientos", "")],
        ["Procedimiento Médico", ficha.get("procedimiento_medico", "")],
        ["Tipo Procedimiento", ficha.get("tipo_procedimiento_medico_descripcion", "N/A")],
        ["Cirugías realizadas", ficha.get("cirugias_realizadas", "")],
        ["Recetas médicas", ficha.get("recetas_medicas", "")],
        ["Medicamentos en consumo", Paragraph(medicamentos_texto, styles['Normal'])], 
        ["Motivo de consulta", ficha.get("motivos_consultas", "")],
        ["Observaciones", ficha.get("observaciones", "")],
        ["Estado de la ficha", ficha.get("estado", "")]
    ]

    table = Table(data, colWidths=[150, 380])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),  # títulos en gris claro
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # ==========================
    # Pie de página
    # ==========================
    pie = Paragraph(
        "<font size=9><i>Este documento es confidencial y forma parte de la "
        "historia clínica del paciente.</i></font>",
        styles["Normal"]
    )
    elements.append(pie)

    # Construcción final
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Ficha_Medica_{ficha.get("paciente_nombre","")}_{ficha.get("paciente_apellido","")}.pdf'

    return response


# ============================
# Obtener todas las fichas
# ============================
@fichaapi.route('/fichas', methods=['GET'])
def getFichas():
    dao = FichaMedicaDao()
    try:
        fichas = dao.getFichas()
        return jsonify(success=True, data=fichas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener fichas médicas: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar fichas médicas."), 500

# ============================
# Obtener ficha por ID
# ============================
@fichaapi.route('/fichas/<int:id_ficha>', methods=['GET'])
def getFicha(id_ficha):
    dao = FichaMedicaDao()
    try:
        ficha = dao.getFichaById(id_ficha)
        if ficha:
            return jsonify(success=True, data=ficha, error=None), 200
        return jsonify(success=False, error=f"No se encontró ficha con ID {id_ficha}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener ficha {id_ficha}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar ficha médica."), 500

# ============================
# Agregar ficha
# ============================
@fichaapi.route('/fichas', methods=['POST'])
def addFicha():
    data = request.get_json() or {}
    dao = FichaMedicaDao()

    campos_requeridos = ['id_paciente', 'id_medico', 'fecha_registro']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        # Medicamentos opcionales
        medicamentos = data.get("medicamentos") or []
        if medicamentos:
            data["id_medicamento"] = ",".join([str(m["id"]) for m in medicamentos])
            data["medicamentos_en_consumo"] = ", ".join([m["nombre"] for m in medicamentos])
        else:
            data["id_medicamento"] = None
            data["medicamentos_en_consumo"] = ""

        # Asegurar que los campos opcionales estén presentes con valores por defecto
        campos_opcionales = {
            "alergias": "",
            "enfermedades": "",
            "diagnosticos": "",
            "sintomas": "",
            "tratamientos": "",
            "cirugias_realizadas": "",
            "recetas_medicas": "",
            "motivos_consultas": "",
            "observaciones": "",
            "estado": "Activo",
            "procedimiento_medico": "",
            "cedula": "",
            "edad": 0
        }
        
        for campo, valor_defecto in campos_opcionales.items():
            if campo not in data or data[campo] is None:
                data[campo] = valor_defecto

        ficha_id = dao.addFicha(data)
        if ficha_id:
            return jsonify(success=True, data={**data, "id_ficha_medica": ficha_id}, error=None), 201
        return jsonify(success=False, error="No se pudo guardar ficha médica."), 500
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al agregar ficha: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar ficha médica."), 500

# ============================
# Actualizar ficha
# ============================
@fichaapi.route('/fichas/<int:id_ficha>', methods=['PUT'])
def updateFicha(id_ficha):
    data = request.get_json() or {}
    dao = FichaMedicaDao()

    campos_requeridos = ['id_paciente', 'id_medico', 'fecha_registro']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        medicamentos = data.get("medicamentos") or []
        if medicamentos:
            data["id_medicamento"] = ",".join([str(m["id"]) for m in medicamentos])
            data["medicamentos_en_consumo"] = ", ".join([m["nombre"] for m in medicamentos])
        else:
            data["id_medicamento"] = None
            data["medicamentos_en_consumo"] = ""

        # Asegurar que los campos obligatorios estén presentes con valores por defecto si es necesario
        campos_obligatorios = {
            "alergias": "",
            "enfermedades": "",
            "diagnosticos": "",
            "sintomas": "",
            "tratamientos": "",
            "cirugias_realizadas": "",
            "recetas_medicas": "",
            "motivos_consultas": "",
            "observaciones": "",
            "estado": "Activo",
            "procedimiento_medico": "",
            "cedula": "",
            "edad": data.get("edad", 0)
        }
        
        for campo, valor_defecto in campos_obligatorios.items():
            if campo not in data or data[campo] is None:
                data[campo] = valor_defecto

        actualizado = dao.updateFicha(id_ficha, data)
        if actualizado:
            return jsonify(success=True, data={**data, "id_ficha_medica": id_ficha}, error=None), 200
        return jsonify(success=False, error=f"No se encontró ficha con ID {id_ficha} o no se pudo actualizar."), 404
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al actualizar ficha {id_ficha}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar ficha médica."), 500

# ============================
# Eliminar ficha
# ============================
@fichaapi.route('/fichas/<int:id_ficha>', methods=['DELETE'])
def deleteFicha(id_ficha):
    dao = FichaMedicaDao()
    try:
        if dao.deleteFicha(id_ficha):
            return jsonify(success=True, data=f"Ficha {id_ficha} eliminada.", error=None), 200
        return jsonify(success=False, error=f"No se encontró ficha con ID {id_ficha}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar ficha {id_ficha}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar ficha médica."), 500