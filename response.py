from flask import Blueprint, request, jsonify, send_file
import json
import os
import csv
import io
import pandas as pd
import numpy as np
from models import Response, Form

response_bp = Blueprint('response', __name__)

# Route 1 : Soumettre une réponse
@response_bp.route('/forms/<form_id>/submit', methods=['POST'])
def submit_response(form_id):
    form = Form.get_by_id(form_id)
    if not form:
        return jsonify({'error': 'Formulaire introuvable'}), 404

    data = request.get_json()
    if not data or not data.get('answers'):
        return jsonify({'error': 'Réponses vides'}), 400

    answers = data['answers']

    # Validation des réponses
    for key, value in answers.items():
        if value == '' or value is None:
            return jsonify({
                'error': f'La question {key} est vide'
            }), 400

        # Vérifier les nombres
        try:
            num = float(value)
            if num < 0:
                return jsonify({
                    'error': 'Les valeurs négatives ne sont pas acceptées'
                }), 400
            if num > 150:
                return jsonify({
                    'error': 'Valeur trop grande'
                }), 400
        except ValueError:
            pass

    response = Response(form_id, answers)
    response.save()
    return jsonify({'message': 'Réponse enregistrée avec succès'}), 201

# Route 2 : Récupérer toutes les réponses
@response_bp.route('/forms/<form_id>/responses', methods=['GET'])
def get_responses(form_id):
    responses = Response.get_all(form_id)
    if not responses:
        return jsonify({'error': 'Aucune réponse encore'}), 404
    return jsonify(responses), 200


# Route 3 : Analyse descriptive
@response_bp.route('/forms/<form_id>/analysis', methods=['GET'])
def analyze(form_id):
    responses = Response.get_all(form_id)

    if not responses:
        return jsonify({'error': 'Aucune réponse encore'}), 404

    # Construire un DataFrame depuis les réponses
    rows = []
    for r in responses:
        rows.append(r['answers'])

    df = pd.DataFrame(rows)

    if df.empty:
        return jsonify({'error': 'Aucune donnée'}), 404

    analysis = {}
    for column in df.columns:
        col_data = df[column]

        # Essayer de convertir en numérique
        numeric = pd.to_numeric(col_data, errors='coerce')

        if numeric.notna().sum() > numeric.isna().sum():
            analysis[column] = {
                'type': 'numerique',
                'count': int(col_data.count()),
                'mean': round(float(numeric.mean()), 2),
                'median': round(float(numeric.median()), 2),
                'std': round(float(numeric.std()), 2),
                'min': round(float(numeric.min()), 2),
                'max': round(float(numeric.max()), 2)
            }
        else:
            analysis[column] = {
                'type': 'categoriel',
                'count': int(col_data.count()),
                'unique': int(col_data.nunique()),
                'distribution': col_data.value_counts().to_dict()
            }

    return jsonify(analysis), 200


# Route 4 : Exporter en CSV
@response_bp.route('/forms/<form_id>/export', methods=['GET'])
def export(form_id):
    responses = Response.get_all(form_id)

    if not responses:
        return jsonify({'error': 'Aucune donnée à exporter'}), 404

    # Construire le CSV en mémoire
    output = io.StringIO()
    rows = [r['answers'] for r in responses]

    if not rows:
        return jsonify({'error': 'Aucune donnée'}), 404

    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'responses_{form_id}.csv'
    )


# Route 5 : Compter les réponses
@response_bp.route('/forms/<form_id>/count', methods=['GET'])
def count_responses(form_id):
    total = Response.count(form_id)
    return jsonify({'count': total}), 200
