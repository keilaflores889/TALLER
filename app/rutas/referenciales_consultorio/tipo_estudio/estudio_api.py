from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_estudio.Tipo_EstudioDao import TipoEstudioDao
import re

# ✅ Validación: letras, números, espacios y "/"
def descripcion_valida(texto):
    return re.fullmatch(r'[A-Za-z0-9ÁÉÍÓÚÑáéíóúñ\s/]+', texto) is not None

estudioapi = Blueprint('estudioapi', __name__)

# ===============================
# Obtener todos los estudios
# ===============================
@estudioapi.route('/estudios', methods=['GET'])
def getEstudios():
    dao = TipoEstudioDao()
    try:
        estudios = dao.getTiposEstudio()
        return jsonify({
            'success': True,
            'data': estudios,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener estudios: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# Obtener estudio por ID
# ===============================
@estudioapi.route('/estudios/<int:estudio_id>', methods=['GET'])
def getEstudio(estudio_id):
    dao = TipoEstudioDao()
    try:
        estudio = dao.getTipoEstudioById(estudio_id)
        if estudio:
            return jsonify({'success': True, 'data': estudio, 'error': None}), 200
        return jsonify({'success': False, 'error': 'Estudio no encontrado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener estudio por ID: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# Agregar nuevo estudio
# ===============================
@estudioapi.route('/estudios', methods=['POST'])
def addEstudio():
    data = request.get_json()
    dao = TipoEstudioDao()

    if 'descripcion' not in data or not data['descripcion'].strip():
        return jsonify({'success': False, 'error': 'El campo descripción es obligatorio.'}), 400

    descripcion = data['descripcion'].strip()
    if not descripcion_valida(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios y "/".'
        }), 400

    try:
        if dao.estudioExiste(descripcion):
            return jsonify({
                'success': False,
                'error': f'El estudio "{descripcion}" ya existe.'
            }), 409

        id_estudio = dao.guardarTipoEstudio(descripcion)
        if id_estudio:
            return jsonify({
                'success': True,
                'data': {'id_tipo_estudio': id_estudio, 'descripcion_estudio': descripcion},
                'error': None
            }), 201
        return jsonify({'success': False, 'error': 'No se pudo guardar el estudio.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar estudio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# Actualizar estudio
# ===============================
@estudioapi.route('/estudios/<int:estudio_id>', methods=['PUT'])
def updateEstudio(estudio_id):
    data = request.get_json()
    dao = TipoEstudioDao()

    if 'descripcion' not in data or not data['descripcion'].strip():
        return jsonify({'success': False, 'error': 'El campo descripción es obligatorio.'}), 400

    descripcion = data['descripcion'].strip()
    if not descripcion_valida(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios y "/".'
        }), 400

    try:
        if dao.updateTipoEstudio(estudio_id, descripcion):
            return jsonify({
                'success': True,
                'data': {'id_tipo_estudio': estudio_id, 'descripcion_estudio': descripcion},
                'error': None
            }), 200
        return jsonify({'success': False, 'error': 'No se pudo actualizar el estudio.'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar estudio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===============================
# Eliminar estudio
# ===============================
@estudioapi.route('/estudios/<int:estudio_id>', methods=['DELETE'])
def deleteEstudio(estudio_id):
    dao = TipoEstudioDao()
    try:
        if dao.deleteTipoEstudio(estudio_id):
            return jsonify({
                'success': True,
                'mensaje': f'Estudio con ID {estudio_id} eliminado correctamente.',
                'error': None
            }), 200
        return jsonify({'success': False, 'error': 'Estudio no encontrado o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar estudio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
