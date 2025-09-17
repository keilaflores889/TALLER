from flask import Blueprint, request, jsonify, current_app as app
from app.dao.usuario.usuarioDao import UsuarioDao

usuarioapi = Blueprint('usuarioapi', __name__)

# Listar usuarios
@usuarioapi.route('/usuarios', methods=['GET'])
def getUsuarios():
    dao = UsuarioDao()
    try:
        usuarios = dao.getUsuarios()
        return jsonify({'success': True, 'data': usuarios, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener usuarios: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

# Obtener usuario por ID
@usuarioapi.route('/usuarios/<int:id_usuario>', methods=['GET'])
def getUsuario(id_usuario):
    dao = UsuarioDao()
    try:
        usuario = dao.getUsuarioById(id_usuario)
        if usuario:
            return jsonify({'success': True, 'data': usuario, 'error': None}), 200
        return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener usuario: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

# Agregar usuario
@usuarioapi.route('/usuarios', methods=['POST'])
def addUsuario():
    data = request.get_json() or {}
    campos = ['nickname', 'clave', 'estado']
    faltantes = [c for c in campos if c not in data or not str(data[c]).strip()]
    if faltantes:
        return jsonify({'success': False, 'error': f'Faltan campos: {", ".join(faltantes)}'}), 400
    dao = UsuarioDao()
    usuario_id = dao.guardarUsuario(data['nickname'], data['clave'], data['estado'])
    if usuario_id:
        return jsonify({'success': True, 'data': {'id_usuario': usuario_id, 'nickname': data['nickname'], 'estado': data['estado']}, 'error': None}), 201
    return jsonify({'success': False, 'error': 'No se pudo guardar el usuario'}), 500

# Actualizar usuario
@usuarioapi.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def updateUsuario(id_usuario):
    data = request.get_json() or {}
    campos = ['nickname', 'clave', 'estado']
    faltantes = [c for c in campos if c not in data or not str(data[c]).strip()]
    if faltantes:
        return jsonify({'success': False, 'error': f'Faltan campos: {", ".join(faltantes)}'}), 400
    dao = UsuarioDao()
    if dao.updateUsuario(id_usuario, data['nickname'], data['clave'], data['estado']):
        return jsonify({'success': True, 'data': {'id_usuario': id_usuario, 'nickname': data['nickname'], 'estado': data['estado']}, 'error': None}), 200
    return jsonify({'success': False, 'error': 'No se pudo actualizar el usuario'}), 404

# Eliminar usuario
@usuarioapi.route('/usuarios/<int:id_usuario>', methods=['DELETE'])
def deleteUsuario(id_usuario):
    dao = UsuarioDao()
    if dao.deleteUsuario(id_usuario):
        return jsonify({'success': True, 'mensaje': f'Usuario {id_usuario} eliminado', 'error': None}), 200
    return jsonify({'success': False, 'error': 'No se pudo eliminar el usuario'}), 404



loginapi = Blueprint('loginapi', __name__)

@usuarioapi.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    nickname = data.get('nickname')
    clave = data.get('clave')

    if not nickname or not clave:
        return jsonify(success=False, error="Faltan datos de login"), 400

    usuariodao = UsuarioDao()
    usuario = usuariodao.verificarLogin(nickname, clave)
    if usuario:
        return jsonify(success=True, data=usuario, error=None), 200
    return jsonify(success=False, error="Usuario o contraseña incorrecta"), 401

