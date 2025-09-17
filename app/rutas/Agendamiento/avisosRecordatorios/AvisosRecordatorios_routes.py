from flask import Blueprint, render_template

avisomod = Blueprint('avisosRecordatorios', __name__, template_folder='templates')


@avisomod.route('/AvisosRecordatorios-index')
def AvisosRecordatoriosIndex():
    return render_template('AvisosRecordatorios-index.html')