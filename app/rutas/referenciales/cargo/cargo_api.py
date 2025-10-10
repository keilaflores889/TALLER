from flask import Blueprint, request, jsonify, current_app as app
import re
from app.dao.referenciales.cargo.CargoDao import CargoDao

cargoapi = Blueprint('cargoapi', __name__)

# ===============================
# Función auxiliar para validar descripción
# ===============================
def validar_descripcion(texto):
    # Permite letras (incluye ñ, tildes), números y espacios
    patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9\s]+$'
    return re.match(patron, texto) is not None


# ===============================
# Trae todos los cargos
# ===============================
@cargoapi.route('/cargos', methods=['GET'])
def getCargos():
    cargodao = CargoDao()
    try:
        cargos = cargodao.getCargos()
        return jsonify({
            'success': True,
            'data': cargos,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los cargos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Trae un cargo por ID
# ===============================
@cargoapi.route('/cargos/<int:cargo_id>', methods=['GET'])
def getCargo(cargo_id):
    cargodao = CargoDao()
    try:
        cargo = cargodao.getCargoById(cargo_id)
        if cargo:
            return jsonify({
                'success': True,
                'data': cargo,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cargo con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Agrega un nuevo cargo
# ===============================
@cargoapi.route('/cargos', methods=['POST'])
def addCargo():
    data = request.get_json()
    cargodao = CargoDao()

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

        # Validar formato
        if not validar_descripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y espacios.'
            }), 400

        # Validar duplicados
        if cargodao.existeDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'Ya existe un cargo con esa descripción.'
            }), 409

        cargo_id = cargodao.guardarCargo(descripcion)
        if cargo_id:
            return jsonify({
                'success': True,
                'data': {
                    'id_cargo': cargo_id,
                    'descripcion': descripcion
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el cargo. Consulte con el administrador.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Actualiza un cargo
# ===============================
@cargoapi.route('/cargos/<int:cargo_id>', methods=['PUT'])
def updateCargo(cargo_id):
    data = request.get_json()
    cargodao = CargoDao()

    campos_requeridos = ['descripcion']

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

        # Validar formato
        if not validar_descripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y espacios.'
            }), 400

        # Validar duplicados (excepto el mismo ID)
        if cargodao.existeDescripcionExceptoId(descripcion, cargo_id):
            return jsonify({
                'success': False,
                'error': 'Otro cargo con esa descripción ya existe.'
            }), 409

        actualizado = cargodao.updateCargo(cargo_id, descripcion)
        if actualizado:
            return jsonify({
                'success': True,
                'data': {
                    'id_cargo': cargo_id,
                    'descripcion': descripcion
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cargo con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Elimina un cargo
# ===============================
@cargoapi.route('/cargos/<int:cargo_id>', methods=['DELETE'])
def deleteCargo(cargo_id):
    cargodao = CargoDao()
    try:
        eliminado = cargodao.deleteCargo(cargo_id)
        if eliminado:
            return jsonify({
                'success': True,
                'mensaje': f'Cargo con ID {cargo_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cargo con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
