from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.tipo_diagnostico.TipoDiagnosticoDao import TipoDiagnosticoDao

diagnosticoapi = Blueprint('diagnosticoapi', __name__)

# Obtener todos los diagnósticos
@diagnosticoapi.route('/diagnosticos', methods=['GET'])
def getDiagnosticos():
    dao = TipoDiagnosticoDao()
    try:
        diagnosticos = dao.getTiposDiagnostico()
        return jsonify({'success': True, 'data': diagnosticos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los diagnósticos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al listar diagnósticos.'}), 500


# Obtener un diagnóstico por ID
@diagnosticoapi.route('/diagnosticos/<int:id_tipo_diagnostico>', methods=['GET'])
def getDiagnostico(id_tipo_diagnostico):
    dao = TipoDiagnosticoDao()
    try:
        diagnostico = dao.getTipoDiagnosticoById(id_tipo_diagnostico)
        if diagnostico:
            return jsonify({'success': True, 'data': diagnostico, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el diagnóstico con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al obtener el diagnóstico.'}), 500


# Agregar un nuevo diagnóstico
@diagnosticoapi.route('/diagnosticos', methods=['POST'])
def addDiagnostico():
    data = request.get_json()
    dao = TipoDiagnosticoDao()

    descripcion_diagnostico = data.get('descripcion_diagnostico', '').strip()
    tipo_diagnostico = data.get('tipo_diagnostico', '').strip()

    # Validaciones de campos obligatorios
    if not descripcion_diagnostico:
        return jsonify({'success': False, 'error': 'El campo descripción es obligatorio.'}), 400
    
    if not tipo_diagnostico:
        return jsonify({'success': False, 'error': 'El campo tipo diagnóstico es obligatorio.'}), 400

    # Validaciones de formato usando el DAO
    if not dao.validarTexto(descripcion_diagnostico):
        return jsonify({'success': False, 'error': 'La descripción solo puede contener letras, espacios y "/"'}), 400

    if not dao.validarTexto(tipo_diagnostico):
        return jsonify({'success': False, 'error': 'El tipo diagnóstico solo puede contener letras, espacios y "/"'}), 400


    # Validaciones de formato usando el DAO
    if not dao.validarTexto(descripcion_diagnostico):
        return jsonify({'success': False, 'error': 'La descripción solo puede contener letras, espacios y "/"'}), 400

    # 👇 AGREGAR AQUÍ
    if not dao.validarPalabraConSentido(descripcion_diagnostico):
        return jsonify({'success': False, 'error': 'La descripción debe contener palabras entendibles.'}), 400

    if not dao.validarTexto(tipo_diagnostico):
        return jsonify({'success': False, 'error': 'El tipo diagnóstico solo puede contener letras, espacios y "/"'}), 400

    # 👇 AGREGAR AQUÍ
    if not dao.validarPalabraConSentido(tipo_diagnostico):
        return jsonify({'success': False, 'error': 'El tipo diagnóstico debe contener al menos una vocal.'}), 400

    # Validación de duplicados
    try:
        if dao.diagnosticoExiste(descripcion_diagnostico):
            return jsonify({'success': False, 'error': f'El diagnóstico "{descripcion_diagnostico}" ya existe.'}), 409

        nuevo_id = dao.guardarTipoDiagnostico(descripcion_diagnostico, tipo_diagnostico)
        if nuevo_id:
            return jsonify({'success': True, 'data': {
                'id_tipo_diagnostico': nuevo_id,
                'descripcion_diagnostico': descripcion_diagnostico,
                'tipo_diagnostico': tipo_diagnostico
            }, 'error': None}), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el diagnóstico.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al guardar el diagnóstico.'}), 500


# Actualizar un diagnóstico
@diagnosticoapi.route('/diagnosticos/<int:id_tipo_diagnostico>', methods=['PUT'])
def updateDiagnostico(id_tipo_diagnostico):
    data = request.get_json()
    dao = TipoDiagnosticoDao()

    descripcion_diagnostico = data.get('descripcion_diagnostico', '').strip()
    tipo_diagnostico = data.get('tipo_diagnostico', '').strip()

    # Validaciones de campos obligatorios
    if not descripcion_diagnostico:
        return jsonify({'success': False, 'error': 'El campo descripción es obligatorio.'}), 400
    
    if not tipo_diagnostico:
        return jsonify({'success': False, 'error': 'El campo tipo diagnóstico es obligatorio.'}), 400

    # Validaciones de formato usando el DAO
    if not dao.validarTexto(descripcion_diagnostico):
        return jsonify({'success': False, 'error': 'La descripción solo puede contener letras, espacios y "/"'}), 400

    if not dao.validarTexto(tipo_diagnostico):
        return jsonify({'success': False, 'error': 'El tipo diagnóstico solo puede contener letras, espacios y "/"'}), 400


        # Validaciones de formato usando el DAO
    if not dao.validarTexto(descripcion_diagnostico):
        return jsonify({'success': False, 'error': 'La descripción solo puede contener letras, espacios y "/"'}), 400

    # 👇 AGREGAR AQUÍ
    if not dao.validarPalabraConSentido(descripcion_diagnostico):
        return jsonify({'success': False, 'error': 'La descripción debe contener palabras entendibles.'}), 400

    if not dao.validarTexto(tipo_diagnostico):
        return jsonify({'success': False, 'error': 'El tipo diagnóstico solo puede contener letras, espacios y "/"'}), 400

    # 👇 AGREGAR AQUÍ
    if not dao.validarPalabraConSentido(tipo_diagnostico):
        return jsonify({'success': False, 'error': 'El tipo diagnóstico debe contener al menos una vocal.'}), 400

    # Validación de duplicados (excluyendo el registro actual)
    try:
        if dao.diagnosticoExisteExceptoId(descripcion_diagnostico, id_tipo_diagnostico):
            return jsonify({'success': False, 'error': f'Ya existe otro diagnóstico con la descripción "{descripcion_diagnostico}".'}), 409

        actualizado = dao.updateTipoDiagnostico(id_tipo_diagnostico, descripcion_diagnostico, tipo_diagnostico)
        if actualizado:
            return jsonify({'success': True, 'data': {
                'id_tipo_diagnostico': id_tipo_diagnostico,
                'descripcion_diagnostico': descripcion_diagnostico,
                'tipo_diagnostico': tipo_diagnostico
            }, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el diagnóstico o no se pudo actualizar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al actualizar el diagnóstico.'}), 500


# Eliminar un diagnóstico
@diagnosticoapi.route('/diagnosticos/<int:id_tipo_diagnostico>', methods=['DELETE'])
def deleteDiagnostico(id_tipo_diagnostico):
    dao = TipoDiagnosticoDao()
    try:
        eliminado = dao.deleteTipoDiagnostico(id_tipo_diagnostico)
        if eliminado:
            return jsonify({'success': True, 'mensaje': f'Diagnóstico con ID {id_tipo_diagnostico} eliminado correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el diagnóstico o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al eliminar el diagnóstico.'}), 500