from flask import Blueprint, render_template, session, request, redirect, url_for, flash, current_app as app
from werkzeug.security import check_password_hash
from app.dao.login.loginDao import LoginDao

logmod = Blueprint('login', __name__, template_folder='templates')

@logmod.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # lo que viene del formulario
        usuario_nombre = request.form['usuario_nombre']
        usuario_clave = request.form['usuario_clave']
        # hacer la validación contra la bd
        login_dao = LoginDao()
        usuario_encontrado = login_dao.buscarUsuario(usuario_nombre)
        if usuario_encontrado and 'usu_nombre' in usuario_encontrado:
            password_hash_del_usuario = usuario_encontrado['usu_clave']
            # if check_password_hash(
            if usuario_clave == password_hash_del_usuario:
                #pwhash=password_hash_del_usuario, password=usuario_clave):
                # Crear la sesión
                session.clear()  # Limpiar cualquier sesión previa
                session.permanent = True
                session['idusuario'] = usuario_encontrado['idusuario']
                session['usu_nombre'] = usuario_encontrado['usu_nombre']
                # session['per_nombre'] = usuario_encontrado['per_nombre']
                # session['grupo'] = usuario_encontrado['grupo']
                return redirect(url_for('login.vista'))
            else:
                flash('Contraseña incorrecta.', 'warning')
        else:
            flash('Error de login, no existe este usuario.', 'warning')
        return redirect(url_for('login.login'))  
    elif request.method == 'GET':
        return render_template('login.html')
    else:
        return render_template('login.html')

@logmod.route('/logout')
def logout():
    session.clear() # limpiar cualquier sesión previa
    flash('Sesion cerrada', 'warning')
    return redirect(url_for('login.login'))

@logmod.route('/vista')
def vista():
    if 'usu_nombre' in session:
        return render_template('vista-index.html')
    else:
        return redirect(url_for('login.login'))