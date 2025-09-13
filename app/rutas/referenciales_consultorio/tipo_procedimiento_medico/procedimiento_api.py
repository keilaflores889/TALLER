from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_procedimiento_medico.Tipo_Procedimiento_MedicoDao import TipoProcedimientoDao
import re

# Validaciones
def texto_valido(texto):
    return re.fullmatch(r'[A-Za-zÁÉÍÓÚÑáéíóúñ\s/]+', texto) is not None  # letras, espacios y "/"

procedimientoapi = Blueprint('procedimientoapi', __name__)

# Obtener todos los procedimientos
@procedimientoapi.route('/procedimientos', methods=['GET'])
def getProcedimientos():
    dao = TipoProcedimientoDao()
    try:
        procedimientos = dao.getTiposProcedimiento()
        return jsonify({'success': True, 'data': procedimientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los procedimientos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al listar procedimientos.'}), 500


# Obtener un procedimiento por ID
@procedimientoapi.route('/procedimientos/<int:id_procedimiento>', methods=['GET'])
def getProcedimiento(id_procedimiento):
    dao = TipoProcedimientoDao()
    try:
        procedimiento = dao.getTipoProcedimientoById(id_procedimiento)
        if procedimiento:
            return jsonify({'success': True, 'data': procedimiento, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el procedimiento con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al obtener el procedimiento.'}), 500


# Agregar un nuevo procedimiento
@procedimientoapi.route('/procedimientos', methods=['POST'])
def addProcedimiento():
    data = request.get_json()
    dao = TipoProcedimientoDao()

    procedimiento = data.get('procedimiento', '').strip()
    descripcion = data.get('descripcion', '').strip()
    duracion = data.get('duracion', '').strip()

    # Validaciones
    if not procedimiento:
        return jsonify({'success': False, 'error': 'El campo procedimiento es obligatorio.'}), 400
    if not texto_valido(procedimiento):
        return jsonify({'success': False, 'error': 'El procedimiento solo puede contener letras, espacios y "/"'}), 400

    if not descripcion:
        return jsonify({'success': False, 'error': 'El campo descripción es obligatorio.'}), 400

    if not duracion:
        return jsonify({'success': False, 'error': 'El campo duración es obligatorio.'}), 400

    try:
        if dao.procedimientoExiste(procedimiento):
            return jsonify({'success': False, 'error': f'El procedimiento "{procedimiento}" ya existe.'}), 409

        nuevo_id = dao.guardarTipoProcedimiento(procedimiento, descripcion, duracion)
        if nuevo_id:
            return jsonify({'success': True, 'data': {
                'id': nuevo_id,
                'procedimiento': procedimiento,
                'descripcion': descripcion,
                'duracion': duracion
            }, 'error': None}), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el procedimiento.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al guardar el procedimiento.'}), 500


# Actualizar un procedimiento
@procedimientoapi.route('/procedimientos/<int:id_procedimiento>', methods=['PUT'])
def updateProcedimiento(id_procedimiento):
    data = request.get_json()
    dao = TipoProcedimientoDao()

    procedimiento = data.get('procedimiento', '').strip()
    descripcion = data.get('descripcion', '').strip()
    duracion = data.get('duracion', '').strip()

    if not procedimiento:
        return jsonify({'success': False, 'error': 'El campo procedimiento es obligatorio.'}), 400
    if not texto_valido(procedimiento):
        return jsonify({'success': False, 'error': 'El procedimiento solo puede contener letras, espacios y "/"'}), 400
    if not descripcion:
        return jsonify({'success': False, 'error': 'El campo descripción es obligatorio.'}), 400
    if not duracion:
        return jsonify({'success': False, 'error': 'El campo duración es obligatorio.'}), 400

    try:
        actualizado = dao.updateTipoProcedimiento(id_procedimiento, procedimiento, descripcion, duracion)
        if actualizado:
            return jsonify({'success': True, 'data': {
                'id': id_procedimiento,
                'procedimiento': procedimiento,
                'descripcion': descripcion,
                'duracion': duracion
            }, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo actualizar el procedimiento.'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al actualizar el procedimiento.'}), 500


# Eliminar un procedimiento
@procedimientoapi.route('/procedimientos/<int:id_procedimiento>', methods=['DELETE'])
def deleteProcedimiento(id_procedimiento):
    dao = TipoProcedimientoDao()
    try:
        eliminado = dao.deleteTipoProcedimiento(id_procedimiento)
        if eliminado:
            return jsonify({'success': True, 'mensaje': f'Procedimiento con ID {id_procedimiento} eliminado correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el procedimiento o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al eliminar el procedimiento.'}), 500
