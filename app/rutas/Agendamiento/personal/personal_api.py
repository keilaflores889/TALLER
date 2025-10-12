from flask import Blueprint, jsonify, request, current_app as app
from app.dao.referenciales.personal.PersonalDao import PersonalDao

personalapi = Blueprint('personalapi', __name__) 


# ==============================
#   Obtener todo el personal
# ==============================
@personalapi.route('/personal', methods=['GET'])
def getPersonal():
    personaldao = PersonalDao()
    try:
        personal = personaldao.getPersonal()
        return jsonify({'success': True, 'data': personal, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todo el personal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar el personal. Consulte con el administrador.'
        }), 500


# ==============================
#   Obtener personal por ID
# ==============================
@personalapi.route('/personal/<int:personal_id>', methods=['GET'])
def getPersonalById(personal_id):
    personaldao = PersonalDao()
    try:
        persona = personaldao.getPersonalById(personal_id)
        if persona:
            return jsonify({'success': True, 'data': persona, 'error': None}), 200
        return jsonify({
            'success': False,
            'error': f'No se encontró la persona con el ID {personal_id}.'
        }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener persona con ID {personal_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar la persona. Consulte con el administrador.'
        }), 500


# ==============================
#   Agregar nuevo personal
# ==============================
@personalapi.route('/personal', methods=['POST'])
def addPersonal():
    data = request.get_json()
    personaldao = PersonalDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento',
                         'telefono', 'direccion', 'correo', 'id_ciudad', 'id_cargo', 'fecha_registro']
    for campo in campos_requeridos:
        if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip()):
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        # Validación de duplicados
        if personaldao.existeDuplicado(data['cedula'], data['correo']):
            return jsonify({
                'success': False,
                'error': 'El personal ya está registrado.'
            }), 409

        personal_id = personaldao.guardarPersonal(
            data['nombre'], data['apellido'], data['cedula'], data['fecha_nacimiento'],
            data['telefono'], data['direccion'], data['correo'],
            data['id_ciudad'], data['id_cargo'], data['fecha_registro']
        )

        if personal_id:
            app.logger.info(f"Personal creado con ID {personal_id}.")
            return jsonify({
                'success': True,
                'data': {**data, 'id_personal': personal_id},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el personal. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar personal: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al guardar el personal. Consulte con el administrador.'
        }), 500


# ==============================
#   Actualizar personal existente
# ==============================
@personalapi.route('/personal/<int:personal_id>', methods=['PUT'])
def updatePersonal(personal_id):
    data = request.get_json()
    personaldao = PersonalDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento',
                         'telefono', 'direccion', 'correo', 'id_ciudad', 'id_cargo', 'fecha_registro']
    for campo in campos_requeridos:
        if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip()):
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        actualizado = personaldao.updatePersonal(
            personal_id, data['nombre'], data['apellido'], data['cedula'], data['fecha_nacimiento'],
            data['telefono'], data['direccion'], data['correo'], data['id_ciudad'], data['id_cargo'],
            data['fecha_registro']
        )

        if actualizado:
            app.logger.info(f"Personal con ID {personal_id} actualizado exitosamente.")
            return jsonify({
                'success': True,
                'data': {**data, 'id_personal': personal_id},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la persona con el ID {personal_id} o no se pudo actualizar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar personal con ID {personal_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al actualizar el personal. Consulte con el administrador.'
        }), 500


# ==============================
#   Eliminar personal
# ==============================
@personalapi.route('/personal/<int:personal_id>', methods=['DELETE'])
def deletePersonal(personal_id):
    personaldao = PersonalDao()
    try:
        if personaldao.deletePersonal(personal_id):
            app.logger.info(f"Personal con ID {personal_id} eliminado.")
            return jsonify({
                'success': True,
                'mensaje': f'Personal con ID {personal_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la persona con el ID {personal_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar personal con ID {personal_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al eliminar el personal. Consulte con el administrador.'
        }), 500
