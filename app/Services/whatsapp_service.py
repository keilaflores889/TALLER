from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
from datetime import datetime
from flask import current_app as app
from app.dao.avisosRecordatorios.AvisosRecordatorioDao import AvisoRecordatorioDao

class WhatsAppService:
    """Servicio para enviar mensajes por WhatsApp Web"""
    
    def __init__(self):
        self.driver = None
        self.conectado = False
        
    def inicializar_navegador(self):
        """Inicializa el navegador con WhatsApp Web"""
        if self.driver is not None:
            return True
        
        try:
            import os
        
            options = webdriver.ChromeOptions()
        
            # Usar SIEMPRE la misma carpeta de sesión (persistente)
            user_data_dir = os.path.join(os.getcwd(), 'whatsapp_session_persistente')
        
            options.add_argument(f'--user-data-dir={user_data_dir}')
            options.add_argument('--profile-directory=Default')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--start-maximized')
        
            print(f"Usando sesion persistente: {user_data_dir}")
        
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.driver.get('https://web.whatsapp.com')
            print("Esperando inicio de sesion en WhatsApp Web...")
            return True
        except Exception as e:
            print(f"Error al inicializar navegador: {e}")
            return False
    
    def esperar_carga(self, timeout=240):
        """Espera a que WhatsApp Web esté listo"""
        try:
            print("   Esperando que cargue WhatsApp Web...")
            
            # Espera inicial para que la página cargue
            time.sleep(5)
            
            tiempo_inicio = time.time()
            tiempo_limite = tiempo_inicio + timeout
            
            while time.time() < tiempo_limite:
                try:
                    # Busca cualquier indicador de que WhatsApp cargó
                    # 1. Campo de búsqueda (ya logueado)
                    campos = self.driver.find_elements(By.XPATH, '//div[@contenteditable="true"]')
                    if len(campos) > 0:
                        print("   WhatsApp Web conectado correctamente")
                        self.conectado = True
                        time.sleep(2)
                        return True
                    
                    # 2. Canvas del QR (necesita escaneo)
                    canvas = self.driver.find_elements(By.TAG_NAME, 'canvas')
                    if len(canvas) > 0:
                        print("   Codigo QR detectado - Escanea con tu telefono")
                        # Sigue esperando...
                    
                    time.sleep(2)
                    
                except Exception as e:
                    # Continúa intentando
                    time.sleep(2)
            
            # Si llegó aquí, se acabó el tiempo
            print("   Tiempo de espera agotado")
            self.conectado = False
            return False
            
        except Exception as e:
            print(f"   Error al esperar carga: {str(e)}")
            self.conectado = False
            return False
    
    def enviar_mensaje(self, numero, mensaje):
        """
        Envía un mensaje por WhatsApp
        Args:
            numero (str): Número con código de país sin signos (ej: 595981234567)
            mensaje (str): Texto del mensaje
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Limpia el número (elimina espacios, guiones, etc)
            numero_limpio = ''.join(filter(str.isdigit, str(numero)))
            
            mensaje_codificado = urllib.parse.quote(mensaje)
            url = f'https://web.whatsapp.com/send?phone={numero_limpio}&text={mensaje_codificado}'
            
            print(f"   Abriendo chat con {numero_limpio}...")
            self.driver.get(url)
            time.sleep(6)
            
            print("   Buscando boton de enviar...")
            
            # Intenta múltiples selectores
            selectores = [
                '//button[@aria-label="Enviar"]',
                '//button[@aria-label="Send"]',
                '//span[@data-icon="send"]',
                '//button[@data-tab="11"]',
                '//button[contains(@class, "send")]',
                '//div[@role="button"][@aria-label="Enviar"]',
                '//div[@role="button"][@aria-label="Send"]'
            ]
            
            boton_encontrado = False
            for i, selector in enumerate(selectores):
                try:
                    boton_enviar = WebDriverWait(self.driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    boton_enviar.click()
                    print(f"   Mensaje enviado (metodo {i+1})")
                    boton_encontrado = True
                    break
                except:
                    continue
            
            if not boton_encontrado:
                print("   Intentando metodo alternativo (Enter)...")
                try:
                    input_box = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                    )
                    input_box.click()
                    time.sleep(1)
                    input_box.send_keys(Keys.ENTER)
                    print("   Mensaje enviado con Enter")
                    boton_encontrado = True
                except Exception as e:
                    print(f"   Metodo alternativo fallo: {str(e)}")
                    
                    try:
                        print("   Ultimo intento...")
                        boton = self.driver.find_element(By.XPATH, '//button[.//span[@data-icon="send"]]')
                        boton.click()
                        print("   Mensaje enviado (ultimo intento)")
                        boton_encontrado = True
                    except:
                        print("   No se pudo enviar el mensaje")
            
            time.sleep(2)
            return boton_encontrado
            
        except Exception as e:
            print(f"   Error al enviar a {numero}: {str(e)}")
            return False
    
    def cerrar(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.conectado = False


class AvisoRecordatorioService:
    """Servicio principal para enviar recordatorios desde la BD"""
    
    def __init__(self):
        self.dao = AvisoRecordatorioDao()
        self.whatsapp = WhatsAppService()
    
    def formatear_mensaje(self, aviso):
        """
        Formatea el mensaje del recordatorio
        Args:
            aviso (dict): Datos del aviso con información del paciente
        Returns:
            str: Mensaje formateado para WhatsApp
        """
        if aviso.get('mensaje') and aviso['mensaje'].strip():
            return aviso['mensaje']
        
        paciente = aviso.get('paciente', 'Estimado paciente')
        fecha = aviso.get('fecha_cita', 'N/A')
        hora = aviso.get('hora_cita', 'N/A')
        personal = aviso.get('personal', 'Nuestro equipo medico')
        consultorio = aviso.get('nombre_consultorio', 'la clinica')
        
        mensaje = f"""Hola {paciente}!

