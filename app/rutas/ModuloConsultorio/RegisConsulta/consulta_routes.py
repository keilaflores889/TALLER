from flask import Blueprint, render_template

consultamod = Blueprint('consultas', __name__, template_folder='templates')


@consultamod.route('/consultas-index')
def consultaIndex():
    return render_template('consultas-index.html')