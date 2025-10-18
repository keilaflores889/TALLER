from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.sintomas.SintomasDao import SintomaDao

sintomaapi = Blueprint('sintomaapi', __name__)

# Trae todos los síntomas
@sintomaapi.route('/sintomas', methods=['GET'])
def getSintomas():
    dao = SintomaDao()
    try:
        sintomas = dao.getSintomas()
        return jsonify({
            'success': True,
            'data': sintomas,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los síntomas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Trae un síntoma por ID
@sintomaapi.route('/sintomas/<int:id_sintoma>', methods=['GET'])
def getSintoma(id_sintoma):
    dao = SintomaDao()
    try:
        sintoma = dao.getSintomaById(id_sintoma)
        if sintoma:
            return jsonify({
                'success': True,
                'data': sintoma,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el síntoma con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo síntoma
@sintomaapi.route('/sintomas', methods=['POST'])
def addSintoma():
    data = request.get_json()
    dao = SintomaDao()

    descripcion_sintoma = data.get('descripcion_sintoma', '').strip()

    # ===== VALIDACIÓN DE CAMPO OBLIGATORIO =====
    if not descripcion_sintoma:
        return jsonify({
            'success': False,
            'error': 'El campo descripción del síntoma es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(descripcion_sintoma):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, espacios, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion_sintoma):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener palabras entendibles.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS =====
    try:
        if dao.sintomaExiste(descripcion_sintoma):
            return jsonify({
                'success': False,
                'error': f'El síntoma "{descripcion_sintoma}" ya existe.'
            }), 409

        id_sintoma = dao.guardarSintoma(descripcion_sintoma)
        if id_sintoma:
            return jsonify({
                'success': True,
                'data': {
                    'id_sintoma': id_sintoma,
                    'descripcion_sintoma': descripcion_sintoma
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el síntoma.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Actualiza un síntoma
@sintomaapi.route('/sintomas/<int:id_sintoma>', methods=['PUT'])
def updateSintoma(id_sintoma):
    data = request.get_json()
    dao = SintomaDao()

    descripcion_sintoma = data.get('descripcion_sintoma', '').strip()

    # ===== VALIDACIÓN DE CAMPO OBLIGATORIO =====
    if not descripcion_sintoma:
        return jsonify({
            'success': False,
            'error': 'El campo descripción del síntoma es obligatorio.'
        }), 400

    # ===== VALIDACIONES DE FORMATO =====
    if not dao.validarTexto(descripcion_sintoma):
        return jsonify({
            'success': False,
            'error': 'La descripción solo puede contener letras, espacios, comas y puntos.'
        }), 400

    if not dao.validarPalabraConSentido(descripcion_sintoma):
        return jsonify({
            'success': False,
            'error': 'La descripción debe contener palabras entendibles.'
        }), 400

    # ===== VALIDACIÓN DE DUPLICADOS (excluyendo el registro actual) =====
    try:
        if dao.sintomaExisteExceptoId(descripcion_sintoma, id_sintoma):
            return jsonify({
                'success': False,
                'error': f'Ya existe otro síntoma con la descripción "{descripcion_sintoma}".'
            }), 409

        if dao.updateSintoma(id_sintoma, descripcion_sintoma):
            return jsonify({
                'success': True,
                'data': {
                    'id_sintoma': id_sintoma,
                    'descripcion_sintoma': descripcion_sintoma
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el síntoma o no se pudo actualizar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Elimina un síntoma
@sintomaapi.route('/sintomas/<int:id_sintoma>', methods=['DELETE'])
def deleteSintoma(id_sintoma):
    dao = SintomaDao()
    try:
        if dao.deleteSintoma(id_sintoma):
            return jsonify({
                'success': True,
                'mensaje': f'Síntoma con ID {id_sintoma} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el síntoma con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500