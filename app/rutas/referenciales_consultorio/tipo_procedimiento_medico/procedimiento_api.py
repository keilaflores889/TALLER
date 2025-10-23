from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_procedimiento_medico.Tipo_Procedimiento_MedicoDao import TipoProcedimientoDao

procedimientoapi = Blueprint('procedimientoapi', __name__)

# Trae todos los procedimientos
@procedimientoapi.route('/procedimientos', methods=['GET'])
def getProcedimientos():
    dao = TipoProcedimientoDao()
    try:
        procedimientos = dao.getTiposProcedimiento()
        return jsonify({
            'success': True,
            'data': procedimientos,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los procedimientos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Trae un procedimiento por ID
@procedimientoapi.route('/procedimientos/<int:id_procedimiento>', methods=['GET'])
def getProcedimientoById(id_procedimiento):
    dao = TipoProcedimientoDao()
    try:
        procedimiento = dao.getTipoProcedimientoById(id_procedimiento)
        if procedimiento:
            return jsonify({
                'success': True,
                'data': procedimiento,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el procedimiento con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo procedimiento
@procedimientoapi.route('/procedimientos', methods=['POST'])
def addProcedimiento():
    data = request.get_json()
    dao = TipoProcedimientoDao()

    procedimiento = data.get('procedimiento', '').strip()
    descripcion = data.get('descripcion', '').strip()
    duracion = data.get('duracion', '').strip()

    # ===== VALIDACIÓN DE CAMPOS OBLIGATORIOS =====
    if not procedimiento:
        return jsonify({
            'success': False,
            'error': 'El campo procedimiento es obligatorio.'
        }), 400

    if not descripcion:
        return jsonify({
            'success': False,
            'error': 'El campo descripción es obligatorio.'
        }), 400

    if not duracion:
        return jsonify({
            'success': False,
            'error': 'El campo duración es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(procedimiento):
        return jsonify({
            'success': False,
            'error': 'El procedimiento solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(procedimiento):
        return jsonify({
            'success': False,
            'error': 'El procedimiento debe contener al menos una vocal.'
        }), 400

    if not dao.validarTexto(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener al menos una vocal.'
        }), 400

    if not dao.validarTexto(duracion):
        return jsonify({
            'success': False,
            'error': 'La duración solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS =====
    try:
        if dao.procedimientoExiste(procedimiento):
            return jsonify({
                'success': False,
                'error': f'El procedimiento "{procedimiento}" ya existe.'
            }), 409

        id_procedimiento = dao.guardarTipoProcedimiento(procedimiento, descripcion, duracion)
        if id_procedimiento:
            return jsonify({
                'success': True,
                'data': {
                    'id_tipo_procedimiento': id_procedimiento,
                    'procedimiento': procedimiento,
                    'descripcion': descripcion,
                    'duracion': duracion
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de procedimiento.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Actualiza un procedimiento
@procedimientoapi.route('/procedimientos/<int:id_procedimiento>', methods=['PUT'])
def updateProcedimiento(id_procedimiento):
    data = request.get_json()
    dao = TipoProcedimientoDao()

    procedimiento = data.get('procedimiento', '').strip()
    descripcion = data.get('descripcion', '').strip()
    duracion = data.get('duracion', '').strip()

    # ===== VALIDACIÓN DE CAMPOS OBLIGATORIOS =====
    if not procedimiento:
        return jsonify({
            'success': False,
            'error': 'El campo procedimiento es obligatorio.'
        }), 400

    if not descripcion:
        return jsonify({
            'success': False,
            'error': 'El campo descripción es obligatorio.'
        }), 400

    if not duracion:
        return jsonify({
            'success': False,
            'error': 'El campo duración es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(procedimiento):
        return jsonify({
            'success': False,
            'error': 'El procedimiento solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(procedimiento):
        return jsonify({
            'success': False,
            'error': 'El procedimiento debe contener al menos una vocal.'
        }), 400

    if not dao.validarTexto(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener al menos una vocal.'
        }), 400

    if not dao.validarTexto(duracion):
        return jsonify({
            'success': False,
            'error': 'La duración solo puede contener letras, números, espacios, guiones, barras, comas y puntos.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS (excluyendo el registro actual) =====
    try:
        if dao.procedimientoExisteExceptoId(procedimiento, id_procedimiento):
            return jsonify({
                'success': False,
                'error': f'Ya existe otro procedimiento con el nombre "{procedimiento}".'
            }), 409

        if dao.updateTipoProcedimiento(id_procedimiento, procedimiento, descripcion, duracion):
            return jsonify({
                'success': True,
                'data': {
                    'id_tipo_procedimiento': id_procedimiento,
                    'procedimiento': procedimiento,
                    'descripcion': descripcion,
                    'duracion': duracion
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de procedimiento o no se pudo actualizar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Elimina un procedimiento
@procedimientoapi.route('/procedimientos/<int:id_procedimiento>', methods=['DELETE'])
def deleteProcedimiento(id_procedimiento):
    dao = TipoProcedimientoDao()
    try:
        if dao.deleteTipoProcedimiento(id_procedimiento):
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de procedimiento con ID {id_procedimiento} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de procedimiento con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500