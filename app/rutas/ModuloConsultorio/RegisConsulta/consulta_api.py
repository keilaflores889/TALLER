from flask import Blueprint, jsonify, request, current_app as app
from app.dao.ModuloConsultorio.RegisConsulta.ConsultasDao import ConsultasDao

consultasapi = Blueprint('consultasapi', __name__)



# ============================
# CONSULTAS CABECERA - Obtener todas
# ============================
@consultasapi.route('/consultas', methods=['GET'])
def getConsultasCabecera():
    dao = ConsultasDao()
    try:
        consultas = dao.getConsultasCabecera()
        return jsonify(success=True, data=consultas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas cabecera: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consultas."), 500

# ============================
# CONSULTAS CABECERA - Obtener por ID
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>', methods=['GET'])
def getConsultaCabecera(id_consulta_cab):
    dao = ConsultasDao()
    try:
        consulta = dao.getConsultaCabeceraById(id_consulta_cab)
        if consulta:
            return jsonify(success=True, data=consulta, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consulta."), 500

# ============================
# CONSULTAS CABECERA - Obtener consulta completa (cabecera + detalles)
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>/completa', methods=['GET'])
def getConsultaCompleta(id_consulta_cab):
    dao = ConsultasDao()
    try:
        consulta = dao.getConsultaCompleta(id_consulta_cab)
        if consulta:
            return jsonify(success=True, data=consulta, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consulta completa {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consulta completa."), 500

# ============================
# CONSULTAS CABECERA - Obtener por paciente
# ============================
@consultasapi.route('/consultas/paciente/<int:id_paciente>', methods=['GET'])
def getConsultasByPaciente(id_paciente):
    dao = ConsultasDao()
    try:
        consultas = dao.getConsultasByPaciente(id_paciente)
        return jsonify(success=True, data=consultas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas del paciente {id_paciente}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consultas por paciente."), 500

# ============================
# CONSULTAS CABECERA - Obtener por médico
# ============================
@consultasapi.route('/consultas/medico/<int:id_medico>', methods=['GET'])
def getConsultasByMedico(id_medico):
    dao = ConsultasDao()
    try:
        consultas = dao.getConsultasByMedico(id_medico)
        return jsonify(success=True, data=consultas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas del médico {id_medico}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consultas por médico."), 500

# ============================
# CONSULTAS CABECERA - Obtener por fecha
# ============================
@consultasapi.route('/consultas/fecha/<string:fecha>', methods=['GET'])
def getConsultasByFecha(fecha):
    dao = ConsultasDao()
    try:
        consultas = dao.getConsultasByFecha(fecha)
        return jsonify(success=True, data=consultas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas por fecha {fecha}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consultas por fecha."), 500

# ============================
# CONSULTAS CABECERA - Obtener por estado
# ============================
@consultasapi.route('/consultas/estado/<string:estado>', methods=['GET'])
def getConsultasByEstado(estado):
    dao = ConsultasDao()
    try:
        consultas = dao.getConsultasByEstado(estado)
        return jsonify(success=True, data=consultas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas por estado {estado}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consultas por estado."), 500

# ============================
# CONSULTAS CABECERA - Agregar nueva
# ============================
@consultasapi.route('/consultas', methods=['POST'])
def addConsultaCabecera():
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_personal', 'id_consultorio', 'id_medico', 'id_paciente', 
                         'fecha_cita', 'hora_cita']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        # Asegurar que los campos opcionales estén presentes con valores por defecto
        if 'estado' not in data or data['estado'] is None:
            data['estado'] = 'programada'
        
        if 'duracion_minutos' in data and data['duracion_minutos'] == '':
            data['duracion_minutos'] = None

        consulta_id = dao.addConsultaCabecera(data)
        if consulta_id:
            return jsonify(success=True, data={**data, "id_consulta_cab": consulta_id}, error=None), 201
        return jsonify(success=False, error="No se pudo guardar la consulta."), 500
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al agregar consulta: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar consulta."), 500

# ============================
# CONSULTAS CABECERA - Actualizar
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>', methods=['PUT'])
def updateConsultaCabecera(id_consulta_cab):
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_personal', 'id_consultorio', 'id_medico', 'id_paciente', 
                         'fecha_cita', 'hora_cita']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        # Asegurar que los campos opcionales estén presentes con valores por defecto
        if 'estado' not in data or data['estado'] is None:
            data['estado'] = 'programada'
        
        if 'duracion_minutos' in data and data['duracion_minutos'] == '':
            data['duracion_minutos'] = None

        actualizado = dao.updateConsultaCabecera(id_consulta_cab, data)
        if actualizado:
            return jsonify(success=True, data={**data, "id_consulta_cab": id_consulta_cab}, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab} o no se pudo actualizar."), 404
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al actualizar consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar consulta."), 500

# ============================
# CONSULTAS CABECERA - Actualizar solo estado
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>/estado', methods=['PATCH'])
def updateEstadoConsulta(id_consulta_cab):
    data = request.get_json() or {}
    dao = ConsultasDao()

    if 'estado' not in data:
        return jsonify(success=False, error="Falta el campo 'estado'."), 400

    try:
        actualizado = dao.updateEstadoConsulta(id_consulta_cab, data['estado'])
        if actualizado:
            return jsonify(success=True, data={"id_consulta_cab": id_consulta_cab, "estado": data['estado']}, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar estado de consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar estado."), 500

# ============================
# CONSULTAS CABECERA - Eliminar
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>', methods=['DELETE'])
def deleteConsultaCabecera(id_consulta_cab):
    dao = ConsultasDao()
    try:
        if dao.deleteConsultaCabecera(id_consulta_cab):
            return jsonify(success=True, data=f"Consulta {id_consulta_cab} eliminada.", error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar consulta."), 500

# ============================
# CONSULTAS DETALLE - Obtener todas
# ============================
@consultasapi.route('/consultas-detalle', methods=['GET'])
def getConsultasDetalle():
    dao = ConsultasDao()
    try:
        detalles = dao.getConsultasDetalle()
        return jsonify(success=True, data=detalles, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas detalle: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalles."), 500

# ============================
# CONSULTAS DETALLE - Obtener por ID
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>', methods=['GET'])
def getConsultaDetalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        detalle = dao.getConsultaDetalleById(id_consulta_detalle)
        if detalle:
            return jsonify(success=True, data=detalle, error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalle."), 500

# ============================
# CONSULTAS DETALLE - Obtener por consulta cabecera
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>/detalles', methods=['GET'])
def getDetallesByConsulta(id_consulta_cab):
    dao = ConsultasDao()
    try:
        detalles = dao.getDetallesByConsultaCab(id_consulta_cab)
        return jsonify(success=True, data=detalles, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener detalles de consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalles."), 500

# ============================
# CONSULTAS DETALLE - Agregar nuevo
# ============================
@consultasapi.route('/consultas-detalle', methods=['POST'])
def addConsultaDetalle():
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_consulta_cab', 'id_sintoma', 'diagnostico', 'tratamiento']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        # Asegurar que los campos opcionales estén presentes
        if 'pieza_dental' in data and data['pieza_dental'] == '':
            data['pieza_dental'] = None
        
        if 'procedimiento' in data and data['procedimiento'] == '':
            data['procedimiento'] = None

        detalle_id = dao.addConsultaDetalle(data)
        if detalle_id:
            return jsonify(success=True, data={**data, "id_consulta_detalle": detalle_id}, error=None), 201
        return jsonify(success=False, error="No se pudo guardar el detalle de consulta."), 500
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al agregar detalle: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar detalle."), 500

# ============================
# CONSULTAS DETALLE - Actualizar
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>', methods=['PUT'])
def updateConsultaDetalle(id_consulta_detalle):
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_consulta_cab', 'id_sintoma', 'diagnostico', 'tratamiento']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        # Asegurar que los campos opcionales estén presentes
        if 'pieza_dental' in data and data['pieza_dental'] == '':
            data['pieza_dental'] = None
        
        if 'procedimiento' in data and data['procedimiento'] == '':
            data['procedimiento'] = None

        actualizado = dao.updateConsultaDetalle(id_consulta_detalle, data)
        if actualizado:
            return jsonify(success=True, data={**data, "id_consulta_detalle": id_consulta_detalle}, error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle} o no se pudo actualizar."), 404
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al actualizar detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar detalle."), 500

# ============================
# CONSULTAS DETALLE - Eliminar
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>', methods=['DELETE'])
def deleteConsultaDetalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        if dao.deleteConsultaDetalle(id_consulta_detalle):
            return jsonify(success=True, data=f"Detalle {id_consulta_detalle} eliminado.", error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar detalle."), 500