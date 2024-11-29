from flask import Blueprint, render_template

registropmod = Blueprint('RegisPaciente', __name__, template_folder='templates')


@registropmod.route('/RegistrarP-index')
def registrarpIndex():
    return render_template('RegistrarP-index.html')