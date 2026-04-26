import os

# Dossier de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base de données SQLite
DATABASE = os.path.join(BASE_DIR, 'database.db')

# Configuration Flask
SECRET_KEY = 'datacollector2026'
DEBUG = True