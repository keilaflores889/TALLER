from flask import Blueprint, jsonify, request, current_app as app
from app.dao.ModuloConsultorio.RegisTratamiento.RegisTratamientoDAO import TratamientoDao

tratamientoapi = Blueprint('tratamientoapi', __name__)

# ============================
# TRATAMIENTOS - Obtener todos
# ============================
@tratamientoapi.route('/Tratamiento', methods=['GET'])
def getTratamientos():
    tratamientodao = TratamientoDao()
    try:
        tratamientos = tratamientodao.getTratamientos()
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los tratamientos. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Obtener por ID
# ============================
@tratamientoapi.route('/Tratamiento/<int:tratamiento_id>', methods=['GET'])
def getTratamiento(tratamiento_id):
    tratamientodao = TratamientoDao()
    try:
        tratamiento = tratamientodao.getTratamientoById(tratamiento_id)
        if tratamiento:
            return jsonify(success=True, data=tratamiento, error=None), 200
        return jsonify(success=False,
                       error=f"No se encontró el tratamiento con el ID {tratamiento_id}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener tratamiento {tratamiento_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar el tratamiento. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Obtener por consulta detalle
# ============================
@tratamientoapi.route('/Tratamiento/consulta/<int:consulta_detalle_id>', methods=['GET'])
def getTratamientosByConsulta(consulta_detalle_id):
    tratamientodao = TratamientoDao()
    try:
        tratamientos = tratamientodao.getTratamientosByConsultaDetalle(consulta_detalle_id)
        return jsonify(success=True, data=tratamientos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos de consulta {consulta_detalle_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los tratamientos. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Obtener por paciente
# ============================
@tratamientoapi.route('/Tratamiento/paciente/<int:paciente_id>', methods=['GET'])
def getTratamientosByPaciente(paciente_id):
    tratamientodao = TratamientoDao()
    try:
        tratamientos = tratamientodao.getTratamientosByPaciente(paciente_id)
        return jsonify(success=True, data=tratamientos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos del paciente {paciente_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los tratamientos. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Obtener por médico
# ============================
@tratamientoapi.route('/Tratamiento/medico/<int:medico_id>', methods=['GET'])
def getTratamientosByMedico(medico_id):
    tratamientodao = TratamientoDao()
    try:
        tratamientos = tratamientodao.getTratamientosByMedico(medico_id)
        return jsonify(success=True, data=tratamientos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos del médico {medico_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar los tratamientos. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Agregar nuevo
# ============================
@tratamientoapi.route('/Tratamiento', methods=['POST'])
def addTratamiento():
    data = request.get_json() or {}
    tratamientodao = TratamientoDao()

    campos_requeridos = [
        'id_consulta_detalle', 'id_medico', 'id_paciente', 'descripcion_tratamiento'
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
    except ValueError:
        return jsonify(success=False,
                       error="Los campos id_consulta_detalle, id_medico e id_paciente deben ser números enteros."), 400

    # Validar formato de fecha si se proporciona
    if data.get('fecha_tratamiento'):
        try:
            from datetime import datetime
            datetime.strptime(data['fecha_tratamiento'], '%Y-%m-%d')
        except ValueError:
            return jsonify(success=False,
                           error="Formato de fecha inválido. Use YYYY-MM-DD"), 400

    try:
        tratamiento_id = tratamientodao.addTratamiento(data)
        if tratamiento_id:
            app.logger.info(f"Tratamiento creado con ID {tratamiento_id}.")
            return jsonify(success=True,
                           data={**data, 'id_tratamiento': tratamiento_id},
                           error=None), 201
        else:
            return jsonify(success=False,
                           error="No se pudo guardar el tratamiento. Consulte con el administrador."), 500

    except Exception as e:
        app.logger.error(f"Error al agregar tratamiento: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al guardar el tratamiento. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Actualizar existente
# ============================
@tratamientoapi.route('/Tratamiento/<int:tratamiento_id>', methods=['PUT'])
def updateTratamiento(tratamiento_id):
    data = request.get_json() or {}
    tratamientodao = TratamientoDao()

    campos_requeridos = ['id_medico', 'id_paciente', 'descripcion_tratamiento']

    faltantes = [campo for campo in campos_requeridos
                 if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip())]

    if faltantes:
        return jsonify(success=False,
                       error=f"Faltan campos obligatorios: {', '.join(faltantes)}"), 400

    # Validar que los IDs sean enteros
    try:
        data['id_medico'] = int(data['id_medico'])
        data['id_paciente'] = int(data['id_paciente'])
    except ValueError:
        return jsonify(success=False,
                       error="Los campos id_medico e id_paciente deben ser números enteros."), 400

    # Validar formato de fecha si se proporciona
    if data.get('fecha_tratamiento'):
        try:
            from datetime import datetime
            datetime.strptime(data['fecha_tratamiento'], '%Y-%m-%d')
        except ValueError:
            return jsonify(success=False,
                           error="Formato de fecha inválido. Use YYYY-MM-DD"), 400

    try:
        actualizado = tratamientodao.updateTratamiento(tratamiento_id, data)
        if actualizado:
            app.logger.info(f"Tratamiento con ID {tratamiento_id} actualizado exitosamente.")
            return jsonify(success=True,
                           data={**data, 'id_tratamiento': tratamiento_id},
                           error=None), 200
        else:
            return jsonify(success=False,
                           error=f"No se encontró el tratamiento con el ID {tratamiento_id} o no se pudo actualizar."), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar tratamiento con ID {tratamiento_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al actualizar el tratamiento. Consulte con el administrador."), 500

# ============================
# TRATAMIENTOS - Eliminar
# ============================
@tratamientoapi.route('/Tratamiento/<int:tratamiento_id>', methods=['DELETE'])
def deleteTratamiento(tratamiento_id):
    tratamientodao = TratamientoDao()
    try:
        if tratamientodao.deleteTratamiento(tratamiento_id):
            app.logger.info(f"Tratamiento con ID {tratamiento_id} eliminado.")
            return jsonify(success=True,
                           data=f"Tratamiento con ID {tratamiento_id} eliminado correctamente.",
                           error=None), 200
        else:
            return jsonify(success=False,
                           error=f"No se encontró el tratamiento con el ID {tratamiento_id} o no se pudo eliminar."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar tratamiento con ID {tratamiento_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al eliminar el tratamiento. Consulte con el administrador."), 500