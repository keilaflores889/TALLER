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
        
        servicio = AvisoRecordatorioService()
        telefono = servicio.obtener_telefono_paciente(aviso['id_paciente'])
        
        if not telefono:
            return jsonify(success=False, error="Paciente sin teléfono registrado")
        
        # ✅ Capturar la instancia de la app ANTES del thread
        app_instance = app._get_current_object()
        
        # Función para ejecutar en segundo plano
        def enviar_en_segundo_plano(app_ctx):
            """Ejecuta el envío dentro del contexto de Flask"""
            with app_ctx.app_context():  # ✅ Agregar contexto
                ws = None
                try:
                    ws = WhatsAppService()
                    print(f"\n{'='*60}")
                    print(f"Iniciando envío de aviso #{id_aviso}")
                    print(f"{'='*60}\n")
                    
                    if ws.inicializar_navegador():
                        if ws.esperar_carga(timeout=240):
                            # Generar el mensaje automático
                            print(f"📝 Generando mensaje automático...")
                            mensaje_generado = servicio.formatear_mensaje(aviso)
                            print(f"✅ Mensaje generado ({len(mensaje_generado)} caracteres)")
                            print(f"Primeros 150 chars: {mensaje_generado[:150]}...")
                            
                            # Enviar por WhatsApp
                            if ws.enviar_mensaje(telefono, mensaje_generado):
                                print(f"✅ Mensaje enviado por WhatsApp")
                                
                                # Guardar el mensaje generado en la BD
                                print(f"💾 Guardando mensaje generado en BD...")
                                datos_actualizacion = {
                                    'id_paciente': aviso['id_paciente'],
                                    'id_personal': aviso['id_personal'],
                                    'id_medico': aviso.get('id_medico'),
                                    'codigo': aviso.get('codigo'),
                                    'fecha_cita': aviso['fecha_cita'],
                                    'hora_cita': aviso['hora_cita'],
                                    'forma_envio': aviso['forma_envio'],
                                    'mensaje': mensaje_generado,
                                    'estado_envio': 'Enviado',
                                    'estado_confirmacion': aviso.get('estado_confirmacion', 'Pendiente')
                                }
                                
                                resultado = dao.updateAviso(id_aviso, datos_actualizacion)
                                
                                if resultado:
                                    print(f"✅ Mensaje guardado en BD correctamente")
                                    print(f"   Longitud guardada: {len(mensaje_generado)} caracteres")
                                else:
                                    print(f"❌ Error al guardar en BD")
                                
                                print(f"\n{'='*60}")
                                print(f"✅ Proceso completado:")
                                print(f"   - Mensaje enviado por WhatsApp")
                                print(f"   - Mensaje guardado en BD")
                                print(f"   - Ventana mantenida abierta")
                                print(f"{'='*60}\n")
                                
                            else:
                                print(f"❌ Error al enviar mensaje")
                                dao.updateAviso(id_aviso, {
                                    **aviso,
                                    'estado_envio': 'Error'
                                })
                                if ws:
                                    ws.cerrar()
                        else:
                            print(f"❌ No se pudo conectar a WhatsApp Web")
                            dao.updateAviso(id_aviso, {
                                **aviso,
                                'estado_envio': 'Error'
                            })
                            if ws:
                                ws.cerrar()
                    else:
                        print(f"❌ No se pudo inicializar el navegador")
                        dao.updateAviso(id_aviso, {
                            **aviso,
                            'estado_envio': 'Error'
                        })
                        
                except Exception as e:
                    print(f"\n❌ Error en proceso de segundo plano: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        dao.updateAviso(id_aviso, {
                            **aviso,
                            'estado_envio': 'Error'
                        })
                    except:
                        pass
                    if ws:
                        ws.cerrar()
        
        # ✅ Iniciar el thread pasando el contexto de la app
        thread = threading.Thread(target=enviar_en_segundo_plano, args=(app_instance,))
        thread.daemon = False
        thread.start()
        
        # Responder inmediatamente al frontend
        return jsonify(
            success=True, 
            mensaje="Proceso iniciado. WhatsApp Web se abrirá en una ventana nueva."
        )
            
    except Exception as e:
        app.logger.error(f"Error en enviar_aviso_individual: {e}")
        return jsonify(success=False, error=str(e))

