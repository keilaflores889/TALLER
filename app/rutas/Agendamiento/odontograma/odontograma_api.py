from flask import Blueprint, request, jsonify, current_app as app, render_template
from app.dao.odontograma.OdontogramaDao import OdontogramaDao
from datetime import date

odontogramaapi = Blueprint('odontogramaapi', __name__)

# ------------------------
# Vista para el template
# ------------------------
@odontogramaapi.route('/odontograma-index', methods=['GET'])
def ver_odontograma():
    return render_template('odontograma/index.html')


# ------------------------
# Crear un nuevo odontograma
# ------------------------
@odontogramaapi.route('/odontograma', methods=['POST'])
def addOdontograma():
    data = request.get_json()
    app.logger.info(f"📌 Datos recibidos en addOdontograma: {data}")
    
    odontograma_dao = OdontogramaDao()
    
    if 'id_ficha_medica' not in data or data['id_ficha_medica'] in (None, "", "null"):
        return jsonify({'success': False, 'error': 'El campo id_ficha_medica es obligatorio.'}), 400

    try:
        # Verificar si ya existe un odontograma para esta ficha médica
        odontograma_existente = odontograma_dao.getOdontogramaByFicha(data['id_ficha_medica'])
        if odontograma_existente:
            return jsonify({'success': False, 'error': 'Ya existe un odontograma para esta ficha médica.'}), 409

        # Crear nuevo odontograma
        odontograma_data = {
            'id_ficha_medica': data['id_ficha_medica'],
            'fecha_registro': data.get('fecha_registro', str(date.today())),
            'observaciones': data.get('observaciones', ''),
            'estado': data.get('estado', 'Activo')
        }
        
        id_odontograma = odontograma_dao.addOdontograma(odontograma_data)
        
        if not id_odontograma:
            return jsonify({'success': False, 'error': 'No se pudo crear el odontograma.'}), 500

        # 👇 Insertar detalles si vienen en la petición
        detalles_insertados = []
        if 'detalles' in data and isinstance(data['detalles'], list):
            for d in data['detalles']:
                detalle_data = {
                    'id_odontograma': id_odontograma,
                    'numero_diente': d.get('diente'),
                    'id_estado_dental': d.get('estado'),
                    'superficie': d.get('superficie', 'Completo')
                    
                }
                id_detalle = odontograma_dao.addDetalleOdontograma(detalle_data)
                if id_detalle:
                    detalle_data['id_odontograma_detalle'] = id_detalle
                    detalles_insertados.append(detalle_data)

        return jsonify({
            'success': True,
            'data': {
                'id_odontograma': id_odontograma,
                **odontograma_data,
                'detalles': detalles_insertados
            },
            'error': None
        }), 201

    except Exception as e:
        app.logger.error(f"Error al crear odontograma: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno al crear el odontograma.'}), 500


# ------------------------
# Listar todos los odontogramas
# ------------------------
@odontogramaapi.route('/odontograma', methods=['GET'])
def getOdontogramas():
    odontograma_dao = OdontogramaDao()
    try:
        odontogramas = odontograma_dao.getOdontogramas()
        return jsonify({'success': True, 'data': odontogramas, 'error': None})
    except Exception as e:
        app.logger.error(f"Error al obtener odontogramas: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener odontogramas'}), 500


# ------------------------
# Obtener odontograma por ID
# ------------------------
@odontogramaapi.route('/odontograma/<int:id_odontograma>', methods=['GET'])
def getOdontograma(id_odontograma):
    odontograma_dao = OdontogramaDao()
    try:
        odontograma = odontograma_dao.getOdontogramaById(id_odontograma)
        if odontograma:
            detalles = odontograma_dao.getDetallesOdontograma(id_odontograma)
            odontograma['detalles'] = detalles
            return jsonify({'success': True, 'data': odontograma, 'error': None})
        return jsonify({'success': False, 'error': 'Odontograma no encontrado'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener odontograma {id_odontograma}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ------------------------
# Actualizar odontograma
# ------------------------
@odontogramaapi.route('/odontograma/<int:id_odontograma>', methods=['PUT'])
def updateOdontograma(id_odontograma):
    data = request.get_json()
    odontograma_dao = OdontogramaDao()
    try:
        # Actualizar la cabecera
        updated = odontograma_dao.updateOdontograma(id_odontograma, data)

        if not updated:
            return jsonify({'success': False, 'error': 'Odontograma no encontrado'}), 404

        # 🔹 Manejar los detalles
        if "detalles" in data and isinstance(data["detalles"], list):
            # 1. Borrar detalles anteriores
            odontograma_dao.deleteDetallesByOdontograma(id_odontograma)

            # 2. Insertar los nuevos detalles
            for d in data["detalles"]:
                detalle_data = {
                    'id_odontograma': id_odontograma,
                    'numero_diente': d.get('diente'),
                    'id_estado_dental': d.get('estado'),
                    'superficie': d.get('superficie', 'Completo')
                }
                odontograma_dao.addDetalleOdontograma(detalle_data)

        return jsonify({'success': True, 'message': 'Odontograma actualizado correctamente'})

    except Exception as e:
        app.logger.error(f"Error al actualizar odontograma {id_odontograma}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ------------------------
# Eliminar odontograma
# ------------------------
@odontogramaapi.route('/odontograma/<int:id_odontograma>', methods=['DELETE'])
def deleteOdontograma(id_odontograma):
    odontograma_dao = OdontogramaDao()
    try:
        deleted = odontograma_dao.deleteOdontograma(id_odontograma)
        if deleted:
            return jsonify({'success': True, 'message': 'Odontograma eliminado'})
        return jsonify({'success': False, 'error': 'Odontograma no encontrado'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar odontograma {id_odontograma}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ------------------------
# Listar estados dentales
# ------------------------
@odontogramaapi.route('/estados-dentales', methods=['GET'])
def getEstadosDentales():
    odontograma_dao = OdontogramaDao()
    try:
        estados = odontograma_dao.getEstadosDentales()
        return jsonify({'success': True, 'data': estados, 'error': None})
    except Exception as e:
        app.logger.error(f"Error al obtener estados dentales: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al obtener estados dentales'}), 500


# ------------------------
# Obtener detalles de un odontograma
# ------------------------
@odontogramaapi.route('/odontograma/<int:id_odontograma>/detalles', methods=['GET'])
def getDetalles(id_odontograma):
    odontograma_dao = OdontogramaDao()
    try:
        detalles = odontograma_dao.getDetallesOdontograma(id_odontograma)
        return jsonify({'success': True, 'data': detalles, 'error': None})
    except Exception as e:
        app.logger.error(f"Error al obtener detalles de odontograma {id_odontograma}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ------------------------
# Agregar un detalle a un odontograma
# ------------------------
@odontogramaapi.route('/odontograma/<int:id_odontograma>/detalles', methods=['POST'])
def addDetalle(id_odontograma):
    data = request.get_json()
    odontograma_dao = OdontogramaDao()
    try:
        detalle_data = {
            'id_odontograma': id_odontograma,
            'numero_diente': data.get('diente'),
            'id_estado_dental': data.get('estado'),
            'superficie': data.get('superficie', 'Completo')
            
        }
        id_detalle = odontograma_dao.addDetalleOdontograma(detalle_data)
        if id_detalle:
            detalle_data['id_odontograma_detalle'] = id_detalle
            return jsonify({'success': True, 'data': detalle_data, 'error': None}), 201
        return jsonify({'success': False, 'error': 'No se pudo crear el detalle'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar detalle en odontograma {id_odontograma}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ------------------------
# Actualizar un detalle
# ------------------------
@odontogramaapi.route('/detalle/<int:id_detalle>', methods=['PUT'])
def updateDetalle(id_detalle):
    data = request.get_json()
    odontograma_dao = OdontogramaDao()
    try:
        updated = odontograma_dao.updateDetalleOdontograma(id_detalle, data)
        if updated:
            return jsonify({'success': True, 'message': 'Detalle actualizado'})
        return jsonify({'success': False, 'error': 'Detalle no encontrado'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar detalle {id_detalle}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500


# ------------------------
# Eliminar un detalle
# ------------------------
@odontogramaapi.route('/detalle/<int:id_detalle>', methods=['DELETE'])
def deleteDetalle(id_detalle):
    odontograma_dao = OdontogramaDao()
    try:
        deleted = odontograma_dao.deleteDetalleOdontograma(id_detalle)
        if deleted:
            return jsonify({'success': True, 'message': 'Detalle eliminado'})
        return jsonify({'success': False, 'error': 'Detalle no encontrado'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar detalle {id_detalle}: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500
