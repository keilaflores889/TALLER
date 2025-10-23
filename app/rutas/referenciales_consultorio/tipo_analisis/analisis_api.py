from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_analisis.Tipo_AnalisisDao import TipoAnalisisDao

analisisapi = Blueprint('analisisapi', __name__)

# Trae todos los análisis
@analisisapi.route('/analisis', methods=['GET'])
def getAnalisis():
    dao = TipoAnalisisDao()
    try:
        analisis = dao.getTiposAnalisis()
        return jsonify({
            'success': True,
            'data': analisis,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Trae un análisis por ID
@analisisapi.route('/analisis/<int:id_analisis>', methods=['GET'])
def getAnalisisById(id_analisis):
    dao = TipoAnalisisDao()
    try:
        analisis = dao.getTipoAnalisisById(id_analisis)
        if analisis:
            return jsonify({
                'success': True,
                'data': analisis,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el análisis con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo análisis
@analisisapi.route('/analisis', methods=['POST'])
def addAnalisis():
    data = request.get_json()
    dao = TipoAnalisisDao()

    descripcion_analisis = data.get('descripcion_analisis', '').strip()

    # ===== VALIDACIÓN DE CAMPO OBLIGATORIO =====
    if not descripcion_analisis:
        return jsonify({
            'success': False,
            'error': 'El campo descripción del análisis es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(descripcion_analisis):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion_analisis):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener al menos una vocal.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS =====
    try:
        if dao.analisisExiste(descripcion_analisis):
            return jsonify({
                'success': False,
                'error': f'El tipo de análisis "{descripcion_analisis}" ya existe.'
            }), 409

        id_analisis = dao.guardarTipoAnalisis(descripcion_analisis)
        if id_analisis:
            return jsonify({
                'success': True,
                'data': {
                    'id_tipo_analisis': id_analisis,
                    'descripcion_analisis': descripcion_analisis
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de análisis.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Actualiza un análisis
@analisisapi.route('/analisis/<int:id_analisis>', methods=['PUT'])
def updateAnalisis(id_analisis):
    data = request.get_json()
    dao = TipoAnalisisDao()

    descripcion_analisis = data.get('descripcion_analisis', '').strip()

    # ===== VALIDACIÓN DE CAMPO OBLIGATORIO =====
    if not descripcion_analisis:
        return jsonify({
            'success': False,
            'error': 'El campo descripción del análisis es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(descripcion_analisis):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion_analisis):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener al menos una vocal.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS (excluyendo el registro actual) =====
    try:
        if dao.analisisExisteExceptoId(descripcion_analisis, id_analisis):
            return jsonify({
                'success': False,
                'error': f'Ya existe otro tipo de análisis con la descripción "{descripcion_analisis}".'
            }), 409

        if dao.updateTipoAnalisis(id_analisis, descripcion_analisis):
            return jsonify({
                'success': True,
                'data': {
                    'id_tipo_analisis': id_analisis,
                    'descripcion_analisis': descripcion_analisis
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de análisis o no se pudo actualizar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Elimina un análisis
@analisisapi.route('/analisis/<int:id_analisis>', methods=['DELETE'])
def deleteAnalisis(id_analisis):
    dao = TipoAnalisisDao()
    try:
        if dao.deleteTipoAnalisis(id_analisis):
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de análisis con ID {id_analisis} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de análisis con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500