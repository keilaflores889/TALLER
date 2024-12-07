from flask import Blueprint, render_template

registrocmod = Blueprint('RegistCita', __name__, template_folder='templates')


@registrocmod.route('/RegistrarC-index')
def registrarcIndex():
    return render_template('RegistrarC-index.html')