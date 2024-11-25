from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.cita.CitaDao import CitaDao
import datetime

citaapi = Blueprint('citaapi', __name__)

# Trae todas las citas
@citaapi.route('/citas', methods=['GET'])
def getCitas():
    citadao = CitaDao()

    try:
        citas = citadao.getCitas()

        # Transformar fechas y horas a cadenas si es necesario
        for cita in citas:
            # Verificar si la fecha es un objeto de fecha o fecha y hora
            if isinstance(cita['fecha'], (datetime.date, datetime.datetime)):
                # Convertir la fecha a formato de cadena (YYYY-MM-DD)
                cita['fecha'] = cita['fecha'].strftime('%Y-%m-%d')
            # Verificar si la hora es un objeto de hora
            if isinstance(cita['hora'], datetime.time):
                # Convertir la hora a formato de cadena (HH:MM)
                cita['hora'] = cita['hora'].strftime('%H:%M')

        return jsonify({
            'success': True,
            'data': citas,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas las citas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Obtiene una cita por ID
@citaapi.route('/citas/<int:cita_id>', methods=['GET'])
def getCita(cita_id):
    citadao = CitaDao()

    try:
        cita = citadao.getCitaById(cita_id)

        if cita:
            # Transformar fecha y hora a cadenas si es necesario
            if isinstance(cita['fecha'], (datetime.date, datetime.datetime)):
                # Convertir la fecha a formato de cadena (YYYY-MM-DD)
                cita['fecha'] = cita['fecha'].strftime('%Y-%m-%d')
            if isinstance(cita['hora'], datetime.time):
                # Convertir la hora a formato de cadena (HH:MM)
                cita['hora'] = cita['hora'].strftime('%H:%M')

            return jsonify({
                'success': True,
                'data': cita,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la cita con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega una nueva cita
@citaapi.route('/citas', methods=['POST'])
def addCita():
    data = request.get_json()
    citadao = CitaDao()

    campos_requeridos = ['nombrepaciente', 'motivoconsulta', 'medico', 'fecha', 'hora']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        # Convertir los valores a mayúsculas
        nombrepaciente = data['nombrepaciente'].upper()
        motivoconsulta = data['motivoconsulta'].upper()
        medico = data['medico'].upper()
        fecha = data['fecha']
        hora = data['hora']
        
        cita_id = citadao.guardarCita(nombrepaciente, motivoconsulta, medico, fecha, hora)

        if cita_id is not None:
            return jsonify({
                'success': True,
                'data': {
                    'id': cita_id,
                    'nombrepaciente': nombrepaciente,
                    'motivoconsulta': motivoconsulta,
                    'medico': medico,
                    'fecha': fecha,
                    'hora': hora
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la cita. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Actualiza una cita
@citaapi.route('/citas/<int:cita_id>', methods=['PUT'])
def updateCita(cita_id):
    data = request.get_json()
    citadao = CitaDao()

    campos_requeridos = ['nombrepaciente', 'motivoconsulta', 'medico', 'fecha', 'hora']

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    nombrepaciente = data['nombrepaciente'].upper()
    motivoconsulta = data['motivoconsulta'].upper()
    medico = data['medico'].upper()
    fecha = data['fecha']
    hora = data['hora']

    try:
        if citadao.updateCita(cita_id, nombrepaciente, motivoconsulta, medico, fecha, hora):
            return jsonify({
                'success': True,
                'data': {
                    'id': cita_id,
                    'nombrepaciente': nombrepaciente,
                    'motivoconsulta': motivoconsulta,
                    'medico': medico,
                    'fecha': fecha,
                    'hora': hora
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la cita con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Elimina una cita
@citaapi.route('/citas/<int:cita_id>', methods=['DELETE'])
def deleteCita(cita_id):
    citadao = CitaDao()

    try:
        if citadao.deleteCita(cita_id):
            return jsonify({
                'success': True,
                'mensaje': f'Cita con ID {cita_id} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la cita con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar cita: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
