from flask import Blueprint, request, jsonify, current_app as app, render_template
from app.dao.RegisCita.RegistroCDao import RegistroCDao
from datetime import time

regiscitaapi = Blueprint('regiscitaapi', __name__)

# ------------------------
# Helpers
# ------------------------
def serialize_time(obj):
    """Convierte objetos time en cadenas serializables."""
    if isinstance(obj, time):
        return obj.strftime('%H:%M:%S')
    return obj

def obtener_id_agenda_actual():
    """
    Devuelve el ID de la agenda actual.
    Ajusta la lógica según tu base de datos o la agenda que quieras mostrar.
    """
    # Ejemplo simple: siempre devuelve 1
    return 1

# ------------------------
# Vista para el template
# ------------------------
@regiscitaapi.route('/registrarc-index/<int:id_agenda_medica>', methods=['GET'])
def ver_registroc(id_agenda_medica):
    return render_template('RegistrarC-index.html', id_agenda_medica=id_agenda_medica)

# ===== NUEVO ENDPOINT PARA OBTENER DISPONIBILIDADES =====
@regiscitaapi.route('/api/v1/disponibilidad-medico/<int:id_medico>', methods=['GET'])
def obtenerDisponibilidadMedico(id_medico):
    fecha_cita = request.args.get('fecha')  # Parámetro requerido
    
    if not fecha_cita:
        return jsonify({
            'success': False, 
            'error': 'El parámetro fecha es requerido.'
        }), 400
    
    registrocdao = RegistroCDao()
    
    try:
        disponibilidades = registrocdao.obtener_disponibilidad_medico(id_medico, fecha_cita)
        return jsonify({
            'success': True, 
            'data': disponibilidades, 
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener disponibilidad del médico {id_medico}: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Ocurrió un error interno al consultar la disponibilidad.'
        }), 500

