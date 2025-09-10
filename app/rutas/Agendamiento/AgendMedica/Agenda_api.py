from flask import Blueprint, jsonify, request, current_app as app
from datetime import datetime
from app.dao.agendmedica.AgendaDao import AgendaDao
from app.dao.referenciales.disponibilidad_horaria.DisponibilidadHorariaDao import DisponibilidadDao

agendaapi = Blueprint('agendaapi', __name__)

# ==============================
#   Obtener todas las agendas
# ==============================
@agendaapi.route('/agenda', methods=['GET'])
def getAgendas():
    agendadao = AgendaDao()
    try:
        agendas = agendadao.getAgendas()
        return jsonify({'success': True, 'data': agendas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener agendas: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar las agendas. Consulte con el administrador."), 500

# ==============================
#   Obtener agenda por ID
# ==============================
@agendaapi.route('/agenda/<int:agenda_id>', methods=['GET'])
def getAgenda(agenda_id):
    agendadao = AgendaDao()
    try:
        agenda = agendadao.getAgendaById(agenda_id)
        if agenda:
            return jsonify(success=True, data=agenda, error=None), 200
        return jsonify(success=False,
                       error=f"No se encontró la agenda con el ID {agenda_id}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener agenda con ID {agenda_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al consultar la agenda. Consulte con el administrador."), 500

# ==============================
#   Agregar nueva agenda
# ==============================
@agendaapi.route('/agenda', methods=['POST'])
def addAgenda():
    data = request.get_json() or {}
    agendadao = AgendaDao()

    campos_requeridos = [
        'id_medico', 'id_dia', 'id_turno', 'codigo',
        'id_personal', 'id_especialidad', 'fecha_agenda'
    ]

    faltantes = [campo for campo in campos_requeridos
                 if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip())]

    if faltantes:
        return jsonify(success=False,
                       error=f"Faltan campos obligatorios: {', '.join(faltantes)}"), 400

    # Resolver horario si viene id_disponibilidad
    horario = data.get('horario_disponible')
    if not horario:
        id_disp = data.get('id_disponibilidad')
        if id_disp:
            try:
                id_disp = int(id_disp)
            except Exception:
                return jsonify(success=False, error="id_disponibilidad inválido"), 400
            dispdao = DisponibilidadDao()
            disp = dispdao.getDisponibilidadById(id_disp)
            if not disp:
                return jsonify(success=False, error="No se encontró la disponibilidad indicada"), 400

            hi = str(disp.get('disponibilidad_hora_inicio') or '').split('.')[0]
            hf = str(disp.get('disponibilidad_hora_fin') or '').split('.')[0]
            if ':' in hi:
                parts = hi.split(':'); hi = f"{parts[0]}:{parts[1]}"
            if ':' in hf:
                parts = hf.split(':'); hf = f"{parts[0]}:{parts[1]}"
            horario = f"{hi} - {hf}"
            data['horario_disponible'] = horario
            if not data.get('cupos'):
                data['cupos'] = disp.get('disponibilidad_cupos', 0)
        else:
            return jsonify(success=False,
                           error="Faltan campos obligatorios: horario_disponible o id_disponibilidad"), 400

    # Chequeo de duplicado con fecha y horario
    try:
        if agendadao.existeDuplicado(
            data['id_medico'], data['id_dia'], data['id_turno'], data['codigo'],
            fecha_agenda=data.get('fecha_agenda'), horario_disponible=data.get('horario_disponible')
        ):
            return jsonify(success=False,
                           error="Ya existe una agenda para este médico en el mismo día, turno, consultorio y horario."), 409

        agenda_id = agendadao.addAgenda(data)
        if agenda_id:
            app.logger.info(f"Agenda creada con ID {agenda_id}.")
            return jsonify(success=True,
                           data={**data, 'id_agenda_medica': agenda_id},
                           error=None), 201
        else:
            return jsonify(success=False,
                           error="No se pudo guardar la agenda. Consulte con el administrador."), 500

    except Exception as e:
        app.logger.error(f"Error al agregar agenda: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al guardar la agenda. Consulte con el administrador."), 500

# ==============================
#   Actualizar agenda existente
# ==============================
@agendaapi.route('/agenda/<int:agenda_id>', methods=['PUT'])
def updateAgenda(agenda_id):
    data = request.get_json() or {}
    agendadao = AgendaDao()

    campos_requeridos = ['id_medico', 'id_dia', 'id_turno', 'codigo',
                         'id_personal', 'id_especialidad', 'fecha_agenda']

    faltantes = [campo for campo in campos_requeridos
                 if not data.get(campo) or (isinstance(data[campo], str) and not data[campo].strip())]

    if faltantes:
        return jsonify(success=False,
                       error=f"Faltan campos obligatorios: {', '.join(faltantes)}"), 400

    horario = data.get('horario_disponible')
    if not horario and data.get('id_disponibilidad'):
        try:
            id_disp = int(data.get('id_disponibilidad'))
        except Exception:
            return jsonify(success=False, error="id_disponibilidad inválido"), 400
        disp = DisponibilidadDao().getDisponibilidadById(id_disp)
        if not disp:
            return jsonify(success=False, error="No se encontró la disponibilidad indicada"), 400
        hi = str(disp.get('disponibilidad_hora_inicio') or '').split('.')[0]
        hf = str(disp.get('disponibilidad_hora_fin') or '').split('.')[0]
        if ':' in hi:
            parts = hi.split(':'); hi = f"{parts[0]}:{parts[1]}"
        if ':' in hf:
            parts = hf.split(':'); hf = f"{parts[0]}:{parts[1]}"
        data['horario_disponible'] = f"{hi} - {hf}"
        if not data.get('cupos'):
            data['cupos'] = disp.get('disponibilidad_cupos', 0)

    try:
        if agendadao.existeDuplicado(
            data['id_medico'], data['id_dia'], data['id_turno'], data['codigo'],
            fecha_agenda=data.get('fecha_agenda'), horario_disponible=data.get('horario_disponible'),
            id_agenda=agenda_id
        ):
            return jsonify(success=False,
                           error="Ya existe otra agenda para este médico en el mismo día, turno, consultorio y horario."), 409

        actualizado = agendadao.updateAgenda(agenda_id, data)
        if actualizado:
            app.logger.info(f"Agenda con ID {agenda_id} actualizada exitosamente.")
            return jsonify(success=True,
                           data={**data, 'id_agenda_medica': agenda_id},
                           error=None), 200
        else:
            return jsonify(success=False,
                           error=f"No se encontró la agenda con el ID {agenda_id} o no se pudo actualizar."), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar agenda con ID {agenda_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al actualizar la agenda. Consulte con el administrador."), 500

# ==============================
#   Eliminar agenda
# ==============================
@agendaapi.route('/agenda/<int:agenda_id>', methods=['DELETE'])
def deleteAgenda(agenda_id):
    agendadao = AgendaDao()
    try:
        if agendadao.deleteAgenda(agenda_id):
            app.logger.info(f"Agenda con ID {agenda_id} eliminada.")
            return jsonify(success=True,
                           data=f"Agenda con ID {agenda_id} eliminada correctamente.",
                           error=None), 200
        else:
            return jsonify(success=False,
                           error=f"No se encontró la agenda con el ID {agenda_id} o no se pudo eliminar."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar agenda con ID {agenda_id}: {str(e)}")
        return jsonify(success=False,
                       error="Ocurrió un error interno al eliminar la agenda. Consulte con el administrador."), 500

# ==============================
#   Obtener disponibilidades por médico y fecha
# ==============================
@agendaapi.route('/agenda/disponibilidad', methods=['GET'])
def disponibilidad_medico():
    id_medico = request.args.get('id_medico')
    fecha = request.args.get('fecha')  # formato 'YYYY-MM-DD'

    if not id_medico or not fecha:
        return jsonify(success=False, error="Faltan parámetros id_medico o fecha"), 400

    try:
        id_medico = int(id_medico)
    except ValueError:
        return jsonify(success=False, error="El parámetro id_medico debe ser un número entero"), 400

    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(success=False, error="Formato de fecha inválido. Use YYYY-MM-DD"), 400

    try:
        dao = DisponibilidadDao()
        data = dao.getDisponibilidadesPorMedicoFecha(id_medico, fecha_obj)
        return jsonify(success=True, data=data, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener disponibilidades médico {id_medico} fecha {fecha}: {e}")
        return jsonify(success=False, error="Ocurrió un error interno al consultar las disponibilidades"), 500
