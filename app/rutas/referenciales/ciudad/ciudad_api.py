from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.ciudad.CiudadDao import CiudadDao

ciuapi = Blueprint('ciuapi', __name__)

# ===============================
# Trae todas las ciudades
# ===============================
@ciuapi.route('/ciudades', methods=['GET'])
def getCiudades():
    ciudao = CiudadDao()
    try:
        ciudades = ciudao.getCiudades()
        return jsonify({
            'success': True,
            'data': ciudades,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas las ciudades: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae una ciudad por ID
# ===============================
@ciuapi.route('/ciudades/<int:ciudad_id>', methods=['GET'])
def getCiudad(ciudad_id):
    ciudao = CiudadDao()
    try:
        ciudad = ciudao.getCiudadById(ciudad_id)
        if ciudad:
            return jsonify({
                'success': True,
                'data': ciudad,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la ciudad con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener ciudad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega una nueva ciudad
# ===============================
@ciuapi.route('/ciudades', methods=['POST'])
def addCiudad():
    data = request.get_json()
    ciudao = CiudadDao()

    campos_requeridos = ['descripcion']

    # Validar que el campo exista y no esté vacío
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400
        if data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'La descripción no puede estar vacía.'
            }), 400

    try:
        descripcion = data['descripcion'].strip().upper()

        # Validar formato de descripción
        if not ciudao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y espacios.'
            }), 400

        # Validar que no exista duplicado
        if ciudao.existeDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'Ya existe una ciudad con esa descripción.'
            }), 409

        ciudad_id = ciudao.guardarCiudad(descripcion)
        if ciudad_id:
            return jsonify({
                'success': True,
                'data': {
                    'id_ciudad': ciudad_id,
                    'descripcion': descripcion
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la ciudad. Consulte con el administrador.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar ciudad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza una ciudad
# ===============================
@ciuapi.route('/ciudades/<int:ciudad_id>', methods=['PUT'])
def updateCiudad(ciudad_id):
    data = request.get_json()
    ciudao = CiudadDao()

    campos_requeridos = ['descripcion']

    # Validar que el campo exista y no esté vacío
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400
        if data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'La descripción no puede estar vacía.'
            }), 400

    try:
        descripcion = data['descripcion'].strip().upper()

        # Validar formato de descripción
        if not ciudao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y espacios.'
            }), 400

        # Validar que no exista otra ciudad con la misma descripción
        if ciudao.existeDescripcionExceptoId(descripcion, ciudad_id):
            return jsonify({
                'success': False,
                'error': 'Otra ciudad con esa descripción ya existe.'
            }), 409

        actualizado = ciudao.updateCiudad(ciudad_id, descripcion)
        if actualizado:
            return jsonify({
                'success': True,
                'data': {
                    'id_ciudad': ciudad_id,
                    'descripcion': descripcion
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la ciudad con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar ciudad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina una ciudad
# ===============================
@ciuapi.route('/ciudades/<int:ciudad_id>', methods=['DELETE'])
def deleteCiudad(ciudad_id):
    ciudao = CiudadDao()
    try:
        eliminado = ciudao.deleteCiudad(ciudad_id)
        if eliminado:
            return jsonify({
                'success': True,
                'mensaje': f'Ciudad con ID {ciudad_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la ciudad con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar ciudad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500