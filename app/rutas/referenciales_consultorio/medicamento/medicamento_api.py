from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales_consultorio.medicamento.MedicamentoDao import MedicamentoDao

medicamentoapi = Blueprint('medicamentoapi', __name__)

# Trae todos los medicamentos
@medicamentoapi.route('/medicamentos', methods=['GET'])
def getMedicamentos():
    dao = MedicamentoDao()
    try:
        medicamentos = dao.getMedicamentos()
        return jsonify({
            'success': True,
            'data': medicamentos,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener medicamentos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# Trae un medicamento por id
@medicamentoapi.route('/medicamentos/<int:id_medicamento>', methods=['GET'])
def getMedicamento(id_medicamento):
    dao = MedicamentoDao()
    try:
        medicamento = dao.getMedicamentoById(id_medicamento)
        if medicamento:
            return jsonify({'success': True, 'data': medicamento, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el medicamento con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener medicamento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# Agrega un nuevo medicamento
@medicamentoapi.route('/medicamentos', methods=['POST'])
def addMedicamento():
    data = request.get_json()
    dao = MedicamentoDao()

    nombre_medicamento = data.get('nombre_medicamento', '').strip()
    dosis = data.get('dosis', '').strip()
    indicaciones = data.get('indicaciones', '').strip()
    forma_farmaceutica = data.get('forma_farmaceutica', '').strip()

    # Validaciones de campos obligatorios
    if not nombre_medicamento:
        return jsonify({'success': False, 'error': 'El campo nombre del medicamento es obligatorio.'}), 400
    
    if not dosis:
        return jsonify({'success': False, 'error': 'El campo dosis es obligatorio.'}), 400
    
    if not indicaciones:
        return jsonify({'success': False, 'error': 'El campo indicaciones es obligatorio.'}), 400
    
    if not forma_farmaceutica:
        return jsonify({'success': False, 'error': 'El campo forma farmacéutica es obligatorio.'}), 400

    # Validaciones de formato usando el DAO
    if not dao.validarTexto(nombre_medicamento):
        return jsonify({'success': False, 'error': 'El nombre del medicamento solo puede contener letras, espacios y "/"'}), 400

    if not dao.validarPalabraConSentido(nombre_medicamento):
        return jsonify({'success': False, 'error': 'El nombre del medicamento debe contener palabras entendibles.'}), 400

    if not dao.validarDosis(dosis):
        return jsonify({'success': False, 'error': 'La dosis tiene un formato inválido. Use formatos como: 500mg, 2.5ml, 10%, etc.'}), 400

    # USAR validarIndicaciones EN LUGAR DE validarTexto
    if not dao.validarIndicaciones(indicaciones):
        return jsonify({'success': False, 'error': 'Las indicaciones contienen caracteres no permitidos.'}), 400

    if not dao.validarPalabraConSentido(indicaciones):
        return jsonify({'success': False, 'error': 'Las indicaciones deben contener palabras entendibles.'}), 400

    if not dao.validarTexto(forma_farmaceutica):
        return jsonify({'success': False, 'error': 'La forma farmacéutica solo puede contener letras, espacios y "/"'}), 400

    if not dao.validarPalabraConSentido(forma_farmaceutica):
        return jsonify({'success': False, 'error': 'La forma farmacéutica debe contener al menos una vocal.'}), 400

    # Validación de duplicados
    try:
        if dao.existeDuplicado(nombre_medicamento, dosis, forma_farmaceutica):
            return jsonify({'success': False, 'error': f'Ya está registrado el medicamento "{nombre_medicamento}" con la dosis "{dosis}" y forma "{forma_farmaceutica}".'}), 409

        id_medicamento = dao.guardarMedicamento(nombre_medicamento, dosis, indicaciones, forma_farmaceutica)
        if id_medicamento:
            return jsonify({'success': True, 'data': {
                'id_medicamento': id_medicamento,
                'nombre_medicamento': nombre_medicamento,
                'dosis': dosis,
                'indicaciones': indicaciones,
                'forma_farmaceutica': forma_farmaceutica
            }, 'error': None}), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el medicamento.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar medicamento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# Actualiza un medicamento
@medicamentoapi.route('/medicamentos/<int:id_medicamento>', methods=['PUT'])
def updateMedicamento(id_medicamento):
    data = request.get_json()
    dao = MedicamentoDao()

    nombre_medicamento = data.get('nombre_medicamento', '').strip()
    dosis = data.get('dosis', '').strip()
    indicaciones = data.get('indicaciones', '').strip()
    forma_farmaceutica = data.get('forma_farmaceutica', '').strip()

    # Validaciones de campos obligatorios
    if not nombre_medicamento:
        return jsonify({'success': False, 'error': 'El campo nombre del medicamento es obligatorio.'}), 400
    
    if not dosis:
        return jsonify({'success': False, 'error': 'El campo dosis es obligatorio.'}), 400
    
    if not indicaciones:
        return jsonify({'success': False, 'error': 'El campo indicaciones es obligatorio.'}), 400
    
    if not forma_farmaceutica:
        return jsonify({'success': False, 'error': 'El campo forma farmacéutica es obligatorio.'}), 400

    # Validaciones de formato usando el DAO
    if not dao.validarTexto(nombre_medicamento):
        return jsonify({'success': False, 'error': 'El nombre del medicamento solo puede contener letras, espacios y "/"'}), 400

    if not dao.validarPalabraConSentido(nombre_medicamento):
        return jsonify({'success': False, 'error': 'El nombre del medicamento debe contener palabras entendibles.'}), 400

    if not dao.validarDosis(dosis):
        return jsonify({'success': False, 'error': 'La dosis tiene un formato inválido. Use formatos como: 500mg, 2.5ml, 10%, etc.'}), 400

    # USAR validarIndicaciones EN LUGAR DE validarTexto
    if not dao.validarIndicaciones(indicaciones):
        return jsonify({'success': False, 'error': 'Las indicaciones contienen caracteres no permitidos.'}), 400

    if not dao.validarPalabraConSentido(indicaciones):
        return jsonify({'success': False, 'error': 'Las indicaciones deben contener al menos una vocal.'}), 400

    if not dao.validarTexto(forma_farmaceutica):
        return jsonify({'success': False, 'error': 'La forma farmacéutica solo puede contener letras, espacios y "/"'}), 400

    if not dao.validarPalabraConSentido(forma_farmaceutica):
        return jsonify({'success': False, 'error': 'La forma farmacéutica debe contener al menos una vocal.'}), 400

    # Validación de duplicados (excluyendo el registro actual)
    try:
        if dao.existeDuplicadoExceptoId(nombre_medicamento, dosis, forma_farmaceutica, id_medicamento):
            return jsonify({'success': False, 'error': f'Ya existe otro medicamento con el nombre "{nombre_medicamento}", dosis "{dosis}" y forma "{forma_farmaceutica}".'}), 409

        if dao.updateMedicamento(id_medicamento, nombre_medicamento, dosis, indicaciones, forma_farmaceutica):
            return jsonify({'success': True, 'data': {
                'id_medicamento': id_medicamento,
                'nombre_medicamento': nombre_medicamento,
                'dosis': dosis,
                'indicaciones': indicaciones,
                'forma_farmaceutica': forma_farmaceutica
            }, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el medicamento o no se pudo actualizar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar medicamento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# Elimina un medicamento
@medicamentoapi.route('/medicamentos/<int:id_medicamento>', methods=['DELETE'])
def deleteMedicamento(id_medicamento):
    dao = MedicamentoDao()
    try:
        if dao.deleteMedicamento(id_medicamento):
            return jsonify({'success': True, 'mensaje': f'Medicamento con ID {id_medicamento} eliminado correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el medicamento con el ID proporcionado o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar medicamento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500