Este es un recordatorio de tu cita medica:

Fecha: {fecha}
Hora: {hora}
Profesional: {personal}
Consultorio: {consultorio}

Por favor, confirma tu asistencia respondiendo este mensaje.

Si necesitas reagendar, contactanos con anticipacion.

Gracias!"""
        
        return mensaje
    
    def obtener_telefono_paciente(self, id_paciente):
        """
        Obtiene el teléfono del paciente desde la BD
        """
        from app.conexion.Conexion import Conexion
        
        sql = "SELECT telefono FROM paciente WHERE id_paciente = %s;"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_paciente,))
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
            return None
        except Exception as e:
            print(f"Error al obtener telefono: {e}")
            return None
        finally:
            cur.close()
            con.close()
    
    def procesar_avisos_pendientes(self):
        """Procesa y envía todos los avisos pendientes de WhatsApp"""
        print(f"\n{'='*60}")
        print(f"Procesando avisos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            avisos = self.dao.getAvisos()
            
            avisos_whatsapp = [
                a for a in avisos 
                if a.get('forma_envio') == 'WhatsApp' 
                and a.get('estado_envio') == 'Pendiente'
            ]
            
            if not avisos_whatsapp:
                print("No hay avisos de WhatsApp pendientes")
                return
            
            print(f"{len(avisos_whatsapp)} avisos para procesar\n")
            
            if not self.whatsapp.inicializar_navegador():
                print("No se pudo inicializar el navegador")
                return
            
            if not self.whatsapp.esperar_carga():
                print("No se pudo conectar a WhatsApp Web")
                self.whatsapp.cerrar()
                return
            
            exitosos = 0
            fallidos = 0
            
            for aviso in avisos_whatsapp:
                id_aviso = aviso['id_aviso']
                paciente = aviso.get('paciente', 'Paciente')
                
                print(f"Procesando aviso #{id_aviso} - {paciente}")
                
                aviso_completo = self.dao.getAvisoById(id_aviso)
                if not aviso_completo:
                    print(f"   No se encontro el aviso\n")
                    continue
                
                id_paciente = aviso_completo.get('id_paciente')
                telefono = self.obtener_telefono_paciente(id_paciente)
                
                if not telefono:
                    print(f"   Paciente sin telefono registrado\n")
                    self._marcar_error(id_aviso)
                    fallidos += 1
                    continue
                
                mensaje = self.formatear_mensaje(aviso)
                
                print(f"   Enviando a: {telefono}")
                if self.whatsapp.enviar_mensaje(telefono, mensaje):
                    self._marcar_enviado(id_aviso)
                    exitosos += 1
                    print(f"   Enviado correctamente\n")
                else:
                    self._marcar_error(id_aviso)
                    fallidos += 1
                    print(f"   Error en envio\n")
                
                time.sleep(3)
            
            print(f"\n{'='*60}")
            print(f"Resumen:")
            print(f"   Exitosos: {exitosos}")
            print(f"   Fallidos: {fallidos}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"Error general al procesar avisos: {str(e)}")
    
    def _marcar_enviado(self, id_aviso):
        """Marca un aviso como enviado"""
        try:
            aviso = self.dao.getAvisoById(id_aviso)
            if aviso:
                aviso['estado_envio'] = 'Enviado'
                self.dao.updateAviso(id_aviso, aviso)
        except Exception as e:
            print(f"Error al marcar como enviado: {e}")
    
    def _marcar_error(self, id_aviso):
        """Marca un aviso como error"""
        try:
            aviso = self.dao.getAvisoById(id_aviso)
            if aviso:
                aviso['estado_envio'] = 'Error'
                self.dao.updateAviso(id_aviso, aviso)
        except Exception as e:
            print(f"Error al marcar como error: {e}")
    
    def ejecutar_una_vez(self):
        """Ejecuta el envío una sola vez"""
        try:
            self.procesar_avisos_pendientes()
        finally:
            input("\nPresiona Enter para cerrar el navegador...")
            self.whatsapp.cerrar()
    
    def mantener_activo(self):
        """Mantiene el servicio activo"""
        print("Servicio de WhatsApp iniciado")
        print("Ejecuta este script cada vez que quieras enviar avisos pendientes\n")
        
        self.procesar_avisos_pendientes()
        
        print("\nProceso completado")
        print("El navegador permanecera abierto para mantener la sesion")
        print("Presiona Ctrl+C para cerrar\n")
        
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nCerrando servicio...")
            self.whatsapp.cerrar()


if __name__ == "__main__":
    servicio = AvisoRecordatorioService()
    servicio.ejecutar_una_vez()