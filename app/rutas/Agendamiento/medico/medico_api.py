from flask import Blueprint, request, jsonify, current_app as app
from app.dao.medico.MedicoDao import MedicoDao

medicoapi = Blueprint('medicoapi', __name__)

# Obtener todas los medicos
@medicoapi.route('/medico', methods=['GET'])
def getMedicos():
    medicodao = MedicoDao()
    try:
        medicos = medicodao.getMedicos()
        return jsonify({
            'success': True,
            'data': medicos,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas los medicos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar los medicos. Consulte con el administrador.'
        }), 500


# Obtener una agenda específica por ID
@medicoapi.route('/medico/<int:medico_id>', methods=['GET'])
def getMedico(medico_id):
    medicodao = MedicoDao()
    try:
        medico = medicodao.getMedicoById(medico_id)
        if medico:
            return jsonify({
                'success': True,
                'data': medico,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el medico con el ID {medico_id}.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener medico con ID {medico_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar el medico. Consulte con el administrador.'
        }), 500


# Agregar una nuevo medico
@medicoapi.route('/medico', methods=['POST'])
def addMedico():
    data = request.get_json()
    medicodao = MedicoDao()

    # Validar campos requeridos
    campos_requeridos = ['id_medico', 'id_persona', 'id_especialidad', 'num_registro']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vacía.'
            }), 400

    try:
        id_medico = data['id_medico']
        id_persona = data['id_persona']
        id_especialidad = data['id_especialidad']
        num_registro = data['num_registro']

        medico_id = medicodao.guardarMedico(id_medico, id_persona, id_especialidad, num_registro)
        if medico_id:
            app.logger.info(f"Medico creada con ID {medico_id}.")
            return jsonify({
                'success': True,
                'data': {'id_medico': medico_id, 'id_medico': id_medico, 'id_persona': id_persona, 'id_especialidad': id_especialidad, 'num_registro': num_registro},
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el medico. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar medico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al guardar medico. Consulte con el administrador.'
        }), 500


# Actualizar una medico existente
@medicoapi.route('/medico/<int:medico_id>', methods=['PUT'])
def updateMedico(medico_id):
    data = request.get_json()
    medicodao = MedicoDao()

    # Validar campos requeridos
    campos_requeridos = ['id_medico', 'id_persona', 'id_especialidad', 'num_registro']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vacía.'
            }), 400

    try:
        id_medico = data['id_medico']
        id_persona = data['id_persona']
        id_especialidad = data['id_especialidad']
        num_registro = data['num_registro']

        if medicodao.updateMedico(medico_id, id_medico, id_persona, id_especialidad, num_registro):
            app.logger.info(f"medico con ID {medico_id} actualizada exitosamente.")
            return jsonify({
                'success': True,
                'data': {'id_medico': medico_id, 'id_medico': id_medico, 'id_persona': id_persona, 'id_especialidad': id_especialidad, 'num_registro': num_registro},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el medico con el ID {medico_id} o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar medico con ID {medico_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al actualizar el medico. Consulte con el administrador.'
        }), 500


# Eliminar medico
@medicoapi.route('/medico/<int:medico_id>', methods=['DELETE'])
def deleteMedico(medico_id):
    medicodao = MedicoDao()
    try:
        if medicodao.deleteMedico(medico_id):
            app.logger.info(f"medico con ID {medico_id} eliminada.")
            return jsonify({
                'success': True,
                'mensaje': f'medico con ID {medico_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el medico con el ID {medico_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar el medico con ID {medico_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al eliminar el medico. Consulte con el administrador.'
        }), 500
