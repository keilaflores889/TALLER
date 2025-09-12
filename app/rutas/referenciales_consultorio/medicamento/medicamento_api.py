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

    # Validación de campos
    required_fields = ['nombre_medicamento', 'dosis', 'indicaciones', 'forma_farmaceutica']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({'success': False, 'error': f'El campo {field} es obligatorio y no puede estar vacío.'}), 400

    nombre = data['nombre_medicamento'].strip()
    dosis = data['dosis'].strip()
    indicaciones = data['indicaciones'].strip()
    forma = data['forma_farmaceutica'].strip()

    try:
        # Verificar duplicado
        if dao.existeDuplicado(nombre, dosis, forma):
            return jsonify({'success': False, 'error': 'Ya está registrado este medicamento con esa dosis y forma farmacéutica.'}), 400

        id_medicamento = dao.guardarMedicamento(nombre, dosis, indicaciones, forma)
        if id_medicamento:
            return jsonify({'success': True, 'data': {
                'id_medicamento': id_medicamento,
                'nombre_medicamento': nombre,
                'dosis': dosis,
                'indicaciones': indicaciones,
                'forma_farmaceutica': forma
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

    required_fields = ['nombre_medicamento', 'dosis', 'indicaciones', 'forma_farmaceutica']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({'success': False, 'error': f'El campo {field} es obligatorio y no puede estar vacío.'}), 400

    nombre = data['nombre_medicamento'].strip()
    dosis = data['dosis'].strip()
    indicaciones = data['indicaciones'].strip()
    forma = data['forma_farmaceutica'].strip()

    try:
        medicamento_existente = dao.getMedicamentoById(id_medicamento)
        if not medicamento_existente:
            return jsonify({'success': False, 'error': 'No se encontró el medicamento con el ID proporcionado.'}), 404

        # Validar duplicados (excepto para el mismo registro)
        if dao.existeDuplicado(nombre, dosis, forma) and (
            medicamento_existente['nombre_medicamento'].upper() != nombre.upper() or
            medicamento_existente['dosis'].upper() != dosis.upper() or
            medicamento_existente['forma_farmaceutica'].upper() != forma.upper()
        ):
            return jsonify({'success': False, 'error': 'Ya existe otro medicamento con ese nombre, dosis y forma.'}), 400

        if dao.updateMedicamento(id_medicamento, nombre, dosis, indicaciones, forma):
            return jsonify({'success': True, 'data': {
                'id_medicamento': id_medicamento,
                'nombre_medicamento': nombre,
                'dosis': dosis,
                'indicaciones': indicaciones,
                'forma_farmaceutica': forma
            }, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo actualizar el medicamento.'}), 500
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
