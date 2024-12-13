from flask import Blueprint, render_template

agendmod = Blueprint('agendmedica', __name__, template_folder='templates')


@agendmod.route('/agenda-index')
def agendaIndex():
    return render_template('agenda-index.html')