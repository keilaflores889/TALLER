from flask import Blueprint, render_template

vistagendamod = Blueprint('vistaAGENDAR', __name__, template_folder='templates')

@vistagendamod.route('/vistaAGENDAR-index')
def vistaAGENDARIndex():
    return render_template('vistaAGENDAR-index.html')