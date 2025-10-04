from flask import Blueprint, render_template

regisdiagnosticomod = Blueprint('Diagnosticos', __name__, template_folder='templates')

@regisdiagnosticomod.route('/Diagnosticos-index')
def DiagnosticoIndex():
    return render_template('Diagnosticos-index.html')