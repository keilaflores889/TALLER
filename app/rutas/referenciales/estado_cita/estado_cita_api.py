from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.estado_cita.EstadoCitaDao import EstadoCitaDao
import re

estacitapi = Blueprint('estacitapi', __name__)


# ===============================
# Función auxiliar para validar descripción
# ===============================
def validar_descripcion(texto):
    patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$'
    return re.match(patron, texto) is not None


# ===============================
# Trae todos los estados de cita
# ===============================
@estacitapi.route('/estadoscitas', methods=['GET'])
def getEstadosCitas():
    estdao = EstadoCitaDao()
    try:
        estados = estdao.getEstadosCitas()
        return jsonify({
            'success': True,
            'data': estados,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los estados de cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Trae un estado de cita por ID
# ===============================
@estacitapi.route('/estadoscitas/<int:estado_id>', methods=['GET'])
def getEstadoCita(estado_id):
    estdao = EstadoCitaDao()
    try:
        estado = estdao.getEstadoCitaById(estado_id)
        if estado:
            return jsonify({
                'success': True,
                'data': estado,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estado de cita con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener estado de cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Agrega un nuevo estado de cita
# ===============================
@estacitapi.route('/estadoscitas', methods=['POST'])
def addEstadoCita():
    data = request.get_json()
    estdao = EstadoCitaDao()

    if not data or 'descripcion' not in data:
        return jsonify({
            'success': False,
            'error': 'El campo descripción es obligatorio.'
        }), 400

    descripcion = data['descripcion'].strip().upper()

    if not descripcion:
        return jsonify({
            'success': False,
            'error': 'La descripción no puede estar vacía.'
        }), 400

    # Validar formato
    if not validar_descripcion(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras y espacios.'
        }), 400

   

    # Validar duplicado
    if estdao.existeDescripcion(descripcion):
        return jsonify({
            'success': False,
            'error': f'Ya existe un estado de cita con la descripción "{descripcion}".'
        }), 409

    try:
        estado_id = estdao.guardarEstadoCita(descripcion)
        if estado_id:
            return jsonify({
                'success': True,
                'data': {'id_estado_cita': estado_id, 'descripcion': descripcion},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el estado de cita.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar estado de cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Actualiza un estado de cita
# ===============================
@estacitapi.route('/estadoscitas/<int:estado_id>', methods=['PUT'])
def updateEstadoCita(estado_id):
    data = request.get_json()
    estdao = EstadoCitaDao()

    if not data or 'descripcion' not in data:
        return jsonify({
            'success': False,
            'error': 'El campo descripción es obligatorio.'
        }), 400

    descripcion = data['descripcion'].strip().upper()

    if not descripcion:
        return jsonify({
            'success': False,
            'error': 'La descripción no puede estar vacía.'
        }), 400

    if not validar_descripcion(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras y espacios.'
        }), 400

   

    if estdao.existeDescripcionExceptoId(descripcion, estado_id):
        return jsonify({
            'success': False,
            'error': f'Otro estado de cita con la descripción "{descripcion}" ya existe.'
        }), 409

    try:
        actualizado = estdao.updateEstadoCita(estado_id, descripcion)
        if actualizado:
            return jsonify({
                'success': True,
                'data': {'id_estado_cita': estado_id, 'descripcion': descripcion},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estado de cita con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar estado de cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Elimina un estado de cita
# ===============================
@estacitapi.route('/estadoscitas/<int:estado_id>', methods=['DELETE'])
def deleteEstadoCita(estado_id):
    estdao = EstadoCitaDao()
    try:
        eliminado = estdao.deleteEstadoCita(estado_id)
        if eliminado:
            return jsonify({
                'success': True,
                'mensaje': f'Estado de cita con ID {estado_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estado de cita con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar estado de cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