@avisoapi.route('/avisos/estadisticas', methods=['GET'])
def estadisticas_avisos():
    """Obtiene estadísticas de los avisos"""
    try:
        avisos = dao.getAvisos()
        
        app.logger.info(f"📊 Total de avisos obtenidos: {len(avisos)}")
        
        # Debug: Ver estructura del primer aviso
        if avisos:
            app.logger.info(f"📋 Ejemplo de aviso: {avisos[0]}")
        
        total = len(avisos)
        
        # Contar por estado de envío
        pendientes = sum(1 for a in avisos if a.get('estado_envio') == 'Pendiente')
        enviados = sum(1 for a in avisos if a.get('estado_envio') == 'Enviado')
        errores = sum(1 for a in avisos if a.get('estado_envio') == 'Error')
        
        # Contar por forma de envío
        whatsapp = sum(1 for a in avisos if a.get('forma_envio') == 'WhatsApp')
        gmail = sum(1 for a in avisos if a.get('forma_envio') == 'Gmail')
        sms = sum(1 for a in avisos if a.get('forma_envio') == 'SMS')
        
        # Contar por confirmación
        confirmados = sum(1 for a in avisos if a.get('estado_confirmacion') == 'Confirmado')
        pendientes_conf = sum(1 for a in avisos if a.get('estado_confirmacion') == 'Pendiente')
        cancelados = sum(1 for a in avisos if a.get('estado_confirmacion') == 'Cancelado')
        
        resultado = {
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
        
        app.logger.info(f"✅ Estadísticas calculadas: {resultado}")
        
        return jsonify(success=True, data=resultado)
        
    except Exception as e:
        app.logger.error(f"❌ Error en estadisticas_avisos: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify(success=False, error=str(e)), 500
    
@avisoapi.route('/avisos/<int:id_aviso>/mensaje-preview', methods=['GET'])
def preview_mensaje(id_aviso):
    """Genera el preview del mensaje automático sin enviarlo"""
    try:
        aviso = dao.getAvisoById(id_aviso)
        if not aviso:
            return jsonify(success=False, error="Aviso no encontrado")
        
        servicio = AvisoRecordatorioService()
        mensaje = servicio.formatear_mensaje(aviso)
        
        return jsonify(success=True, mensaje=mensaje)
    except Exception as e:
        app.logger.error(f"Error en preview_mensaje: {e}")
        return jsonify(success=False, error=str(e))
    
# ==========================================
#  VALIDACIÓN DE DUPLICADOS
# ==========================================
@avisoapi.route('/avisos/verificar-duplicado', methods=['POST'])
def verificar_duplicado():
    """Verifica si existe un aviso duplicado"""
    try:
        data = request.get_json()
        
        id_paciente = data.get('id_paciente')
        id_medico = data.get('id_medico')
        fecha_cita = data.get('fecha_cita')
        hora_cita = data.get('hora_cita')
        id_aviso_excluir = data.get('id_aviso_excluir')
        
        if not id_paciente or not fecha_cita or not hora_cita:
            return jsonify(
                success=False, 
                error="Faltan parámetros obligatorios"
            ), 400
        
        duplicado = dao.existeDuplicado(
            id_paciente=id_paciente,
            id_medico=id_medico,
            fecha_cita=fecha_cita,
            hora_cita=hora_cita,
            id_aviso_excluir=id_aviso_excluir
        )
        
        return jsonify(success=True, duplicado=duplicado)
        
    except Exception as e:
        app.logger.error(f"Error en verificar_duplicado: {e}")
        return jsonify(success=False, error=str(e)), 500