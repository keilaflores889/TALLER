from flask import Flask
from flask import render_template
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

# creamos el token
csrf = CSRFProtect()
csrf.init_app(app)

# inicializar el secret key
app.secret_key = b'_5#y2L"F6Q7z\n\xec]/'

# Establecer duración de la sesión, 15 minutos
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

# importar modulo de seguridad
from app.rutas.login.login_routes import logmod
app.register_blueprint(logmod)


# importar referenciales agendamiento
from app.rutas.vista.vista_routes import vistamod #vista principal
from app.rutas.referenciales.ciudad.ciudad_routes import ciumod #ciudad

from app.rutas.referenciales.cargo.cargo_routes import cargomod #cargo
from app.rutas.referenciales.consultorio.consultorio_routes import consulmod
from app.rutas.referenciales.paises.pais_routes import paimod   #pais
from app.rutas.referenciales.disponibilidad_horaria.disponibilidad_routes import disponibilidadmod
from app.rutas.referenciales.nacionalidad.nacionalidad_routes import naciomod  #nacionalidad
from app.rutas.referenciales.ocupacion.ocupacion_routes import ocupmod  #ocupacion
from app.rutas.referenciales.estado_civil.estado_civil_routes import estacivmod  #estado civil
from app.rutas.referenciales.sexo.sexo_routes import sexmod  #sexo
from app.rutas.referenciales.estado_cita.estado_cita_routes import estacitmod  #estado de la cita
from app.rutas.referenciales.persona.persona_routes import persmod  #persona
from app.rutas.referenciales.especialidad.especialidad_routes import especimod  #especialidad
from app.rutas.referenciales.dia.dia_routes import diamod  #dia
from app.rutas.referenciales.duracion_consulta.duracion_consulta_routes import duraconsumod  #duracion de la consulta
from app.rutas.referenciales.turno.turno_routes import turmod  #turno



#importacion de modulo de agendamiento
from app.rutas.Agendamiento.registcita.registrarc_routes import registrocmod
from app.rutas.Agendamiento.agendmedica.agenda_routes import agendmod
from app.rutas.Agendamiento.regispaciente.registrop_routes import registropmod
from app.rutas.Agendamiento.medico.medico_routes import medicomod
from app.rutas.Agendamiento.personal.personal_routes import personalmod
from app.rutas.Agendamiento.avisosRecordatorios.AvisosRecordatorios_routes import avisomod
from app.rutas.Agendamiento.ficha_medica.ficha_medica_routes import fichamod

from app.rutas.Agendamiento.odontograma.odontograma_routes import odontogramamod

#referenciales de consultorio
from app.rutas.referenciales_consultorio.medicamento.medicamento_routes import medicamentomod
from app.rutas.referenciales_consultorio.sintoma.sintoma_routes import sintomod
from app.rutas.referenciales_consultorio.tipo_analisis.analisis_routes import analisismod
from app.rutas.referenciales_consultorio.tipo_estudio.estudio_routes import estudiomod
from app.rutas.referenciales_consultorio.tipo_procedimiento_medico.procedimiento_routes import procedimientomod
from app.rutas.referenciales_consultorio.tipo_diagnostico.tipo_diagnostico_routes import diagnosticomod

#movimientos modulo consultorio
from app.rutas.ModuloConsultorio.RegisConsulta.consulta_routes import consultamod
from app.rutas.ModuloConsultorio.RegisDiagnostico.diagnostico_routes import regisdiagnosticomod
from app.rutas.ModuloConsultorio.RegisTratamiento.tratamiento_routes import registratamientomod