# ------------------------
# 🔹 Nuevo: Listar agendas
# ------------------------
@regiscitaapi.route('/agendas', methods=['GET'])
def listarAgendas():
    registrocdao = RegistroCDao()
    try:
        agendas = registrocdao.getAgendas()
        return jsonify({'success': True, 'data': agendas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener agendas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al consultar las agendas.'}), 500


# ------------------------
# Obtener todos los registros
# ------------------------
@regiscitaapi.route('/registroc', methods=['GET'])
def RegistrosC():
    registrocdao = RegistroCDao()
    try:
        registrosc = registrocdao.getRegistrosC()
        for registro in registrosc:
            if 'hora' in registro and isinstance(registro['hora'], time):
                registro['hora'] = serialize_time(registro['hora'])
        return jsonify({'success': True, 'data': registrosc, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas los registros: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al consultar las citas.'}), 500

# ------------------------
# Obtener un registro por ID
# ------------------------
@regiscitaapi.route('/registroc/<int:cita_id>', methods=['GET'])
def getRegistroC(cita_id):
    registrocdao = RegistroCDao()
    try:
        registroc = registrocdao.getRegistroCById(cita_id)
        if registroc:
            if 'hora' in registroc and isinstance(registroc['hora'], time):
                registroc['hora'] = serialize_time(registroc['hora'])
            return jsonify({'success': True, 'data': registroc, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': f'No se encontró el registro con el ID {cita_id}.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener registro con ID {cita_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al consultar el registro.'}), 500

# ------------------------
# Agregar un nuevo registro
# ------------------------
@regiscitaapi.route('/registroc', methods=['POST'])
def addRegistroC():
    data = request.get_json()
    app.logger.info(f"📌 Datos recibidos en addRegistroC: {data}")
    print("Datos recibidos en API:", data)
    registrocdao = RegistroCDao()

    campos_requeridos = ['id_paciente', 'id_medico', 'id_especialidad', 'id_turno', 
                         'fecha_cita', 'hora', 'id_estado', 'motivo_consulta', 'id_agenda_medica']
    for campo in campos_requeridos:
        if campo not in data or data[campo] in (None, "", "null"):
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio.'}), 400

    try:
        id_agenda = int(data['id_agenda_medica']) if data['id_agenda_medica'] else None
        id_agenda_medica = data.get("id_agenda_medica")
        print("ID agenda recibido:", id_agenda_medica)  # 👈 debug
        cita_id = registrocdao.guardarRegistroC(
            data['id_paciente'], 
            data['id_medico'], 
            data['id_especialidad'], 
            data['id_turno'],
            data['fecha_cita'], 
            data['hora'], 
            data['id_estado'], 
            data['motivo_consulta'], 
            id_agenda
        )

        if cita_id == "DUPLICADO":
            return jsonify({'success': False, 'error': 'Ya existe esta cita para el mismo médico, fecha y hora.'}), 409

        if cita_id == "SIN_CUPOS":
            return jsonify({'success': False, 'error': 'No hay cupos disponibles en esta agenda.'}), 409

        # ===== NUEVA VALIDACIÓN =====
        if cita_id == "FUERA_DE_HORARIO":
            return jsonify({'success': False, 'error': 'La hora seleccionada está fuera del horario de disponibilidad del médico para esta fecha.'}), 409

        return jsonify({
            'success': True,
            'data': {
                'id_cita': cita_id,
                'id_paciente': data['id_paciente'],
                'id_medico': data['id_medico'],
                'id_especialidad': data['id_especialidad'],
                'id_turno': data['id_turno'],
                'fecha_cita': data['fecha_cita'],
                'hora': data['hora'],
                'id_estado': data['id_estado'],
                'motivo_consulta': data['motivo_consulta'],
                'id_agenda_medica': id_agenda
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al agregar el registro: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al guardar el registro.'}), 500

# ------------------------
# Actualizar un registro
# ------------------------
@regiscitaapi.route('/registroc/<int:cita_id>', methods=['PUT'])
def updateRegistroC(cita_id):
    data = request.get_json()
    app.logger.info(f"📌 Datos recibidos en updateRegistroC: {data}")
    
    registrocdao = RegistroCDao()

    campos_requeridos = ['id_paciente', 'id_medico', 'id_especialidad', 'id_turno', 
                         'fecha_cita', 'hora', 'id_estado', 'motivo_consulta', 'id_agenda_medica']
    for campo in campos_requeridos:
        if campo not in data or data[campo] in (None, "", "null"):
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio.'}), 400

    try:
        id_agenda = int(data['id_agenda_medica']) if data['id_agenda_medica'] else None

        exito = registrocdao.updateRegistroC(
            cita_id, 
            data['id_paciente'], 
            data['id_medico'], 
            data['id_especialidad'], 
            data['id_turno'],
            data['fecha_cita'], 
            data['hora'], 
            data['id_estado'], 
            data['motivo_consulta'], 
            id_agenda
        )
        
        if exito == "SIN_CUPOS":
            return jsonify({'success': False, 'error': 'No hay cupos disponibles en esta agenda.'}), 409
            
        # ===== NUEVA VALIDACIÓN =====
        if exito == "FUERA_DE_HORARIO":
            return jsonify({'success': False, 'error': 'La hora seleccionada está fuera del horario de disponibilidad del médico para esta fecha.'}), 409
        
        if exito:
            return jsonify({
                'success': True,
                'data': {
                    'id_cita': cita_id,
                    'id_paciente': data['id_paciente'],
                    'id_medico': data['id_medico'],
                    'id_especialidad': data['id_especialidad'],
                    'id_turno': data['id_turno'],
                    'fecha_cita': data['fecha_cita'],
                    'hora': data['hora'],
                    'id_estado': data['id_estado'],
                    'motivo_consulta': data['motivo_consulta'],
                    'id_agenda_medica': id_agenda
                },
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': f'No se encontró el registro con el ID {cita_id} o no se pudo actualizar.'}), 404

    except Exception as e:
        app.logger.error(f"Error al actualizar registro con ID {cita_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al actualizar el registro.'}), 500

# ------------------------
# Eliminar un registro
# ------------------------
@regiscitaapi.route('/registroc/<int:cita_id>', methods=['DELETE'])
def deleteRegistroC(cita_id):
    registrocdao = RegistroCDao()
    try:
        if registrocdao.deleteRegistroC(cita_id):
            return jsonify({'success': True, 'mensaje': f'Registro con ID {cita_id} eliminado correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': f'No se encontró el registro con el ID {cita_id} o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar registro con ID {cita_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al eliminar el registro.'}), 500