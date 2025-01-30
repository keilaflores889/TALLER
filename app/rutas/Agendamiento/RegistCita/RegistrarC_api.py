from flask import Blueprint, request, jsonify, current_app as app
from app.dao.RegisCita.RegistroCDao import RegistroCDao
from datetime import time

regiscitaapi = Blueprint('regiscitaapi', __name__)

def serialize_time(obj):
    """Convierte objetos time en cadenas serializables."""
    if isinstance(obj, time):
        return obj.strftime('%H:%M:%S')
    return obj

# Obtener todas los registros
@regiscitaapi.route('/registroc', methods=['GET'])
def RegistrosC():
    registrocdao = RegistroCDao()
    try:
        registrosc = registrocdao.getRegistrosC()
        # Serializar cualquier objeto time dentro de los registros
        for registro in registrosc:
            if 'hora' in registro and isinstance(registro['hora'], time):
                registro['hora'] = serialize_time(registro['hora'])
        return jsonify({
            'success': True,
            'data': registrosc,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas los registros: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurri\u00f3 un error interno al consultar las agendas. Consulte con el administrador.'
        }), 500

# Obtener un registro específico por ID
@regiscitaapi.route('/registroc/<int:cita_id>', methods=['GET'])
def getRegistroC(cita_id):
    registrocdao = RegistroCDao()
    try:
        registroc = registrocdao.getRegistroCById(cita_id)
        if registroc:
            if 'hora' in registroc and isinstance(registroc['hora'], time):
                registroc['hora'] = serialize_time(registroc['hora'])
            return jsonify({
                'success': True,
                'data': registroc,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontr\u00f3 el registro con el ID {cita_id}.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener registro con ID {cita_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurri\u00f3 un error interno al consultar el registro. Consulte con el administrador.'
        }), 500

# Agregar un nuevo registro
@regiscitaapi.route('/registroc', methods=['POST'])
def addRegistroC():
    data = request.get_json()
    registrocdao = RegistroCDao()

    # Validar campos requeridos
    campos_requeridos = ['id_paciente', 'id_medico', 'id_especialidad', 'fecha_cita', 'hora', 'id_estado', 'motivo_consulta']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo].strip():
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vac\u00eda.'
            }), 400

    try:
        id_paciente = data['id_paciente']
        id_medico = data['id_medico']
        id_especialidad = data['id_especialidad']
        fecha_cita = data['fecha_cita']
        hora = data['hora']
        id_estado = data['id_estado']
        motivo_consulta = data['motivo_consulta']

        cita_id = registrocdao.guardarRegistroC(id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta)
        if cita_id is not None:
            return jsonify({
                'success': True,
                'data': {
                    'id': cita_id,
                    'id_paciente': id_paciente,
                    'id_medico': id_medico,
                    'id_especialidad': id_especialidad,
                    'fecha_cita': fecha_cita,
                    'hora': hora,
                    'id_estado': id_estado,
                    'motivo_consulta': motivo_consulta,
                },
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el registro. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar el registro: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurri\u00f3 un error interno al guardar el registro. Consulte con el administrador.'
        }), 500

# Actualizar el registro existente
@regiscitaapi.route('/registroc/<int:cita_id>', methods=['PUT'])
def updateRegistroC(cita_id):
    data = request.get_json()
    registrocdao = RegistroCDao()

    # Validar campos requeridos
    campos_requeridos = ['id_paciente', 'id_medico', 'id_especialidad', 'fecha_cita', 'hora', 'id_estado', 'motivo_consulta']
    for campo in campos_requeridos:
        if not data.get(campo) or not isinstance(data[campo], str) or not data[campo].strip():
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y debe ser una cadena no vac\u00eda.'
            }), 400

    try:
        id_paciente = data['id_paciente']
        id_medico = data['id_medico']
        id_especialidad = data['id_especialidad']
        fecha_cita = data['fecha_cita']
        hora = data['hora']
        id_estado = data['id_estado']
        motivo_consulta = data['motivo_consulta']

        if registrocdao.updateRegistroC(cita_id, id_paciente, id_medico, id_especialidad, fecha_cita, hora, id_estado, motivo_consulta):
            app.logger.info(f"Registro de cita con ID {cita_id} actualizada exitosamente.")
            return jsonify({
                'success': True,
                'data': {
                    'id': cita_id,
                    'id_paciente': id_paciente,
                    'id_medico': id_medico,
                    'id_especialidad': id_especialidad,
                    'fecha_cita': fecha_cita,
                    'hora': hora,
                    'id_estado': id_estado,
                    'motivo_consulta': motivo_consulta,
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontr\u00f3 el registro con el ID {cita_id} o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar registro con ID {cita_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurri\u00f3 un error interno al actualizar el registro. Consulte con el administrador.'
        }), 500

# Eliminar un registro
@regiscitaapi.route('/registroc/<int:cita_id>', methods=['DELETE'])
def deleteRegistroC(cita_id):
    registrocdao = RegistroCDao()
    try:
        if registrocdao.deleteRegistroC(cita_id):
            app.logger.info(f"El registro de cita con ID {cita_id} eliminada.")
            return jsonify({
                'success': True,
                'mensaje': f'Registro con ID {cita_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'No se encontr\u00f3 el registro con el ID {cita_id} o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar registro con ID {cita_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurri\u00f3 un error interno al eliminar el registro. Consulte con el administrador.'
        }), 500
