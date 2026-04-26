from flask import Blueprint, request, jsonify, session
from models import Form

form_bp = Blueprint('form', __name__)

# Route 1 : Récupérer les formulaires de l'utilisateur connecté
@form_bp.route('/forms', methods=['GET'])
def get_forms():
    user_id = session.get('user_id')
    forms = Form.get_all(user_id=user_id)
    return jsonify(forms), 200

# Route 2 : Créer un formulaire
@form_bp.route('/forms', methods=['POST'])
def create_form():
    data = request.get_json()

    if not data.get('title') or not data.get('questions'):
        return jsonify({
            'error': 'Titre et questions obligatoires'
        }), 400

    user_id = session.get('user_id')

    form = Form(
        title=data['title'],
        description=data.get('description', ''),
        questions=data['questions']
    )
    form_id = form.save(user_id=user_id)
    return jsonify({'message': 'Formulaire créé', 'id': form_id}), 201

# Route 3 : Récupérer un formulaire par son ID
@form_bp.route('/forms/<form_id>', methods=['GET'])
def get_form(form_id):
    form = Form.get_by_id(form_id)
    if not form:
        return jsonify({'error': 'Formulaire introuvable'}), 404
    return jsonify(form), 200