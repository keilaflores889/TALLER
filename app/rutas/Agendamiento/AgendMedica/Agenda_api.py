from flask import Blueprint, request, jsonify, current_app as app
from app.dao.AgendMedica.AgendaDao import AgendaDao

agendaapi = Blueprint('agendaapi', __name__)

# Obtener todas las agendas médicas
@agendaapi.route('/Agenda', methods=['GET'])
def getAgendas():
    agendadao = AgendaDao()
    try:
        agendas = agendadao.getAgendas()
        return jsonify({
            'success': True,
            'data': agendas,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas las agendas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar las agendas. Consulte con el administrador.'
        }), 500


# Obtener una agenda específica por ID
@agendaapi.route('/Agenda/<int:agenda_medica_id>', methods=['GET'])
def getAgenda(agenda_medica_id):
    agendadao = AgendaDao()
    try:
        agenda = agendadao.getAgendaById(agenda_medica_id)
        if agenda:
            return jsonify({
                'success': True,
                'data': agenda,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la agenda con el ID {agenda_medica_id}.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener agenda con ID {agenda_medica_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al consultar la agenda. Consulte con el administrador.'
        }), 500


# Agregar una nueva agenda
@agendaapi.route('/Agenda', methods=['POST'])
def addAgenda():
    data = request.get_json()
    agendadao = AgendaDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre_medico', 'dia', 'turno']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo].strip():
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vacía.'
            }), 400

    try:
        nombre_medico = data['nombre_medico'].strip()
        dia = data['dia'].strip()
        turno = data['turno'].strip()

        agenda_medica_id = agendadao.guardarAgenda(nombre_medico, dia, turno)
        if agenda_medica_id:
            app.logger.info(f"Agenda médica creada con ID {agenda_medica_id}.")
            return jsonify({
                'success': True,
                'data': {'id_agenda_medica': agenda_medica_id, 'nombre_medico': nombre_medico, 'dia': dia, 'turno': turno},
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar la agenda. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar agenda: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al guardar la agenda. Consulte con el administrador.'
        }), 500


# Actualizar una agenda existente
@agendaapi.route('/Agenda/<int:agenda_medica_id>', methods=['PUT'])
def updateAgenda(agenda_medica_id):
    data = request.get_json()
    agendadao = AgendaDao()

    # Validar campos requeridos
    campos_requeridos = ['nombre_medico', 'dia', 'turno']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo].strip():
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vacía.'
            }), 400

    try:
        nombre_medico = data['nombre_medico'].strip()
        dia = data['dia'].strip()
        turno = data['turno'].strip()

        if agendadao.updateAgenda(agenda_medica_id, nombre_medico, dia, turno):
            app.logger.info(f"Agenda médica con ID {agenda_medica_id} actualizada exitosamente.")
            return jsonify({
                'success': True,
                'data': {'id_agenda_medica': agenda_medica_id, 'nombre_medico': nombre_medico, 'dia': dia, 'turno': turno},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la agenda con el ID {agenda_medica_id} o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar agenda con ID {agenda_medica_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al actualizar la agenda. Consulte con el administrador.'
        }), 500


# Eliminar una agenda
@agendaapi.route('/Agenda/<int:agenda_medica_id>', methods=['DELETE'])
def deleteAgenda(agenda_medica_id):
    agendadao = AgendaDao()
    try:
        if agendadao.deleteAgenda(agenda_medica_id):
            app.logger.info(f"Agenda médica con ID {agenda_medica_id} eliminada.")
            return jsonify({
                'success': True,
                'mensaje': f'Agenda con ID {agenda_medica_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontró la agenda con el ID {agenda_medica_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar agenda con ID {agenda_medica_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno al eliminar la agenda. Consulte con el administrador.'
        }), 500
