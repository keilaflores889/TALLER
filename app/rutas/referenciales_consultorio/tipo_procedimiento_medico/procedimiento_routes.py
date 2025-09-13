from flask import Blueprint, render_template

procedimientomod = Blueprint('procedimiento', __name__, template_folder='templates')

@procedimientomod.route('/procedimiento-index')
def procedimientoIndex():
    return render_template('procedimiento-index.html')
