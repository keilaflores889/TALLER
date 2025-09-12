from flask import Blueprint, render_template

analisismod = Blueprint('analisis', __name__, template_folder='templates')

@analisismod.route('/analisis-index')
def analisisIndex():
    return render_template('analisis-index.html')
