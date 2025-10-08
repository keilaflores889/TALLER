from flask import Blueprint, jsonify, request, current_app as app
from datetime import datetime
from app.dao.ModuloConsultorio.RegisDiagnostico.RegDiagnosticoDao import DiagnosticoDao
Rdiagnosticoapi = Blueprint('Rdiagnosticoapi', __name__)

# ==============================
#   Obtener todos los diagnósticos
# ==============================
@Rdiagnosticoapi.route('/Diagnostico', methods=['GET'])
def getDiagnosticos():
    diagnosticodao = DiagnosticoDao()
    try:
        diagnosticos = diagnosticodao.getDiagnosticos()
        return jsonify({'success': True, 'data': diagnosticos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los diagnósticos. Consulte con el administrador."), 500

# ==============================
#   Obtener diagnóstico por ID
# ==============================
@Rdiagnosticoapi.route('/Diagnostico/<int:diagnostico_id>', methods=['GET'])
def getDiagnostico(diagnostico_id):
    diagnosticodao = DiagnosticoDao()
    try:
        diagnostico = diagnosticodao.getDiagnosticoById(diagnostico_id)
        if diagnostico:
            return jsonify(success=True, data=diagnostico, error=None), 200
        return jsonify(success=False,
                       error=f"No se encontró el diagnóstico con el ID {diagnostico_id}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener diagnóstico con ID {diagnostico_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar el diagnóstico. Consulte con el administrador."), 500

# ==============================
#   Obtener diagnósticos por consulta detalle
# ==============================
@Rdiagnosticoapi.route('/Diagnostico/consulta/<int:consulta_detalle_id>', methods=['GET'])
def getDiagnosticosByConsulta(consulta_detalle_id):
    diagnosticodao = DiagnosticoDao()
    try:
        diagnosticos = diagnosticodao.getDiagnosticosByConsultaDetalle(consulta_detalle_id)
        return jsonify(success=True, data=diagnosticos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos de consulta {consulta_detalle_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los diagnósticos. Consulte con el administrador."), 500

# ==============================
#   Obtener diagnósticos por paciente
# ==============================
@Rdiagnosticoapi.route('/Diagnostico/paciente/<int:paciente_id>', methods=['GET'])
def getDiagnosticosByPaciente(paciente_id):
    diagnosticodao = DiagnosticoDao()
    try:
        diagnosticos = diagnosticodao.getDiagnosticosByPaciente(paciente_id)
        return jsonify(success=True, data=diagnosticos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos del paciente {paciente_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los diagnósticos. Consulte con el administrador."), 500

# ==============================
#   Obtener diagnósticos por médico
# ==============================
@Rdiagnosticoapi.route('/Diagnostico/medico/<int:medico_id>', methods=['GET'])
def getDiagnosticosByMedico(medico_id):
    diagnosticodao = DiagnosticoDao()
    try:
        diagnosticos = diagnosticodao.getDiagnosticosByMedico(medico_id)
        return jsonify(success=True, data=diagnosticos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos del médico {medico_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los diagnósticos. Consulte con el administrador."), 500

# ==============================
#   Agregar nuevo diagnóstico
# ==============================
@Rdiagnosticoapi.route('/Diagnostico', methods=['POST'])
def addDiagnostico():
    data = request.get_json() or {}
    diagnosticodao = DiagnosticoDao()

    campos_requeridos = [
        'id_consulta_detalle', 'id_medico', 'id_paciente', 'descripcion_diagnostico'
    ]

    faltantes = [campo for campo in campos_requeridos
                 if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip())]

    if faltantes:
        return jsonify(success=False,
                       error=f"Faltan campos obligatorios: {', '.join(faltantes)}"), 400

    # Validar que los IDs sean enteros
    try:
        data['id_consulta_detalle'] = int(data['id_consulta_detalle'])
        data['id_medico'] = int(data['id_medico'])
        data['id_paciente'] = int(data['id_paciente'])
        if data.get('id_tipo_diagnostico'):
            data['id_tipo_diagnostico'] = int(data['id_tipo_diagnostico'])
    except ValueError:
        return jsonify(success=False,
                       error="Los campos id_consulta_detalle, id_medico, id_paciente e id_tipo_diagnostico deben ser números enteros."), 400

    # Validar formato de fecha si se proporciona
    if data.get('fecha_diagnostico'):
        try:
            datetime.strptime(data['fecha_diagnostico'], '%Y-%m-%d')
        except ValueError:
            return jsonify(success=False,
                           error="Formato de fecha inválido. Use YYYY-MM-DD"), 400

    try:
        diagnostico_id = diagnosticodao.addDiagnostico(data)
        if diagnostico_id:
            app.logger.info(f"Diagnóstico creado con ID {diagnostico_id}.")
            return jsonify(success=True,
                           data={**data, 'id_diagnostico': diagnostico_id},
                           error=None), 201
        else:
            return jsonify(success=False,
                           error="No se pudo guardar el diagnóstico. Consulte con el administrador."), 500

    except Exception as e:
        app.logger.error(f"Error al agregar diagnóstico: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al guardar el diagnóstico. Consulte con el administrador."), 500

# ==============================
#   Actualizar diagnóstico existente
# ==============================
@Rdiagnosticoapi.route('/Diagnostico/<int:diagnostico_id>', methods=['PUT'])
def updateDiagnostico(diagnostico_id):
    data = request.get_json() or {}
    diagnosticodao = DiagnosticoDao()

    campos_requeridos = ['id_medico', 'id_paciente', 'descripcion_diagnostico']

    faltantes = [campo for campo in campos_requeridos
                 if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip())]

    if faltantes:
        return jsonify(success=False,
                       error=f"Faltan campos obligatorios: {', '.join(faltantes)}"), 400

    # Validar que los IDs sean enteros
    try:
        data['id_medico'] = int(data['id_medico'])
        data['id_paciente'] = int(data['id_paciente'])
        if data.get('id_tipo_diagnostico'):
            data['id_tipo_diagnostico'] = int(data['id_tipo_diagnostico'])
    except ValueError:
        return jsonify(success=False,
                       error="Los campos id_medico, id_paciente e id_tipo_diagnostico deben ser números enteros."), 400

    # Validar formato de fecha si se proporciona
    if data.get('fecha_diagnostico'):
        try:
            datetime.strptime(data['fecha_diagnostico'], '%Y-%m-%d')
        except ValueError:
            return jsonify(success=False,
                           error="Formato de fecha inválido. Use YYYY-MM-DD"), 400

    try:
        actualizado = diagnosticodao.updateDiagnostico(diagnostico_id, data)
        if actualizado:
            app.logger.info(f"Diagnóstico con ID {diagnostico_id} actualizado exitosamente.")
            return jsonify(success=True,
                           data={**data, 'id_diagnostico': diagnostico_id},
                           error=None), 200
        else:
            return jsonify(success=False,
                           error=f"No se encontró el diagnóstico con el ID {diagnostico_id} o no se pudo actualizar."), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar diagnóstico con ID {diagnostico_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al actualizar el diagnóstico. Consulte con el administrador."), 500

# ==============================
#   Eliminar diagnóstico
# ==============================
@Rdiagnosticoapi.route('/Diagnostico/<int:diagnostico_id>', methods=['DELETE'])
def deleteDiagnostico(diagnostico_id):
    diagnosticodao = DiagnosticoDao()
    try:
        if diagnosticodao.deleteDiagnostico(diagnostico_id):
            app.logger.info(f"Diagnóstico con ID {diagnostico_id} eliminado.")
            return jsonify(success=True,
                           data=f"Diagnóstico con ID {diagnostico_id} eliminado correctamente.",
                           error=None), 200
        else:
            return jsonify(success=False,
                           error=f"No se encontró el diagnóstico con el ID {diagnostico_id} o no se pudo eliminar."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar diagnóstico con ID {diagnostico_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al eliminar el diagnóstico. Consulte con el administrador."), 500