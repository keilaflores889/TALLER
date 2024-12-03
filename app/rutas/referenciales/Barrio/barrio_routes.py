from flask import Blueprint, render_template

barriomod = Blueprint('barrio', __name__, template_folder='templates')

@barriomod.route('/barrio-index')
def barrioIndex():
    return render_template('barrio-index.html')