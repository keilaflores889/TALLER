from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_estudio.Tipo_EstudioDao import TipoEstudioDao

estudioapi = Blueprint('estudioapi', __name__)

# Trae todos los estudios
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
        app.logger.error(f"Error al obtener todos los estudios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Trae un estudio por ID
@estudioapi.route('/estudios/<int:id_estudio>', methods=['GET'])
def getEstudioById(id_estudio):
    dao = TipoEstudioDao()
    try:
        estudio = dao.getTipoEstudioById(id_estudio)
        if estudio:
            return jsonify({
                'success': True,
                'data': estudio,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estudio con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo estudio
@estudioapi.route('/estudios', methods=['POST'])
def addEstudio():
    data = request.get_json()
    dao = TipoEstudioDao()

    descripcion_estudio = data.get('descripcion_estudio', '').strip()

    # ===== VALIDACIÓN DE CAMPO OBLIGATORIO =====
    if not descripcion_estudio:
        return jsonify({
            'success': False,
            'error': 'El campo descripción del estudio es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(descripcion_estudio):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion_estudio):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener al menos una vocal.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS =====
    try:
        if dao.estudioExiste(descripcion_estudio):
            return jsonify({
                'success': False,
                'error': f'El tipo de estudio "{descripcion_estudio}" ya existe.'
            }), 409

        id_estudio = dao.guardarTipoEstudio(descripcion_estudio)
        if id_estudio:
            return jsonify({
                'success': True,
                'data': {
                    'id_tipo_estudio': id_estudio,
                    'descripcion_estudio': descripcion_estudio
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de estudio.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Actualiza un estudio
@estudioapi.route('/estudios/<int:id_estudio>', methods=['PUT'])
def updateEstudio(id_estudio):
    data = request.get_json()
    dao = TipoEstudioDao()

    descripcion_estudio = data.get('descripcion_estudio', '').strip()

    # ===== VALIDACIÓN DE CAMPO OBLIGATORIO =====
    if not descripcion_estudio:
        return jsonify({
            'success': False,
            'error': 'El campo descripción del estudio es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(descripcion_estudio):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion_estudio):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener al menos una vocal.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS (excluyendo el registro actual) =====
    try:
        if dao.estudioExisteExceptoId(descripcion_estudio, id_estudio):
            return jsonify({
                'success': False,
                'error': f'Ya existe otro tipo de estudio con la descripción "{descripcion_estudio}".'
            }), 409

        if dao.updateTipoEstudio(id_estudio, descripcion_estudio):
            return jsonify({
                'success': True,
                'data': {
                    'id_tipo_estudio': id_estudio,
                    'descripcion_estudio': descripcion_estudio
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de estudio o no se pudo actualizar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Elimina un estudio
@estudioapi.route('/estudios/<int:id_estudio>', methods=['DELETE'])
def deleteEstudio(id_estudio):
    dao = TipoEstudioDao()
    try:
        if dao.deleteTipoEstudio(id_estudio):
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de estudio con ID {id_estudio} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de estudio con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500