# registrar referenciales
modulo0 = '/referenciales' 
app.register_blueprint(vistamod, url_prefix=f'{modulo0}/vista') 
app.register_blueprint(ciumod, url_prefix=f'{modulo0}/ciudad') #ciudad
app.register_blueprint(cargomod, url_prefix=f'{modulo0}/cargo') #cargo
app.register_blueprint(consulmod, url_prefix=f'{modulo0}/consultorio')
app.register_blueprint(paimod, url_prefix=f'{modulo0}/paises') #pais
app.register_blueprint(disponibilidadmod, url_prefix=f'{modulo0}/disponibilidad')
app.register_blueprint(naciomod, url_prefix=f'{modulo0}/nacionalidad')  #nacionalidad
app.register_blueprint(ocupmod, url_prefix=f'{modulo0}/ocupacion')  #ocupacion
app.register_blueprint(estacivmod, url_prefix=f'{modulo0}/estadocivil')  #estado civil
app.register_blueprint(sexmod, url_prefix=f'{modulo0}/sexo')  #sexo
app.register_blueprint(estacitmod, url_prefix=f'{modulo0}/estadocita')  #estado de la cita
app.register_blueprint(persmod, url_prefix=f'{modulo0}/persona') #persona
app.register_blueprint(especimod, url_prefix=f'{modulo0}/especialidad') #especialidad
app.register_blueprint(diamod, url_prefix=f'{modulo0}/dia') #dia
app.register_blueprint(duraconsumod, url_prefix=f'{modulo0}/duracionconsulta') #duracion de la consulta
app.register_blueprint(turmod, url_prefix=f'{modulo0}/turno') #turno


# registrar referenciales de consultorio
modulo0 = '/referenciales_consultorio'
app.register_blueprint(medicamentomod, url_prefix=f'{modulo0}/medicamento')
app.register_blueprint(sintomod, url_prefix=f'{modulo0}/sintoma')
app.register_blueprint(analisismod, url_prefix=f'{modulo0}/analisis')
app.register_blueprint(estudiomod, url_prefix=f'{modulo0}/estudio')
app.register_blueprint(procedimientomod, url_prefix=f'{modulo0}/procedimiento')
app.register_blueprint(diagnosticomod, url_prefix=f'{modulo0}/diagnostico')

# registrar movimientos consultorios
modulo0 = '/Moduloconsultorios'
app.register_blueprint(consultamod, url_prefix=f'{modulo0}/consultorios')
app.register_blueprint(regisdiagnosticomod, url_prefix=f'{modulo0}/Diagnosticos')
app.register_blueprint(registratamientomod, url_prefix=f'{modulo0}/tratamiento')

# registrar agendamientos
modulo0 = '/agendamientos'
app.register_blueprint(registrocmod, url_prefix=f'{modulo0}/registcita')  # cita
app.register_blueprint(agendmod, url_prefix=f'{modulo0}/agendmedica')  # cita
app.register_blueprint(registropmod, url_prefix=f'{modulo0}/registrop')
app.register_blueprint(medicomod, url_prefix=f'{modulo0}/medico')
app.register_blueprint(personalmod, url_prefix=f'{modulo0}/personal')

app.register_blueprint(avisomod, url_prefix=f'{modulo0}/avisos')
app.register_blueprint(fichamod, url_prefix=f'{modulo0}/ficha')
app.register_blueprint(odontogramamod, url_prefix=f'{modulo0}/odontograma')

from app.rutas.referenciales.disponibilidad_horaria.disponibilidad_api import disponibilidadapi
#ciudad
from app.rutas.referenciales.ciudad.ciudad_api import ciuapi

from app.rutas.referenciales.consultorio.consultorio_api import consultorioapi

#cargo
from app.rutas.referenciales.cargo.cargo_api import cargoapi
#pais
from app.rutas.referenciales.paises.pais_api import paisapi
#nacionalidad
from app.rutas.referenciales.nacionalidad.nacionalidad_api import nacioapi
#nacionalidad
from app.rutas.referenciales.ocupacion.ocupacion_api import ocupapi
#estado civil
from app.rutas.referenciales.estado_civil.estado_civil_api import estacivapi
#sexo
from app.rutas.referenciales.sexo.sexo_api import sexapi
#estado de la cita
from app.rutas.referenciales.estado_cita.estado_cita_api import estacitapi
#persona
from app.rutas.referenciales.persona.persona_api import persapi
#especialidad
from app.rutas.referenciales.especialidad.especialidad_api import especiapi
#dia
from app.rutas.referenciales.dia.dia_api import diaapi
#duracion de la consulta
from app.rutas.referenciales.duracion_consulta.duracion_consulta_api import duraconsuapi
#turno
from app.rutas.referenciales.turno.turno_api import turnoapi





