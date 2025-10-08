from flask import Blueprint, render_template

registratamientomod = Blueprint('tratamiento', __name__, template_folder='templates')

@registratamientomod.route('/tratamiento-index')
def TratamientoIndex():
    return render_template('tratamiento-index.html')