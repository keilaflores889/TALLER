from flask import Blueprint, render_template

personalmod = Blueprint('personal', __name__, template_folder='templates')


@personalmod.route('/personal-index')
def personalIndex():
    return render_template('personal-index.html')