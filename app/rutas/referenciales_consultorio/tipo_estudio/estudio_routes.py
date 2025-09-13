from flask import Blueprint, render_template

estudiomod = Blueprint('estudio', __name__, template_folder='templates')

@estudiomod.route('/estudio-index')
def estudioIndex():
    return render_template('estudio-index.html')
