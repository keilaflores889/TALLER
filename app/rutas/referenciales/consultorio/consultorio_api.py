from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.consultorio.ConsultorioDao import ConsultorioDao

consultorioapi = Blueprint('consultorioapi', __name__)

# Trae todos los consultorios
@consultorioapi.route('/consultorios', methods=['GET'])
def getConsultorios():
    dao = ConsultorioDao()
    try:
        consultorios = dao.getConsultorios()
        return jsonify({
            'success': True,
            'data': consultorios,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultorios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# Trae un consultorio por código
@consultorioapi.route('/consultorios/<int:codigo>', methods=['GET'])
def getConsultorio(codigo):
    dao = ConsultorioDao()
    try:
        consultorio = dao.getConsultorioById(codigo)
        if consultorio:
            return jsonify({'success': True, 'data': consultorio, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el consultorio con el código proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consultorio: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# Agrega un nuevo consultorio
@consultorioapi.route('/consultorios', methods=['POST'])
def addConsultorio():
    data = request.get_json()
    dao = ConsultorioDao()

    # Validación de campos
    required_fields = ['nombre_consultorio', 'direccion', 'telefono', 'correo']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({'success': False, 'error': f'El campo {field} es obligatorio y no puede estar vacío.'}), 400

    nombre = data['nombre_consultorio'].strip()
    direccion = data['direccion'].strip()
    telefono = data['telefono'].strip()
    correo = data['correo'].strip()

    try:
        # Verificar duplicado
        if dao.existeDuplicado(nombre, correo):
            return jsonify({'success': False, 'error': 'Ya está registrado este consultorio'}), 400

        codigo = dao.guardarConsultorio(nombre, direccion, telefono, correo)
        if codigo:
            return jsonify({'success': True, 'data': {
                'codigo': codigo,
                'nombre_consultorio': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'correo': correo
            }, 'error': None}), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el consultorio.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar consultorio: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# Actualiza un consultorio
@consultorioapi.route('/consultorios/<int:codigo>', methods=['PUT'])
def updateConsultorio(codigo):
    data = request.get_json()
    dao = ConsultorioDao()

    required_fields = ['nombre_consultorio', 'direccion', 'telefono', 'correo']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({'success': False, 'error': f'El campo {field} es obligatorio y no puede estar vacío.'}), 400

    nombre = data['nombre_consultorio'].strip()
    direccion = data['direccion'].strip()
    telefono = data['telefono'].strip()
    correo = data['correo'].strip()

    try:
        # Verificar duplicado antes de actualizar (excepto el mismo código)
        consultorio_existente = dao.getConsultorioById(codigo)
        if not consultorio_existente:
            return jsonify({'success': False, 'error': 'No se encontró el consultorio con el código proporcionado.'}), 404

        if dao.existeDuplicado(nombre, correo) and (
            consultorio_existente['nombre_consultorio'].upper() != nombre.upper() or 
            consultorio_existente['correo'].upper() != correo.upper()
        ):
            return jsonify({'success': False, 'error': 'Ya existe otro consultorio con ese nombre o correo.'}), 400

        if dao.updateConsultorio(codigo, nombre, direccion, telefono, correo):
            return jsonify({'success': True, 'data': {
                'codigo': codigo,
                'nombre_consultorio': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'correo': correo
            }, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo actualizar el consultorio.'}), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar consultorio: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# Elimina un consultorio
@consultorioapi.route('/consultorios/<int:codigo>', methods=['DELETE'])
def deleteConsultorio(codigo):
    dao = ConsultorioDao()
    try:
        if dao.deleteConsultorio(codigo):
            return jsonify({'success': True, 'mensaje': f'Consultorio con código {codigo} eliminado correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el consultorio con el código proporcionado o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar consultorio: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500
