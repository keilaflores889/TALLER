from flask import Blueprint, jsonify, request, current_app as app, render_template
from app.dao.ModuloConsultorio.RegisConsulta.ConsultasDao import ConsultasDao
import os
from datetime import datetime

consultasapi = Blueprint('consultasapi', __name__)

# Definir la carpeta de templates para este blueprint
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, 'templates')

# Crear el blueprint con la carpeta de templates
consultasapi = Blueprint(
    'consultasapi',
    __name__,
    template_folder=template_folder
)

# ============================
# CONSULTAS CABECERA - Obtener todas
# ============================
@consultasapi.route('/consultas', methods=['GET'])
def getConsultasCabecera():
    dao = ConsultasDao()
    try:
        consultas = dao.getConsultasCabecera()
        return jsonify(success=True, data=consultas, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas cabecera: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consultas."), 500

# ============================
# CONSULTAS CABECERA - Obtener por ID
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>', methods=['GET'])
def getConsultaCabecera(id_consulta_cab):
    dao = ConsultasDao()
    try:
        consulta = dao.getConsultaCabeceraById(id_consulta_cab)
        if consulta:
            return jsonify(success=True, data=consulta, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consulta."), 500

# ============================
# CONSULTAS CABECERA - Obtener consulta completa (cabecera + detalles + diagnósticos)
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>/completa', methods=['GET'])
def getConsultaCompleta(id_consulta_cab):
    dao = ConsultasDao()
    try:
        consulta = dao.getConsultaCompleta(id_consulta_cab)
        if consulta:
            return jsonify(success=True, data=consulta, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consulta completa {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar consulta completa."), 500

# ============================
# CONSULTAS CABECERA - Agregar nueva
# ============================
@consultasapi.route('/consultas', methods=['POST'])
def addConsultaCabecera():
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_personal', 'id_consultorio', 'id_medico', 'id_paciente', 
                         'fecha_cita', 'hora_cita']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        if 'estado' not in data or data['estado'] is None:
            data['estado'] = 'programada'
        
        if 'duracion_minutos' in data and data['duracion_minutos'] == '':
            data['duracion_minutos'] = None

        consulta_id = dao.addConsultaCabecera(data)
        if consulta_id:
            return jsonify(success=True, data={**data, "id_consulta_cab": consulta_id}, error=None), 201
        return jsonify(success=False, error="No se pudo guardar la consulta."), 500
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al agregar consulta: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar consulta."), 500

# ============================
# CONSULTAS CABECERA - Actualizar
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>', methods=['PUT'])
def updateConsultaCabecera(id_consulta_cab):
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_personal', 'id_consultorio', 'id_medico', 'id_paciente', 
                         'fecha_cita', 'hora_cita']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        if 'estado' not in data or data['estado'] is None:
            data['estado'] = 'programada'
        
        if 'duracion_minutos' in data and data['duracion_minutos'] == '':
            data['duracion_minutos'] = None

        actualizado = dao.updateConsultaCabecera(id_consulta_cab, data)
        if actualizado:
            return jsonify(success=True, data={**data, "id_consulta_cab": id_consulta_cab}, error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab} o no se pudo actualizar."), 404
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al actualizar consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar consulta."), 500

# ============================
# CONSULTAS CABECERA - Eliminar
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>', methods=['DELETE'])
def deleteConsultaCabecera(id_consulta_cab):
    dao = ConsultasDao()
    try:
        if dao.deleteConsultaCabecera(id_consulta_cab):
            return jsonify(success=True, data=f"Consulta {id_consulta_cab} eliminada.", error=None), 200
        return jsonify(success=False, error=f"No se encontró consulta con ID {id_consulta_cab}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar consulta."), 500

# ============================
# CONSULTAS DETALLE - Obtener todas
# ============================
@consultasapi.route('/consultas-detalle', methods=['GET'])
def getConsultasDetalle():
    dao = ConsultasDao()
    try:
        detalles = dao.getConsultasDetalle()
        return jsonify(success=True, data=detalles, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas detalle: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalles."), 500

# ============================
# CONSULTAS DETALLE - Obtener todas con información completa
# ============================
@consultasapi.route('/consultas-detalle-info', methods=['GET'])
def getConsultasDetalleConInfo():
    dao = ConsultasDao()
    try:
        detalles = dao.getConsultasDetalleConInfo()
        return jsonify(success=True, data=detalles, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas detalle con info: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalles."), 500

# ============================
# CONSULTAS DETALLE - Obtener por ID
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>', methods=['GET'])
def getConsultaDetalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        detalle = dao.getConsultaDetalleById(id_consulta_detalle)
        if detalle:
            return jsonify(success=True, data=detalle, error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalle."), 500

# ============================
# CONSULTAS DETALLE - Obtener por ID con información completa
# ============================
@consultasapi.route('/consultas-detalle-info/<int:id_consulta_detalle>', methods=['GET'])
def getConsultaDetalleConInfo(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        detalle = dao.getConsultaDetalleByIdConInfo(id_consulta_detalle)
        if detalle:
            return jsonify(success=True, data=detalle, error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al obtener detalle con info {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalle."), 500

# ============================
# CONSULTAS DETALLE - Obtener por consulta cabecera
# ============================
@consultasapi.route('/consultas/<int:id_consulta_cab>/detalles', methods=['GET'])
def getDetallesByConsulta(id_consulta_cab):
    dao = ConsultasDao()
    try:
        detalles = dao.getDetallesByConsultaCab(id_consulta_cab)
        return jsonify(success=True, data=detalles, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener detalles de consulta {id_consulta_cab}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar detalles."), 500

# ============================
# CONSULTAS DETALLE - Agregar nuevo
# ============================
@consultasapi.route('/consultas-detalle', methods=['POST'])
def addConsultaDetalle():
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_consulta_cab', 'id_sintoma', 'diagnostico', 'tratamiento']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        if 'pieza_dental' in data and data['pieza_dental'] == '':
            data['pieza_dental'] = None
        
        if 'procedimiento' in data and data['procedimiento'] == '':
            data['procedimiento'] = None
        
        if 'id_tipo_diagnostico' in data and data['id_tipo_diagnostico'] == '':
            data['id_tipo_diagnostico'] = None

        if 'id_tipo_procedimiento' in data and data['id_tipo_procedimiento'] == '':
            data['id_tipo_procedimiento'] = None

        detalle_id = dao.addConsultaDetalle(data)
        
        if detalle_id:
            return jsonify(
                success=True, 
                data={**data, "id_consulta_detalle": detalle_id},
                message="Detalle guardado correctamente",
                error=None
            ), 201
        
        return jsonify(success=False, error="No se pudo guardar el detalle de consulta."), 500
        
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al agregar consulta detalle: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar consulta detalle."), 500

# ============================
# CONSULTAS DETALLE - Actualizar
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>', methods=['PUT'])
def updateConsultaDetalle(id_consulta_detalle):
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_consulta_cab', 'id_sintoma', 'diagnostico', 'tratamiento']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        if 'pieza_dental' in data and data['pieza_dental'] == '':
            data['pieza_dental'] = None
        
        if 'procedimiento' in data and data['procedimiento'] == '':
            data['procedimiento'] = None
        
        if 'id_tipo_diagnostico' in data and data['id_tipo_diagnostico'] == '':
            data['id_tipo_diagnostico'] = None

        if 'id_tipo_procedimiento' in data and data['id_tipo_procedimiento'] == '':
            data['id_tipo_procedimiento'] = None

        actualizado = dao.updateConsultaDetalle(id_consulta_detalle, data)
        if actualizado:
            return jsonify(success=True, data={**data, "id_consulta_detalle": id_consulta_detalle}, error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle} o no se pudo actualizar."), 404
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al actualizar consulta detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar consulta detalle."), 500

# ============================
# CONSULTAS DETALLE - Eliminar
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>', methods=['DELETE'])
def deleteConsultaDetalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        if dao.deleteConsultaDetalle(id_consulta_detalle):
            return jsonify(success=True, data=f"Detalle {id_consulta_detalle} eliminado.", error=None), 200
        return jsonify(success=False, error=f"No se encontró detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar consulta detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar consulta detalle."), 500

# ============================
# DIAGNÓSTICOS - Obtener todos los diagnósticos de una consulta detalle
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>/diagnosticos', methods=['GET'])
def getDiagnosticosByConsultaDetalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        diagnosticos = dao.getDiagnosticosByConsultaDetalle(id_consulta_detalle)
        return jsonify(success=True, data=diagnosticos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos de consulta detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar diagnósticos."), 500

# ============================
# DIAGNÓSTICOS - Agregar diagnóstico adicional
# ============================
@consultasapi.route('/diagnosticos', methods=['POST'])
def addDiagnostico():
    data = request.get_json() or {}
    dao = ConsultasDao()

    app.logger.info(f"📝 Datos recibidos en API: {data}")

    campos_requeridos = ['id_consulta_detalle', 'descripcion_diagnostico']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    # ✅ VALIDAR id_tipo_diagnostico
    if 'id_tipo_diagnostico' not in data or not data.get('id_tipo_diagnostico'):
        return jsonify(
            success=False, 
            error="El campo tipo diagnóstico es obligatorio."
        ), 400

    try:
        diagnostico_id = dao.addDiagnostico(data)
        if diagnostico_id:
            return jsonify(
                success=True, 
                data={**data, "id_diagnostico": diagnostico_id},
                message="Diagnóstico agregado correctamente",
                error=None
            ), 201
        return jsonify(success=False, error="No se pudo guardar el diagnóstico."), 500
    except ValueError as ve:
        es_duplicado = "Ya existe" in str(ve)
        codigo_http = 409 if es_duplicado else 400
        app.logger.warning(f"⚠️ Validación fallida: {str(ve)}")
        return jsonify(
            success=False, 
            error=str(ve),
            type="duplicate" if es_duplicado else "validation"
        ), codigo_http
    except Exception as e:
        app.logger.error(f"Error al agregar diagnóstico: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar diagnóstico."), 500

# ============================
# DIAGNÓSTICOS - Actualizar diagnóstico
# ============================
@consultasapi.route('/diagnosticos/<int:id_diagnostico>', methods=['PUT'])
def updateDiagnostico(id_diagnostico):
    data = request.get_json() or {}
    dao = ConsultasDao()

    try:
        actualizado = dao.updateDiagnostico(id_diagnostico, data)
        if actualizado:
            return jsonify(
                success=True, 
                data={**data, "id_diagnostico": id_diagnostico},
                message="Diagnóstico actualizado correctamente",
                error=None
            ), 200
        return jsonify(success=False, error=f"No se encontró diagnóstico con ID {id_diagnostico}."), 404
    except ValueError as ve:
        es_duplicado = "Ya existe" in str(ve)
        codigo_http = 409 if es_duplicado else 400
        app.logger.warning(f"⚠️ Validación fallida al actualizar diagnóstico: {str(ve)}")
        return jsonify(
            success=False, 
            error=str(ve),
            type="duplicate" if es_duplicado else "validation"
        ), codigo_http
    except Exception as e:
        app.logger.error(f"Error al actualizar diagnóstico {id_diagnostico}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar diagnóstico."), 500

# ============================
# DIAGNÓSTICOS - Eliminar diagnóstico
# ============================
@consultasapi.route('/diagnosticos/<int:id_diagnostico>', methods=['DELETE'])
def deleteDiagnostico(id_diagnostico):
    dao = ConsultasDao()
    try:
        if dao.deleteDiagnostico(id_diagnostico):
            return jsonify(success=True, data=f"Diagnóstico {id_diagnostico} eliminado.", error=None), 200
        return jsonify(success=False, error=f"No se encontró diagnóstico con ID {id_diagnostico}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar diagnóstico {id_diagnostico}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar diagnóstico."), 500

# ============================
# ACTUALIZAR DIAGNÓSTICO PRINCIPAL (consultas_detalle)
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>/diagnostico-principal', methods=['PUT'])
def updateDiagnosticoPrincipal(id_consulta_detalle):
    data = request.get_json() or {}
    dao = ConsultasDao()

    if not data.get('diagnostico'):
        return jsonify(success=False, error="El campo 'diagnostico' es obligatorio"), 400

    try:
        actualizado = dao.updateDiagnosticoPrincipal(id_consulta_detalle, data)
        if actualizado:
            return jsonify(
                success=True,
                data=data,
                message="Diagnóstico principal actualizado correctamente",
                error=None
            ), 200
        return jsonify(success=False, error=f"No se encontró consulta detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar diagnóstico principal: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar diagnóstico principal."), 500

# ============================
# ACTUALIZAR TRATAMIENTO PRINCIPAL (consultas_detalle)
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>/tratamiento-principal', methods=['PUT'])
def updateTratamientoPrincipal(id_consulta_detalle):
    data = request.get_json() or {}
    dao = ConsultasDao()

    if not data.get('tratamiento'):
        return jsonify(success=False, error="El campo 'tratamiento' es obligatorio"), 400

    try:
        actualizado = dao.updateTratamientoPrincipal(id_consulta_detalle, data)
        if actualizado:
            return jsonify(
                success=True,
                data=data,
                message="Tratamiento principal actualizado correctamente",
                error=None
            ), 200
        return jsonify(success=False, error=f"No se encontró consulta detalle con ID {id_consulta_detalle}."), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar tratamiento principal: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar tratamiento principal."), 500
    

# ============================
# TRATAMIENTOS - Obtener todos los tratamientos de una consulta detalle
# ============================
@consultasapi.route('/consultas-detalle/<int:id_consulta_detalle>/Tratamiento', methods=['GET'])
def getTratamientosByConsultaDetalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        tratamientos = dao.getTratamientosByConsultaDetalle(id_consulta_detalle)
        return jsonify(success=True, data=tratamientos, error=None), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos de consulta detalle {id_consulta_detalle}: {str(e)}")
        return jsonify(success=False, error="Error interno al consultar tratamientos."), 500

# ============================
# TRATAMIENTOS - Agregar tratamiento adicional
# ============================
@consultasapi.route('/Tratamiento', methods=['POST'])
def addTratamiento():
    data = request.get_json() or {}
    dao = ConsultasDao()

    campos_requeridos = ['id_consulta_detalle', 'id_medico', 'id_paciente', 'descripcion_tratamiento']
    faltantes = [c for c in campos_requeridos if not data.get(c)]
    if faltantes:
        return jsonify(success=False, error=f"Faltan campos: {', '.join(faltantes)}"), 400

    try:
        tratamiento_id = dao.addTratamiento(data)
        if tratamiento_id:
            return jsonify(
                success=True, 
                data={**data, "id_tratamiento": tratamiento_id},
                message="Tratamiento agregado correctamente",
                error=None
            ), 201
        return jsonify(success=False, error="No se pudo guardar el tratamiento."), 500
    except ValueError as ve:
        es_duplicado = "Ya existe" in str(ve)
        codigo_http = 409 if es_duplicado else 400
        app.logger.warning(f"⚠️ Validación fallida al agregar tratamiento: {str(ve)}")
        return jsonify(
            success=False, 
            error=str(ve),
            type="duplicate" if es_duplicado else "validation"
        ), codigo_http
    except Exception as e:
        app.logger.error(f"Error al agregar tratamiento: {str(e)}")
        return jsonify(success=False, error="Error interno al guardar tratamiento."), 500

# ============================
# TRATAMIENTOS - Actualizar tratamiento
# ============================
@consultasapi.route('/Tratamiento/<int:id_tratamiento>', methods=['PUT'])
def updateTratamiento(id_tratamiento):
    data = request.get_json() or {}
    dao = ConsultasDao()

    try:
        actualizado = dao.updateTratamiento(id_tratamiento, data)
        if actualizado:
            return jsonify(
                success=True, 
                data={**data, "id_tratamiento": id_tratamiento},
                message="Tratamiento actualizado correctamente",
                error=None
            ), 200
        return jsonify(success=False, error=f"No se encontró tratamiento con ID {id_tratamiento}."), 404
    except ValueError as ve:
        return jsonify(success=False, error=str(ve)), 400
    except Exception as e:
        app.logger.error(f"Error al actualizar tratamiento {id_tratamiento}: {str(e)}")
        return jsonify(success=False, error="Error interno al actualizar tratamiento."), 500

# ============================
# TRATAMIENTOS - Eliminar tratamiento
# ============================
@consultasapi.route('/Tratamiento/<int:id_tratamiento>', methods=['DELETE'])
def deleteTratamiento(id_tratamiento):
    dao = ConsultasDao()
    try:
        if dao.deleteTratamiento(id_tratamiento):
            return jsonify(success=True, data=f"Tratamiento {id_tratamiento} eliminado.", error=None), 200
        return jsonify(success=False, error=f"No se encontró tratamiento con ID {id_tratamiento}."), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar tratamiento {id_tratamiento}: {str(e)}")
        return jsonify(success=False, error="Error interno al eliminar tratamiento."), 500
    
# ============================
# FICHA MÉDICA - Generar ficha médica completa del paciente
# ============================
@consultasapi.route('/ficha-medica/<int:id_paciente>', methods=['GET'])
def generarFichaMedica(id_paciente):
    dao = ConsultasDao()
    try:
        app.logger.info(f"📋 Generando ficha médica para paciente ID: {id_paciente}")
        datos = dao.getFichaMedicaPaciente(id_paciente)
        
        if datos:
            # ✅ Pasamos la fecha actual al template
            return render_template(
                'ficha_medica.html',
                datos=datos,
                now=datetime.now()
            )
        else:
            app.logger.warning("⚠️ No se encontraron datos para el paciente.")
            return jsonify({"success": False, "error": "No se encontraron datos para el paciente."}), 404
    except Exception as e:
        app.logger.error(f"❌ Error al generar ficha médica: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    

# ============================
# DIAGNÓSTICOS - Obtener diagnósticos por consulta_detalle
# ============================
@consultasapi.route('/Diagnostico/consulta-detalle/<int:id_consulta_detalle>', methods=['GET'])
def obtener_diagnosticos_por_detalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        app.logger.info(f"🔍 Buscando diagnósticos para consulta_detalle ID: {id_consulta_detalle}")
        diagnosticos = dao.getDiagnosticosByConsultaDetalle(id_consulta_detalle)
        
        if diagnosticos:
            app.logger.info(f"✅ Se encontraron {len(diagnosticos)} diagnósticos")
            return jsonify(success=True, data=diagnosticos, error=None), 200
        else:
            app.logger.warning(f"⚠️ No se encontraron diagnósticos para consulta_detalle {id_consulta_detalle}")
            return jsonify(success=False, error='No se encontraron diagnósticos', data=[]), 404
            
    except Exception as e:
        app.logger.error(f"❌ Error al obtener diagnósticos: {str(e)}")
        return jsonify(success=False, error=str(e)), 500


# ============================
# TRATAMIENTOS - Obtener tratamientos por consulta_detalle
# ============================
@consultasapi.route('/Tratamiento/consulta-detalle/<int:id_consulta_detalle>', methods=['GET'])
def obtener_tratamientos_por_detalle(id_consulta_detalle):
    dao = ConsultasDao()
    try:
        app.logger.info(f"🔍 Buscando tratamientos para consulta_detalle ID: {id_consulta_detalle}")
        tratamientos = dao.getTratamientosByConsultaDetalle(id_consulta_detalle)
        
        if tratamientos:
            app.logger.info(f"✅ Se encontraron {len(tratamientos)} tratamientos")
            return jsonify(success=True, data=tratamientos, error=None), 200
        else:
            app.logger.warning(f"⚠️ No se encontraron tratamientos para consulta_detalle {id_consulta_detalle}")
            return jsonify(success=False, error='No se encontraron tratamientos', data=[]), 404
            
    except Exception as e:
        app.logger.error(f"❌ Error al obtener tratamientos: {str(e)}")
        return jsonify(success=False, error=str(e)), 500


# ============================
# DIAGNÓSTICOS - Actualizar diagnóstico (ACTUALIZADO)
# ============================
@consultasapi.route('/Diagnostico/<int:id_diagnostico>', methods=['PUT'])
def actualizar_diagnostico(id_diagnostico):
    data = request.get_json() or {}
    dao = ConsultasDao()

    try:
        app.logger.info(f"📝 Actualizando diagnóstico ID: {id_diagnostico}")
        app.logger.debug(f"Datos recibidos: {data}")
        
        actualizado = dao.updateDiagnostico(id_diagnostico, data)
        
        if actualizado:
            app.logger.info(f"✅ Diagnóstico {id_diagnostico} actualizado correctamente")
            return jsonify(
                success=True, 
                data={**data, "id_diagnostico": id_diagnostico},
                message='Diagnóstico actualizado correctamente',
                error=None
            ), 200
        else:
            app.logger.warning(f"⚠️ No se encontró diagnóstico con ID {id_diagnostico}")
            return jsonify(
                success=False, 
                error=f'No se encontró diagnóstico con ID {id_diagnostico}'
            ), 404
    except ValueError as ve:
        es_duplicado = "Ya existe" in str(ve)
        codigo_http = 409 if es_duplicado else 400
        app.logger.warning(f"⚠️ Validación fallida al actualizar diagnóstico: {str(ve)}")
        return jsonify(
            success=False, 
            error=str(ve),
            type="duplicate" if es_duplicado else "validation"
        ), codigo_http
    except Exception as e:
        app.logger.error(f"❌ Error al actualizar diagnóstico: {str(e)}")
        return jsonify(success=False, error=str(e)), 500


# ============================
# TRATAMIENTOS - Actualizar tratamiento (ACTUALIZADO)
# ============================
@consultasapi.route('/Tratamiento/<int:id_tratamiento>', methods=['PUT'])
def actualizar_tratamiento(id_tratamiento):
    data = request.get_json() or {}
    dao = ConsultasDao()

    try:
        app.logger.info(f"📝 Actualizando tratamiento ID: {id_tratamiento}")
        app.logger.debug(f"Datos recibidos: {data}")
        
        actualizado = dao.updateTratamiento(id_tratamiento, data)
        
        if actualizado:
            app.logger.info(f"✅ Tratamiento {id_tratamiento} actualizado correctamente")
            return jsonify(
                success=True, 
                data={**data, "id_tratamiento": id_tratamiento},
                message='Tratamiento actualizado correctamente',
                error=None
            ), 200
        else:
            app.logger.warning(f"⚠️ No se encontró tratamiento con ID {id_tratamiento}")
            return jsonify(
                success=False, 
                error=f'No se encontró tratamiento con ID {id_tratamiento}'
            ), 404
    except ValueError as ve:
        es_duplicado = "Ya existe" in str(ve)
        codigo_http = 409 if es_duplicado else 400
        app.logger.warning(f"⚠️ Validación fallida al actualizar tratamiento: {str(ve)}")
        return jsonify(
            success=False, 
            error=str(ve),
            type="duplicate" if es_duplicado else "validation"
        ), codigo_http
    except Exception as e:
        app.logger.error(f"❌ Error al actualizar tratamiento: {str(e)}")
        return jsonify(success=False, error=str(e)), 500
    
    
