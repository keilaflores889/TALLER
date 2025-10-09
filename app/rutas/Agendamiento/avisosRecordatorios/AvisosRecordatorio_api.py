from flask import Blueprint, jsonify, request, current_app as app
from app.dao.avisosRecordatorios.AvisosRecordatorioDao import AvisoRecordatorioDao
from app.Services.whatsapp_service import AvisoRecordatorioService, WhatsAppService
import threading

avisoapi = Blueprint('avisoapi', __name__, url_prefix='/api/v1')

dao = AvisoRecordatorioDao()

# ==========================================
#  ENDPOINTS ORIGINALES
# ==========================================

# Listar todos los avisos
@avisoapi.route('/avisos', methods=['GET'])
def listar_avisos():
    try:
        avisos = dao.getAvisos()
        return jsonify(success=True, data=avisos)
    except Exception as e:
        app.logger.error(f"Error en listar_avisos: {e}")
        return jsonify(success=False, error=str(e))

# Obtener aviso por id
@avisoapi.route('/avisos/<int:id_aviso>', methods=['GET'])
def get_aviso(id_aviso):
    try:
        aviso = dao.getAvisoById(id_aviso)
        if aviso:
            return jsonify(success=True, data=aviso)
        return jsonify(success=False, error="Aviso no encontrado")
    except Exception as e:
        app.logger.error(f"Error en get_aviso: {e}")
        return jsonify(success=False, error=str(e))

# Crear aviso
@avisoapi.route('/avisos', methods=['POST'])
def crear_aviso():
    data = request.get_json()
    try:
        id_aviso = dao.addAviso(data)
        if id_aviso:
            return jsonify(success=True, mensaje="Aviso creado", id=id_aviso)
        return jsonify(success=False, error="No se pudo crear aviso")
    except Exception as e:
        app.logger.error(f"Error en crear_aviso: {e}")
        return jsonify(success=False, error=str(e))

# Actualizar aviso
@avisoapi.route('/avisos/<int:id_aviso>', methods=['PUT'])
def actualizar_aviso(id_aviso):
    data = request.get_json()
    try:
        if dao.updateAviso(id_aviso, data):
            return jsonify(success=True, mensaje="Aviso actualizado")
        return jsonify(success=False, error="No se pudo actualizar aviso")
    except Exception as e:
        app.logger.error(f"Error en actualizar_aviso: {e}")
        return jsonify(success=False, error=str(e))

# Eliminar aviso
@avisoapi.route('/avisos/<int:id_aviso>', methods=['DELETE'])
def eliminar_aviso(id_aviso):
    try:
        if dao.deleteAviso(id_aviso):
            return jsonify(success=True, mensaje="Aviso eliminado")
        return jsonify(success=False, error="No se pudo eliminar aviso")
    except Exception as e:
        app.logger.error(f"Error en eliminar_aviso: {e}")
        return jsonify(success=False, error=str(e))


# ==========================================
#  ENDPOINTS PARA WHATSAPP
# ==========================================

# Enviar todos los avisos pendientes de WhatsApp
@avisoapi.route('/avisos/enviar-whatsapp', methods=['POST'])
def enviar_avisos_whatsapp():
    try:
        servicio = AvisoRecordatorioService()
        servicio.procesar_avisos_pendientes()
        return jsonify(success=True, mensaje="Proceso de envío completado.")
    except Exception as e:
        app.logger.error(f"Error en enviar_avisos_whatsapp: {e}")
        return jsonify(success=False, error=str(e))


