from flask import Blueprint, render_template

registropmod = Blueprint('regispersona', __name__, template_folder='templates')


@registropmod.route('/registrarp-index')
def registrarpIndex():
    return render_template('registrarp-index.html')