from flask import Blueprint, request, jsonify, session
from models import User

auth_bp = Blueprint('auth', __name__)

# Route 1 : Inscription
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Tous les champs sont obligatoires'}), 400

    if len(password) < 6:
        return jsonify({
            'error': 'Le mot de passe doit avoir au moins 6 caractères'
        }), 400

    user = User(name, email, password)
    success = user.save()

    if not success:
        return jsonify({'error': 'Cet email est déjà utilisé'}), 409

    return jsonify({'message': 'Compte créé avec succès'}), 201


# Route 2 : Connexion
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email et mot de passe obligatoires'}), 400

    user = User.verify_password(email, password)

    if not user:
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401

    # Sauvegarder l'utilisateur dans la session
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']

    return jsonify({
        'message': 'Connexion réussie',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }), 200


# Route 3 : Déconnexion
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Déconnexion réussie'}), 200


# Route 4 : Vérifier si connecté
@auth_bp.route('/me', methods=['GET'])
def me():
    if 'user_id' not in session:
        return jsonify({'error': 'Non connecté'}), 401

    return jsonify({
        'user': {
            'id': session['user_id'],
            'name': session['user_name'],
            'email': session['user_email']
        }
    }), 200