@avisoapi.route('/avisos/<int:id_aviso>/enviar-whatsapp', methods=['POST'])
def enviar_aviso_individual(id_aviso):
    """Envía un aviso individual por WhatsApp de forma asíncrona"""
    try:
        aviso = dao.getAvisoById(id_aviso)
        if not aviso:
            return jsonify(success=False, error="Aviso no encontrado")
        
        if aviso.get('forma_envio') != 'WhatsApp':
            return jsonify(success=False, error="Este aviso no es de WhatsApp")
        
        # ✅ Ahora usamos el teléfono que ya viene en el aviso
        telefono = aviso.get('telefono_paciente')
        
        if not telefono:
            return jsonify(success=False, error="Paciente sin teléfono registrado")
        
        # Función para ejecutar en segundo plano
        def enviar_en_segundo_plano():
            try:
                ws = WhatsAppService()
                servicio = AvisoRecordatorioService()
                
                print(f"\n{'='*60}")
                print(f"Iniciando envío de aviso #{id_aviso}")
                print(f"{'='*60}\n")
                
                if ws.inicializar_navegador():
                    if ws.esperar_carga(timeout=240):
                        mensaje = servicio.formatear_mensaje(aviso)
                        if ws.enviar_mensaje(telefono, mensaje):
                            aviso['estado_envio'] = 'Enviado'
                            dao.updateAviso(id_aviso, aviso)
                            print(f"\n{'='*60}")
                            print(f"Mensaje enviado correctamente")
                            print(f"{'='*60}\n")
                        else:
                            aviso['estado_envio'] = 'Error'
                            dao.updateAviso(id_aviso, aviso)
                            print(f"\nError al enviar mensaje\n")
                    else:
                        aviso['estado_envio'] = 'Error'
                        dao.updateAviso(id_aviso, aviso)
                        print(f"\nNo se pudo conectar a WhatsApp Web\n")
                        ws.cerrar()
                else:
                    aviso['estado_envio'] = 'Error'
                    dao.updateAviso(id_aviso, aviso)
                    print(f"\nNo se pudo inicializar el navegador\n")
                    
            except Exception as e:
                print(f"\nError en proceso de segundo plano: {e}\n")
                try:
                    aviso['estado_envio'] = 'Error'
                    dao.updateAviso(id_aviso, aviso)
                except:
                    pass
        
        # Iniciar el thread en segundo plano
        thread = threading.Thread(target=enviar_en_segundo_plano)
        thread.daemon = True
        thread.start()
        
        # Responder inmediatamente al frontend
        return jsonify(
            success=True, 
            mensaje="Proceso iniciado. WhatsApp Web se abrirá en una ventana nueva. Escanea el QR y espera."
        )
            
    except Exception as e:
        app.logger.error(f"Error en enviar_aviso_individual: {e}")
        return jsonify(success=False, error=str(e))


@avisoapi.route('/avisos/estadisticas', methods=['GET'])
def estadisticas_avisos():
    """Obtiene estadísticas de los avisos"""
    try:
        avisos = dao.getAvisos()
        
        total = len(avisos)
        pendientes = len([a for a in avisos if a.get('estado_envio') == 'Pendiente'])
        enviados = len([a for a in avisos if a.get('estado_envio') == 'Enviado'])
        errores = len([a for a in avisos if a.get('estado_envio') == 'Error'])
        
        whatsapp = len([a for a in avisos if a.get('forma_envio') == 'WhatsApp'])
        gmail = len([a for a in avisos if a.get('forma_envio') == 'Gmail'])
        sms = len([a for a in avisos if a.get('forma_envio') == 'SMS'])
        
        # ✅ Agregar estadísticas de confirmación
        confirmados = len([a for a in avisos if a.get('estado_confirmacion') == 'Confirmado'])
        pendientes_conf = len([a for a in avisos if a.get('estado_confirmacion') == 'Pendiente'])
        cancelados = len([a for a in avisos if a.get('estado_confirmacion') == 'Cancelado'])
        
        return jsonify(
            success=True,
            data={
                'total': total,
                'por_estado': {
                    'pendientes': pendientes,
                    'enviados': enviados,
                    'errores': errores
                },
                'por_forma_envio': {
                    'whatsapp': whatsapp,
                    'gmail': gmail,
                    'sms': sms
                },
                'por_confirmacion': {
                    'confirmados': confirmados,
                    'pendientes': pendientes_conf,
                    'cancelados': cancelados
                }
            }
        )
    except Exception as e:
        app.logger.error(f"Error en estadisticas_avisos: {e}")
        return jsonify(success=False, error=str(e))