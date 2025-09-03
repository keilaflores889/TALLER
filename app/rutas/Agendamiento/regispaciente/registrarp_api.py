from flask import Blueprint, jsonify, request, current_app as app
from app.dao.RegisPaciente.RegistroPDao import PacienteDao
pacienteapi = Blueprint('pacienteapi', __name__) 


# ==============================
#   Obtener todos los pacientes
# ==============================
@pacienteapi.route('/paciente', methods=['GET'])
def getPacientes():
    pacientedao = PacienteDao()
    try:
        pacientes = pacientedao.getPacientes()
        return jsonify({'success': True, 'data': pacientes, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los pacientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar los pacientes. Consulte con el administrador.'
        }), 500


# ==============================
#   Obtener paciente por ID
# ==============================
@pacienteapi.route('/paciente/<int:paciente_id>', methods=['GET'])
def getPaciente(paciente_id):
    pacientedao = PacienteDao()
    try:
        paciente = pacientedao.getPacienteById(paciente_id)
        if paciente:
            return jsonify({'success': True, 'data': paciente, 'error': None}), 200
        return jsonify({
            'success': False,
            'error': f'No se encontró el paciente con el ID {paciente_id}.'
        }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener paciente con ID {paciente_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar el paciente. Consulte con el administrador.'
        }), 500


# ==============================
#   Agregar nuevo paciente
# ==============================
@pacienteapi.route('/paciente', methods=['POST'])
def addPaciente():
    data = request.get_json()
    pacientedao = PacienteDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula_entidad',
                         'fecha_nacimiento', 'fecha_registro', 'id_ciudad']
    for campo in campos_requeridos:
        if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip()):
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400

    try:
        paciente_id = pacientedao.guardarPaciente(
            data['nombre'], data['apellido'], data['cedula_entidad'],
            data['fecha_nacimiento'], data['fecha_registro'],
            data.get('telefono'), data.get('direccion'),
            data.get('correo'), data['id_ciudad']
        )

        if paciente_id:
            return jsonify({
                'success': True,
                'data': {**data, 'id_paciente': paciente_id},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Paciente ya está registrado.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno.'}), 500

    try:
        # Validación de duplicados (cédula)
        if pacientedao.existeDuplicado(data['cedula_entidad']):
            return jsonify({
                'success': False,
                'error': 'El paciente ya está registrado con esa cédula.'
            }), 409

        paciente_id = pacientedao.guardarPaciente(
            data['nombre'], data['apellido'], data['cedula_entidad'],
            data['fecha_nacimiento'], data['fecha_registro'],
            data['telefono'], data['direccion'], data['correo'], data['id_ciudad']
        )

        if paciente_id:
            app.logger.info(f"Paciente creado con ID {paciente_id}.")
            return jsonify({
                'success': True,
                'data': {**data, 'id_paciente': paciente_id},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el paciente. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar paciente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al guardar el paciente. Consulte con el administrador.'
        }), 500


# ==============================
#   Actualizar paciente existente
# ==============================
@pacienteapi.route('/paciente/<int:paciente_id>', methods=['PUT'])
def updatePaciente(paciente_id):
    data = request.get_json()
    pacientedao = PacienteDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula_entidad', 
                         'fecha_nacimiento', 'fecha_registro', 
                         'telefono', 'direccion', 'correo', 'id_ciudad']
    for campo in campos_requeridos:
        if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip()):
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        actualizado = pacientedao.updatePaciente(
            paciente_id, data['nombre'], data['apellido'], data['cedula_entidad'],
            data['fecha_nacimiento'], data['fecha_registro'],
            data['telefono'], data['direccion'], data['correo'], data['id_ciudad']
        )

        if actualizado:
            app.logger.info(f"Paciente con ID {paciente_id} actualizado exitosamente.")
            return jsonify({
                'success': True,
                'data': {**data, 'id_paciente': paciente_id},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el paciente con el ID {paciente_id} o no se pudo actualizar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar paciente con ID {paciente_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al actualizar el paciente. Consulte con el administrador.'
        }), 500


# ==============================
#   Eliminar paciente
# ==============================
@pacienteapi.route('/paciente/<int:paciente_id>', methods=['DELETE'])
def deletePaciente(paciente_id):
    pacientedao = PacienteDao()
    try:
        if pacientedao.deletePaciente(paciente_id):
            app.logger.info(f"Paciente con ID {paciente_id} eliminado.")
            return jsonify({
                'success': True,
                'mensaje': f'Paciente con ID {paciente_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró el paciente con el ID {paciente_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar paciente con ID {paciente_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al eliminar el paciente. Consulte con el administrador.'
        }), 500
