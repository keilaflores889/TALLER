from flask import Blueprint, request, jsonify, current_app as app
from app.dao.usuario.usuarioDao import UsuarioDao

usuarioapi = Blueprint('usuarioapi', __name__)

# Trae todos los usuarios
@usuarioapi.route('/usuarios', methods=['GET'])
def getUsuarios():
    usuariodao = UsuarioDao()

    try:
        usuarios = usuariodao.getUsuarios()

        return jsonify({
            'success': True,
            'data': usuarios,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los usuarios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@usuarioapi.route('/usuarios/<int:usuario_id>', methods=['GET'])
def getUsuario(usuario_id):
    usuariodao = UsuarioDao()

    try:
        usuario = usuariodao.getUsuarioById(usuario_id)

        if usuario:
            return jsonify({
                'success': True,
                'data': usuario,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el usuario con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# Agrega un nuevo usuario
@usuarioapi.route('/usuarios', methods=['POST'])
def addUsuario():
    data = request.get_json()
    usuariodao = UsuarioDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['nickname', 'clave', 'estado']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                            'success': False,
                            'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
                            }), 400

    try:
        nickname = data['nickname']
        clave = data['clave']
        estado = data['estado']
        usuario_id = usuariodao.guardarUsuario(nickname, clave, estado)
        if usuario_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_usuario': usuario_id, 'nickname': nickname, 'clave': clave, 'estado': estado},
                'error': None
            }), 201
        else:
            return jsonify({ 'success': False, 'error': 'No se pudo guardar el usuario. Consulte con el administrador.' }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@usuarioapi.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def updateUsuario(usuario_id):
    data = request.get_json()
    usuariodao = UsuarioDao()

    # Validar que el JSON no esté vacío y tenga las propiedades necesarias
    campos_requeridos = ['nickname', 'clave', 'estado']

    # Verificar si faltan campos o son vacíos
    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or len(data[campo].strip()) == 0:
            return jsonify({
                            'success': False,
                            'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
                            }), 400
    nickname = data['nickname']
    clave = data['clave']
    estado = data['estado']
    
    try:
        if usuariodao.updateUsuario(usuario_id, nickname, clave, estado):
            return jsonify({
                'success': True,
                'data': {'id_usuario': usuario_id, 'nickname': nickname, 'clave': clave, 'estado': estado},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró al usuario con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

@usuarioapi.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
def deleteUsuario(usuario_id):
    usuariodao = UsuarioDao()

    try:
        # Usar el retorno de eliminarUsuario para determinar el éxito
        if usuariodao.deleteUsuario(usuario_id):
            return jsonify({
                'success': True,
                'mensaje': f'Usuario con ID {usuario_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el usuario con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
