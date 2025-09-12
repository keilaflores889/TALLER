from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_analisis.Tipo_AnalisisDao import TipoAnalisisDao
import re

def descripcion_valida(texto):
    return re.fullmatch(r'[A-Za-z0-9ÁÉÍÓÚÑáéíóúñ\s]+', texto) is not None

analisisapi = Blueprint('analisisapi', __name__)
def descripcion_valida(texto):
    # Acepta letras, números, espacios, acentos, "/" y "-"
    return re.fullmatch(r'[A-Za-z0-9ÁÉÍÓÚÑáéíóúñ\s/-]+', texto) is not None

# Trae todos los análisis
@analisisapi.route('/analisis', methods=['GET'])
def getAnalisis():
    dao = TipoAnalisisDao()
    try:
        analisis = dao.getTiposAnalisis()
        return jsonify({'success': True, 'data': analisis, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los análisis: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500

# Trae un análisis por ID
@analisisapi.route('/analisis/<int:id_analisis>', methods=['GET'])
def getAnalisisById(id_analisis):
    dao = TipoAnalisisDao()
    try:
        analisis = dao.getTipoAnalisisById(id_analisis)
        if analisis:
            return jsonify({'success': True, 'data': analisis, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el análisis con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener análisis: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500

# Agrega un nuevo análisis
@analisisapi.route('/analisis', methods=['POST'])
def addAnalisis():
    data = request.get_json()
    dao = TipoAnalisisDao()

    if 'analisis_des' not in data or not data['analisis_des'].strip():
        return jsonify({'success': False, 'error': 'El campo analisis_des es obligatorio.'}), 400

    descripcion = data['analisis_des'].strip().upper()
    if not descripcion_valida(descripcion):
        return jsonify({'success': False, 'error': 'La descripción solo puede contener letras, números y espacios.'}), 400

    try:
        if dao.analisisExiste(descripcion):
            return jsonify({'success': False, 'error': f'El análisis "{descripcion}" ya existe.'}), 409

        id_analisis = dao.guardarTipoAnalisis(descripcion)
        if id_analisis:
            return jsonify({'success': True, 'data': {'id_analisis': id_analisis, 'analisis_des': descripcion}, 'error': None}), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el análisis.'}), 500

    except Exception as e:
        app.logger.error(f"Error al agregar análisis: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500

# Actualiza un análisis
@analisisapi.route('/analisis/<int:id_analisis>', methods=['PUT'])
def updateAnalisis(id_analisis):
    data = request.get_json()
    dao = TipoAnalisisDao()

    if 'analisis_des' not in data or not data['analisis_des'].strip():
        return jsonify({'success': False, 'error': 'El campo analisis_des es obligatorio.'}), 400

    descripcion = data['analisis_des'].strip().upper()
    if not descripcion_valida(descripcion):
        return jsonify({'success': False, 'error': 'La descripción solo puede contener letras, números y espacios.'}), 400

    try:
        # Actualiza solo si no existe duplicado en otro registro
        if dao.updateTipoAnalisis(id_analisis, descripcion):
            return jsonify({'success': True, 'data': {'id_analisis': id_analisis, 'analisis_des': descripcion}, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'La descripción del análisis ya existe o no se pudo actualizar.'}), 409

    except Exception as e:
        app.logger.error(f"Error al actualizar análisis: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500

# Elimina un análisis
@analisisapi.route('/analisis/<int:id_analisis>', methods=['DELETE'])
def deleteAnalisis(id_analisis):
    dao = TipoAnalisisDao()
    try:
        if dao.deleteTipoAnalisis(id_analisis):
            return jsonify({'success': True, 'mensaje': f'Análisis con ID {id_analisis} eliminado correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el análisis con el ID proporcionado o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar análisis: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500
