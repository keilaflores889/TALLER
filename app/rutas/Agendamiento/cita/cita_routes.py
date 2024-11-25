from flask import Blueprint, render_template, jsonify
from app.dao.referenciales.cita.CitaDao import CitaDao

citamod = Blueprint('cita', __name__, template_folder='templates')

@citamod.route('/cita-index')
def citaIndex():
    citadao = CitaDao()
    return render_template('cita-index.html', lista_citas=citadao.getCitas())
