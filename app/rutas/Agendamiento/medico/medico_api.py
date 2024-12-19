from flask import Blueprint, jsonify, request, current_app as app
from app.dao.medico.MedicoDao import MedicoDao

medicoapi = Blueprint('medicoapi', __name__) 

# Obtener todos los médicos
@medicoapi.route('/medico', methods=['GET'])
def getMedicos():
    medicodao = MedicoDao()
    try:
        medicos = medicodao.getMedicos()  # Llama al DAO para obtener todos los médicos
        return jsonify({
            'success': True,
            'data': medicos,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los médicos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar los médicos. Consulte con el administrador.'
        }), 500


# Obtener un médico específico por ID
@medicoapi.route('/medico/<int:medico_id>', methods=['GET'])
def getMedico(medico_id):
    medicodao = MedicoDao()
    try:
        medico = medicodao.getMedicoById(medico_id)  # Obtiene un médico por ID
        if medico:
            return jsonify({
                'success': True,
                'data': medico,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el médico con el ID {medico_id}.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener médico con ID {medico_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar el médico. Consulte con el administrador.'
        }), 500


# Agregar un nuevo médico
@medicoapi.route('/medico', methods=['POST'])
def addMedico():
    data = request.get_json()
    medicodao = MedicoDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'id_especialidad', 'num_registro']
    for campo in campos_requeridos:
        if not data.get(campo):
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400

    try:
        nombre = data['nombre']
        apellido = data['apellido']
        id_especialidad = data['id_especialidad']
        num_registro = data['num_registro']

        # Guardar médico en la base de datos
        medico_id = medicodao.guardarMedico(nombre, apellido, id_especialidad, num_registro)
        if medico_id:
            return jsonify({
                'success': True,
                'data': {
                    'id_medico': medico_id,
                    'nombre': nombre,
                    'apellido': apellido,
                    'id_especialidad': id_especialidad,
                    'num_registro': num_registro
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el médico. Consulte con el administrador.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar médico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al guardar el médico. Consulte con el administrador.'
        }), 500


# Actualizar un médico existente
@medicoapi.route('/medico/<int:medico_id>', methods=['PUT'])
def updateMedico(medico_id):
    data = request.get_json()
    medicodao = MedicoDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'id_especialidad', 'num_registro']
    for campo in campos_requeridos:
        if not data.get(campo):
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400

    try:
        nombre = data['nombre']
        apellido = data['apellido']
        id_especialidad = data['id_especialidad']
        num_registro = data['num_registro']

        # Actualizar médico en la base de datos
        actualizado = medicodao.updateMedico(medico_id, nombre, apellido, id_especialidad, num_registro)
        if actualizado:
            return jsonify({
                'success': True,
                'data': {
                    'id_medico': medico_id,
                    'nombre': nombre,
                    'apellido': apellido,
                    'id_especialidad': id_especialidad,
                    'num_registro': num_registro
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el médico con el ID {medico_id} o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar médico con ID {medico_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al actualizar el médico. Consulte con el administrador.'
        }), 500


# Eliminar un médico
@medicoapi.route('/medico/<int:medico_id>', methods=['DELETE'])
def deleteMedico(medico_id):
    medicodao = MedicoDao()
    try:
        eliminado = medicodao.deleteMedico(medico_id)  # Eliminar médico por ID
        if eliminado:
            return jsonify({
                'success': True,
                'mensaje': f'Médico con ID {medico_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el médico con el ID {medico_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar el médico con ID {medico_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al eliminar el médico. Consulte con el administrador.'
        }), 500