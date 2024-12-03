from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.Barrio.BarrioDao import BarrioDao
barrioapi = Blueprint('barrioapi', __name__)

# Trae todas las barrios
@barrioapi.route('/barrio', methods=['GET'])
def getBarrios():
    barriodao = BarrioDao()

    try:
        barrios = barriodao.getBarrios()

        return jsonify({
            'success': True,
            'data': barrios,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas los barrios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@barrioapi.route('/barrio/<int:barrio_id>', methods=['GET'])
def getBarrio(barrio_id):
    barriodao = BarrioDao()

    try:
        barrio = barriodao.getBarrioById(barrio_id)

        if barrio:
            return jsonify({
                'success': True,
                'data': barrio,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el barrio con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener barrio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega una nueva barrio
@barrioapi.route('/barrio', methods=['POST'])
def addBarrio():
    data = request.get_json()
    barriodao = BarrioDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['descripcion']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                            'success': False,
                            'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
                            }), 400

    try:
        descripcion = data['descripcion'].upper()
        barrio_id = barriodao.guardarBarrio(descripcion)
        if barrio_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_barrio': barrio_id, 'descripcion': descripcion},
                'error': None
            }), 201
        else:
            return jsonify({ 'success': False, 'error': 'No se pudo guardar el barrio. Consulte con el administrador.' }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar barrio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@barrioapi.route('/barrio/<int:barrio_id>', methods=['PUT'])
def updateBarrio(barrio_id):
    data = request.get_json()
    barriodao = BarrioDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['descripcion']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                            'success': False,
                            'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
                            }), 400
    descripcion = data['descripcion']
    try:
        if barriodao.updateBarrio(barrio_id, descripcion.upper()):
            return jsonify({
                'success': True,
                'data': {'id_barrio': barrio_id, 'descripcion': descripcion},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el barrio con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar barrio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@barrioapi.route('/barrio/<int:barrio_id>', methods=['DELETE'])
def deleteBarrio(barrio_id):
    barriodao = BarrioDao()

    try:
        # Usar el retorno de eliminarbarrio para determinar el éxito
        if barriodao.deleteBarrio(barrio_id):
            return jsonify({
                'success': True,
                'mensaje': f'Barrio con ID {barrio_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el barrio con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar barrio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
    
