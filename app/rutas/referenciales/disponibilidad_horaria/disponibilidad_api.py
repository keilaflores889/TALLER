from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.disponibilidad_horaria.DisponibilidadHorariaDao import DisponibilidadDao

disponibilidadapi = Blueprint('disponibilidadapi', __name__)

@disponibilidadapi.route('/disponibilidades', methods=['GET'])
def getDisponibilidades():
    dao = DisponibilidadDao()
    try:
        disponibilidades = dao.getDisponibilidades()
        return jsonify({'success': True, 'data': disponibilidades, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener disponibilidades: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@disponibilidadapi.route('/disponibilidades/<int:id_disponibilidad>', methods=['GET'])
def getDisponibilidadById(id_disponibilidad):
    dao = DisponibilidadDao()
    try:
        d = dao.getDisponibilidadById(id_disponibilidad)
        if d:
            return jsonify({'success': True, 'data': d, 'error': None}), 200
        return jsonify({'success': False, 'error': 'No se encontró la disponibilidad'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener disponibilidad: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@disponibilidadapi.route('/disponibilidades', methods=['POST'])
def addDisponibilidad():
    data = request.get_json()
    dao = DisponibilidadDao()

    campos_requeridos = ['id_medico', 'disponibilidad_fecha', 'disponibilidad_hora_inicio', 'disponibilidad_hora_fin', 'disponibilidad_cupos']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio'}), 400

    try:
        new_id = dao.guardarDisponibilidad(
            data['id_medico'],
            data['disponibilidad_hora_inicio'],
            data['disponibilidad_hora_fin'],
            data['disponibilidad_fecha'],
            data['disponibilidad_cupos']
        )
        if new_id:
            return jsonify({'success': True, 'data': {'id_disponibilidad': new_id}, 'error': None}), 201
        return jsonify({'success': False, 'error': 'Este horario ya está registrado'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar disponibilidad: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@disponibilidadapi.route('/disponibilidades/<int:id_disponibilidad>', methods=['PUT'])
def updateDisponibilidad(id_disponibilidad):
    data = request.get_json()
    dao = DisponibilidadDao()

    campos_requeridos = ['id_medico', 'disponibilidad_fecha', 'disponibilidad_hora_inicio', 'disponibilidad_hora_fin', 'disponibilidad_cupos']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio'}), 400

    try:
        exito = dao.updateDisponibilidad(
            id_disponibilidad,
            data['id_medico'],
            data['disponibilidad_hora_inicio'],
            data['disponibilidad_hora_fin'],
            data['disponibilidad_fecha'],
            data['disponibilidad_cupos']
        )
        if exito:
            return jsonify({'success': True, 'data': {'id_disponibilidad': id_disponibilidad}, 'error': None}), 200
        return jsonify({'success': False, 'error': 'No se encontró la disponibilidad o no se pudo actualizar'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar disponibilidad: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@disponibilidadapi.route('/disponibilidades/<int:id_disponibilidad>', methods=['DELETE'])
def deleteDisponibilidad(id_disponibilidad):
    dao = DisponibilidadDao()
    try:
        exito = dao.deleteDisponibilidad(id_disponibilidad)
        if exito:
            return jsonify({'success': True, 'mensaje': f'Disponibilidad {id_disponibilidad} eliminada', 'error': None}), 200
        return jsonify({'success': False, 'error': 'No se encontró la disponibilidad o no se pudo eliminar'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar disponibilidad: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
