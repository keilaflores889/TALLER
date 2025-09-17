from flask import Blueprint, render_template

fichamod = Blueprint('ficha', __name__, template_folder='templates')


@fichamod.route('/ficha-index')
def fichaIndex():
    return render_template('ficha-index.html')