#agendamiento
from app.rutas.Agendamiento.registcita.registrarc_api import regiscitaapi
from app.rutas.Agendamiento.agendmedica.agenda_api import agendaapi
from app.rutas.Agendamiento.regispaciente.registrarp_api import pacienteapi
from app.rutas.Agendamiento.medico.medico_api import medicoapi
from app.rutas.Agendamiento.personal.personal_api import personalapi

from app.rutas.Agendamiento.avisosRecordatorios.AvisosRecordatorio_api import avisoapi
from app.rutas.Agendamiento.ficha_medica.ficha_medica_api import fichaapi

from app.rutas.Agendamiento.odontograma.odontograma_api import odontogramaapi
#consultorio referenciales
from app.rutas.referenciales_consultorio.medicamento.medicamento_api import medicamentoapi
from app.rutas.referenciales_consultorio.sintoma.sintoma_api import sintomaapi
from app.rutas.referenciales_consultorio.tipo_analisis.analisis_api import analisisapi
from app.rutas.referenciales_consultorio.tipo_estudio.estudio_api import estudioapi
from app.rutas.referenciales_consultorio.tipo_procedimiento_medico.procedimiento_api import procedimientoapi
from app.rutas.referenciales_consultorio.tipo_diagnostico.tipo_diagnostico_api import diagnosticoapi

#movimientos modulo consultorio
from app.rutas.ModuloConsultorio.RegisConsulta.consulta_api import consultasapi
from app.rutas.ModuloConsultorio.RegisDiagnostico.diagnostico_api import Rdiagnosticoapi
from app.rutas.ModuloConsultorio.RegisTratamiento.tratamiento_api import tratamientoapi

# APIS v1
#Ciudad
version1 = '/api/v1'
app.register_blueprint(ciuapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(consultorioapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(disponibilidadapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(cargoapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(personalapi, url_prefix=version1)

#Pais
app.register_blueprint(paisapi, url_prefix=version1)

#nacionalidad

app.register_blueprint(nacioapi, url_prefix=version1)

#ocupacion

app.register_blueprint(ocupapi, url_prefix=version1)

#Estado civil

app.register_blueprint(estacivapi, url_prefix=version1)

#sexo

app.register_blueprint(sexapi, url_prefix=version1)

#Estado de la cita

app.register_blueprint(estacitapi, url_prefix=version1)

#persona

app.register_blueprint(persapi, url_prefix=version1)

#especialidad

app.register_blueprint(especiapi, url_prefix=version1)

#dia

app.register_blueprint(diaapi, url_prefix=version1)

#duracion de la consulta
app.register_blueprint(duraconsuapi, url_prefix=version1)

#turno
app.register_blueprint(turnoapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(odontogramaapi, url_prefix=version1)
# Cita

version1 = '/api/v1'
app.register_blueprint(regiscitaapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(agendaapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(pacienteapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(medicoapi, url_prefix=version1)

app.register_blueprint(avisoapi, url_prefix=version1)

app.register_blueprint(fichaapi, url_prefix=version1)

app.register_blueprint(estudioapi, url_prefix=version1)

#referenciales consultorio
version1 = '/api/v1'
app.register_blueprint(medicamentoapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(sintomaapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(analisisapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(procedimientoapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(diagnosticoapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(tratamientoapi, url_prefix=version1)

#movimientos modulo consultorio
version1 = '/api/v1'
app.register_blueprint(consultasapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(Rdiagnosticoapi, url_prefix=version1)

@app.route('/login')
def login():
    return render_template('login-index.html')

@app.route('/vista')
def vista():
    return render_template('vista-index.html')