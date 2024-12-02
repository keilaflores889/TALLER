from flask import Blueprint, request, jsonify, current_app as app
from app.dao.RegisPaciente.RegistroPDao import RegistroPDao

registropapi = Blueprint('registropapi', __name__)

# Obtener todas los registros
@registropapi.route('/RegistroP', methods=['GET'])
def getRegistrosP():
    registropdao = RegistroPDao()
    try:
        registrosp = registropdao.getRegistrosP()
        return jsonify({
            'success': True,
            'data': registrosp,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas los registros: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar las agendas. Consulte con el administrador.'
        }), 500


# Obtener un registro específica por ID
@registropapi.route('/RegistroP/<int:persona_id>', methods=['GET'])
def getRegistroP(persona_id):
    registropdao = RegistroPDao()
    try:
        registrop = registropdao.getRegistroPById(persona_id)
        if registrop:
            return jsonify({
                'success': True,
                'data': registrop,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el registro con el ID {persona_id}.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener registro con ID {persona_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar el registro. Consulte con el administrador.'
        }), 500


# Agregar un nuevo registro
@registropapi.route('/RegistroP', methods=['POST'])
def addRegistroP():
    data = request.get_json()
    registropdao = RegistroPDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula_identidad', 'fecha_nacimiento', 'fecha_registro', 'telefono', 'id_ciudad', 'id_barrio']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo].strip():
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vacía.'
            }), 400

    try:
        nombre = data['nombre'].upper()
        apellido = data['apellido'].upper()
        cedula_identidad = data['cedula_identidad']
        fecha_nacimiento = data['fecha_nacimiento']
        fecha_registro = data['fecha_registro']
        telefono = data['telefono']
        id_ciudad = data['id_ciudad']
        id_barrio = data['id_barrio']

        persona_id = registropdao.guardarRegistroP(nombre, apellido, cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio)
        if persona_id is not None:
            return jsonify({
                'success': True,
                'data': {'id': persona_id, 'nombre': nombre, 'apellido': apellido, 'cedula_identidad': cedula_identidad, 'fecha_nacimiento': fecha_nacimiento, 'fecha_registro': fecha_registro, 'telefono':telefono, 'id_ciudad': id_ciudad, 'id_barrio': id_barrio,},
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el registro. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar el registro: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al guardar el registro. Consulte con el administrador.'
        }), 500


# Actualizar el registro existente
@registropapi.route('/RegistroP/<int:persona_id>', methods=['PUT'])
def updateRegistroP(persona_id):
    data = request.get_json()
    registropdao = RegistroPDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula_identidad', 'fecha_nacimiento', 'fecha_registro', 'telefono', 'id_ciudad', 'id_barrio']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo].strip():
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vacía.'
            }), 400

    try:
        nombre = data['nombre'].strip().upper()
        apellido = data['apellido'].strip().upper()
        cedula_identidad = data['cedula_identidad']
        fecha_nacimiento = data['fecha_nacimiento']
        fecha_registro = data['fecha_registro']
        telefono = data['telefono']
        id_ciudad = data['id_ciudad']
        id_barrio = data['id_barrio']


        if registropdao.updateRegistroP(persona_id, nombre.strip().upper(), apellido.strip().upper(), cedula_identidad, fecha_nacimiento, fecha_registro, telefono, id_ciudad, id_barrio):
            app.logger.info(f"Registro de persona con ID {persona_id} actualizada exitosamente.")
            return jsonify({
                'success': True,
                'data': {'id': persona_id, 'nombre': nombre, 'apellido': apellido, 'cedula_identidad': cedula_identidad, 'fecha_nacimiento': fecha_nacimiento, 'fecha_registro': fecha_registro, 'telefono':telefono, 'id_ciudad':id_ciudad, 'id_barrio': id_barrio},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el registro con el ID {persona_id} o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar registro con ID {persona_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al actualizar el registro. Consulte con el administrador.'
        }), 500


# Eliminar una registro
@registropapi.route('/RegistroP/<int:persona_id>', methods=['DELETE'])
def deleteRegistroP(persona_id):
    registropdao = RegistroPDao()
    try:
        if registropdao.deleteRegistroP(persona_id):
            app.logger.info(f"El registro de persona con ID {persona_id} eliminada.")
            return jsonify({
                'success': True,
                'mensaje': f'Registro con ID {persona_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el registro con el ID {persona_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar registro con ID {persona_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al eliminar el registro. Consulte con el administrador.'
        }), 500
