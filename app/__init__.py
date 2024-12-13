from flask import Flask
from flask import render_template

app = Flask(__name__)

# importar referenciales
from app.rutas.login.login_routes import loginmod
from app.rutas.login.vista_routes import vistamod
from app.rutas.referenciales.ciudad.ciudad_routes import ciumod #ciudad
from app.rutas.referenciales.Barrio.barrio_routes import barriomod
from app.rutas.referenciales.paises.pais_routes import paimod   #pais
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


#importacion de cita
from app.rutas.Agendamiento.RegistCita.RegistrarC_routes import registrocmod
from app.rutas.Agendamiento.vistaAGENDAR.vistaAGENDAR_routes import vistagendamod
from app.rutas.Agendamiento.agendmedica.agenda_routes import agendmod
from app.rutas.Agendamiento.RegisPaciente.RegistroP_routes import registropmod
from app.rutas.Agendamiento.medico.medico_routes import medicomod
# registrar referenciales
modulo0 = '/referenciales' 
app.register_blueprint(loginmod, url_prefix=f'{modulo0}/login') 
app.register_blueprint(vistamod, url_prefix=f'{modulo0}/login') 
app.register_blueprint(ciumod, url_prefix=f'{modulo0}/ciudad') #ciudad
app.register_blueprint(barriomod, url_prefix=f'{modulo0}/barrio')
app.register_blueprint(paimod, url_prefix=f'{modulo0}/paises') #pais
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


# registrar agendamientos
modulo0 = '/agendamientos'

app.register_blueprint(registrocmod, url_prefix=f'{modulo0}/RegistCita')  # cita
app.register_blueprint(vistagendamod, url_prefix=f'{modulo0}/cita')  # cita
app.register_blueprint(agendmod, url_prefix=f'{modulo0}/agendmedica')  # cita
app.register_blueprint(registropmod, url_prefix=f'{modulo0}/RegisPaciente')
app.register_blueprint(medicomod, url_prefix=f'{modulo0}/medico')
#ciudad
from app.rutas.referenciales.ciudad.ciudad_api import ciuapi

#pais
from app.rutas.referenciales.paises.pais_api import paisapi

from app.rutas.referenciales.Barrio.barrio_api import barrioapi

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





#cita

from app.rutas.Agendamiento.RegistCita.RegistrarC_api import regiscitaapi
from app.rutas.Agendamiento.agendmedica.agenda_api import agendaapi
from app.rutas.Agendamiento.RegisPaciente.RegistrarP_api import registropapi
from app.rutas.Agendamiento.medico.medico_api import medicoapi

# APIS v1
#Ciudad
version1 = '/api/v1'
app.register_blueprint(ciuapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(barrioapi, url_prefix=version1)

#Pais
version1 = '/api/v1'
app.register_blueprint(paisapi, url_prefix=version1)

#nacionalidad
version1 = '/api/v1'
app.register_blueprint(nacioapi, url_prefix=version1)

#ocupacion
version1 = '/api/v1'
app.register_blueprint(ocupapi, url_prefix=version1)

#Estado civil
version1 = '/api/v1'
app.register_blueprint(estacivapi, url_prefix=version1)

#sexo
version1 = '/api/v1'
app.register_blueprint(sexapi, url_prefix=version1)

#Estado de la cita
version1 = '/api/v1'
app.register_blueprint(estacitapi, url_prefix=version1)

#persona
version1 = '/api/v1'
app.register_blueprint(persapi, url_prefix=version1)

#especialidad
version1 = '/api/v1'
app.register_blueprint(especiapi, url_prefix=version1)

#dia
version1 = '/api/v1'
app.register_blueprint(diaapi, url_prefix=version1)

#duracion de la consulta
version1 = '/api/v1'
app.register_blueprint(duraconsuapi, url_prefix=version1)



#turno
version1 = '/api/v1'
app.register_blueprint(turnoapi, url_prefix=version1)



# Cita



version1 = '/api/v1'
app.register_blueprint(regiscitaapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(agendaapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(registropapi, url_prefix=version1)

version1 = '/api/v1'
app.register_blueprint(medicoapi, url_prefix=version1)



@app.route('/login')
def login():
    return render_template('login-index.html')

@app.route('/vista')
def vista():
    return render_template('vista-index.html')