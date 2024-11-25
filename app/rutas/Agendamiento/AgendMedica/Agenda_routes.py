from flask import Blueprint, render_template

agendmod = Blueprint('AgendMedica', __name__, template_folder='templates')


@agendmod.route('/Agenda-index')
def agendaIndex():
    return render_template('Agenda-index.html')