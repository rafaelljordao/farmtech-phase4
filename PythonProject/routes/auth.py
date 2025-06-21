from flask import Blueprint, request, jsonify

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'test' and password == '123':
        return jsonify({'message': 'Login bem-sucedido!'}), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401
