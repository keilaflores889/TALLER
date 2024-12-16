from flask import Blueprint, render_template

registrocmod = Blueprint('registcita', __name__, template_folder='templates')


@registrocmod.route('/registrarc-index')
def registrarcIndex():
    return render_template('registrarc-index.html')