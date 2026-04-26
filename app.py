import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, redirect, session
from flask_cors import CORS
import config

app = Flask(
    __name__,
    template_folder='frontend',
    static_folder='frontend/static'
)

app.secret_key = config.SECRET_KEY
CORS(app)

from routes.form import form_bp
from routes.response import response_bp
from routes.auth import auth_bp

app.register_blueprint(form_bp, url_prefix='/api')
app.register_blueprint(response_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create-form')
def create_form():
    return render_template('create_form.html')

@app.route('/fill-form/<form_id>')
def fill_form(form_id):
    return render_template('fill_form.html', form_id=form_id)

@app.route('/result/<form_id>')
def result_form(form_id):
    return render_template('result_form.html', form_id=form_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    from models import init_db
    init_db()
    print("✅ Base de données initialisée !")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)